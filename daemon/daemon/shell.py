import os
import subprocess
import logging as log
import asyncio
from websockets.exceptions import ConnectionClosed

SHELL_PROMPT_PREFIX = "[easyshell] "

class ShellProfile:
    def __init__(self, ps1="", shell_args=[]):
        self.ps1 = ps1
        self.shell_args = shell_args

class BashProfile(ShellProfile):
    def __init__(self):
        super().__init__(
            ps1=SHELL_PROMPT_PREFIX + "\\u@\\h: \\w\\$ ",
            shell_args=["--norc"]
        )

class ZshProfile(ShellProfile):
    def __init__(self):
        super().__init__(
            ps1=SHELL_PROMPT_PREFIX + "%n@%m: %~%# ",
            shell_args=["--no-rcs"]
        )

class ShProfile(ShellProfile):
    def __init__(self):
        super().__init__(ps1=SHELL_PROMPT_PREFIX + "$ ")

class Shell:
    """Class to interface with the system shell."""

    def __init__(self, forced_shell=None):
        self.shell = self.get_shell(forced_shell)
        self.home_directory = self.get_home_directory()
        self.username = self.get_username()

        self.input_func = None
        self.output_func = None

        self.shell_profile = None
        if "bash" in self.shell:
            self.shell_profile = BashProfile()
        elif "zsh" in self.shell:
            self.shell_profile = ZshProfile()
        else:
            raise ValueError(f"Unsupported shell: {self.shell}")
        
        self.alive = asyncio.Event()
        self._tasks = []

    def get_shell(self, forced=None):
        """Get the user's preferred shell from the environment."""
        if forced:
            return forced
        
        return os.getenv("SHELL", "/bin/sh")

    def get_home_directory(self):
        """Get the user's home directory from the environment."""
        return os.getenv("HOME", "/home/user")
    
    def get_username(self):
        """Get the current user's username from the environment."""
        return os.getenv("USER")
    
    def get_environment_variables(self):
        """Get a dictionary of relevant environment variables."""
        
        output = subprocess.check_output(["printenv"], text=True)
        env_vars = {}
        for line in output.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value

        env_vars["SHELL"] = self.shell
        env_vars["PS1"] = self.shell_profile.ps1

        return env_vars
    
    def set_input_source(self, input_func):
        """Set the input source for the shell."""
        self.input_func = input_func

    def set_output_sink(self, output_func):
        """Set the output sink for the shell."""
        self.output_func = output_func

    async def enter(self):
        """
        Enter an interactive shell session.
        It keeps track of the user's environment, 
        especially $PATH, $USER, $HOME and the current working directory.
        """
        if not self.input_func or not self.output_func:
            raise ValueError("Input source and output sink must be set before entering shell.")

        log.info(f"Running: {[self.shell, *self.shell_profile.shell_args]}")
        
        self.alive.set()
        process = subprocess.Popen(
            [self.shell, *self.shell_profile.shell_args],
            env=self.get_environment_variables(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        async def read_stdout():
            try:
                loop = asyncio.get_running_loop()
                while self.alive.is_set():
                    output = await loop.run_in_executor(None, process.stdout.readline)
                    if output:
                        self.output_func(output)
                    if process.poll() is not None:  # returns int (exit status) or none
                        break
            except asyncio.CancelledError:
                raise

        async def feed_stdin():
            try:
                while self.alive.is_set() and process.stdin:
                    try:
                        input_data = await self.input_func()
                        if input_data:
                            process.stdin.write(input_data + "\n")  # 'enter'
                            process.stdin.flush()
                    except ConnectionClosed:
                        log.info("Input connection closed. Exiting shell input.")
                        break
                    except Exception as e:
                        log.info(f"Error while writing to shell: {e}")
            except asyncio.CancelledError:
                raise

        self._tasks = [
            asyncio.create_task(read_stdout()),
            asyncio.create_task(feed_stdin())
        ]

        try:
            await asyncio.wait(self._tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
            self.alive.clear()
            if process.poll() is None:
                process.terminate()
                try:
                    await asyncio.get_running_loop().run_in_executor(None, process.wait)
                except Exception:
                    process.kill()

    async def exit(self):
        self.alive.clear()
        for t in self._tasks:
            t.cancel()
        self._tasks.clear()
        log.info("Shell session ended.")
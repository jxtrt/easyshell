import os
import subprocess

class ShellProfile:
    def __init__(self, ps1="", shell_args=None):
        self.ps1 = ps1
        self.shell_args = shell_args

class BashProfile(ShellProfile):
    def __init__(self):
        super().__init__(
            ps1="[easyshell] \\u@\\h: \\w\\$ ",
            shell_args=["--norc"]
        )

class ZshProfile(ShellProfile):
    def __init__(self):
        super().__init__(
            ps1="[easyshell] %n@%m: %~%# ",
            shell_args=["--no-rcs"]
        )

class ShProfile(ShellProfile):
    def __init__(self):
        super().__init__(ps1="$ ")

class Shell:
    """Class to interface with the system shell."""

    def __init__(self, forced_shell=None):
        self.shell = self.get_shell(forced_shell)
        self.home_directory = self.get_home_directory()
        self.username = self.get_username()

        self.shell_profile = None
        if "bash" in self.shell:
            self.shell_profile = BashProfile()
        elif "zsh" in self.shell:
            self.shell_profile = ZshProfile()
        else:
            raise ValueError(f"Unsupported shell: {self.shell}")

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
    
    def enter(self):
        """
        Enter an interactive shell session.
        It keeps track of the user's environment, 
        especially $PATH, $USER, $HOME and the current working directory.
        """
        try:
            print(f"Running: {[self.shell, *self.shell_profile.shell_args]}")
            subprocess.run(
                [self.shell, *self.shell_profile.shell_args],
                env=self.get_environment_variables(),
                check=True
            )
        except FileNotFoundError:
            print(f"Shell {self.shell} not found. Falling back to /bin/sh.")
            subprocess.run(
                ["/bin/sh"], 
                env=self.get_environment_variables(),
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while entering shell: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


        # Note: This will open a new shell session.
        # The user can exit this session to return to the main program.


import os
import subprocess

class Shell:
    """Class to interface with the system shell."""

    def __init__(self):
        self.shell = self.get_shell()
        self.home_directory = self.get_home_directory()
        self.username = self.get_username()

    def get_shell(self):
        """Get the user's preferred shell from the environment."""
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
        return env_vars
    
    def run_line(self, line: str):
        """Run a single line of shell command."""
        process = subprocess.Popen(
            [self.shell, "-c", line],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.get_environment_variables()
        )
        stdout, stderr = process.communicate()

        return {
            "code": process.returncode, 
            "stdout": stdout.decode(), 
            "stderr": stderr.decode()
        }
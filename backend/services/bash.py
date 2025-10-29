import subprocess
from typing import Any, Dict, List
from google.genai import types
import re
import shlex
class Bash:
    """
    An implementation of a tool that executes Bash commands
    """
    def __init__(self, config):
        self.config = config

        self.cwd = config.root_dir  # The current working directory
        self._allowed_commands = config.allowed_commands  # Allowed commands

    def exec_bash_command(self, cmd: str) -> Dict[str, str]:
        """
        Execute the bash command after checking the allowlist.
        """
        if cmd:
            # Prevent command injection via backticks or $. This blocks variables too.
            if re.search(r"[`$]", cmd):
                return {"error": "Command injection patterns are not allowed."}

            # Check the allowlist
            for cmd_part in self._split_commands(cmd):
                if cmd_part not in self.config.allowed_commands:
                    return {"error": "Parts of this command were not in the allowlist."}

            return self._run_bash_command(cmd)

        return {"error": "No command was provided"}

    def _split_commands(self, cmd_str) -> List[str]:
        """
        Split a command string into individual commands, without the parameters.
        """
        parts = re.split(r'[;&|]+', cmd_str)
        commands = []

        for part in parts:
            tokens = shlex.split(part.strip())

            if tokens:
                commands.append(tokens[0])

        return commands
 
    def to_json_schema(self) -> Dict[str, Any]:
        """
        Convert the function signature to a JSON schema for LLM tool calling.
        """
        return types.FunctionDeclaration(
            name="exec_bash_command",
            description="Executes a bash command in the shell and returns the output or error.",
            parameters={
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "The bash command to execute"
                    }
                },
                "required": ["cmd"],
            })
 
    def _run_bash_command(self, cmd: str) -> Dict[str, str]:
        """
        Runs the bash command and catches exceptions (if any).
        """
        stdout = ""
        stderr = ""
        new_cwd = self.cwd
 
        try:
            # Wrap the command so we can keep track of the working directory.
            wrapped = f"{cmd};echo __END__;pwd"
            result = subprocess.run(
                wrapped, shell=True, cwd=self.cwd,
                capture_output=True, text=True,
                # executable="/bin/bash"
            )
            stderr = result.stderr
            # Find the separator marker
            split = result.stdout.split("__END__")
            stdout = split[0].strip()
 
            # If no output/error at all, inform that the call was successful.
            if not stdout and not stderr:
                stdout = "Command executed successfully, without any output."
 
            # Get the new working directory, and change it
            new_cwd = split[-1].strip()
            self.cwd = new_cwd
        except Exception as e:
            stdout = ""
            stderr = str(e)

        if "du" in cmd and not stderr:
            stdout = self._format_du_output(stdout)

        return {"stdout": stdout, "stderr": stderr, "cwd": new_cwd}

    def _format_du_output(self, output: str) -> str:
        lines = output.strip().split('\n')
        formatted_lines = []
        for line in lines:
            parts = line.split('\t')
            if len(parts) == 2:
                size, name = parts[0], parts[1]
                formatted_lines.append(f"- {name}: {size}")
        return "\n".join(formatted_lines)
import subprocess
import os

class DockerManager:
    def __init__(self, installation_dir="~/.mark2tex"):
        self.installation_dir = os.path.expanduser(installation_dir)

    def compile(self, input_file, template):
        """
        Executes the Mark2TeX build inside a Docker container with double volume mapping.

        :param input_file: The markdown file to compile.
        :param template: The template type (tcc, artigo, projeto).
        :return: A generator that yields stdout/stderr lines.
        """
        cwd = os.getcwd()

        # The command based on the design spec:
        # docker run --rm --user $(id -u):$(id -g) -v PWD:/app -v ~/.mark2tex/templates:/app/templates mark2tex bash /app/bin/build.sh "$INPUT" "$TEMPLATE"

        # We use subprocess.Popen to stream output in real-time
        command = [
            "docker", "run", "--rm",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-v", f"{cwd}:/app",
            "-v", f"{self.installation_dir}/templates:/app/templates",
            "mark2tex",
            "bash", "/opt/mark2tex/bin/build.sh", input_file, template
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in process.stdout:
            yield line

        process.wait()
        if process.returncode != 0:
            yield f"\n❌ Error: Docker process exited with code {process.returncode}"

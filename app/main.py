import os
import shutil
import subprocess
import sys
import tempfile

def main():
    command = sys.argv[3]
    args = sys.argv[4:]

    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(command, tmpdir)
        os.chroot(tmpdir)
        completed_process = subprocess.Popen(
            [command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = completed_process.communicate()
        if stdout:
            print(stdout.decode("utf-8"), end="")
        if stderr:
            print(stderr.decode("utf-8"), end="", file=sys.stderr)
        sys.exit(completed_process.returncode)

if __name__ == "__main__":
    main()
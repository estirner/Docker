import os
import shutil
import subprocess
import sys
import tempfile

def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    directory_path = tempfile.mkdtemp()
    shutil.copy2(command, directory_path)
    os.chroot(directory_path)
    command = os.path.join("/", os.path.basename(command))
    completed_process = subprocess.run([command, *args], capture_output=True)
    print(completed_process.stdout.decode(), end="")
    print(completed_process.stderr.decode(), end="", file=sys.stderr)
    exit(completed_process.returncode)

if __name__ == "__main__":
    main()
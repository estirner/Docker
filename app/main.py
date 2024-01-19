import subprocess
import sys

def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    
    completed_process = subprocess.Popen(
        [command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = completed_process.communicate()
    if stdout:
        print(stdout.decode("utf-8"), end="")
    if stderr:
        print(stderr.decode("utf-8"), end="", file=sys.stderr)

if __name__ == "__main__":
    main()
import subprocess
import sys

def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    
    completed_process = subprocess.Popen([command, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = completed_process.communicate()

    if stdout:
        print(stdout.decode("utf-8").rstrip(), end="")

if __name__ == "__main__":
    main()
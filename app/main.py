import subprocess
import sys


def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    
    completed_process = subprocess.run([command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(completed_process.stdout.decode("utf-8"))


if __name__ == "__main__":
    main()
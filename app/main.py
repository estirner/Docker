import subprocess
import sys


def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    
    completed_process = subprocess.run([command, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Output:", completed_process.stdout.decode("utf-8"))
    print("Error:", completed_process.stderr.decode("utf-8"))


if __name__ == "__main__":
    main()
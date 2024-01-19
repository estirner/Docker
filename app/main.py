import subprocess
import sys


def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    
    try:
        output = subprocess.check_output([command, *args], stderr=subprocess.STDOUT)
        print(output.decode("utf-8").rstrip(), end="\n")
    except subprocess.CalledProcessError as e:
        print(e.output.decode("utf-8").rstrip(), end="")


if __name__ == "__main__":
    main()
import os
import shutil
import subprocess
import sys
import tempfile
import ctypes
import requests
import tarfile
import json

DOCKER_REGISTRY = "https://registry-1.docker.io"

def authenticate(image):
    response = requests.get(f"{DOCKER_REGISTRY}/v2/{image}/manifests/latest", headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"})
    auth_url = response.headers["Www-Authenticate"].split(" ")[1].split(",")[0].split("=")[1].strip('"')
    token_response = requests.get(auth_url)
    token = token_response.json()["token"]
    return token

def fetch_manifest(image, token):
    headers = {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{DOCKER_REGISTRY}/v2/{image}/manifests/latest", headers=headers)
    return response.json()

def pull_and_extract_layers(image, manifest, token, directory_path):
    headers = {"Authorization": f"Bearer {token}"}
    for layer in manifest["layers"]:
        response = requests.get(f"{DOCKER_REGISTRY}/v2/{image}/blobs/{layer['digest']}", headers=headers, stream=True)
        file = tarfile.open(fileobj=response.raw, mode="r|*")
        file.extractall(path=directory_path)

def main():
    image = "library/python"
    command = sys.argv[3]
    args = sys.argv[4:]

    token = authenticate(image)
    manifest = fetch_manifest(image, token)

    directory_path = tempfile.mkdtemp()
    pull_and_extract_layers(image, manifest, token, directory_path)

    shutil.copy2(command, directory_path)
    os.chroot(directory_path)
    command = os.path.join("/", os.path.basename(command))

    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    libc.unshare(0x20000000)

    completed_process = subprocess.run(
        [command, *args],
        capture_output=True
    )

    print(completed_process.stdout.decode(), end="")
    print(completed_process.stderr.decode(), end="", file=sys.stderr)
    exit(completed_process.returncode)

if __name__ == "__main__":
    main()
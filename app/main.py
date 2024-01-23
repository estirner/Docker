import os
import shutil
import subprocess
import sys
import tempfile
import ctypes
import urllib.request
import urllib.error
import tarfile
import json

DOCKER_REGISTRY = "https://registry-1.docker.io"

def authenticate(image):
    tag = "latest"
    if ":" in image:
        image, tag = image.split(":")    
    request = urllib.request.Request(
        f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image}:pull",
        None,
        {},
    )
    token_response = urllib.request.urlopen(request)
    data = json.loads(token_response.read().decode("utf-8"))
    return data["access_token"]

def fetch_manifest(image, token):
    request = urllib.request.Request(
        f"https://registry.hub.docker.com/v2/library/{image}/manifests/{tag}",
        headers={
            "Accept": "application/vnd.docker.distribution.manifest.v2+json",
            "Authorization": f"Bearer {token}",
        },
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode("utf-8"))

def pull_and_extract_layers(image, manifest, token, directory_path):
    for layer in manifest["layers"]:
        request = urllib.request.Request(
            f"https://registry.hub.docker.com/v2/library/{image}/blobs/{layer['digest']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response = urllib.request.urlopen(request)
        layer_file = os.path.join(directory_path, "layer.tar")
        with open(layer_file, "wb") as f:
            shutil.copyfileobj(response, f)
        with tarfile.open(layer_file) as tar:
            tar.extractall(path=directory_path)
        os.remove(layer_file)

def main():
    command = sys.argv[3]
    args = sys.argv[4:]
    image = sys.argv[2]

    directory_path = tempfile.mkdtemp()
    token = authenticate(image)
    manifest = fetch_manifest(image, token)
    pull_and_extract_layers(image, manifest, token, directory_path)
    command = os.path.join("/", command.lstrip("/"))
    os.chroot(directory_path)
    os.chdir("/")

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
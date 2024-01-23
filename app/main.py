import os
import shutil
import subprocess
import sys
import tempfile
import ctypes
import json
import base64
import urllib.request
import tarfile
import io

DOCKER_REGISTRY_URL = "https://registry-1.docker.io/v2/"

def authenticate(image):
    try:
        response = urllib.request.urlopen(DOCKER_REGISTRY_URL + "/" + image + "/manifests/latest")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            auth_info = e.info()['Www-Authenticate']
            auth_url = auth_info.split('"')[1]
            auth_response = urllib.request.urlopen(auth_url)
            token = json.loads(auth_response.read().decode())['token']
            return token
        else:
            raise e

def fetch_manifest(image, token):
    request = urllib.request.Request(DOCKER_REGISTRY_URL + "/" + image + "/manifests/latest")
    request.add_header("Authorization", "Bearer " + token)
    response = urllib.request.urlopen(request)
    manifest = json.loads(response.read().decode())
    return manifest

def pull_and_extract_layers(image, manifest, token, directory_path):
    for layer in manifest['layers']:
        request = urllib.request.Request(DOCKER_REGISTRY_URL + "/" + image + "/blobs/" + layer['digest'])
        request.add_header("Authorization", "Bearer " + token)
        response = urllib.request.urlopen(request)
        layer_tar = tarfile.open(fileobj=io.BytesIO(response.read()))
        layer_tar.extractall(path=directory_path)

def main():
    image = sys.argv[2].split(':')[0]
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
        ["unshare", "--fork", "--pid", "--mount-proc", command, *args],
        capture_output=True
    )

    print(completed_process.stdout.decode(), end="")
    print(completed_process.stderr.decode(), end="", file=sys.stderr)

    exit(completed_process.returncode)

if __name__ == "__main__":
    main()
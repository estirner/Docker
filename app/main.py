import os
import shutil
import subprocess
import sys
import tempfile
import ctypes
import json
import urllib.request
import tarfile
import io

DOCKER_REGISTRY_URL = "https://registry-1.docker.io/v2/"

def authenticate(image):
    try:
        request = urllib.request.Request(DOCKER_REGISTRY_URL + "/" + image + "/manifests/latest")
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            auth_info = e.info()['Www-Authenticate']
            realm, service, _ = map(lambda x: x.split('=')[1].strip('"'), auth_info.split(','))
            auth_url = f"{realm}?service={service}&scope=repository:{image}:pull"
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
        [command, *args],
        capture_output=True
    )

    print(completed_process.stdout.decode(), end="")
    print(completed_process.stderr.decode(), end="", file=sys.stderr)

    exit(completed_process.returncode)

if __name__ == "__main__":
    main()
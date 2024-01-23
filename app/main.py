import os
import shutil
import subprocess
import sys
import tempfile
import ctypes
import urllib.request
import tarfile
import json
import urllib.parse

def main():
    image_name = sys.argv[1]
    image_tag = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]

    directory_path = tempfile.mkdtemp()
    shutil.copy2(command, directory_path)
    os.chroot(directory_path)
    command = os.path.join("/", os.path.basename(command))

    libc = ctypes.cdll.LoadLibrary("libc.so.6")
    libc.unshare(0x20000000)

    base_url = "https://registry.hub.docker.com"
    if "/" not in image_name:
        image_name = "library/" + image_name
    manifest_url = f"{base_url}/v2/{image_name}/manifests/{image_tag}"
    manifest_url = urllib.parse.quote(manifest_url, safe=":/")
    manifest_request = urllib.request.Request(manifest_url, headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"})
    with urllib.request.urlopen(manifest_request) as manifest_response:
        if manifest_response.status == 200:
            manifest = json.load(manifest_response)
            layers = manifest["layers"]
            for layer in layers:
                digest = layer["digest"]
                blob_url = f"{base_url}/v2/{image_name}/blobs/{digest}"
                blob_url = urllib.parse.quote(blob_url, safe=":/")
                blob_request = urllib.request.Request(blob_url)
                with urllib.request.urlopen(blob_request) as blob_response:
                    if blob_response.status == 200:
                        with tempfile.NamedTemporaryFile() as layer_file:
                            shutil.copyfileobj(blob_response, layer_file)
                            layer_file.flush()
                            with tarfile.open(layer_file.name) as tar:
                                tar.extractall(path="/")
                    else:
                        print(f"Error: Failed to fetch layer {digest}", file=sys.stderr)
        else:
            print(f"Error: Failed to fetch manifest for {image_name}:{image_tag}", file=sys.stderr)

    completed_process = subprocess.run(
        [command, *args],
        capture_output=True
    )

    print(completed_process.stdout.decode(), end="")
    print(completed_process.stderr.decode(), end="", file=sys.stderr)
    exit(completed_process.returncode)

if __name__ == "__main__":
    main()
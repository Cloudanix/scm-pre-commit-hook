import argparse
import json
import os
import platform
import shutil
import subprocess
from zipfile import ZipFile

import requests
from rich.console import Console

BINARY_VERSION = "v0.0.4-5"

PRE_COMMIT_VERSION = os.environ.get('PRE_COMMIT_VERSION')
if PRE_COMMIT_VERSION:
    print(f"PRE_COMMIT_VERSION: {PRE_COMMIT_VERSION}")
    BINARY_VERSION = PRE_COMMIT_VERSION

console = Console()


def get_arch():
    arch = platform.machine().lower()
    console.print(f"Architecture: {arch}")

    if arch in ["x86_64", "i386"]:
        return "amd64"

    elif arch in ["aarch64", "arm64", "arm"]:
        return "arm"

    else:
        return None


def get_os():
    system_name = platform.system().lower()
    console.print(f"System: {system_name}")

    if system_name == "linux":
        return "linux"

    elif system_name == "darwin":
        return "macos"

    else:
        return None


def setup_scanner():
    OS = get_os()
    ARCH = get_arch()
    if not OS or not ARCH:
        console.print("Failed to determine OS and Architecture of the machine")
        return False

    console.print(f"Downloading scanner for {OS} - {ARCH}")

    cache_path = os.path.join(os.getenv("HOME"), ".cache", "pre-commit")
    console.print(f"Cache Path: {cache_path}")

    if not os.path.exists(cache_path):
        os.makedirs(cache_path, exist_ok=True)

    scanner_archive = f"{OS}-{ARCH}-pre-commit-{BINARY_VERSION}.zip"
    scanner_archive_path = os.path.join(cache_path, scanner_archive)
    console.print(f"Scanner archive Path: {scanner_archive_path}")

    if not os.path.exists(scanner_archive_path):
        console.print(f"Latest version is getting downloaded: {BINARY_VERSION}")

        scanner_download_url = f"http://localhost:3000/download?file_name={scanner_archive}"
        response = requests.get(scanner_download_url)
        if response.status_code == 200:
            with open(scanner_archive_path, "wb") as f:
                f.write(response.content)

            console.print(f"Latest version downloaded successfully: {scanner_download_url}")

        else:
            console.print(f"Failed to upgrade scanner: {scanner_download_url}")
            return False

    if os.path.exists(scanner_archive_path):
        console.print(f"Latest version of scanner available: {BINARY_VERSION}")

    else:
        return False

    try:
        with ZipFile(scanner_archive_path, 'r') as zObject:
            zObject.extractall(path="cloudanix/")

        os.chmod("cloudanix/main", 0o755)

        return True

    except Exception as e:
        console.print(f"Failed to elevate privileges for scanner: {e}")
        return False


def transfer_files(filenames): 
    os.makedirs("cloudanix/action", exist_ok=True)

    for filename in filenames:
        os.makedirs(f"cloudanix/action/{filename}", exist_ok=True)
        shutil.copy(filename, f"cloudanix/action/{filename}")


def print_secrets(data: list[dict]):
    if data:
        console.print("[bold][red][center]Secrets:")
        for result in data:
            console.print(f"[bold]{result['regex']}")
            console.print(f"[#FFFFFF]File: {result['fileName']}")
            console.print(f"[#FFFFFF]Hashed Value: {result['hashedValue']}")
            console.print(f"[#FFFFFF]Line number: {result['lineNumber']}")
            console.print("\n")


def print_vulnerabilities(data):
    if data:
        console.print("[bold][red][center]Vulnerabilities:")
        for result in data:
            console.print(f"[bold]{result['category']}")
            console.print(f"[#FFFFFF]File: {result['path']}")
            console.print(f"[#FFFFFF]lines: {result['lines']}")
            console.print(f"[#FFFFFF]{result['message']}")
            console.print(f"[#FFFFFF]Start: {result['start']} End: {result['end']}")
            console.print("\n")

    else:
        console.print("No vulnerabilities found")


def delete_files():
    os.makedirs("cloudanix/", exist_ok=True)
    shutil.rmtree("cloudanix")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    console.print(f"Processing files: {args.filenames}")

    # try:
    if setup_scanner() is False:
        console.print("Failed to setup scanner")
        return 0

    transfer_files(filenames=args.filenames)

    proc = subprocess.run(["cd cloudanix && ./main"], shell=True, text=True, capture_output=True)
    print(proc.returncode)
    print(proc.stdout)
    print(proc.stderr)
    if proc.returncode != 0:
        console.print(f"Failed to run hook: {proc.stderr}")
        return 0

    # try:
    results = json.loads(proc.stdout)
    if results.get("secrets"):
        print_secrets(results["secrets"])

    else:
        console.print("No secrets found")

    if results.get("vulnerabilities"):
        print_vulnerabilities(results["vulnerabilities"])

    else:
        console.print("No vulnerabilities found")

    if results["secrets"] or results["vulnerabilities"]:
        print(results)
        return 1

    # except Exception as e:
    #     console.print(f"Failed to parse output: {e}")
    #     return 0

    # except Exception as e:
    #     console.print(f"Failed to scan files for Secrets or Vulnerabilities: {e}")
    #     return 0

    # finally:
    # delete_files()

    console.print("Completed scanning process")

    return 0

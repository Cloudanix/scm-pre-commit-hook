import argparse
import os
import shutil
import subprocess
import json
from rich.console import Console
import requests
from zipfile import ZipFile 
import platform


BINARY_VERSION = "0.0.2"


def get_arch():
    arch = platform.machine()
    if arch == "x86_64":
        return "amd64"
    elif arch == "aarch64":
        return "arm"

def get_os():
    system_name = platform.system()
    
    if system_name == "Linux":
        return "linux"
    elif system_name == "Darwin":
        return "macos"
    else:
        return None



def setup_binary():
    OS = get_os()
    ARCH = get_arch()
    if not OS or not ARCH:
        return False
    zip_file = f"{OS}:{ARCH}-pre-commit-v{BINARY_VERSION}.zip"
    cache_path = os.path.join(os.getenv("HOME"), ".cache","pre-commit",zip_file)
    if not os.path.exists(cache_path):
        response = requests.get(f"https://console.cloudanix.com/download?file_name={zip_file}")
        with open(cache_path, "wb") as f:
            f.write(response.content)
        
    with ZipFile(cache_path, 'r') as zObject:
        zObject.extractall(path="cloudanix/")
    
    try:
        os.chmod("cloudanix/dist/main", 0o755)
    except Exception as e:
        print(f"Failed to escalate to executable permission: {e}")

def transfer_files(filenames): 
    os.makedirs("cloudanix/dist/action", exist_ok=True)
    for filename in filenames:
        os.makedirs(f"cloudanix/dist/action/{filename}", exist_ok=True)
        shutil.copy(filename, f"cloudanix/dist/action/{filename}")
        
def print_secrets(data: list[dict]):
    if data:
        console = Console()
        console.print("[bold][red][center]Secrets:")
        for result in data:
            console.print(f"[bold] {result['regex']}")
            console.print(f"[#FFFFFF]File: {result['fileName']}")
            console.print(f"[#FFFFFF]Hashed Value: {result['hashedValue']}")
            console.print(f"[#FFFFFF]Line number: {result['lineNumber']}")
            console.print("\n")

def print_vulnerabilities(data):
    if data:
        console = Console()
        console.print("[bold][red][center]Vulnerabilities:")
        for result in data:
            console.print(f"[bold] {result['category']}")
            console.print(f"[#FFFFFF]File: {result['path']}")
            console.print(f"[#FFFFFF]lines: {result['lines']}")
            console.print(f"[#FFFFFF]{result['message']}")
            console.print(f"[#FFFFFF]Start: {result['start']} End: {result['end']}")
            console.print("\n")

    else:
        print("No vulnerabilities found")
        
def delete_files():
    os.makedirs("cloudanix/", exist_ok=True)
    shutil.rmtree("cloudanix")
    

def main():
    parser = argparse.ArgumentParser()
    console = Console()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()
    if setup_binary() == False:
        console.print("Failed to setup binary")
        return 0
    
    transfer_files(filenames=args.filenames)
    
    proc = subprocess.run(["cd cloudanix/dist && ./main"], shell=True, text=True, capture_output=True)
    delete_files()
    if proc.returncode != 0:
        console.print(f"Failed to run hook: {proc.stderr}")
        return 0

    try:
        results = json.loads(proc.stdout)
        print_secrets(results["secrets"])
        print_vulnerabilities(results["vulnerabilities"])
        if results["secrets"] or results["vulnerabilities"]:
            return 1
            
    except Exception as e:
        console.print(f"Failed to parse output: {e}")
        return 0

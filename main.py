import argparse
import os
import shutil
import subprocess
import json
from rich.console import Console

def transfer_files(filenames): 
    os.makedirs("dist/action", exist_ok=True)
    for filename in filenames:
        shutil.copy(filename, f"dist/action/{filename}")
        
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
    os.makedirs("dist/action", exist_ok=True)
    shutil.rmtree("dist/action")
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()
    transfer_files(filenames=args.filenames)
    console = Console()
    proc = subprocess.run(["cd dist && ./main"], shell=True, text=True, capture_output=True)
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
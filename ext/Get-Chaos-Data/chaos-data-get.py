#!/usr/bin/env python3
import argparse
import os
import shutil
import zipfile
import json
import requests

# Helper functions for downloading and manipulating files

def download_file(url, output_dir, i):
    filename = url.split("/")[-1]
    filepath = os.path.join(output_dir, filename)

    print(f"\033[33mFound[{i}] Downloading {url} to {filepath}...\033[0m")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"\033[32mFinished downloading {url}\033[0m")
    return filepath


def unzip_file(filepath, output_dir):
    print(f"\033[33mUnzipping {filepath} to {output_dir}...\033[0m")
    with zipfile.ZipFile(filepath, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    print(f"\033[32mFinished unzipping {filepath}\033[0m")


def merge_files(input_dir, output_file, collect=False):
    print(f"\033[33mMerging files in {input_dir} into {output_file}...\033[0m")
    with open(output_file, "w") as outfile:
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)
            if filepath.endswith('.zip'):
                os.remove(filepath)
                continue
            with open(filepath, "r") as infile:
                outfile.write(infile.read())
            if collect:
                os.remove(filepath)

    print(f"\033[32mFinished merging files into {output_file}\033[0m")


# Set up argument parsing
parser = argparse.ArgumentParser(description="\033[36mDownload and manipulate URL lists\033[0m")
parser.add_argument("-p", "--platform", choices=["hackerone", "bugcrowd", "yeswehack", "null"],
                    help="\033[36mFilter URLs by platform\033[0m")
parser.add_argument("-n", "--name",
                    help="\033[36mFilter URLs by program name\033[0m")
parser.add_argument("-b", "--bounty", choices=["true", "false"],
                    help="\033[36mFilter URLs by bounty status\033[0m")
parser.add_argument("-a", "--all", action="store_true",
                    help="\033[36mDownload URLs from all programs\033[0m")
parser.add_argument("-o", "--output", default="chaos-output",
                    help="\033[36mOutput directory\033[0m")
args = parser.parse_args()

# Show help if no arguments provided
if not (args.platform or args.name or args.bounty or args.all):
    parser.print_help()
    exit()
    
# Download index.json file if it does not exist
if not os.path.exists('index.json'):
    print("Downloading https://chaos-data.projectdiscovery.io/index.json file.")
    json_url = 'https://chaos-data.projectdiscovery.io/index.json'
    r = requests.get(json_url)
    with open('index.json', 'wb') as f:
        f.write(r.content)
    
# Load the URL data from the index.json file
with open("index.json") as f:
    url_data = json.load(f)

# Filter the URL data based on the provided arguments
if args.platform:
    if args.platform == "null":
        url_data = [d for d in url_data if not d.get("platform")]
    else:
        url_data = [d for d in url_data if d.get("platform") == args.platform]
if args.name:
    url_data = [d for d in url_data if d.get("name") == args.name]

if args.bounty:
    url_data = [d for d in url_data if str(d.get("bounty")).lower() == args.bounty.lower()]

# Print the number of URLs found based on the provided arguments
print(f"\033[33mFound {len(url_data)} URLs to download.\033[0m")



if not os.path.exists(args.output):
    os.makedirs(args.output)

for i, d in enumerate(url_data, start=1):
    url = d.get("URL")
    filepath = download_file(url, args.output, i)
    unzip_file(filepath, args.output)
    os.remove(filepath)


merge_files(args.output, os.path.join(args.output, "merged.txt"))

# Print the message after all URLs have been downloaded and manipulated
print("Done!")

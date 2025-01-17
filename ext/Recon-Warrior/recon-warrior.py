#!/usr/bin/env python3

import argparse
import os
import subprocess
import glob
import shutil
from colorama import Fore, Style
from concurrent import futures

GITHUBTOKEN = '<your github token>'
CHAOS_KEY = '<your chaos key>'

def banner():
    banner = """
         \033[1;36m______                       _    _                 _            \033[0m
         \033[1;36m| ___ \                     | |  | |               (_)           \033[0m
         \033[1;36m| |_/ /___  ___ ___  _ __   | |  | | __ _ _ __ _ __ _  ___  _ __ \033[0m
         \033[1;36m|    // _ \/ __/ _ \| '_ \  | |/\| |/ _` | '__| '__| |/ _ \| '__|\033[0m
         \033[1;36m| |\ \  __/ (_| (_) | | | | \  /\  / (_| | |  | |  | | (_) | |   \033[0m
         \033[1;36m\_| \_\___|\___\___/|_| |_|  \/  \/ \__,_|_|  |_|  |_|\___/|_|   \033[0m

         \033[1;33m--------------------------------------------------\033[0m
         \033[0;31m[\033[0m\033[1;36m+\033[0m\033[0;31m]\033[0m \033[1;34mhttps://github.com/InfoSecWarrior/\033[0m
         \033[0;31m[\033[0m\033[1;36m+\033[0m\033[0;31m]\033[0m \033[0m\033[1;32mAutomation For Bug Hunting Web Reconnaissance\033[0m
         \033[1;33m--------------------------------------------------\033[0m
                                                \033[0;31mby @ArmourInfosec\033[0m
         """
    # Print the colored banner
    print(banner)

def run_passive_subdomain(domain, output_dir):
    commands = [
        (f"subfinder -all -d {domain} -silent >> {output_dir}/subfinder-{domain}-domains.txt",
         "Start Passive Subdomains Finding"),
        (f"amass enum -passive -d {domain} -silent -o {output_dir}/amass-{domain}-domains.txt",
         "Start Amass Passive Enum"),
        (f"findomain -t {domain} | grep -E '^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{{2,}}$' >> {output_dir}/findomain-{domain}-domains.txt",
         "Start Findomain Resolved"),
        (f"assetfinder -subs-only {domain} >> {output_dir}/assetfinder-{domain}-domains.txt",
         "Start Assetfinder Subdomains Finding"),
        (f"gauplus -t 5 -random-agent -subs {domain} | unfurl -u domains >> {output_dir}/gauplus-{domain}-domains.txt",
         "Start Gauplus Subdomains Finding"),
        (f"waybackurls {domain} | unfurl -u domains >> {output_dir}/waybackurls-{domain}-domains.txt",
         "Start Waybackurls Subdomains Finding"),
    ]

    if GITHUBTOKEN and GITHUBTOKEN != '<your github token>':
        github_command = f"github-subdomains -raw -d {domain} -t {GITHUBTOKEN} -o {output_dir}/github-subdomains-{domain}-domains.txt > /dev/null"
        commands.append((github_command, "Start GitHub Subdomains Finding"))

    if CHAOS_KEY and CHAOS_KEY != '<your chaos key>':
        chaos_command = f"chaos -key {CHAOS_KEY} -d {domain} -silent >> {output_dir}/chaos-{domain}-domains.txt"
        commands.append((chaos_command, "Start Chaos Subdomains Finding"))

    processes = []

    for command, message in commands:
        print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL}", message, "on", domain)
        process = subprocess.Popen(command, shell=True)
        processes.append(process)

    for process in processes:
        process.wait()

    # Execute findomain command with regex pattern
    findomain_command = f"findomain -t {domain} | grep -E '^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{{2,}}$'"
    findomain_output = subprocess.check_output(findomain_command, shell=True).decode("utf-8")

    # Write findomain output to file
    findomain_output_file = os.path.join(output_dir, f"findomain-{domain}-domains.txt")
    with open(findomain_output_file, "w") as f:
        f.write(findomain_output)

    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Passive subdomain enumeration completed for", domain)


def merge_domains_files(output_dir):
    merged_domains = []

    for file_path in glob.glob(os.path.join(output_dir, "*domains.txt")):
        with open(file_path, "r") as f:
            merged_domains.extend(f.read().splitlines())

    with open(os.path.join(output_dir, "domains-list.txt"), "w") as f:
        f.write("\n".join(merged_domains))

    for file_path in glob.glob(os.path.join(output_dir, "*domains.txt")):
        os.remove(file_path)

    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Merging domain files completed")


def create_output_dir(output_dir, in_scope_file, out_of_scope_file):
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "web-recon-out")
        os.makedirs(output_dir, exist_ok=True)
    else:
        os.makedirs(output_dir, exist_ok=True)
    if in_scope_file:
        shutil.copyfile(in_scope_file, os.path.join(output_dir, "in-scope.txt"))
    if out_of_scope_file:
        shutil.copyfile(out_of_scope_file, os.path.join(output_dir, "out-of-scope.txt"))
    naabu_scan_dir = os.path.join(output_dir, "naabu-scan")
    os.makedirs(naabu_scan_dir, exist_ok=True)
    return output_dir


def split_domains_file(input_file, output_dir):
    domains_file = os.path.join(output_dir, "domains-list.txt")
    if not os.path.exists(domains_file):
        open(domains_file, "a").close()
    with open(input_file, "r") as f:
        lines = f.readlines()

    num_lines = len(lines)
    chunk_size = 50  # Number of lines per chunk
    num_files = num_lines // chunk_size
    if num_lines % chunk_size != 0:
        num_files += 1

    for i in range(num_files):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk = lines[start_idx:end_idx]

        file_path = os.path.join(output_dir, "naabu-scan", f"domains_{i+1}.txt")
        with open(file_path, "w") as f:
            f.write("".join(chunk))

    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Splitting domains file completed")


def run_naabu_scan(domain_list, output_file):
    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Start naabu scan for {domain_list}")
    naabu_command = f"naabu -top-ports 1000 -l {domain_list} -silent >> {output_file}"
    subprocess.run(naabu_command, shell=True)

    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Naabu scan completed for {domain_list}")

def run_httpx_probes(input_file, output_file):
    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Running httpx probes for {input_file}")
    httpx_command = f"httpx -sc -probe -method -hash -title -server -td -l {input_file} -json -silent > {output_file}"
    subprocess.run(httpx_command, shell=True)

    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} httpx probes completed for {input_file}")
    pass

def filter_web_urls(input_file, output_file):
    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Filtering web URLs for {input_file}")
    command = f"jq -r 'select(.failed == false) | .url' {input_file}"
    subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    with open(output_file, 'w') as f:
        f.write(subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout)
    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Filtering web URLs completed")

# Function to filter service ports
def filter_service_ports(input_file, output_file):
    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Filtering service ports for {input_file}")
    command = f"jq -r 'select(.failed == true) | .input' {input_file}"
    subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    with open(output_file, 'w') as f:
        f.write(subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout)
    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Filtering service ports completed")

def main():
    parser = argparse.ArgumentParser(description="Web Recon Script")
    parser.add_argument("-is", "--in_scope", help="In scope file")
    parser.add_argument("-os", "--out_of_scope", help="Out of scope file")
    parser.add_argument("-o", "--output", help="Output directory", default="web-recon-output")

    args = parser.parse_args()

    if not args.in_scope and not args.out_of_scope:
        banner()
        return  # Exit the function if only printing the banner

    output_dir = create_output_dir(args.output, args.in_scope, args.out_of_scope)

    if args.in_scope:
        in_scope_domains = []
        with open(args.in_scope, "r") as f:
            in_scope_domains = f.read().splitlines()

        with futures.ThreadPoolExecutor() as executor:
            executor.map(lambda d: run_passive_subdomain(d, output_dir), in_scope_domains)

        merge_domains_files(output_dir)

    if args.out_of_scope:
        with open(args.out_of_scope, "r") as out_of_scope:
            out_of_scope_domains = out_of_scope.read().splitlines()

        with open(os.path.join(output_dir, "domains-list.txt"), "r") as f:
            domains = f.read().splitlines()

        in_scope_domains = [
            domain
            for domain in domains
            if not any(domain.endswith(out_of_scope_domain) for out_of_scope_domain in out_of_scope_domains)
        ]

        with open(os.path.join(output_dir, "domains-list.txt"), "w") as f:
            f.write("\n".join(in_scope_domains))

        subprocess.run(["sort", "-u", "-o", os.path.join(output_dir, "domains-list.txt"), os.path.join(output_dir, "domains-list.txt")])

    split_domains_file(os.path.join(output_dir, "domains-list.txt"), output_dir)

    naabu_scan_dir = os.path.join(output_dir, "naabu-scan")
    domain_lists = sorted(glob.glob(os.path.join(naabu_scan_dir, "*.txt")))
    output_file = os.path.join(output_dir, "naabu-scan.txt")

    for domain_list in domain_lists:
        run_naabu_scan(domain_list, output_file)

    input_file = output_file
    output_file = os.path.join(output_dir, "httpx-output.json")
    run_httpx_probes(input_file, output_file)
    

    filter_web_urls(output_file, os.path.join(output_dir, "web-urls.txt"))
    filter_service_ports(output_file, os.path.join(output_dir, "service-ports.txt"))
    
    # Run gowitness command with print statements
    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Running gowitness for web urls")

    gowitness_command = f"gowitness file -f {os.path.join(output_dir, 'web-urls.txt')} --db-path={os.path.join(output_dir, 'gowitness-weburls-output.sqlite3')} --screenshot-path={os.path.join(output_dir, 'gowitness-weburls-screenshots')} --fullpage"

    with open(os.devnull, 'w') as devnull:
        subprocess.run(gowitness_command, shell=True, stdout=devnull, stderr=devnull)
        print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Gowitness completed for web urls")

    print(f"{Fore.BLUE}[ INFO ]{Style.RESET_ALL} Running gowitness for service ports")

    gowitness_command = f"gowitness file -f {os.path.join(output_dir, 'service-ports.txt')} --db-path={os.path.join(output_dir, 'gowitness-service-ports-output.sqlite3')} --screenshot-path={os.path.join(output_dir, 'gowitness-service-ports-screenshots')} --fullpage"

    with open(os.devnull, 'w') as devnull:
        subprocess.run(gowitness_command, shell=True, stdout=devnull, stderr=devnull)
    
        print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Gowitness completed for service ports")
    
    print(f"{Fore.GREEN}[ SUCCESS ]{Style.RESET_ALL} Web Recon completed")

if __name__ == "__main__":
    main()

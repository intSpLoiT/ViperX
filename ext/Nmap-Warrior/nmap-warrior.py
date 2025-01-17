#!/usr/bin/python3
import argparse
import os
import subprocess
import shutil
import sys
import time
import platform
import re
import ctypes
from colorama import Fore, Style, init

# Initialize colorama
init()

SECONDS = time.perf_counter()


# ------------------------------------------------------------------
# Banner
# ------------------------------------------------------------------

def banner():
    print("    ____      ____     _____            _       __                _           ")
    print("   /  _/___  / __/___ / ___/___  ____  | |     / /___ ___________(_)___  _____")
    print("   / // __ \\/ /_/ __ \\__ \\/ _ \\/ ___/  | | /| / / __ `/ ___/ ___/ / __ \\/ ___/")
    print(" _/ // / / / __/ /_/ /__/ /  __/ /__   | |/ |/ / /_/ / /  / /  / / /_/ / /    ")
    print("/___/_/ /_/_/  \\____/____/\\___/\\___/   |__/|__/\\__,_/_/  /_/  /_/\\____/_/     ")
    print("                                                                              ")
    print("  github.com/InfoSecWarrior                                 by @ArmourInfosec ")
    print("\n")

# ------------------------------------------------------------------
# Print Functions
# ------------------------------------------------------------------

def INFO_PRINT():
    return (Fore.BLUE + " [ INFO  ] " + Style.RESET_ALL)
    
def WARNING_PRINT():
    return (Fore.YELLOW + " [WARNING] " + Style.RESET_ALL)

def ERROR_PRINT():
    return (Fore.RED + " [ ERROR ] " + Style.RESET_ALL)

def COMMAND_PRINT():
    return (Fore.GREEN + " [ COMMAND ] " + Style.RESET_ALL)

def NOTIFY_PRINT():
    return (Fore.MAGENTA + " [NOTIFY ] " + Style.RESET_ALL)


# ------------------------------------------------------------------
# Help
# ------------------------------------------------------------------

parser = argparse.ArgumentParser(usage='nmap-warrior.py [-t|--target, -l|--list] target [Options]')
parser.add_argument('-t', '--target', help='Target Domain or IP Address')
parser.add_argument('-l', '--list', help='Path to file containing a List of Target Hosts to scan (one per line)')
parser.add_argument('-o', '--output', help='Define Output Folder', default='nmap_outputs')
parser.add_argument('-s', '--silent', action='store_true', help='Disable Print the Banner')
parser.add_argument('-p', '--portscan', action='store_true', help='Port scan')
parser.add_argument('-v', '--versionscan', action='store_true', help='Service Version Detection (Requires root privileges)')
parser.add_argument('-u', '--udpscan', action='store_true', help='UDP Ports Scan With Version Detection')
args = parser.parse_args()

# ------------------------------------------------------------------
# Files And Directory Variables
# ------------------------------------------------------------------

TARGET_HOST = args.target
TARGET_HOST_LIST = args.list
NMAP_OUTPUT_DIR = args.output
LIVE_HOSTS_FILE = "LIVE-HOSTS.txt"
DOWN_HOSTS_FILE = "DOWN-HOSTS.txt"
LOG_FILE = "LOG-FILE.txt"
MAIN_OUTPUT_DIR = os.getcwd()
LIVE_HOSTS_FILE_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, "LIVE-HOSTS.txt"))
DOWN_HOSTS_FILE_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, "DOWN-HOSTS.txt"))
LOG_FILE_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, LOG_FILE))
LIVE_HOSTS_TRY_1_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-1'))
LIVE_HOSTS_TRY_2_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-2'))
LIVE_HOSTS_TRY_3_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-3'))
LIVE_HOSTS_TRY_4_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-4'))
GNMAP_FILE_PATH_1 = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-1.gnmap'))
GNMAP_FILE_PATH_2 = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-2.gnmap'))
GNMAP_FILE_PATH_3 = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-3.gnmap'))
GNMAP_FILE_PATH_4 = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'LIVE-HOSTS-TRY-4.gnmap'))
ALL_HOSTS_TCP_OPEN_PORTS_GNMAP_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'ALL-HOSTS-TCP-OPEN-PORTS.gnmap'))
ALL_HOSTS_TCP_OPEN_PORTS_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'ALL-HOSTS-TCP-OPEN-PORTS.txt'))
ALL_HOSTS_TCP_OPEN_PORTS_STD_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, 'ALL-HOSTS-TCP-OPEN-PORTS-STD.txt'))

# ------------------------------------------------------------------
# Extract Live Hosts function
# ------------------------------------------------------------------

def EXTRACT_LIVE_HOSTS(TRY):
    live_hosts = []
    down_hosts = []

    with open(TRY, 'r') as gnmap_file:
        for line in gnmap_file:
            # Match lines with host status
            match = re.search(r'Host: (\S+) .*Status: (\S+)', line)
            if match:
                ip = match.group(1)
                status = match.group(2)
                if status == "Up":
                    live_hosts.append(ip)
                elif status == "Down":
                    down_hosts.append(ip)

    with open(LIVE_HOSTS_FILE_PATH, 'a') as live_hosts_file:
        for host in live_hosts:
            live_hosts_file.write(f"{host}\n")

    with open(DOWN_HOSTS_FILE_PATH, 'w') as down_hosts_file:
        for host in down_hosts:
            down_hosts_file.write(f"{host}\n")

# ------------------------------------------------------------------
# Extract IP And PORTS function [IP:PORT,PORT]
# ------------------------------------------------------------------

def EXPTRACT_IP_PORTS(input_file):
    # Regular expression patterns for matching IP and open ports
    ip_pattern = re.compile(r"Host:\s(\d+\.\d+\.\d+\.\d+)")
    ports_pattern = re.compile(r"(\d+)/open/tcp")
    
    ip_ports_map = {}  # Dictionary to store IP and corresponding ports

    with open(input_file, 'r') as file:
        current_ip = None

        for line in file:
            # Check if the line contains an IP address
            ip_match = ip_pattern.search(line)
            if ip_match:
                current_ip = ip_match.group(1)  # Update the current IP
                if current_ip not in ip_ports_map:
                    ip_ports_map[current_ip] = []  # Initialize list of ports for the IP
            
            # Check if the line contains open ports
            if current_ip:
                open_ports = ports_pattern.findall(line)
                ip_ports_map[current_ip].extend(open_ports)

    # Filter out IPs with no open ports
    ip_ports_map = {ip: ports for ip, ports in ip_ports_map.items() if ports}

    # Write results to the output file only if there are results
    if ip_ports_map:
        with open(ALL_HOSTS_TCP_OPEN_PORTS_PATH, 'w') as outfile:
            for ip, ports in ip_ports_map.items():
                outfile.write(f"{ip}:{','.join(ports)}\n")

# ------------------------------------------------------------------
# Extract IP And PORTS STD function [IP:PORT]
# ------------------------------------------------------------------

def EXPTRACT_IP_PORTS_STD(filename):
    ip_ports = []
    
    # Regular expression patterns for matching the IP address and open ports
    ip_pattern = re.compile(r"Host:\s(\d+\.\d+\.\d+\.\d+)\s+\(\)")
    ports_pattern = re.compile(r"(\d+)/open/tcp")
    
    with open(filename, 'r') as file:
        ip = None
        for line in file:
            # Check if the line contains an IP address
            ip_match = ip_pattern.search(line)
            if ip_match:
                ip = ip_match.group(1)
            
            # Check if the line contains open ports
            if ip and ports_pattern.search(line):
                ports = ports_pattern.findall(line)
                for port in ports:
                    ip_ports.append(f"{ip}:{port}")
    
        with open(f'{ALL_HOSTS_TCP_OPEN_PORTS_STD_PATH}', 'w') as outfile:
            for line in ip_ports:
                outfile.write(line + '\n')

# ------------------------------------------------------------------
# Hosts Discovering nmap function
# ------------------------------------------------------------------

def DISCOVERING_HOSTS_WITH_PING():

    if TARGET_HOST:
        subprocess.run(f"nmap -v -n -sn {TARGET_HOST} -oA {LIVE_HOSTS_TRY_1_PATH}", capture_output=True, text=True, shell=True)
    elif TARGET_HOST_LIST:
        subprocess.run(f"nmap -v -n -sn -iL {TARGET_HOST_LIST} -oA {LIVE_HOSTS_TRY_1_PATH}", capture_output=True, text=True, shell=True)
    EXTRACT_LIVE_HOSTS(GNMAP_FILE_PATH_1)

# ------------------------------------------------------------------
# NMAP TCP SYN Ping function
# ------------------------------------------------------------------

def DISCOVERING_HOSTS_WITH_TCPSYNCHRONIZATION():
    subprocess.run(f"nmap -v -n -sn -PS21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080 -iL {DOWN_HOSTS_FILE_PATH} -oA {LIVE_HOSTS_TRY_2_PATH}", capture_output=True, text=True, shell=True)
    EXTRACT_LIVE_HOSTS(GNMAP_FILE_PATH_2)

# ------------------------------------------------------------------
# NMAP TCP ACK Ping function
# ------------------------------------------------------------------

def DISCOVERING_HOSTS_WITH_TCPACKNOWLEDGEMENT():

    subprocess.run(f"nmap -v -n -sn -PA21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080 -iL {DOWN_HOSTS_FILE_PATH} -oA {LIVE_HOSTS_TRY_3_PATH}", capture_output=True, text=True, shell=True)
    EXTRACT_LIVE_HOSTS(GNMAP_FILE_PATH_3)

# ------------------------------------------------------------------
# NMAP UDP Ping function
# ------------------------------------------------------------------

def DISCOVERING_HOSTS_WITH_UDP():

    subprocess.run(f"nmap -v -n -sn -PU631,161,137,123,138,1434,445,135,67,53 -iL {DOWN_HOSTS_FILE_PATH} -oA {LIVE_HOSTS_TRY_4_PATH}", capture_output=True, text=True, shell=True)
    EXTRACT_LIVE_HOSTS(GNMAP_FILE_PATH_4)

# ------------------------------------------------------------------
# Nmap Open TCP Ports Scanning function
# ------------------------------------------------------------------
def OPENPORTS_NMAP(HOST):
    HOST_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, f'{HOST}-TCP-Scan'))
    HOST_GNMAP_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, f'{HOST}-TCP-Scan.gnmap'))
    subprocess.run(f"nmap -v -Pn -T 4 -p- --exclude-ports 9100 {HOST} -oA {HOST_PATH}", capture_output=True, text=True, shell=True)

    HOST_GNMAP_FILE = open(HOST_GNMAP_PATH, 'r')

    with open(ALL_HOSTS_TCP_OPEN_PORTS_GNMAP_PATH, 'a') as file:
        for line in HOST_GNMAP_FILE:
            file.write(line)
    
    HOST_GNMAP_FILE.close()

# ------------------------------------------------------------------
# Nmap TCP Ports Service Version Detection function
# ------------------------------------------------------------------
def VERSION_DETECTION(ip, ports):
    HOST_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, f'{HOST}-TCP-Version-Detection'))
    subprocess.run(f"nmap -v -Pn -sT -sV -A -O -sC {ip} -p {ports} -oA {HOST_PATH}", capture_output=True, text=True, shell=True)

# ------------------------------------------------------------------
# Nmap UDP Ports Scanning function
# ------------------------------------------------------------------

def UDP_PORT_SCAN(IP):
    HOST_PATH = os.path.normpath(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, f'{IP}-UDP-Version-Detection'))
    UDP_PORTS="7,53,67,68,69,88,111,123,135,137,138,161,162,445,631,749,1434,1812,1813,2049,5432"
    subprocess.run(f"nmap -v -Pn -sU -sV -sC -p {UDP_PORTS} {IP} -oA {HOST_PATH}", capture_output=True, text=True, shell=True)

# ------------------------------------------------------------------
# Script Exec Entry Point 
# ------------------------------------------------------------------

# Print help if no arguments are provided
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

elif not TARGET_HOST and not TARGET_HOST_LIST:
    print(f"{ERROR_PRINT()} Target is missing, try using -t <Target Domain or IP Address> / -l <ip_list>")
    print(f"{ERROR_PRINT()} Please provide any one TARGET Option")

elif TARGET_HOST and TARGET_HOST_LIST: # Check Is used Target and List Peremater at same time
    print(f"{ERROR_PRINT()} Multiple Target are provide, try using -t <Target Domain or IP Address> / -l <ip_list>")
    print(f"{ERROR_PRINT()} Please provide Only one TARGET Option")
    

elif TARGET_HOST or TARGET_HOST_LIST: # Check Target is Provide
        
    # ------------------------------------------------------------------
    # Check Nmap install or Not
    # ------------------------------------------------------------------
    if not shutil.which("nmap"):
        print(f"{ERROR_PRINT()} Nmap is not install.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Check Version Detection Switch
    # ------------------------------------------------------------------
    if args.versionscan:
        if not args.portscan:
            print(f"{ERROR_PRINT()} -p is required for Service Version Detection")
            sys.exit(1)
        elif platform.system() == "Linux":
            if os.getuid() != 0:
                print(f"{ERROR_PRINT()} Requires root privileges for Service Version Detection")
                sys.exit(1)
        elif platform.system() == "Windows":
            if ctypes.windll.shell32.IsUserAnAdmin() == 0:
                print(f"{ERROR_PRINT()} Requires Administrator privileges for Service Version Detection")
                sys.exit(1)

    # ------------------------------------------------------------------
    # Output Directory And Files Manage
    # ------------------------------------------------------------------

    if os.path.exists(NMAP_OUTPUT_DIR):

        print(f"{ERROR_PRINT()} {NMAP_OUTPUT_DIR} Directory already Exists Please choose a different location")
        sys.exit(1)

    else:

        os.makedirs(NMAP_OUTPUT_DIR)
                
        with open (f'{LIVE_HOSTS_FILE_PATH}', 'w') as f:
            pass

        with open (f'{DOWN_HOSTS_FILE_PATH}', 'w') as f:
            pass

        with open (f'{LOG_FILE_PATH}', 'w') as f:
            pass

    # ------------------------------------------------------------------
    # Check Silent Mode or Not
    # ------------------------------------------------------------------
    
    if not args.silent:
        banner()

    # ------------------------------------------------------------------
    # Check OS
    # ------------------------------------------------------------------

    if platform.system() == "Windows":
        print(f"{INFO_PRINT()} The script is running on Windows")
    elif platform.system() == "Linux":
        print(f"{INFO_PRINT()} The script is running on Linux")
    else:
        print(f"{INFO_PRINT()} Unknown OS")

    # ------------------------------------------------------------------
    # Check notify install or Not
    # ------------------------------------------------------------------

    NOTIFY_CONF = subprocess.run(f"echo '{os.path.basename(__file__)} Starting' | notify -silent", capture_output=True, text=True, shell=True).returncode


    if not shutil.which("notify"):
        print(f"{ERROR_PRINT()} Notify is not install.")

    elif NOTIFY_CONF != 0:
        print(f"{ERROR_PRINT()} Notify is not config.")
    else:
        pass

    if NOTIFY_CONF != 0:
        print(f"{INFO_PRINT()} Start Discovering Live Hosts using Nmap [ -n -sn ] Please wait...")
    else:
        print(f"{INFO_PRINT()} Start Discovering Live Hosts using Nmap [ -n -sn ] Please wait...")
        subprocess.run(f'echo "{INFO_PRINT()} Start Discovering Live Hosts using Nmap [ -n -sn ] Please wait..." | notify -silent', capture_output=True, shell=True, text=True)
        print(f"{NOTIFY_PRINT()} Notification Send")

    # ------------------------------------------------------------------
    # Run NMAP function
    # ------------------------------------------------------------------

    DISCOVERING_HOSTS_WITH_PING()

    # ------------------------------------------------------------------
    # Run NMAP TCP SYN function
    # ------------------------------------------------------------------

    if os.path.getsize(DOWN_HOSTS_FILE_PATH) != 0:
        
        print(f"{INFO_PRINT()} Run TCP SYN ping [ -sn -PS21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080 ] Please wait...")
        
        DISCOVERING_HOSTS_WITH_TCPSYNCHRONIZATION()

    # ------------------------------------------------------------------
    # Run nmap TCP ACK function
    # ------------------------------------------------------------------
    
    if os.path.getsize(DOWN_HOSTS_FILE_PATH) != 0:
        
        print(f"{INFO_PRINT()} Run TCP ACK ping [ -sn -PA21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080 ] Please wait...")
        
        DISCOVERING_HOSTS_WITH_TCPACKNOWLEDGEMENT()

    # ------------------------------------------------------------------
    # Run nmap UDP Ping Scan function
    # ------------------------------------------------------------------

    if os.path.getsize(DOWN_HOSTS_FILE_PATH) != 0:
        
        print(f"{INFO_PRINT()} Run UDP ping  [ -sn -PU631,161,137,123,138,1434,445,135,67,53 ] Please wait...")
        
        DISCOVERING_HOSTS_WITH_UDP()

    if NOTIFY_CONF != 0:
        print(f"{INFO_PRINT()} Discovering Live Hosts is Completed")
    else:
        print(f"{INFO_PRINT()} Discovering Live Hosts is Completed")
        subprocess.run(f'echo "{INFO_PRINT()} Discovering Live Hosts is Completed" | notify -silent', capture_output=True, text=True, shell=True)
        print(f"{NOTIFY_PRINT()} Notification Send")

    duration = time.perf_counter() - SECONDS
    print(f'{INFO_PRINT()} Elapsed Time: {int(duration / 60)} minutes and {int(duration % 60)} seconds.')

    with open(LIVE_HOSTS_FILE_PATH) as f:
        ALL_LIVE_HOSTS = [line.strip() for line in f if line.strip()]
    
    with open(DOWN_HOSTS_FILE_PATH) as f:
        ALL_DOWN_HOSTS = [line.strip() for line in f if line.strip()]

    if NOTIFY_CONF != 0:
        print(f'{INFO_PRINT()} Number of Live Hosts found : {Fore.YELLOW} {len(ALL_LIVE_HOSTS)} {Style.RESET_ALL} ( {Fore.GREEN}{LIVE_HOSTS_FILE_PATH} {Style.RESET_ALL})')
        print(f'{INFO_PRINT()} Number of Downed Hosts found : {Fore.RED} {len(ALL_DOWN_HOSTS)} {Style.RESET_ALL} ( {Fore.RED}{DOWN_HOSTS_FILE_PATH} {Style.RESET_ALL})')
    else:
        subprocess.run(f'echo "{INFO_PRINT()} Number of Live Hosts found : {Fore.YELLOW} {len(ALL_LIVE_HOSTS)} {Style.RESET_ALL} ( {Fore.GREEN}{LIVE_HOSTS_FILE_PATH} {Style.RESET_ALL})" | notify -silent', capture_output=True, text=True, shell=True)
        subprocess.run(f'echo "{INFO_PRINT()} Number of Downed Hosts found : {Fore.RED} {len(ALL_DOWN_HOSTS)} {Style.RESET_ALL} ( {Fore.RED}{DOWN_HOSTS_FILE_PATH} {Style.RESET_ALL})" | notify -silent', capture_output=True, text=True, shell=True)
        print(f'{INFO_PRINT()} Number of Live Hosts found : {Fore.YELLOW} {len(ALL_LIVE_HOSTS)} {Style.RESET_ALL} ( {Fore.GREEN}{os.path.normpath(LIVE_HOSTS_FILE_PATH)} {Style.RESET_ALL})')
        print(f'{INFO_PRINT()} Number of Downed Hosts found : {Fore.RED} {len(ALL_DOWN_HOSTS)} {Style.RESET_ALL} ( {Fore.RED}{DOWN_HOSTS_FILE_PATH} {Style.RESET_ALL})')
        print(f"{NOTIFY_PRINT()} Notification Send")
        
    # ------------------------------------------------------------------
    # Open Ports Scanning
    # ------------------------------------------------------------------

    if args.portscan:

        if len(ALL_LIVE_HOSTS) == 0:
            print(f'{ERROR_PRINT()} No any Live Host found !!')
            sys.exit(1)
        
        if NOTIFY_CONF != 0:
            print(f'{INFO_PRINT()} Start Scanning Open Ports using Nmap [ -v -Pn -p- ] Please wait...')
        else:
            subprocess.run(f'echo "{INFO_PRINT()} Start Scanning Open Ports using Nmap [ -v -Pn -p- ] Please wait..." | notify -silent', capture_output=True, text=True, shell=True)
            print(f'{INFO_PRINT()} Start Scanning Open Ports using Nmap [ -v -Pn -p- ] Please wait...')
            print(f"{NOTIFY_PRINT()} Notification Send")

        for i, HOST in enumerate(ALL_LIVE_HOSTS, start=1):
            print(f"{INFO_PRINT()} Scanning TCP Open Ports with Nmap on {Fore.YELLOW} {HOST} {Style.RESET_ALL} ({Fore.BLUE}{i}{Style.RESET_ALL}/{Fore.GREEN}{len(ALL_LIVE_HOSTS)}{Style.RESET_ALL})")
            OPENPORTS_NMAP(HOST)
        
        if NOTIFY_CONF != 0:
            print(f'{INFO_PRINT()} Scanning TCP Open Ports is Completed')
        else:
            subprocess.run(f'echo "{INFO_PRINT()} Scanning TCP Open Ports is Completed" | notify -silent', capture_output=True, text=True, shell=True)
            print(f'{INFO_PRINT()} Scanning TCP Open Ports is Completed')
            print(f"{NOTIFY_PRINT()} Notification Send")

        EXPTRACT_IP_PORTS(ALL_HOSTS_TCP_OPEN_PORTS_GNMAP_PATH)
        EXPTRACT_IP_PORTS_STD(ALL_HOSTS_TCP_OPEN_PORTS_GNMAP_PATH)

        duration = time.perf_counter() - SECONDS
        print(f'{INFO_PRINT()} Elapsed Time: {int(duration / 60)} minutes and {int(duration % 60)} seconds.')
        print(f'{INFO_PRINT()} All Hosts with Open Ports are saved in : {Fore.GREEN} {ALL_HOSTS_TCP_OPEN_PORTS_PATH} {Style.RESET_ALL}')
        print(f'{INFO_PRINT()} All Hosts with Open Ports are saved in (Standard output ): {Fore.GREEN} {ALL_HOSTS_TCP_OPEN_PORTS_STD_PATH} {Style.RESET_ALL}')

    # ------------------------------------------------------------------
    # Service Version Detection
    # ------------------------------------------------------------------
    
    if args.versionscan:
        
        if os.path.exists(os.path.join(MAIN_OUTPUT_DIR, NMAP_OUTPUT_DIR, "ALL-HOSTS-TCP-OPEN-PORTS.txt")) == True:
        
            if NOTIFY_CONF != 0:
                print(f'{INFO_PRINT()} Start Service Version Detection using Nmap [ -v -Pn -sT -sV -A -O -sC ] Please wait...')
            else:
                subprocess.run(f'echo "{INFO_PRINT()} Start Service Version Detection using Nmap [ -v -Pn -sT -sV -A -O -sC ] Please wait..." | notify -silent', capture_output=True, text=True, shell=True)
                print(f'{INFO_PRINT()} Start Service Version Detection using Nmap [ -v -Pn -sT -sV -A -O -sC ] Please wait...')
                print(f"{NOTIFY_PRINT()} Notification Send")
        
            with open(ALL_HOSTS_TCP_OPEN_PORTS_PATH) as f:
                ALL_HOSTS_OPEN_PORTS = [line.strip() for line in f if line.strip()]
            
            for i, host_value in enumerate(ALL_HOSTS_OPEN_PORTS, start=1):

                print(f"{INFO_PRINT()} Scanning Service Version Detection with Nmap on {Fore.YELLOW}{host_value}{Style.RESET_ALL} ({Fore.BLUE}{i}{Style.RESET_ALL}/{Fore.GREEN}{len(ALL_HOSTS_OPEN_PORTS)}{Style.RESET_ALL})")
                ip, ports = host_value.split(":")                
                VERSION_DETECTION(ip, ports)
            
            if NOTIFY_CONF != 0:
                print(f'{INFO_PRINT()} Service Version Detection is Completed')
            else:
                subprocess.run(f'echo "{INFO_PRINT()} Service Version Detection is Completed" | notify -silent', capture_output=True, text=True, shell=True)
                print(f'{INFO_PRINT()} Service Version Detection is Completed')
                print(f"{NOTIFY_PRINT()} Notification Send")

        else:
            print(f'{WARNING_PRINT()} Not Found Open Ports')
        


    # ------------------------------------------------------------------
    # Run nmap UDP Port scan
    # ------------------------------------------------------------------
    
    if args.udpscan:
        
        if len(ALL_LIVE_HOSTS) == 0:
            print(f'{ERROR_PRINT()} No any Live Host found !!')
            sys.exit(1)
        
        if NOTIFY_CONF != 0:
            print(f'{INFO_PRINT()} Start Scanning UDP Ports using Nmap [ -v -Pn -p- ] Please wait...')
        else:
            subprocess.run(f'echo "{INFO_PRINT()} Start Scanning UDP Ports using Nmap [ -v -Pn -p- ] Please wait..." | notify -silent', capture_output=True, text=True, shell=True)
            print(f'{INFO_PRINT()} Start Scanning UDP Ports using Nmap [ -v -Pn -p- ] Please wait...')
            print(f"{NOTIFY_PRINT()} Notification Send")

        for i, IP in enumerate(ALL_LIVE_HOSTS, start=1):
            print(f"{INFO_PRINT()} Scanning UDP Ports with Nmap on {Fore.YELLOW} {IP} {Style.RESET_ALL} ({Fore.BLUE}{i}{Style.RESET_ALL}/{Style.RESET_ALL}{Fore.GREEN}{len(ALL_LIVE_HOSTS)}{Style.RESET_ALL})")
            UDP_PORT_SCAN(IP)

        if NOTIFY_CONF != 0:
            print(f'{INFO_PRINT()} Scanning UDP Ports is Completed')
        else:
            subprocess.run(f'echo "{INFO_PRINT()} Scanning UDP Ports is Completed" | notify -silent', capture_output=True, text=True, shell=True)
            print(f'{INFO_PRINT()} Scanning UDP Ports is Completed')
            print(f"{NOTIFY_PRINT()} Notification Send")

else:
    parser.print_help()

#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import signal
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    BLUE = Fore.BLUE  # Add blue color
    RESET = Style.RESET_ALL

    FORMATS = {
        logging.INFO: f'[{BLUE}%(levelname)s{RESET}][%(asctime)s] %(message)s',
        logging.ERROR: f'[{RED}%(levelname)s{RESET}][%(asctime)s] %(message)s',
        logging.WARNING: f'[{YELLOW}%(levelname)s{RESET}][%(asctime)s] %(message)s',
        logging.DEBUG: f'[{CYAN}%(levelname)s{RESET}][%(asctime)s] %(message)s',
        logging.CRITICAL: f'[{MAGENTA}%(levelname)s{RESET}][%(asctime)s] %(message)s'
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


# Set up logging
logger = logging.getLogger('Scanner')
logger.setLevel(logging.INFO)

# Create console handler with colored formatter
ch = logging.StreamHandler()
ch.setFormatter(ColoredFormatter())
logger.addHandler(ch)

# List of required tools
REQUIRED_TOOLS = [
    'nmap',
    'jq',
    'grep',
    'cut',
    'tr',
    'httpx',
    'dirsearch',
    'whatweb',
    'nikto',
    'nuclei'
]

def banner():
    print("    ____      ____     _____            _       __                _           ")
    print("   /  _/___  / __/___ / ___/___  ____  | |     / /___ ___________(_)___  _____")
    print("   / // __ \\/ /_/ __ \\__ \\/ _ \\/ ___/  | | /| / / __ `/ ___/ ___/ / __ \\/ ___/")
    print(" _/ // / / / __/ /_/ /__/ /  __/ /__   | |/ |/ / /_/ / /  / /  / / /_/ / /    ")
    print("/___/_/ /_/_/  \\____/____/\\___/\\___/   |__/|__/\\__,_/_/  /_/  /_/\\____/_/     ")
    print("                                                                              ")
    print("  github.com/InfoSecWarrior                                 by @ArmourInfosec ")
    print("\n")

def check_dependencies():
    missing_tools = []
    for tool in REQUIRED_TOOLS:
        if not shutil.which(tool):
            missing_tools.append(tool)
    if missing_tools:
        logger.error(f"Missing required tools: {', '.join(missing_tools)}")
        sys.exit(1)
    logger.info("All dependencies are satisfied.")

def run_command(command, cwd=None, acceptable_exit_codes=[0]):
    logger.info(f"Executing command: {command}")
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line, end='')

        process.stdout.close()
        return_code = process.wait()

        if return_code not in acceptable_exit_codes:
            logger.error(f"Command failed with exit code {return_code}: {command}")
            raise subprocess.CalledProcessError(return_code, command)

        logger.info(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        raise
    except Exception as e:
        logger.error(f"An error occurred while executing command: {command}")
        logger.error(str(e))
        raise

def filter_output(input_file, output_file, jq_filter, cwd):
    """
    Filters JSON output using jq and saves the result to a file.
    """
    logger.info(f"Filtering output for {input_file} with filter '{jq_filter}'...")
    command = f"jq -r '{jq_filter}' {input_file}"
    try:
        run_command(command, cwd=cwd)
    except subprocess.CalledProcessError:
        logger.error("Filtering failed.")
        return
    # Read the filtered data
    try:
        with open(os.path.join(cwd, input_file), 'r') as f_in:
            filtered_data = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True
            ).stdout
        # Filter out lines that end with a colon
        clean_data = '\n'.join(line for line in filtered_data.splitlines() if not line.endswith(':'))
        with open(os.path.join(cwd, output_file), 'w') as f_out:
            f_out.write(clean_data)
        logger.info(f"Filtering completed: {output_file}")
    except Exception as e:
        logger.error(f"Failed to filter output: {e}")

def run_nmap_all_ports(target, output_dir, prefix):
    """
    Runs Nmap to scan all ports.
    """
    logger.info(f"Running Nmap all ports scan on {target}...")
    cmd = f"nmap -v -Pn -p- {target} -oA {prefix}-all-ports-scan-output"
    run_command(cmd, cwd=output_dir)

def extract_open_ports(target, output_dir, prefix):
    """
    Extracts open ports from Nmap output.
    """
    nmap_output_file = f"{prefix}-all-ports-scan-output.nmap"
    open_ports_list_file = f"{prefix}-open-ports-list-output.txt"
    logger.info(f"Extracting open ports from {nmap_output_file}...")
    cmd = f"grep open {nmap_output_file} | cut -d '/' -f 1 | tr '\\n' ',' > {open_ports_list_file}"
    try:
        run_command(cmd, cwd=output_dir)
        with open(os.path.join(output_dir, open_ports_list_file), 'r') as f:
            open_ports = f.read().strip().rstrip(',')
        if open_ports:
            logger.info(f"Open ports found: {open_ports}")
        else:
            logger.warning("No open ports found.")
        return open_ports
    except subprocess.CalledProcessError:
        logger.error("Failed to extract open ports.")
        return ''
    except FileNotFoundError:
        logger.error(f"Open ports list file not found: {open_ports_list_file}")
        return ''

def run_nmap_version(target, open_ports, output_dir, prefix):
    """
    Runs Nmap for server and version detection on open ports.
    """
    logger.info("Running Nmap server and version detection on open ports...")
    cmd = f"nmap -v -Pn -sT -sV -sC -A -O -p {open_ports} {target} -oA {prefix}-nmap-version-scan-output"
    run_command(cmd, cwd=output_dir)

def run_httpx(target, output_dir, prefix):
    """
    Runs httpx scan on open ports with predefined rate limiting and timeout.
    """
    rate_limit = 100  # Predefined rate limit
    timeout = 10       # Predefined timeout in seconds
    logger.info("Running httpx on open ports...")
    host_open_ports_file = f"{prefix}-host-open-ports-output.txt"
    httpx_output_file = f"{prefix}-httpx-output.json"
    try:
        with open(os.path.join(output_dir, host_open_ports_file), 'r') as f:
            open_ports = [line.strip() for line in f if line.strip()]
        with open(os.path.join(output_dir, host_open_ports_file), 'w') as f:
            for port in open_ports:
                f.write(f"{port}\n")
    except FileNotFoundError:
        logger.error(f"Host open ports file not found: {host_open_ports_file}")
        return ''
    cmd = (
        f"httpx -sc -probe -method -hash -title -server -td "
        f"-l {host_open_ports_file} -json -silent "
        f"--rate-limit {rate_limit} --timeout {timeout} > {httpx_output_file}"
    )
    run_command(cmd, cwd=output_dir)
    return httpx_output_file

def run_dirsearch(url, output_dir, prefix, port):
    """
    Runs dirsearch on a given URL.
    """
    logger.info(f"Running dirsearch on {url}...")
    dirsearch_output = f"{prefix}-dirsearch-{port}-output.txt"
    cmd = f"dirsearch -u {url} -o {dirsearch_output} -q 2>/dev/null"
    run_command(cmd, cwd=output_dir)
    return dirsearch_output

def run_dirsearch_wordlist(url, output_dir, prefix, port, wordlist):
    """
    Runs dirsearch with a custom wordlist on a given URL.
    """
    if not os.path.isfile(wordlist):
        logger.error(f"Wordlist not found: {wordlist}")
        return ''
    logger.info(f"Running dirsearch with wordlist on {url}...")
    dirsearch_wordlist_output = f"{prefix}-dirsearch-{port}-wordlist-output.txt"
    cmd = f"dirsearch -u {url} -w {wordlist} -o {dirsearch_wordlist_output} -q 2>/dev/null"
    run_command(cmd, cwd=output_dir)
    return dirsearch_wordlist_output

def run_whatweb(url, output_dir, prefix, port):
    """
    Runs WhatWeb on a given URL.
    """
    logger.info(f"Running WhatWeb on {url}...")
    whatweb_output = f"{prefix}-whatweb-{port}-output.txt"
    cmd = f"whatweb {url} --color=never > {whatweb_output}"
    run_command(cmd, cwd=output_dir)
    return whatweb_output

def run_nikto_on_url(url, output_dir, prefix, port):
    """
    Runs Nikto scan on a given URL.
    """
    logger.info(f"Running Nikto on {url}...")
    nikto_output = f"{prefix}-nikto-{port}-output.txt"
    cmd = f"nikto -ask no -host {url} -output {nikto_output}"
    # Allow exit codes 0 (no vulnerabilities) and 1 (vulnerabilities found)
    run_command(cmd, cwd=output_dir, acceptable_exit_codes=[0, 1])
    return nikto_output

def run_nuclei_on_port(target, port, output_dir, prefix):
    """
    Runs Nuclei scan on a given host:port.
    """
    logger.info(f"Running Nuclei on {target}:{port}...")
    nuclei_output = f"{prefix}-nuclei-{port}-output.txt"
    cmd = f"nuclei -silent -u {target}:{port} -o {nuclei_output}"
    run_command(cmd, cwd=output_dir)
    return nuclei_output

def process_url(url, output_dir, prefix, index, wordlist, executor):
    """
    Processes a single URL by running dirsearch, dirsearch with wordlist, WhatWeb, and Nikto.
    All tasks are submitted to the provided executor for concurrent execution.
    """
    try:
        # Extract port from URL (default to 80 if no port is specified)
        parsed_url = url.split(':')
        port = parsed_url[-1] if len(parsed_url) > 2 else '80'  # Defaults to port 80
        
        # Run dirsearch
        dirsearch_out = run_dirsearch(url, output_dir, prefix, port)
        
        # Run dirsearch with custom wordlist
        dirsearch_wordlist_out = run_dirsearch_wordlist(url, output_dir, prefix, port, wordlist)
        
        # Run whatweb
        whatweb_out = run_whatweb(url, output_dir, prefix, port)
        
        # Submit Nikto scan to the executor
        executor.submit(run_nikto_on_url, url, output_dir, prefix, port)
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred while processing URL {url}: {e}")

def process_target(target, output_dir, args, single_target, outputdir_name):
    """
    Processes a single target by running all scans and managing concurrent Nikto and Nuclei executions.
    """
    prefix = outputdir_name if single_target else target.replace('/', '_')
    target_dir = output_dir if single_target else os.path.join(output_dir, target.replace('/', '_'))

    # Create target directory if it's a multiple target scenario
    if not single_target:
        try:
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(f"Created directory: {target_dir}")
        except Exception as e:
            logger.error(f"Failed to create directory '{target_dir}': {e}")
            return

    try:
        # Run Nmap all ports scan
        run_nmap_all_ports(target, target_dir, prefix)

        # Extract open ports
        open_ports = extract_open_ports(target, target_dir, prefix)

        if open_ports:
            # Run Nmap server and version detection
            run_nmap_version(target, open_ports, target_dir, prefix)

            # Save open ports for httpx
            host_open_ports_file = f"{prefix}-host-open-ports-output.txt"
            try:
                with open(os.path.join(target_dir, host_open_ports_file), 'w') as f:
                    for port in open_ports.split(','):
                        f.write(f"{target}:{port}\n")
                logger.debug(f"Host open ports saved to {host_open_ports_file}")
            except Exception as e:
                logger.error(f"Failed to write to {host_open_ports_file}: {e}")

            # Run httpx
            httpx_output_file = run_httpx(target, target_dir, prefix)

            # Filter web URLs
            filtered_web_urls_file = f"{prefix}-filtered-web-urls-output.txt"
            filter_output(httpx_output_file, filtered_web_urls_file, "select(.failed == false) | .url", cwd=target_dir)

            # Read filtered URLs
            try:
                with open(os.path.join(target_dir, filtered_web_urls_file), 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                logger.error(f"Filtered web URLs file not found: {filtered_web_urls_file}")
                urls = []

            if urls:
                # Run web scans concurrently
                with ThreadPoolExecutor(max_workers=args.threads) as nikto_executor:
                    futures = []
                    for i, url in enumerate(urls, start=1):
                        futures.append(nikto_executor.submit(process_url, url, target_dir, prefix, i, args.wordlist, nikto_executor))
                    # Wait for all URL-related scans to complete
                    for future in as_completed(futures):
                        pass  # No progress indication
            else:
                logger.warning(f"No URLs to scan for target: {target}")

            # Run Nuclei scans concurrently on open ports
            with ThreadPoolExecutor(max_workers=args.threads) as nuclei_executor:
                nuclei_futures = []
                for port in open_ports.split(','):
                    nuclei_futures.append(nuclei_executor.submit(run_nuclei_on_port, target, port, target_dir, prefix))
                # Wait for all Nuclei scans to complete
                for future in as_completed(nuclei_futures):
                    pass  # No progress indication
        else:
            logger.warning(f"No open ports found for target: {target}")
    except subprocess.CalledProcessError:
        logger.error(f"Scanning failed for target {target}.")
    except Exception as e:
        logger.error(f"An error occurred while processing target {target}: {e}")
    finally:
        logger.info(f"Completed scanning for target: {target}")

def signal_handler(sig, frame):
    logger.info("Interrupt received. Shutting down gracefully...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="Run various network and web security scans.")
    parser.add_argument('-t', '--targets', required=True, nargs='+', help='Target IP address(es) or domain(s)')
    parser.add_argument('-o', '--outputdir', help='Output directory (default: target name)', default=None)
    parser.add_argument('--wordlist', default="/usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt",
                        help='Custom wordlist for dirsearch')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    parser.add_argument('--threads', type=int, default=4, help='Number of parallel threads for scanning URLs')
    args = parser.parse_args()

    if args.targets and args.outputdir:
        banner()

    # Set output directory to target name if not specified
    if args.outputdir is None:
        banner()
        if len(args.targets) == 1:
            args.outputdir = os.path.basename(args.targets[0])  # Set output dir to target name if only one target
        else:
            logger.error("Output directory must be specified when scanning multiple targets.")
            sys.exit(1)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    check_dependencies()

    output_dir = os.path.abspath(args.outputdir)
    outputdir_name = os.path.basename(output_dir)

    single_target = len(args.targets) == 1

    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory set to: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to create output directory '{output_dir}': {e}")
        sys.exit(1)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for target in args.targets:
            futures.append(executor.submit(process_target, target, output_dir, args, single_target, outputdir_name))

        for future in as_completed(futures):
            pass

if __name__ == "__main__":
    main()

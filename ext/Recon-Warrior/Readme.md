<h1 align="center">Recon Warrior Python Script</h1>
<p align="center">
  <a href="#description">Description</a> •
  <a href="#features">Features</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#usage">Usage</a> •
  <a href="#workflow">Workflow</a>
</p>

# Description

Recon Warrior is a Python script that automates various web reconnaissance tasks for bug hunting. It utilizes multiple tools to perform subdomain enumeration, HTTP probing, and screenshot capture.

## Features

- Passive subdomain enumeration using tools like Subfinder, Amass, Findomain, Assetfinder, Gauplus, and Waybackurls.
- Optional active subdomain enumeration using GitHub Subdomains and Chaos.
- Splitting the domains file into smaller chunks for parallel processing.
- Naabu port scanning for discovered subdomains.
- HTTPX probing to collect information about web services.
- Filtering web URLs and service ports from the HTTPX output.
- Automated screenshot capture using Gowitness.

## Prerequisites

- Python 3
- Required: subfinder, amass, findomain, assetfinder, gauplus, waybackurls, github-subdomains, naabu, httpx, gowitness, jq
- GitHub token (for GitHub Subdomains)
- Chaos key (for Chaos subdomain enumeration)

## Usage

The script accepts the following command-line arguments:

```
python recon-warrior.py -is in-scope.txt -os out-of-scope.txt -o output_dir
```

- `-is` or `--in_scope`: Path to the file containing in-scope domains (one domain per line).
- `-os` or `--out_of_scope`: Path to the file containing out-of-scope domains (one domain per line).
- `-o` or `--output`: Output directory to store the generated files and screenshots (default: web-recon-output).

Note: Either the in-scope or out-of-scope file is required for the script to perform web reconnaissance.

### Output

The script generates the following files and directories in the specified output directory:

- `domains-list.txt`: Merged list of discovered subdomains.
- `naabu-scan`: Directory containing the split domain files for naabu scanning.
- `naabu-scan.txt`: Combined naabu scan output for all subdomains.
- `httpx-output.json`: Output file containing HTTPX probes results.
- `web-urls.txt`: Filtered web URLs extracted from the HTTPX output.
- `service-ports.txt`: Filtered service ports extracted from the HTTPX output.
- `gowitness-output.sqlite3`: Gowitness database file for storing screenshots.
- `gowitness-screenshots`: Directory containing the captured screenshots.

### Example of In-Scope File

```
www.example.com
example.com
test.com
```

### Example of out-of-scope file

```
test.example.com
user.example.com
example.com
```

## Workflow

The script performs the following steps:

1. Passive Subdomain Enumeration: It runs various tools to find subdomains passively.
2. Merging Domain Files: It merges the generated domain files into a single file.
3. Removing Out-of-Scope Domains: It removes all subdomains found in the out-of-scope file from the merged domain file.
4. Sorting Domains: It sorts the merged domain file and removes duplicates.
5. Splitting Domains: If the in-scope file is provided, it splits the domains into smaller files for naabu scanning.
6. Naabu Scanning: It runs naabu scans on the generated domain files.
7. HTTPX Probes: It runs httpx probes on the naabu scan results.
8. Filtering URLs: It filters the web URLs from the httpx output.
9. Filtering Service Ports: It filters the service ports from the httpx output.
10. Gowitness: It captures screenshots using Gowitness for web URLs and service ports.


## Contributing

Contributions to the Recon warrior Script are welcome! If you have any bug fixes, feature enhancements, or suggestions, please open an issue or submit a pull request.

<h1 align=center>Get Chaos Data Python Script.</h1>

<p align="center">
  <a href="#description">Description</a> •
  <a href="#prerequisites">Prerequisites</a> •
  <a href="#examples">Examples</a>
</p>

## Description

The script is a command-line tool that allows users to download and manipulate URL lists related to bug bounty programs from the Chaos platform created by Project Discovery. The tool accepts various arguments to filter URLs by platform, program name, and bounty status. The script uses the requests library to download the URLs and saves them to the specified **chaos-output** directory. It then unzips the downloaded files and merges the resulting text files into a single **merged.txt** file. The script also includes error handling for failed downloads and removes any extracted zip files. Once all URLs have been downloaded and manipulated, the script outputs a **"Done!"** message to indicate completion.

## Prerequisites

-   **Python 3:-** This script is written in Python 3, so you will need to have Python 3 installed on your system in order to run it.

-   **Required modules:-** The script uses several modules that are not included with the standard Python library. You will need to install the following modules using pip: 

    ```argparse os shutil zipfile json requests```

## Installation

```
wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/main/Get-Chaos-Data/chaos-data-get.py
```


## Examples

**To use the script, follow these steps:**

1. Run the script using the command python script_name.py (replace "script_name" with the actual name of the script).

2. Use the command-line arguments to filter the URLs based on the desired criteria. The available arguments are:

    ```
    -p or --platform: Filter URLs by platform (choose from "hackerone", "bugcrowd", "yeswehack", or "null").

    -n or --name: Filter URLs by program name.
    
    -b or --bounty: Filter URLs by bounty status (choose from "true" or 
    "false").
    
    -a or --all: Download URLs from all programs.
    
    -o or --output: Output directory (default is "chaos-output").
    ```
3. If no arguments are provided, the script will print the help message showing the available options.

4. The script will load the URL data from the index.json file and filter it based on the provided arguments.

5. The script will then download and manipulate the URL lists based on the filtered data, and save the results in the output directory.

6. After all URLs have been downloaded and manipulated, the script will print the message "Done!".

**These are examples of how to use the script:**

-   To download URLs from the HackerOne platform.

    ```
    python chaos-data-get.py -p hackerone
    ```
-   To download URLs from the HackerOne platform that have a bounty.
    ```
    python chaos-data-get.py -p hackerone -b true
    ```
-   To download URLs from the HackerOne platform that do not have a bounty 
    ```
    python chaos-data-get.py -p hackerone -b false
    ```

-   To download URLs from the Bugcrowd platform.
    ```
    python chaos-data-get.py -p bugcrowd
    ```

-   To download URLs from the Bugcrowd platform that have a bounty.
    ```
    python chaos-data-get.py -p bugcrowd -b true
    ```

-   To download URLs from the Bugcrowd platform that do not have a bounty.
    ```
    python chaos-data-get.py -p bugcrowd -b false
    ```

-   To download URLs from programs that do not have a platform specified.

    ```
    python chaos-data-get.py -p null
    ```

-   To download URLs from programs that do not have a platform specified and have a bounty. 
    ```
    python chaos-data-get.py -p null -b true
    ```

-   To download URLs from programs that do not have a platform specified and do not have a bounty. 

    ```
    python chaos-data-get.py -p null -b false
    ```

-   To download URLs from the YesWeHack platform.
    ```
    python chaos-data-get.py -p yeswehack
    ```
-   To download URLs from all programs.
    
    ```
    python chaos-data-get.py -a
    ```

-   To download URLs from the specific program name.
    ```
    python chaos-data-get.py -n Adobe
    ```

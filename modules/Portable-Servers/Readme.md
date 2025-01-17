
<h1 align="center">Portable Server Scripts</h1>

A collection of portable server scripts designed for pentesting, and quick setup of servers in Python.

## Scripts

### 1. FTP-Server.py

A simple FTP server using `pyftpdlib`.

**Usage:**
```bash
python FTP-Server.py [-h] [-H HOST] [-P PORT] [-u USER] [-p PASSWORD] [-d DIRECTORY] [--disable-anonymous]
```

**Options:**
- `-H`, `--host`: IP address to bind the FTP server (default: `0.0.0.0`).
- `-P`, `--port`: Port number for the FTP server (default: `21`).
- `-u`, `--user`: Username for the FTP server (optional).
- `-p`, `--password`: Password for the FTP server user (optional).
- `-d`, `--directory`: Directory to share via FTP (default: `/tmp`).
- `--disable-anonymous`: Disable anonymous access to the FTP server.


### 2. HTTP-PUT-Server.py
A simple HTTP server with custom directory listing and drag-and-drop uploads.

**Usage:**
```bash
python HTTP-PUT-Server.py [-h] [-p PORT] [-d DIRECTORY]
```

**Options:**
- `-p`, `--port`: Port to serve HTTP on (default: `80`).
- `-d`, `--directory`: Directory to serve (default: current directory).




### 3. Python3-https.py
A secure HTTPS server using Python 3.

**Usage:**
```bash
python Python3-https.py [-h] [-c CERT] [-k KEY] [-H HOST] [-p PORT] [-d DIRECTORY]
```

**Options:**
- `-c`, `--cert`: Path to the SSL certificate (default: `cert.pem`).
- `-k`, `--key`: Path to the SSL key (default: `key.pem`).
- `-H`, `--host`: Host to bind to (default: `0.0.0.0`).
- `-p`, `--port`: Port to bind to (default: `443`).
- `-d`, `--directory`: Directory to serve (default: current directory).


### 4. Python2-https.py
A secure HTTPS server using Python 2.

**Usage:**
```bash
python2.7 Python2-https.py [-h] [-c CERT] [-k KEY] [-H HOST] [-p PORT] [-d DIRECTORY]
```

**Options:**
- `-c`, `--cert`: Path to the SSL certificate (default: `cert.pem`).
- `-k`, `--key`: Path to the SSL key (default: `key.pem`).
- `-H`, `--host`: Host to bind to (default: `0.0.0.0`).
- `-p`, `--port`: Port to bind to (default: `443`).
- `-d`, `--directory`: Directory to serve (default: current directory).


## Requirements

- Python 2.7 or Python 3.x
- Required Python libraries:
  - `pyftpdlib` for FTP-Server.py

## Installation
- FTP Server:
  ```bash
  wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/refs/heads/main/Portable-Servers/FTP-Server.py
  ```
  ```bash
  pip install pyftpdlib
  ```
- HTTP PUT Server:
  ```bash
  wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/refs/heads/main/Portable-Servers/HTTP-PUT-Server.py
  ```
  
- Python 3 HTTPS Server:
  ```bash
  wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/refs/heads/main/Portable-Servers/Python3-https.py
  ```

- Python 2 HTTPS Server:
  ```bash
  wget https://raw.githubusercontent.com/InfoSecWarrior/Offensive-Pentesting-Scripts/refs/heads/main/Portable-Servers/Python2-https.py
  ```



## Usage
Run any of the scripts with the appropriate arguments based on your use case. For example:

To start an FTP server:
```bash
python FTP-Server.py -H 127.0.0.1 -P 2121 -d /tmp
```

To start an HTTP PUT server:
```bash
python HTTP-PUT-Server.py -p 8080 -d /var/www
```

To start a secure HTTPS server with Python 3:
```bash
python Python3-https.py -c cert.pem -k key.pem -d /var/www
```

To start a secure HTTPS server with Python 2:
```bash
python2.7 Python2-https.py -c cert.pem -k key.pem
```

# IP Range Scanner

A simple Python script to test connectivity to IP ranges and find reachable servers.

## What it does

- Reads IP ranges from `ranges.txt` file
- Tests random IPs from each range (only changes last octet)
- Tests 100 IPs simultaneously

## Installation on Server

### Method 1: Direct Download
```bash
wget https://raw.githubusercontent.com/erfjab/range-scanner/refs/heads/master/scanner.py
```

### Method 2: Manual Copy (if internet is restricted)
1. Copy the source code from the GitHub link above
2. Create a new file: `nano scanner.py`
3. Paste the code and save

### Requirements
- Python 3.x (usually pre-installed)
- No external dependencies needed

## Setup IP Ranges

Create `ranges.txt` file:
```bash
nano ranges.txt
```

Add your IP ranges (one per line):
```
78.46.0.0/15
185.199.108.0/22
```

Example: `78.46.0.0/15` will test IPs like:
- 78.46.0.1
- 78.46.0.45  
- 78.46.0.200
- ...

## Running the Scanner

```bash
python3 scanner.py
```

## Results

### During Scan
- `✓ IP - REACHABLE` - Working IP found
- `✗ IP - UNREACHABLE` - IP not responding

### After Completion
- Summary shows total tested vs successful IPs

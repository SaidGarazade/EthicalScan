# Recon-Attack-Tool


## 💻 Usage Examples

### Basic Directory Scan
Perform a simple directory enumeration on the target website:
python3 recon.py -u https://example.com -d

### Advanced Directory Scan
Scan with 50 threads and specific file extensions:
python3 recon.py -u https://example.com -d -t 50 -x php,html,txt

### Subdomain Enumeration with IP Resolution
Discover subdomains and resolve their IP addresses:
python3 recon.py -u example.com -s

### Vulnerability Scan
Check for common security vulnerabilities:
python3 recon.py -u https://example.com -V

### Full Comprehensive Scan
Run all scan types with a custom wordlist:
python3 recon.py -u https://example.com -d -s -V -w custom.txt

### Stealth Mode
Slow scan with delays to avoid detection:
python3 recon.py -u https://example.com -d -t 5 --delay 1

### Scan Through Proxy
Route traffic through a proxy server:
python3 recon.py -u https://example.com -d --proxy http://127.0.0.1:8080

### Export Results
Save scan results to a JSON file:
python3 recon.py -u https://example.com -d -o results.json

--------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------
Contact / Author
Maintained By: EthicalScan / Said Garazade
If you have questions or feature requests, please open an issue in this repository.

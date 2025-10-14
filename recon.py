#!/usr/bin/env python3
"""
EthicalScan v2.0 - Advanced Web Security Scanner
Professional penetration testing tool
"""

import requests
import socket
import dns.resolver
import threading
import argparse
import sys
import time
import random
import json
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
warnings.filterwarnings('ignore')

# Colorama initialize
init(autoreset=True)

class WebReconPro:
    def __init__(self, target, threads=20, timeout=5, delay=0, proxy=None):
        self.target = target
        self.threads = threads
        self.timeout = timeout
        self.delay = delay
        self.proxy = proxy
        self.found_items = []
        self.checked = 0
        self.lock = threading.Lock()
        
        # Multiple User-Agents for evasion
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Setup session with retry
        self.session = self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set proxy if provided
        if self.proxy:
            session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        
        return session
    
    def _get_random_headers(self):
        """Generate random headers for WAF evasion"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def print_banner(self):
        banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
║               EthicalScan v2.0 - ADVANCED                   ║
║          Professional Web Security Scanner                    ║
║   Directory • Files • Subdomains • Vulnerabilities           ║
║   WAF Bypass • Multi-threading • Proxy Support               ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    def directory_scan(self, wordlist_file=None, extensions=None, status_codes=None, recursive=False):
        """Advanced Directory/File Bruteforce"""
        
        # Enhanced default wordlist
        wordlist = [
            # Admin panels
            'admin', 'administrator', 'admin_area', 'adminpanel', 'control', 'controlpanel',
            'admin1', 'admin2', 'moderator', 'webadmin', 'adminarea', 'bb-admin',
            # Login pages
            'login', 'signin', 'sign-in', 'auth', 'authentication', 'connect', 'portal',
            # Config files
            'config', 'configuration', 'settings', 'setup', 'install', 'installation',
            # Databases
            'db', 'database', 'sql', 'mysql', 'mssql', 'postgres', 'mongodb',
            # Backups
            'backup', 'backups', 'bak', 'old', 'temp', 'tmp', 'test', 'demo',
            # API endpoints
            'api', 'rest', 'graphql', 'v1', 'v2', 'v3', 'swagger', 'docs',
            # CMS specific
            'wp-admin', 'wp-content', 'wp-includes', 'wp-config', 'wordpress',
            'administrator', 'joomla', 'drupal', 'cms',
            # Upload dirs
            'uploads', 'upload', 'files', 'file', 'documents', 'images', 'media',
            # Development
            'dev', 'development', 'test', 'testing', 'stage', 'staging', 'beta',
            # Common files
            'robots.txt', 'sitemap.xml', '.htaccess', '.env', '.git', '.svn',
            'web.config', 'crossdomain.xml', 'clientaccesspolicy.xml',
            # Sensitive files
            'config.php', 'database.php', 'db.php', 'connect.php', 'settings.php',
            'index.php', 'index.html', 'default.php', 'home.php',
            # Security
            'phpmyadmin', 'pma', 'mysql', 'adminer', 'phpMyAdmin',
            'shell', 'webshell', 'backdoor', 'cmd', 'console',
            # Info disclosure
            'phpinfo.php', 'info.php', 'test.php', 'debug.php', 'trace.php'
        ]
        
        # Load custom wordlist
        if wordlist_file:
            try:
                with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                    wordlist = [line.strip() for line in f if line.strip()]
                print(f"{Fore.GREEN}[+] Custom wordlist loaded: {len(wordlist)} words{Style.RESET_ALL}")
            except FileNotFoundError:
                print(f"{Fore.RED}[-] Wordlist file not found: {wordlist_file}{Style.RESET_ALL}")
                return
        
        # Add extensions
        if extensions:
            extended_wordlist = []
            for word in wordlist:
                extended_wordlist.append(word)
                for ext in extensions:
                    extended_wordlist.append(f"{word}.{ext}")
            wordlist = extended_wordlist
        
        # Default status codes to report
        if not status_codes:
            status_codes = [200, 201, 202, 204, 301, 302, 307, 308, 401, 403, 405, 500]
        
        print(f"\n{Fore.YELLOW}[*] Directory Scan started: {self.target}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Wordlist: {len(wordlist)} entries{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Threads: {self.threads}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Timeout: {self.timeout}s{Style.RESET_ALL}")
        if self.delay:
            print(f"{Fore.YELLOW}[*] Delay: {self.delay}s (stealth mode){Style.RESET_ALL}")
        if self.proxy:
            print(f"{Fore.YELLOW}[*] Proxy: {self.proxy}{Style.RESET_ALL}")
        print()
        
        def check_path(path):
            try:
                if self.delay:
                    time.sleep(self.delay)
                
                url = urljoin(self.target, path)
                headers = self._get_random_headers()
                
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=False,
                    verify=False
                )
                
                with self.lock:
                    self.checked += 1
                
                # Check if status code is in our list
                if response.status_code in status_codes:
                    size = len(response.content)
                    lines = response.text.count('\n')
                    words = len(response.text.split())
                    
                    result = {
                        'url': url,
                        'status': response.status_code,
                        'size': size,
                        'lines': lines,
                        'words': words,
                        'path': path,
                        'redirect': response.headers.get('Location', '')
                    }
                    
                    with self.lock:
                        self.found_items.append(result)
                    
                    # Color coding
                    if response.status_code == 200:
                        color = Fore.GREEN
                        status_text = "OK"
                    elif response.status_code in [301, 302, 307, 308]:
                        color = Fore.CYAN
                        status_text = "REDIRECT"
                    elif response.status_code in [401, 403]:
                        color = Fore.YELLOW
                        status_text = "AUTH REQUIRED"
                    elif response.status_code == 405:
                        color = Fore.MAGENTA
                        status_text = "METHOD NOT ALLOWED"
                    elif response.status_code >= 500:
                        color = Fore.RED
                        status_text = "SERVER ERROR"
                    else:
                        color = Fore.WHITE
                        status_text = str(response.status_code)
                    
                    redirect_info = f" -> {result['redirect']}" if result['redirect'] else ""
                    print(f"{color}[{status_text:^18}] {url:<60} [Size: {size:>8}] [Lines: {lines:>5}]{redirect_info}{Style.RESET_ALL}")
                    
                    return result
                
            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.RequestException:
                pass
            except Exception:
                pass
            
            return None
        
        # Multi-threading scan
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_path, path): path for path in wordlist}
            
            try:
                for future in as_completed(futures):
                    pass
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Scan stopped (Ctrl+C){Style.RESET_ALL}")
                executor._threads.clear()
                return
        
        elapsed = time.time() - start_time
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Directory scan completed!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Found: {len(self.found_items)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Checked: {self.checked}/{len(wordlist)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Time: {elapsed:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Speed: {self.checked/elapsed:.2f} req/s{Style.RESET_ALL}")
    
    def subdomain_scan(self, wordlist_file=None, resolve_ip=True):
        """Advanced Subdomain Enumeration with DNS and HTTP verification"""
        
        # Extract domain
        parsed = urlparse(self.target)
        domain = parsed.netloc or parsed.path
        domain = domain.replace('www.', '')
        
        # Enhanced subdomain wordlist
        subdomains = [
            # Common
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
            'webdisk', 'ns', 'cpanel', 'whm', 'autodiscover', 'autoconfig',
            # Admin/Management
            'admin', 'administrator', 'moderator', 'webmaster', 'sysadmin',
            'panel', 'control', 'manager', 'console',
            # Development
            'dev', 'development', 'test', 'testing', 'stage', 'staging', 'demo',
            'sandbox', 'qa', 'uat', 'preprod', 'prod', 'production',
            # Services
            'blog', 'forum', 'shop', 'store', 'api', 'cdn', 'static', 'media',
            'images', 'img', 'assets', 'downloads', 'files', 'upload', 'uploads',
            # Mobile
            'm', 'mobile', 'wap', 'touch', 'app', 'apps',
            # Geographic
            'us', 'eu', 'asia', 'uk', 'de', 'fr', 'jp', 'cn',
            # Cloud
            'cloud', 'aws', 'azure', 'gcp', 'digitalocean', 'heroku',
            # Communication
            'chat', 'im', 'irc', 'messenger', 'voice', 'video', 'meet', 'zoom',
            # Security
            'vpn', 'firewall', 'gateway', 'proxy', 'secure', 'ssl', 'tls',
            # Monitoring
            'monitor', 'monitoring', 'status', 'stats', 'analytics', 'metrics',
            'grafana', 'prometheus', 'kibana', 'elk',
            # Databases
            'db', 'database', 'mysql', 'postgres', 'mongo', 'redis', 'sql',
            # Misc
            'git', 'svn', 'jenkins', 'ci', 'cd', 'docker', 'k8s', 'kubernetes'
        ]
        
        if wordlist_file:
            try:
                with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"{Fore.RED}[-] Subdomain wordlist not found{Style.RESET_ALL}")
                return
        
        print(f"\n{Fore.YELLOW}[*] Subdomain Scan started: {domain}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Wordlist: {len(subdomains)} subdomains{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Threads: {self.threads}{Style.RESET_ALL}\n")
        
        def check_subdomain(sub):
            subdomain = f"{sub}.{domain}"
            try:
                # DNS resolution
                answers = dns.resolver.resolve(subdomain, 'A', lifetime=self.timeout)
                ips = [str(rdata) for rdata in answers]
                
                # HTTP verification
                http_status = None
                https_status = None
                title = None
                
                if resolve_ip:
                    # Try HTTPS first
                    try:
                        url = f"https://{subdomain}"
                        headers = self._get_random_headers()
                        resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                        https_status = resp.status_code
                        
                        # Extract title
                        if 'text/html' in resp.headers.get('Content-Type', ''):
                            import re
                            title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
                            if title_match:
                                title = title_match.group(1).strip()[:50]
                    except:
                        pass
                    
                    # Try HTTP
                    try:
                        url = f"http://{subdomain}"
                        headers = self._get_random_headers()
                        resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                        http_status = resp.status_code
                        
                        if not title and 'text/html' in resp.headers.get('Content-Type', ''):
                            import re
                            title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
                            if title_match:
                                title = title_match.group(1).strip()[:50]
                    except:
                        pass
                
                result = {
                    'subdomain': subdomain,
                    'ips': ips,
                    'http_status': http_status,
                    'https_status': https_status,
                    'title': title
                }
                
                with self.lock:
                    self.found_items.append(result)
                
                # Pretty output
                ip_str = ', '.join(ips)
                status_str = ""
                if https_status:
                    status_str = f"[HTTPS: {https_status}]"
                elif http_status:
                    status_str = f"[HTTP: {http_status}]"
                
                title_str = f" - {title}" if title else ""
                
                print(f"{Fore.GREEN}[+] {subdomain:<45} => {ip_str:<40} {status_str}{title_str}{Style.RESET_ALL}")
                return result
                
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                pass
            except Exception:
                pass
            
            return None
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_subdomain, sub): sub for sub in subdomains}
            
            try:
                for future in as_completed(futures):
                    pass
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Scan stopped (Ctrl+C){Style.RESET_ALL}")
                return
        
        elapsed = time.time() - start_time
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Subdomain scan completed!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Found: {len(self.found_items)} subdomains{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Time: {elapsed:.2f} seconds{Style.RESET_ALL}")
    
    def vulnerability_scan(self):
        """Advanced Security & Vulnerability Checks"""
        print(f"\n{Fore.YELLOW}[*] Vulnerability Scan started...{Style.RESET_ALL}\n")
        
        vulnerabilities = []
        
        try:
            headers = self._get_random_headers()
            response = self.session.get(self.target, headers=headers, timeout=self.timeout, verify=False)
            
            # 1. Security Headers Check
            print(f"{Fore.CYAN}[1] Security Headers Analysis:{Style.RESET_ALL}\n")
            
            security_headers = {
                'Strict-Transport-Security': ('HSTS', 'HIGH', 'HTTPS enforcement missing'),
                'X-Frame-Options': ('Clickjacking', 'MEDIUM', 'Clickjacking protection missing'),
                'X-Content-Type-Options': ('MIME-Sniffing', 'MEDIUM', 'MIME-sniffing protection missing'),
                'X-XSS-Protection': ('XSS', 'LOW', 'XSS protection header missing'),
                'Content-Security-Policy': ('CSP', 'HIGH', 'Content Security Policy missing'),
                'Referrer-Policy': ('Privacy', 'LOW', 'Referrer policy not set'),
                'Permissions-Policy': ('Feature Policy', 'LOW', 'Permissions policy missing')
            }
            
            for header, (vuln_type, severity, description) in security_headers.items():
                if header in response.headers:
                    print(f"{Fore.GREEN}  [✓] {header:<35} => {response.headers[header][:50]}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}  [✗] {header:<35} => Missing [{severity} RISK]{Style.RESET_ALL}")
                    vulnerabilities.append({
                        'type': vuln_type,
                        'severity': severity,
                        'header': header,
                        'description': description
                    })
            
            # 2. Server Information Disclosure
            print(f"\n{Fore.CYAN}[2] Information Disclosure:{Style.RESET_ALL}\n")
            
            info_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
            for header in info_headers:
                if header in response.headers:
                    print(f"{Fore.YELLOW}  [!] {header:<25} => {response.headers[header]}{Style.RESET_ALL}")
                    vulnerabilities.append({
                        'type': 'Information Disclosure',
                        'severity': 'LOW',
                        'header': header,
                        'value': response.headers[header]
                    })
            
            # 3. Common Vulnerability Files
            print(f"\n{Fore.CYAN}[3] Sensitive Files Check:{Style.RESET_ALL}\n")
            
            sensitive_files = [
                ('.git/HEAD', 'Git Repository Exposed'),
                ('.env', 'Environment File Exposed'),
                ('phpinfo.php', 'PHP Info Page'),
                ('test.php', 'Test File'),
                ('backup.sql', 'SQL Backup File'),
                ('web.config', 'Config File'),
                ('.htaccess', 'Apache Config'),
                ('admin/', 'Admin Panel'),
                ('wp-config.php', 'WordPress Config')
            ]
            
            for file, description in sensitive_files:
                try:
                    url = urljoin(self.target, file)
                    r = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                    if r.status_code == 200:
                        print(f"{Fore.RED}  [VULN] {file:<25} => {description} [Status: {r.status_code}]{Style.RESET_ALL}")
                        vulnerabilities.append({
                            'type': 'Sensitive File',
                            'severity': 'HIGH',
                            'file': file,
                            'url': url,
                            'description': description
                        })
                except:
                    pass
            
            # 4. HTTP Methods Check
            print(f"\n{Fore.CYAN}[4] HTTP Methods Analysis:{Style.RESET_ALL}\n")
            
            dangerous_methods = ['PUT', 'DELETE', 'TRACE', 'CONNECT']
            allowed_methods = []
            
            try:
                r = self.session.options(self.target, headers=headers, timeout=self.timeout, verify=False)
                if 'Allow' in r.headers:
                    allowed_methods = r.headers['Allow'].split(',')
                    allowed_methods = [m.strip() for m in allowed_methods]
                    
                    for method in dangerous_methods:
                        if method in allowed_methods:
                            print(f"{Fore.RED}  [VULN] {method} method enabled{Style.RESET_ALL}")
                            vulnerabilities.append({
                                'type': 'HTTP Method',
                                'severity': 'MEDIUM',
                                'method': method,
                                'description': f'{method} method should be disabled'
                            })
                    
                    safe_methods = [m for m in allowed_methods if m not in dangerous_methods]
                    if safe_methods:
                        print(f"{Fore.GREEN}  [✓] Safe methods: {', '.join(safe_methods)}{Style.RESET_ALL}")
            except:
                pass
            
            # Summary
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Vulnerability Summary:{Style.RESET_ALL}")
            
            high = len([v for v in vulnerabilities if v['severity'] == 'HIGH'])
            medium = len([v for v in vulnerabilities if v['severity'] == 'MEDIUM'])
            low = len([v for v in vulnerabilities if v['severity'] == 'LOW'])
            
            print(f"  {Fore.RED}HIGH: {high}{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}MEDIUM: {medium}{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}LOW: {low}{Style.RESET_ALL}")
            print(f"  Total: {len(vulnerabilities)}")
            
            self.found_items = vulnerabilities
            
        except Exception as e:
            print(f"{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")
    
    def save_results(self, filename=None, format='json'):
        """Save results to file"""
        if not filename:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"webrecon_{timestamp}.{format}"
        
        try:
            if format == 'json':
                data = {
                    'target': self.target,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'results': self.found_items,
                    'stats': {
                        'total_found': len(self.found_items),
                        'total_checked': self.checked
                    }
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format == 'txt':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"WebRecon Pro v2.0 - Scan Results\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"Target: {self.target}\n")
                    f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Found: {len(self.found_items)}\n")
                    f.write(f"{'='*80}\n\n")
                    
                    for item in self.found_items:
                        f.write(f"{json.dumps(item, indent=2, ensure_ascii=False)}\n")
                        f.write(f"{'-'*80}\n")
            
            print(f"\n{Fore.GREEN}[✓] Results saved: {filename}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[-] Save error: {str(e)}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(
        description='WebRecon Pro v2.0 - Advanced Web Security Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Fore.CYAN}Examples:{Style.RESET_ALL}

  # Directory scan (basic)
  python3 recon.py -u https://example.com -d

  # Directory scan (advanced)
  python3 recon.py -u https://example.com -d -t 50 -x php,html,txt

  # Subdomain scan with IP resolve
  python3 recon.py -u example.com -s

  # Vulnerability scan
  python3 recon.py -u https://example.com -V

  # Full scan with custom wordlist
  python3 recon.py -u https://example.com -d -s -V -w custom.txt

  # Stealth mode (slow + delay)
  python3 recon.py -u https://example.com -d -t 5 --delay 1

  # Use proxy
  python3 recon.py -u https://example.com -d --proxy http://127.0.0.1:8080

  # Export results
  python3 recon.py -u https://example.com -d -o results.json
        """
    )
    
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-d', '--directory', action='store_true', help='Directory/File scan')
    parser.add_argument('-s', '--subdomain', action='store_true', help='Subdomain enumeration')
    parser.add_argument('-V', '--vuln', action='store_true', help='Vulnerability scan')
    parser.add_argument('-w', '--wordlist', help='Custom wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=20, help='Number of threads (default: 20)')
    parser.add_argument('-x', '--extensions', help='File extensions (comma separated): php,html,txt')
    parser.add_argument('--delay', type=float, default=0, help='Request delay (stealth mode)')
    parser.add_argument('--timeout', type=int, default=5, help='Request timeout (default: 5)')
    parser.add_argument('--proxy', help='Proxy URL (http://ip:port)')
    parser.add_argument('-o', '--output', help='Output file (JSON or TXT)')
    parser.add_argument('--status', help='Status codes (comma separated): 200,301,403')
    
    args = parser.parse_args()
    
    # Disable warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Parse extensions
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(',')]
    
    # Parse status codes
    status_codes = None
    if args.status:
        status_codes = [int(code.strip()) for code in args.status.split(',')]
    
    # Create scanner instance
    scanner = WebReconPro(
        args.url, 
        threads=args.threads, 
        timeout=args.timeout,
        delay=args.delay,
        proxy=args.proxy
    )
    
    scanner.print_banner()
    
    # Run selected scans
    if args.directory:
        scanner.directory_scan(
            wordlist_file=args.wordlist,
            extensions=extensions,
            status_codes=status_codes
        )
    
    if args.subdomain:
        scanner.subdomain_scan(wordlist_file=args.wordlist)
    
    if args.vuln:
        scanner.vulnerability_scan()
    
    # If no scan selected, show help
    if not (args.directory or args.subdomain or args.vuln):
        print(f"{Fore.RED}[!] Select scan type: -d (directory), -s (subdomain), -V (vulnerability){Style.RESET_ALL}\n")
        parser.print_help()
        sys.exit(1)
    
    # Save results
    if args.output and scanner.found_items:
        output_format = 'json' if args.output.endswith('.json') else 'txt'
        scanner.save_results(args.output, format=output_format)
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[✓] Scan completed!{Style.RESET_ALL}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Program stopped (Ctrl+C){Style.RESET_ALL}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Critical error: {str(e)}{Style.RESET_ALL}\n")
        sys.exit(1)

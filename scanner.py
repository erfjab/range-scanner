import subprocess
import threading
import time
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class IPRangeChecker:
    def __init__(self, ranges_file='ranges.txt', ips_per_range=10, timeout=3):
        self.ranges_file = ranges_file
        self.ips_per_range = ips_per_range
        self.timeout = timeout
        self.successful_ips = []
        self.lock = threading.Lock()
    
    def cidr_to_ip_list(self, cidr):
        try:
            network, prefix = cidr.strip().split('/')
            ip_parts = [int(x) for x in network.split('.')]
            base_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            ips = []
            attempts = 0
            max_attempts = self.ips_per_range * 10
            
            while len(ips) < self.ips_per_range and attempts < max_attempts:
                last_octet = random.randint(1, 254)
                ip = f"{base_ip}.{last_octet}"
                
                if ip not in ips:
                    ips.append(ip)
                attempts += 1
            
            return ips
        except Exception as e:
            print(f"Error parsing CIDR {cidr}: {e}")
            return []
    
    def ping_ip(self, ip):
        try:
            if sys.platform.startswith('win'):
                cmd = ['ping', '-n', '1', '-w', str(self.timeout * 1000), ip]
            else:
                cmd = ['ping', '-c', '1', '-W', str(self.timeout), ip]
            
            result = subprocess.run(cmd, 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL, 
                                  timeout=self.timeout + 1)
            
            return result.returncode == 0
        except:
            return False
    
    def test_ip_batch(self, ips, range_name):
        successful = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ip = {executor.submit(self.ping_ip, ip): ip for ip in ips}
            
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    if future.result():
                        successful.append(ip)
                        print(f"✓ {ip} - REACHABLE")
                    else:
                        print(f"✗ {ip} - UNREACHABLE")
                except:
                    print(f"✗ {ip} - ERROR")
        
        return successful
    
    def load_ranges(self):
        try:
            with open(self.ranges_file, 'r') as f:
                ranges = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return ranges
        except FileNotFoundError:
            print(f"Error: File '{self.ranges_file}' not found!")
            print("Please create ranges.txt with CIDR ranges, one per line.")
            print("Example content:")
            print("78.46.0.0/15")
            return []
        except Exception as e:
            print(f"Error reading ranges file: {e}")
            return []
    
    def run_check(self):
        print("=" * 60)
        print("IP Range Connectivity Checker")
        print("=" * 60)
        
        ranges = self.load_ranges()
        if not ranges:
            return
        
        print(f"Loaded {len(ranges)} IP ranges")
        print(f"Testing {self.ips_per_range} random IPs per range")
        print(f"Timeout: {self.timeout} seconds")
        print("-" * 60)
        
        all_successful = []
        
        for i, cidr_range in enumerate(ranges, 1):
            print(f"\n[{i}/{len(ranges)}] Testing range: {cidr_range}")

            ips = self.cidr_to_ip_list(cidr_range)
            if not ips:
                print(f"Could not generate IPs from range: {cidr_range}")
                continue
            
            print(f"Generated {len(ips)} IPs to test...")

            successful = self.test_ip_batch(ips, cidr_range)
            all_successful.extend(successful)
            
            if successful:
                print(f"✓ Range {cidr_range}: {len(successful)}/{len(ips)} IPs reachable")
            else:
                print(f"✗ Range {cidr_range}: No reachable IPs found")
        
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        
        if all_successful:
            print(f"✓ Found {len(all_successful)} reachable IPs:")
            for ip in sorted(all_successful, key=lambda x: tuple(int(part) for part in x.split('.'))):
                print(f"  {ip}")            
        else:
            print("✗ No reachable IPs found in any range")
        
        print(f"\nTotal ranges tested: {len(ranges)}")
        print(f"Total IPs tested: {sum(len(self.cidr_to_ip_list(r)) for r in ranges)}")
        print(f"Successful connections: {len(all_successful)}")

def main():
    print("Starting IP connectivity check...")
    
    try:
        with open('ranges.txt', 'r') as f:
            pass
    except FileNotFoundError:
        print("Creating sample ranges.txt file...")
        with open('ranges.txt', 'w') as f:
            f.write("# IP ranges to test (CIDR notation)\n")
            f.write("# One range per line\n")
            f.write("78.46.0.0/15\n")
        print("Sample ranges.txt created. Please edit it with your desired ranges.")
        return
    
    checker = IPRangeChecker(
        ranges_file='ranges.txt',
        ips_per_range=100,
        timeout=3
    )
    
    start_time = time.time()
    checker.run_check()
    end_time = time.time()
    
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()

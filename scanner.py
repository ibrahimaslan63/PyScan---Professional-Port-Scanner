import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import json
import time
from datetime import datetime

# Terminal renklendirme için basit ANSI kodları
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def get_service_name(port):
    """Port numarasına göre bilinen servis adını döner."""
    try:
        return socket.getservbyport(port)
    except:
        return "Unknown Service"

def banner_grab(s):
    """Bağlantı kurulan porttan servis bilgisini (banner) çekmeye çalışır."""
    try:
        s.settimeout(2)
        # Bazı servisler önce veri gönderir (SSH, FTP), bazıları tetikleme bekler (HTTP)
        s.send(b'Hello\r\n')
        banner = s.recv(1024).decode().strip()
        return banner
    except:
        return "No banner available"

def scan_port(target, port, timeout, results):
    """Tek bir portu tarar ve sonuçları listeye ekler."""
    try:
        # AF_INET: IPv4, SOCK_STREAM: TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((target, port))
            
            if result == 0:
                service = get_service_name(port)
                banner = banner_grab(s)
                
                port_info = {
                    "port": port,
                    "status": "open",
                    "service": service,
                    "banner": banner
                }
                results.append(port_info)
                print(f"{Colors.GREEN}[+] Port {port:5} ({service:12}) is OPEN. Banner: {banner}{Colors.RESET}")
    except Exception:
        pass

def save_results(results, filename, format_type='json'):
    """Sonuçları dosyaya kaydeder."""
    if format_type == 'json':
        with open(f"{filename}.json", 'w') as f:
            json.dump(results, f, indent=4)
    else:
        with open(f"{filename}.txt", 'w') as f:
            for res in results:
                f.write(f"Port: {res['port']} | Service: {res['service']} | Banner: {res['banner']}\n")

def main():
    print(f"{Colors.BLUE}{Colors.BOLD}--- PyScan: Professional Port Scanner ---{Colors.RESET}")
    
    # 1. Girdileri Al
    target = input(f"{Colors.YELLOW}Hedef IP veya Domain: {Colors.RESET}")
    try:
        target_ip = socket.gethostbyname(target)
        print(f"{Colors.BLUE}Tarama başlatılıyor: {target_ip}{Colors.RESET}")
    except socket.gaierror:
        print(f"{Colors.RED}[!] Hata: Domain çözülemedi.{Colors.RESET}")
        return

    port_range = input(f"{Colors.YELLOW}Port Aralığı (Örn: 1-1024): {Colors.RESET}")
    start_port, end_port = map(int, port_range.split('-'))
    
    timeout = float(input(f"{Colors.YELLOW}Timeout (Örn: 0.5): {Colors.RESET}") or 0.5)
    thread_count = int(input(f"{Colors.YELLOW}Thread Sayısı (Örn: 100): {Colors.RESET}") or 100)

    results = []
    start_time = datetime.now()

    # 4. Multi-threading Uygula
    print(f"\n{Colors.BOLD}Taranıyor...{Colors.RESET}\n")
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(scan_port, target_ip, port, timeout, results)

    end_time = datetime.now()
    total_time = end_time - start_time

    # 7. Çıktı ve Kayıt
    print(f"\n{Colors.BLUE}{'='*40}{Colors.RESET}")
    print(f"{Colors.BOLD}Tarama Tamamlandı!{Colors.RESET}")
    print(f"Toplam Açık Port: {len(results)}")
    print(f"Süre: {total_time}")
    
    if results:
        save_choice = input(f"\nSonuçlar kaydedilsin mi? (y/n): ").lower()
        if save_choice == 'y':
            filename = f"scan_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            save_results(results, filename, 'json')
            print(f"{Colors.GREEN}[+] Sonuçlar {filename}.json olarak kaydedildi.{Colors.RESET}")

if __name__ == "__main__":
    main()
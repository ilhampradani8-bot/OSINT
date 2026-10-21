"""
Modul OWASP Amass Style Subdomain & Attack Surface Scanner
Melakukan enumerasi subdomain aktif, pemetaan infrastruktur DNS via Cloudflare DoH,
dan deteksi portal internal/eksposur server (admin, dev, vpn, api, mail, lpse, sso).
"""

import urllib.request
import urllib.parse
import json
import concurrent.futures
from typing import Dict, Any, List

COMMON_SUBDOMAINS = [
    # Layanan Umum & API
    "www", "api", "app", "dev", "staging", "test", "beta",
    # Otentikasi & Akses
    "admin", "portal", "login", "auth", "sso", "vpn", "dashboard",
    # Mail & Komunikasi
    "mail", "webmail", "smtp", "pop", "mx",
    # Server & Infrastruktur
    "ns1", "ns2", "cloud", "cdn", "static", "media", "storage",
    # Khusus Instansi Indonesia (Pemerintah & Kampus)
    "lpse", "simpeg", "siak", "dosen", "mhs", "presensi", "jdih", "layanan"
]

def check_subdomain_doh(domain: str, prefix: str) -> Dict[str, Any]:
    target_host = f"{prefix}.{domain}".lower()
    doh_url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(target_host)}&type=A"
    
    try:
        req = urllib.request.Request(
            doh_url,
            headers={"Accept": "application/dns-json", "User-Agent": "OSINT-Amass/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.getcode() == 200:
                data = json.loads(resp.read().decode("utf-8"))
                answers = data.get("Answer", [])
                ips = [ans.get("data") for ans in answers if ans.get("data") and not ans.get("data").endswith(".")]
                cnames = [ans.get("data") for ans in answers if ans.get("data") and ans.get("data").endswith(".")]
                
                if ips or cnames:
                    return {
                        "subdomain": target_host,
                        "prefix": prefix,
                        "found": True,
                        "ips": ips,
                        "cnames": cnames,
                        "status": "Aktif (Resolved)"
                    }
    except Exception:
        pass

    return {
        "subdomain": target_host,
        "prefix": prefix,
        "found": False,
        "ips": [],
        "cnames": [],
        "status": "NXDOMAIN"
    }

def enumerate_subdomains(domain_input: str, max_workers: int = 10) -> Dict[str, Any]:
    raw = domain_input.strip().lower()
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlparse(raw)
        domain = parsed.netloc or raw
    else:
        domain = raw

    # Hilangkan www. jika ada untuk root domain
    if domain.startswith("www."):
        domain = domain[4:]

    if not domain or "." not in domain:
        return {"valid": False, "error": "Masukkan nama domain yang valid (contoh: kemkes.go.id atau tokopedia.com)."}

    active_subdomains = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(check_subdomain_doh, domain, prefix): prefix
            for prefix in COMMON_SUBDOMAINS
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res["found"]:
                active_subdomains.append(res)

    active_subdomains.sort(key=lambda x: x["subdomain"])

    return {
        "valid": True,
        "domain": domain,
        "total_probed": len(COMMON_SUBDOMAINS),
        "total_found": len(active_subdomains),
        "subdomains": active_subdomains
    }

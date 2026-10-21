"""
Modul GhostIntel / Domain, IP & Indonesian Breach Signature Analyzer
Menganalisis domain, DNS, IP Geolocation, dan membandingkan profil target
dengan basis data riwayat kebocoran data publik di Indonesia (Tokopedia, BPJS, KPU, dll).
"""

import urllib.request
import urllib.parse
import json
from typing import Dict, Any, List

# Basis Data Riwayat Kebocoran Data Terbuka di Indonesia (Indonesian Breach Intelligence)
INDONESIA_HISTORICAL_BREACHES = [
    {
        "nama_insiden": "Tokopedia Data Leak (2020)",
        "tahun": 2020,
        "estimasi_korban": "91 Juta Akun",
        "data_bocor": ["Nama Lengkap", "Alamat Email", "Nomor Telepon", "Hash Password (SHA2-384)", "Tanggal Lahir"],
        "tingkat_keparahan": "Kritis",
        "deskripsi": "Salah satu insiden kebocoran terbesar di Indonesia. Data dijual di forum RaidForums/Breached."
    },
    {
        "nama_insiden": "Bhinneka.com (2020)",
        "tahun": 2020,
        "estimasi_korban": "1.2 Juta Akun",
        "data_bocor": ["Nama", "Email", "Password Hash", "Nomor HP"],
        "tingkat_keparahan": "Tinggi",
        "deskripsi": "Kebocoran data e-commerce B2B/B2C komputer & elektronik."
    },
    {
        "nama_insiden": "Bukalapak (2019)",
        "tahun": 2019,
        "estimasi_korban": "13 Juta Akun",
        "data_bocor": ["Username", "Email", "Hash Password", "Nama", "Alamat IP"],
        "tingkat_keparahan": "Tinggi",
        "deskripsi": "Dijual oleh peretas Gnosticplayers di dark web."
    },
    {
        "nama_insiden": "BPJS Kesehatan (2021)",
        "tahun": 2021,
        "estimasi_korban": "279 Juta Baris Data",
        "data_bocor": ["NIK", "Nomor KK", "Nama Lengkap", "Nomor HP", "Alamat", "Gaji/Upah", "Status Faskes", "Foto/Data Anggota"],
        "tingkat_keparahan": "Sangat Kritis",
        "deskripsi": "Memuat data demografi kependudukan hampir seluruh warga negara Indonesia."
    },
    {
        "nama_insiden": "Komisi Pemilihan Umum / KPU RI (2020 & 2023)",
        "tahun": 2023,
        "estimasi_korban": "204 Juta DPT",
        "data_bocor": ["NIK", "Nomor Kartu Keluarga", "Nama Lengkap", "Tempat/Tgl Lahir", "Jenis Kelamin", "Alamat Domisili", "Nomor TPS"],
        "tingkat_keparahan": "Sangat Kritis",
        "deskripsi": "Data Daftar Pemilih Tetap (DPT) seluruh Indonesia dibagikan oleh pelaku anonim (Jimbo)."
    },
    {
        "nama_insiden": "Perusahaan Listrik Negara / PLN (2022)",
        "tahun": 2022,
        "estimasi_korban": "17 Juta Pelanggan",
        "data_bocor": ["ID Pelanggan", "Nama Konsumen", "Alamat Rumah", "Tipe Kwh", "Nomor Meteran Listrik"],
        "tingkat_keparahan": "Tinggi",
        "deskripsi": "Memungkinkan pelacakan alamat riil tempat tinggal berdasarkan ID pelanggan PLN."
    },
    {
        "nama_insiden": "Indihome / Telkom Indonesia (2022)",
        "tahun": 2022,
        "estimasi_korban": "26 Juta Log",
        "data_bocor": ["Riwayat Browsing (URL)", "Waktu Akses", "IP Address", "Nama Pelanggan", "Jenis Kelamin", "NIK"],
        "tingkat_keparahan": "Kritis",
        "deskripsi": "Log riwayat penjelajahan internet pelanggan beserta identitas pengguna."
    },
    {
        "nama_insiden": "Direktorat Jenderal Imigrasi (2023)",
        "tahun": 2023,
        "estimasi_korban": "34 Juta Paspor",
        "data_bocor": ["Nomor Paspor", "Nama Lengkap", "Tanggal Lahir", "Jenis Kelamin", "Masa Berlaku Paspor"],
        "tingkat_keparahan": "Tinggi",
        "deskripsi": "Data paspor warga negara Indonesia yang diterbitkan Ditjen Imigrasi Kemenkumham."
    }
]

def resolve_dns_records(domain: str) -> Dict[str, List[str]]:
    """Resolve DNS records A, MX, TXT, NS via Cloudflare DoH"""
    types = ["A", "MX", "TXT", "NS", "SOA"]
    results = {}
    
    clean_domain = domain.strip().lower()
    if clean_domain.startswith("http://") or clean_domain.startswith("https://"):
        parsed = urllib.parse.urlparse(clean_domain)
        clean_domain = parsed.netloc or clean_domain

    for rtype in types:
        doh_url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(clean_domain)}&type={rtype}"
        try:
            req = urllib.request.Request(
                doh_url,
                headers={"Accept": "application/dns-json", "User-Agent": "OSINT-GhostIntel/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.getcode() == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    answers = [item.get("data") for item in data.get("Answer", []) if item.get("data")]
                    results[rtype] = answers
        except Exception:
            results[rtype] = []

    return results

def get_ip_geolocation(ip_or_domain: str) -> Dict[str, Any]:
    """Mengambil informasi geolokasi IP via public endpoint"""
    target = ip_or_domain.strip().lower()
    if target.startswith("http://") or target.startswith("https://"):
        parsed = urllib.parse.urlparse(target)
        target = parsed.netloc or target

    try:
        url = f"http://ip-api.com/json/{urllib.parse.quote(target)}"
        req = urllib.request.Request(url, headers={"User-Agent": "OSINT-GhostIntel/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.getcode() == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "success":
                    return {
                        "ip": data.get("query"),
                        "country": data.get("country"),
                        "country_code": data.get("countryCode"),
                        "region_name": data.get("regionName"),
                        "city": data.get("city"),
                        "zip": data.get("zip"),
                        "lat": data.get("lat"),
                        "lon": data.get("lon"),
                        "timezone": data.get("timezone"),
                        "isp": data.get("isp"),
                        "org": data.get("org"),
                        "as_number": data.get("as")
                    }
    except Exception:
        pass

    return {
        "ip": target,
        "country": "Informasi tidak tersedia / Offline",
        "isp": "N/A",
        "city": "N/A"
    }

def analyze_target_intel(target_query: str) -> Dict[str, Any]:
    target = target_query.strip()
    if not target:
        return {"valid": False, "error": "Target domain/IP/entitas tidak boleh kosong."}

    # DNS Lookup
    dns_records = resolve_dns_records(target)
    
    # IP Geolocation
    geo_info = get_ip_geolocation(target)

    # Analisis Korelasi Kebocoran Data Indonesia
    # Evaluasi seberapa rentan identitas target jika pernah terdaftar di layanan lokal
    breach_analysis = []
    for item in INDONESIA_HISTORICAL_BREACHES:
        breach_analysis.append({
            "insiden": item["nama_insiden"],
            "tahun": item["tahun"],
            "skala": item["estimasi_korban"],
            "vektor_bocor": ", ".join(item["data_bocor"]),
            "keparahan": item["tingkat_keparahan"],
            "relevansi_identitas": "Bisa mengungkap NIK & Domisili" if "NIK" in item["data_bocor"] else "Bisa mengungkap Kredensial & HP",
            "ringkasan": item["deskripsi"]
        })

    return {
        "valid": True,
        "query": target,
        "dns": dns_records,
        "geolocation": geo_info,
        "breach_intelligence": breach_analysis,
        "summary": {
            "total_insiden_tercatat": len(INDONESIA_HISTORICAL_BREACHES),
            "vektor_ancaman_tertinggi": "NIK, Nomor KK, No HP, dan Alamat Rumah Fisik",
            "rekomendasi_penyelidikan": "Lakukan cross-check NIK dengan modul NIK Decoder dan Dorking site:go.id."
        }
    }

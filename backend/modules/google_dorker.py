"""
Modul Indo & Asia Google Dorking Generator
Menyediakan pustaka Google Dorks terkurasi untuk investigasi entitas di Indonesia & Asia
(Pemerintah go.id, Kampus ac.id, Identitas KTP/KK, Direktori Terbuka, dan Kredensial).
"""

import urllib.parse
from typing import Dict, Any, List

DORK_TEMPLATES = [
    # Kategori 1: Pemerintah & Instansi RI (go.id)
    {
        "category": "Instansi Pemerintah RI (go.id)",
        "title": "Dokumen PDF Resmi ASN / Surat Keputusan (SK)",
        "dork": 'site:go.id filetype:pdf "{target}"',
        "description": "Menemukan dokumen PDF resmi pemerintah (SK Pengangkatan, Surat Tugas, Laporan) yang memuat nama target."
    },
    {
        "category": "Instansi Pemerintah RI (go.id)",
        "title": "Data Pengadaan LPSE / LKPP & Tender",
        "dork": 'site:lpse.*.go.id OR site:inaproc.id "{target}"',
        "description": "Mengecek keterlibatan target dalam proyek tender pengadaan barang dan jasa pemerintah."
    },
    {
        "category": "Instansi Pemerintah RI (go.id)",
        "title": "Pengumuman CPNS / PPPK / Ujian Kedinasan",
        "dork": 'site:go.id "CPNS" OR "PPPK" "{target}"',
        "description": "Mencari riwayat seleksi kepegawaian aparatur sipil negara."
    },

    # Kategori 2: Akademik & Kampus RI (ac.id)
    {
        "category": "Akademik & Perguruan Tinggi (ac.id)",
        "title": "Ijazah, Skripsi, & Transkrip Akademik",
        "dork": 'site:ac.id filetype:pdf "skripsi" OR "thesis" OR "ijazah" "{target}"',
        "description": "Menemukan karya ilmiah, laporan penelitian, atau publikasi wisuda kampus."
    },
    {
        "category": "Akademik & Perguruan Tinggi (ac.id)",
        "title": "Biodata Mahasiswa & Dosen (PDDikti)",
        "dork": 'site:ac.id "NIM" OR "NIP" OR "KRS" "{target}"',
        "description": "Mengekstrak nomor induk mahasiswa (NIM) atau riwayat studi di perguruan tinggi."
    },

    # Kategori 3: Dokumen KTP, KK, & NIK Terbuka
    {
        "category": "Kependudukan & NIK KTP",
        "title": "Dokumen Terbuka Berisi NIK & Tempat Lahir",
        "dork": 'filetype:pdf OR filetype:xls "NIK" "Tempat Lahir" "{target}"',
        "description": "Menemukan berkas lampiran formulir atau bansos yang memuat NIK dan data pribadi."
    },
    {
        "category": "Kependudukan & NIK KTP",
        "title": "Daftar Pemilih / DPT / Sensus Wilayah",
        "dork": '"Daftar Pemilih" OR "DPT" "{target}" filetype:pdf',
        "description": "Mencari publikasi nomor TPS dan kelurahan domisili target."
    },

    # Kategori 4: Kredensial & Berkas Sensitif
    {
        "category": "Kredensial & Kebocoran",
        "title": "Pastebin & Public Text Dumps",
        "dork": 'site:pastebin.com OR site:controlc.com OR site:rentry.co "{target}"',
        "description": "Mencari kebocoran teks, log sandi, atau catatan publik yang menyebut target."
    },
    {
        "category": "Kredensial & Kebocoran",
        "title": "File Backup & Database SQL Terpapar",
        "dork": 'filetype:sql OR filetype:env OR filetype:log "{target}"',
        "description": "Mendeteksi apakah nama atau email target tersimpan dalam berkas konfigurasi publik."
    },

    # Kategori 5: Media Sosial & Forum Lokal
    {
        "category": "Forum & Media Lokal",
        "title": "Jejak Forum Kaskus & Kompasiana",
        "dork": 'site:kaskus.co.id OR site:kompasiana.com "{target}"',
        "description": "Mencari postingan lama di komunitas Kaskus atau tulisan opini warga."
    },
    {
        "category": "Forum & Media Lokal",
        "title": "Profil LinkedIn & Karir Indonesia",
        "dork": 'site:id.linkedin.com/in/ "{target}"',
        "description": "Menemukan profil karir profesional target di LinkedIn regional Indonesia."
    },

    # Kategori 6: Direktori Terbuka (Open Directory)
    {
        "category": "Direktori Terbuka",
        "title": "Open Directory Berkas Foto & Arsip",
        "dork": 'intitle:"index of /" (jpg|png|pdf|zip) "{target}"',
        "description": "Mencari server web yang membiarkan direktori file terbuka tanpa autentikasi."
    }
]

def generate_dorks(target_input: str) -> Dict[str, Any]:
    target = target_input.strip()
    if not target:
        return {"valid": False, "error": "Target pencarian (nama/email/NIK) tidak boleh kosong."}

    dork_results: List[Dict[str, Any]] = []
    
    for item in DORK_TEMPLATES:
        rendered_dork = item["dork"].replace("{target}", target)
        google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(rendered_dork)}"
        
        dork_results.append({
            "category": item["category"],
            "title": item["title"],
            "dork": rendered_dork,
            "description": item["description"],
            "google_url": google_search_url
        })

    return {
        "valid": True,
        "target": target,
        "total_dorks": len(dork_results),
        "dorks": dork_results
    }

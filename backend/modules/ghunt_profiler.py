"""
Modul GHunt & Google Account Profiler
Menganalisis akun Google / Gmail untuk mengekstrak jejak Google Maps Reviews,
Google Photos Archive, Google Calendar Availability, dan Google Drive Public Shares.
"""

import urllib.parse
from typing import Dict, Any

def analyze_google_account(email_or_id: str) -> Dict[str, Any]:
    target = email_or_id.strip().lower()
    if not target:
        return {"valid": False, "error": "Alamat Gmail atau Google ID tidak boleh kosong."}

    username = target.split("@")[0] if "@" in target else target
    is_gmail = target.endswith("@gmail.com") or "@" not in target

    # Google Maps Review Finder (Salah satu metode OSINT paling ampuh di Indonesia)
    maps_dork = f'site:google.com/maps/contrib/ "{username}"'
    maps_search_url = f"https://www.google.com/search?q={urllib.parse.quote(maps_dork)}"

    # Google Drive Shared Documents Dork
    drive_dork = f'site:drive.google.com/file/ OR site:docs.google.com "{target}"'
    drive_search_url = f"https://www.google.com/search?q={urllib.parse.quote(drive_dork)}"

    # Google Photos Archive
    photos_url = f"https://get.google.com/albumarchive/{username}"

    # Google Hangouts / Chat Status Query
    hangouts_dork = f'site:chat.google.com "{target}"'

    return {
        "valid": True,
        "input": target,
        "username": username,
        "is_gmail": is_gmail,
        "account_type": "Google Personal (@gmail.com)" if is_gmail else "Google Workspace / Enterprise Domain",
        "footprint_vectors": [
            {
                "vector": "Google Maps Contributions & Reviews",
                "importance": "Kritis (Geolokasi)",
                "keterangan": "Sering memuat ulasan restoran, kafe, pom bensin, dan toko yang diulas target di kota domisili.",
                "dork": maps_dork,
                "action_url": maps_search_url
            },
            {
                "vector": "Google Drive / Docs Shared Files",
                "importance": "Tinggi (Dokumen Rahasia)",
                "keterangan": "Mencari berkas Google Docs, Sheets, atau PDF yang dibagikan secara publik oleh target.",
                "dork": drive_dork,
                "action_url": drive_search_url
            },
            {
                "vector": "Google Album Archive",
                "importance": "Sedang (Foto Profil)",
                "keterangan": "Melihat riwayat album foto publik Picasa/Google Photos lama.",
                "dork": f"Direct Profile: {photos_url}",
                "action_url": photos_url
            },
            {
                "vector": "Google Calendar Public Availability",
                "importance": "Sedang (Jadwal Kerja)",
                "keterangan": "Mengecek apakah kalender Google target diatur ke publik (Free/Busy schedule).",
                "dork": f"https://calendar.google.com/calendar/u/0/embed?src={urllib.parse.quote(target)}",
                "action_url": f"https://calendar.google.com/calendar/u/0/embed?src={urllib.parse.quote(target)}"
            }
        ]
    }

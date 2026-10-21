#!/usr/bin/env python3
"""
MY-OSINT Retro Windows 95/98 Server
Server HTTP API mandiri (Zero-Dependency) untuk melayani frontend retro Windows 90s
dan mengeksekusi 7 modul OSINT Asia & Indonesia.
"""

import sys
import os
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Tambahkan direktori root backend ke sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from modules.nik_parser import parse_nik
from modules.phone_tracer import analyze_phone
from modules.holehe_checker import check_email_footprint
from modules.username_tracker import scan_username
from modules.google_dorker import generate_dorks
from modules.ghunt_profiler import analyze_google_account
from modules.ghost_intel import analyze_target_intel
from modules.amass_scanner import enumerate_subdomains
from modules.gov_apis import query_gov_registries
from database import (
    log_security_event, get_security_logs, clear_security_logs,
    save_osint_result, get_osint_result
)

PUBLIC_DIR = os.path.join(BASE_DIR, "public")

class RetroOSINTHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Format log ala retro command prompt
        sys.stderr.write(f"[OSINT-95] {self.address_string()} - {format%args}\n")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_json(self, status_code: int, data: dict):
        response_body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(response_body)

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Real-time Streaming Endpoint (Maltego Graph + SpiderFoot Live Stream)
        if path == "/api/stream":
            query = qs.get("query", [""])[0].strip()
            location = qs.get("location", [""])[0].strip()
            address = qs.get("address", [""])[0].strip()
            email = qs.get("email", [""])[0].strip()
            phone = qs.get("phone", [""])[0].strip()

            if not query and email:
                query = email
            elif not query and phone:
                query = phone
            elif not query and location:
                query = location

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_cors_headers()
            self.end_headers()

            def send_event(event_name, data):
                msg = f"event: {event_name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                try:
                    self.wfile.write(msg.encode("utf-8"))
                    self.wfile.flush()
                except Exception:
                    pass

            if not query:
                send_event("error", {"message": "Target query tidak boleh kosong. Masukkan minimal salah satu dari: Nama, Lokasi, Alamat, Email, atau No HP."})
                return

            import concurrent.futures
            from modules.username_tracker import TARGET_PLATFORMS, check_single_site

            # 1. Inisialisasi Root Target Node (Maltego Style)
            send_event("log", {"level": "INIT", "source": "SpiderFoot", "message": f"Memulai audit intelijen real-time untuk target: '{query}'"})
            send_event("graph_node", {
                "id": "root",
                "label": query,
                "type": "target",
                "icon": "🎯",
                "color": "#00007c",
                "details": f"Target Penyelidikan Utama: {query}"
            })

            digits_only = "".join([c for c in query if c.isdigit()])
            has_spaces = " " in query.strip()
            if has_spaces:
                # Untuk nama lengkap seperti 'ilham pradani', gabungkan menjadi 'ilhampradani'
                import re
                clean_username = re.sub(r'[^a-zA-Z0-9._-]', '', query.replace(" ", "").lower())
                underscore_username = re.sub(r'[^a-zA-Z0-9._-]', '', query.replace(" ", "_").lower())
                send_event("log", {"level": "INFO", "source": "SpiderFoot", "message": f"Target nama lengkap terdeteksi: '{query}'. Mengekstrak permutasi alias: '@{clean_username}' & '@{underscore_username}'"})
            else:
                clean_username = query.replace("@", "").strip()
                underscore_username = clean_username

            # 2. Real-time Phone & Carrier Tracer (Truecaller / Telco HLR)
            if query.startswith("08") or query.startswith("+") or (len(digits_only) >= 9 and len(digits_only) <= 14):
                send_event("log", {"level": "QUERY", "source": "Truecaller/HLR", "message": f"Mengecek prefix telekomunikasi & operator seluler Asia..."})
                phone_res = analyze_phone(query)
                if phone_res.get("valid"):
                    telco = phone_res["telekomunikasi"]
                    lok = phone_res["lokasi"]
                    send_event("log", {"level": "SUCCESS", "source": "Truecaller/HLR", "message": f"Operator Terdeteksi: {telco['operator']} ({telco['brand']}) | Wilayah: {lok['hlr_regional']} | {lok['bendera']} {lok['negara']}"})
                    
                    phone_node_id = "node_phone"
                    send_event("graph_node", {"id": phone_node_id, "label": f"{telco['operator']}", "type": "phone", "icon": "📞", "color": "#800080", "details": f"{phone_res['format']['e164']} | {telco['operator']} ({telco['brand']}) | {lok['hlr_regional']}"})
                    send_event("graph_edge", {"from": "root", "to": phone_node_id, "label": "mobile_carrier"})

                    wa_node_id = "node_whatsapp"
                    send_event("graph_node", {"id": wa_node_id, "label": "WhatsApp Active Link", "type": "chat", "icon": "💬", "color": "#25d366", "url": phone_res["osint_links"]["whatsapp_chat"]})
                    send_event("graph_edge", {"from": phone_node_id, "to": wa_node_id, "label": "messaging_channel"})

            # 4. Real-time Email & Epieos Footprint
            if "@" in query:
                send_event("log", {"level": "QUERY", "source": "Epieos/Holehe", "message": f"Memeriksa server MX, email temporer, dan Gravatar avatar..."})
                email_res = check_email_footprint(query)
                if email_res.get("valid"):
                    gravatar = email_res.get("gravatar", {})
                    domain_info = email_res.get("analisis_domain", {})
                    
                    email_node_id = "node_email"
                    send_event("graph_node", {"id": email_node_id, "label": f"{domain_info['nama_provider']}", "type": "email", "icon": "✉️", "color": "#0055aa", "details": f"Provider: {domain_info['nama_provider']} | MX: {domain_info['mx_status']}"})
                    send_event("graph_edge", {"from": "root", "to": email_node_id, "label": "primary_email"})

                    if gravatar.get("found"):
                        send_event("log", {"level": "SUCCESS", "source": "Gravatar/Epieos", "message": f"Ditemukan profil Gravatar publik! Nama: {gravatar['profile'].get('display_name')} | Lokasi: {gravatar['profile'].get('current_location')}"})
                        grav_node_id = "node_gravatar"
                        send_event("graph_node", {"id": grav_node_id, "label": f"Profil: {gravatar['profile'].get('display_name') or 'Avatar'}", "type": "profile", "icon": "🖼️", "color": "#b8860b", "details": f"Bio: {gravatar['profile'].get('about')} | Lokasi: {gravatar['profile'].get('current_location')}"})
                        send_event("graph_edge", {"from": email_node_id, "to": grav_node_id, "label": "public_identity"})

            # 5. Real-time Shodan / GhostIntel DNS & IP Geolocation
            send_event("log", {"level": "QUERY", "source": "Shodan/GhostIntel", "message": f"Melakukan kueri DNS-over-HTTPS Cloudflare & Geolocation IP..."})
            ghost_res = analyze_target_intel(query)
            if ghost_res.get("valid"):
                geo = ghost_res.get("geolocation", {})
                if geo.get("country") and geo.get("country") != "Informasi tidak tersedia / Offline":
                    geo_node_id = "node_geo"
                    send_event("log", {"level": "SUCCESS", "source": "Shodan/Geo", "message": f"Geolokasi IP Ditemukan: {geo.get('city')}, {geo.get('country')} | ISP: {geo.get('isp')} | ASN: {geo.get('as_number')}"})
                    send_event("graph_node", {"id": geo_node_id, "label": f"{geo.get('city') or geo.get('country')} ({geo.get('isp')})", "type": "geo", "icon": "🌐", "color": "#b22222", "details": f"IP: {geo.get('ip')} | ISP: {geo.get('isp')} | Kota: {geo.get('city')}, {geo.get('country')} | Lat: {geo.get('lat')}, Lon: {geo.get('lon')}"})
                    send_event("graph_edge", {"from": "root", "to": geo_node_id, "label": "network_infrastructure"})

            # 6. OWASP Amass Subdomain & Infrastructure Scanner (Jika target domain atau host)
            clean_dom = query.split("@")[-1].strip() if "@" in query else query.strip()
            if "." in clean_dom and " " not in clean_dom:
                send_event("log", {"level": "QUERY", "source": "OWASP-Amass", "message": f"Memindai subdomain aktif & exposure internal untuk {clean_dom}..."})
                amass_res = enumerate_subdomains(clean_dom, max_workers=6)
                if amass_res.get("valid") and amass_res.get("subdomains"):
                    send_event("log", {"level": "SUCCESS", "source": "OWASP-Amass", "message": f"Ditemukan {len(amass_res['subdomains'])} subdomain aktif via DoH!"})
                    for sub in amass_res["subdomains"][:8]:
                        sub_node_id = f"sub_{sub['prefix']}"
                        send_event("graph_node", {
                            "id": sub_node_id,
                            "label": sub["subdomain"],
                            "type": "subdomain",
                            "icon": "🖥️",
                            "color": "#7c2d12",
                            "details": f"IPs: {', '.join(sub['ips'])} | CNAMEs: {', '.join(sub['cnames'])}"
                        })
                        send_event("graph_edge", {"from": "root", "to": sub_node_id, "label": "active_subdomain"})

            # 7. Indonesia Gov Public Registries (PDDikti, Putusan MA, PSE, LPSE, OJK, LHKPN, DJKI, AHU)
            send_event("log", {"level": "QUERY", "source": "Registri-RI", "message": f"Menghubungkan secara daring ke basis data resmi Republik Indonesia..."})
            gov_res = query_gov_registries(query, location=location, address=address, email=email, phone=phone)
            if gov_res.get("valid"):
                # Stream candidate profiles (discovering real people from PDDikti)
                candidates = gov_res.get("candidate_profiles", [])
                if candidates:
                    send_event("log", {"level": "SUCCESS", "source": "PDDikti-Live", "message": f"Ditemukan {len(candidates)} kandidat identitas daring dari PDDikti Kemdiktisaintek!"})
                    for c in candidates:
                        send_event("candidate_profile", c)

                # Jika ada input NIK 16 digit yang divalidasi
                if gov_res.get("parsed_nik"):
                    p_nik = gov_res["parsed_nik"]
                    nik_node_id = "node_nik"
                    send_event("log", {"level": "SUCCESS", "source": "NIK-Decoder", "message": f"NIK Terverifikasi: {p_nik.get('kabupaten')}, {p_nik.get('provinsi')} | Umur: {p_nik.get('umur')} Thn"})
                    send_event("graph_node", {
                        "id": nik_node_id,
                        "label": f"NIK: {gov_res.get('masked_nik')}",
                        "type": "nik",
                        "icon": "🪪",
                        "color": "#000080",
                        "status_badge": "NIK KEMENDAGRI",
                        "temuan_ringkas": f"{p_nik.get('kabupaten')}, {p_nik.get('provinsi')} - Lahir: {p_nik.get('tanggal_lahir')} ({p_nik.get('umur')} Thn)",
                        "ekstraksi_data": [
                            {"label": "NIK (Masked)", "nilai": gov_res.get("masked_nik")},
                            {"label": "Kabupaten / Kota", "nilai": p_nik.get("kabupaten")},
                            {"label": "Provinsi", "nilai": p_nik.get("provinsi")},
                            {"label": "Kecamatan", "nilai": p_nik.get("kecamatan")},
                            {"label": "Tanggal Lahir", "nilai": p_nik.get("tanggal_lahir")},
                            {"label": "Jenis Kelamin", "nilai": p_nik.get("jenis_kelamin")}
                        ],
                        "details": f"NIK: {gov_res.get('masked_nik')} | {p_nik.get('kabupaten')}, {p_nik.get('provinsi')}"
                    })
                    send_event("graph_edge", {"from": "root", "to": nik_node_id, "label": "nik_demographic"})

                for reg in gov_res.get("registries", []):
                    reg_node_id = f"gov_{reg['id']}"
                    if reg.get("status_badge") and "TIDAK" not in reg.get("status_badge") and "NIR" not in reg.get("status_badge"):
                        send_event("log", {"level": "HIT", "source": "Registri-RI", "message": f"[+] {reg['nama_layanan']} -> [{reg['status_badge']}] {reg.get('temuan_ringkas', '')}"})
                    send_event("graph_node", {
                        "id": reg_node_id,
                        "label": reg["nama_layanan"],
                        "type": "gov",
                        "icon": reg.get("status_icon", "🏛️"),
                        "color": reg.get("status_color", "#1e3a8a"),
                        "url": reg["search_url"],
                        "instansi": reg["instansi"],
                        "kategori": reg["kategori"],
                        "status_badge": reg.get("status_badge", "TERDATA"),
                        "temuan_ringkas": reg.get("temuan_ringkas", "-"),
                        "ekstraksi_data": reg.get("ekstraksi_data", []),
                        "parameter_terindex": reg["parameter_terindex"],
                        "details": f"[{reg.get('status_badge', '')}] {reg.get('temuan_ringkas', '-')}"
                    })
                    send_event("graph_edge", {"from": "root", "to": reg_node_id, "label": "gov_registry"})
                    send_event("gov_registry_item", reg)


            # 8. Real-time Sherlock Scanning: Stream each platform as it responds!
            send_event("log", {"level": "SCAN", "source": "Sherlock-Live", "message": f"Menjalankan pemindaian paralel di {len(TARGET_PLATFORMS)} platform media sosial & forum..."})
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_site = {
                    executor.submit(check_single_site, site, clean_username): site
                    for site in TARGET_PLATFORMS
                }
                for future in concurrent.futures.as_completed(future_to_site):
                    res = future.result()
                    send_event("stream_item", res)
                    
                    if res["found"]:
                        send_event("log", {"level": "HIT", "source": "Sherlock-Live", "message": f"[+] DITEMUKAN PROFIL AKTIF: {res['platform']} ({res['category']}) -> {res['profile_url']}"})
                        soc_node_id = f"soc_{res['platform'].replace(' ', '_')}"
                        send_event("graph_node", {
                            "id": soc_node_id,
                            "label": f"{res['platform']}",
                            "type": "social",
                            "icon": "👤",
                            "color": "#008080",
                            "url": res["profile_url"],
                            "details": f"Platform: {res['platform']} | Kategori: {res['category']} | Wilayah: {res['region']}"
                        })
                        send_event("graph_edge", {"from": "root", "to": soc_node_id, "label": "social_account"})
            # Jika target nama lengkap memiliki spasi, sertakan direktori pencarian nama lengkap
            if has_spaces:
                import urllib.parse
                encoded = urllib.parse.quote(query.strip())
                name_platforms = [
                    {"name": "LinkedIn People Search", "url": f"https://www.linkedin.com/search/results/all/?keywords={encoded}", "cat": "Karir"},
                    {"name": "PDDikti Kemendikbud RI", "url": f"https://pddikti.kemdikbud.go.id/data_mahasiswa?keyword={encoded}", "cat": "Akademik"},
                    {"name": "Facebook Directory", "url": f"https://www.facebook.com/search/people/?q={encoded}", "cat": "Sosial"},
                    {"name": "Google Dork ASN go.id", "url": f"https://www.google.com/search?q={urllib.parse.quote('site:go.id \"' + query + '\"')}", "cat": "Pemerintah"}
                ]
                for p in name_platforms:
                    node_id = f"name_{p['name'].replace(' ', '_')}"
                    send_event("stream_item", {
                        "platform": p["name"],
                        "category": p["cat"],
                        "region": "Indonesia/Global",
                        "found": True,
                        "status": "Pencarian Nama Lengkap",
                        "profile_url": p["url"],
                        "http_code": 200,
                        "duration_ms": 10
                    })
                    send_event("graph_node", {
                        "id": node_id,
                        "label": p["name"],
                        "type": "directory",
                        "icon": "📋",
                        "color": "#1e3a8a",
                        "url": p["url"],
                        "details": f"Pencarian Nama Lengkap: '{query}'"
                    })
                    send_event("graph_edge", {"from": "root", "to": node_id, "label": "full_name_query"})

            # 7. Selesai & Simpan ke Basis Data SQL Lokal
            positive_findings = []
            if gov_res.get("valid"):
                for r in gov_res.get("registries", []):
                    if r.get("status_badge") and "404" not in r.get("status_badge") and "TIDAK" not in r.get("status_badge") and "NIR" not in r.get("status_badge"):
                        positive_findings.append({
                            "source": r["nama_layanan"],
                            "temuan": r.get("temuan_ringkas", ""),
                            "data": r.get("ekstraksi_data", []),
                            "url": r.get("search_url")
                        })
                
                # Catat ke SQLite
                save_osint_result(
                    query=query,
                    name=location or query.title(),
                    phone=phone,
                    location=location or address,
                    candidates=candidates,
                    registries=gov_res.get("registries", []),
                    positive_findings=positive_findings
                )
                log_security_event("AUDIT", "Basis Data SQL", f"Hasil intelijen untuk '{query}' dicatat ke SQLite lokal", target=query)

            send_event("log", {"level": "COMPLETE", "source": "SpiderFoot", "message": "Penyelidikan intelijen real-time selesai. Data tersimpan di SQLite lokal."})
            send_event("done", {"status": "SUCCESS", "message": "Penyelidikan selesai."})
            return

        # Logs & Security Events Endpoint (SQLite)
        if path == "/api/logs":
            lvl = qs.get("level", ["ALL"])[0]
            try:
                lim = int(qs.get("limit", [200])[0])
            except Exception:
                lim = 200
            logs = get_security_logs(level=lvl, limit=lim)
            self.send_json(200, {
                "valid": True,
                "total_stored": len(logs),
                "logs": logs
            })
            return

        # Cached OSINT Record Endpoint (SQLite)
        if path == "/api/cached":
            target_q = qs.get("query", [""])[0]
            cached_data = get_osint_result(target_q)
            if cached_data:
                self.send_json(200, {"valid": True, "found": True, "record": cached_data})
            else:
                self.send_json(200, {"valid": True, "found": False})
            return

        # Status Endpoint
        if path == "/api/status":
            self.send_json(200, {
                "status": "ONLINE",
                "os_emulator": "Microsoft Windows 95/98 Classic",
                "database": "SQLite3 (Local Persistent Archive)",
                "active_engines": [
                    "PDDikti Kemdiktisaintek Live Query",
                    "Indonesia Gov Public Registries Prober",
                    "Sherlock & Maigret Social Tracker",
                    "NIK & KTP Regional Demographics Decoder",
                    "Phone & Carrier Lookup (Asia Telco)",
                    "Email Audit & Registration Checker (Holehe)",
                    "Security & WAF Event Logger"
                ],
                "engine_count": 7
            })
            return

        # Serve Static Files
        if path == "/" or path == "":
            filepath = os.path.join(PUBLIC_DIR, "index.html")
        else:
            clean_path = path.lstrip("/")
            filepath = os.path.join(PUBLIC_DIR, clean_path)

        if os.path.isfile(filepath):
            mime_type, _ = mimetypes.guess_type(filepath)
            if not mime_type:
                mime_type = "application/octet-stream"
            
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", f"{mime_type}; charset=utf-8" if "text" in mime_type or "javascript" in mime_type or "css" in mime_type else mime_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_cors_headers()
                self.end_headers()
                if not head_only:
                    self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"500 Internal Error: {str(e)}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found in C:\\WINDOWS\\SYSTEM32\\OSINT\\")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Baca body JSON
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self.send_json(400, {"valid": False, "error": "Request body harus berupa format JSON valid."})
            return

        # Router Modul API
        try:
            if path == "/api/logs/clear":
                clear_security_logs()
                self.send_json(200, {"valid": True, "message": "Log keamanan berhasil dibersihkan."})
                return

            elif path == "/api/nik":
                nik_input = body.get("nik", "")
                result = parse_nik(nik_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/phone":
                phone_input = body.get("phone", "")
                result = analyze_phone(phone_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/email":
                email_input = body.get("email", "")
                result = check_email_footprint(email_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/username":
                username_input = body.get("username", "")
                result = scan_username(username_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/dorks":
                target_input = body.get("target", "")
                result = generate_dorks(target_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/ghunt":
                account_input = body.get("target", "")
                result = analyze_google_account(account_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/ghostintel":
                target_input = body.get("target", "")
                result = analyze_target_intel(target_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/amass":
                domain_input = body.get("domain", "")
                result = enumerate_subdomains(domain_input)
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/gov":
                query_input = body.get("query", "")
                loc_input = body.get("location", "")
                addr_input = body.get("address", "")
                em_input = body.get("email", "")
                ph_input = body.get("phone", "")
                result = query_gov_registries(
                    query_input,
                    location=loc_input,
                    address=addr_input,
                    email=em_input,
                    phone=ph_input
                )
                self.send_json(200 if result.get("valid") else 400, result)

            elif path == "/api/unified":
                # Eksekusi penyelidikan terpadu berdasarkan format input
                query = str(body.get("query", "")).strip()
                unified_results = {"query": query, "modules_triggered": []}

                digits_only = "".join([c for c in query if c.isdigit()])
                
                # Jika 16 digit angka -> Jalankan NIK
                if len(digits_only) == 16:
                    unified_results["nik"] = parse_nik(digits_only)
                    unified_results["modules_triggered"].append("NIK Decoder")

                # Jika berawalan nomor telepon (08xx atau +62)
                if query.startswith("08") or query.startswith("+") or (len(digits_only) >= 9 and len(digits_only) <= 14):
                    unified_results["phone"] = analyze_phone(query)
                    unified_results["modules_triggered"].append("Phone Tracer")

                # Jika email (@)
                if "@" in query:
                    unified_results["email"] = check_email_footprint(query)
                    unified_results["ghunt"] = analyze_google_account(query)
                    unified_results["modules_triggered"].extend(["Holehe Email", "GHunt Profiler"])

                # Selalu jalankan Dorker & Username search
                unified_results["dorks"] = generate_dorks(query)
                unified_results["username"] = scan_username(query)
                unified_results["ghostintel"] = analyze_target_intel(query)
                unified_results["modules_triggered"].extend(["Google Dorker", "Username Scanner", "GhostIntel"])

                self.send_json(200, unified_results)

            else:
                self.send_json(404, {"error": f"Endpoint API '{path}' tidak ditemukan."})

        except Exception as e:
            self.send_json(500, {"error": f"Kesalahan internal server: {str(e)}"})

def run_server(port=8080):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, RetroOSINTHandler)
    print("=" * 65)
    print("  [★] MY-OSINT RETRO WINDOWS 95/98 ENGINE (7 ASIA/INDO MODULES)")
    print("=" * 65)
    print(f"  > Port HTTP   : http://localhost:{port}")
    print(f"  > Public Dir  : {PUBLIC_DIR}")
    print(f"  > Engines (7) : NIK, Phone, Holehe, Username, Dorker, GHunt, GhostIntel")
    print("=" * 65)
    print("Tekan CTRL+C untuk menghentikan server.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server dimatikan.")
        httpd.server_close()

if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)

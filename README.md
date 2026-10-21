# MY-OSINT 95 (Asian & Indonesian Intelligence Suite)

Aplikasi OSINT Identitas Terpadu khusus **Asia & Indonesia** dengan antarmuka klasik **Windows 95/98 (Retro 90s OS)** yang dibangun mengacu pada pedoman desain [`ui.md`](file:///home/ilhampradani/Unduhan/MY-OSINT/ui.md).

---

## 💻 7 Mesin Intelijen yang Disertakan

| Modul | Nama Mesin | Fokus & Kemampuan |
| :---: | :--- | :--- |
| **1** | **NIK & KTP Demographics Decoder** | Mengurai 16 digit NIK secara offline: Provinsi (38 provinsi RI), Kabupaten/Kota, Kecamatan, Tanggal Lahir, Usia, Gender, Zodiak & Shio. |
| **2** | **Phone & Asia Telco Tracer** | Melacak operator seluler Indonesia (Telkomsel, Indosat, XL, Smartfren, Tri), estimasi HLR regional, kode negara Asia, format E.164, deep link WhatsApp & Telegram. |
| **3** | **Email Audit & Holehe Footprint** | Validasi RFC 5322, DNS MX resolver, deteksi email temporer, ekstraksi profil Gravatar, dan analisis registrasi akun. |
| **4** | **Social Username Tracker** | Pelacakan simultan username di 35+ platform (Kaskus, Telegram, Tokopedia, TikTok, Carousell, GitHub, dll). |
| **5** | **Indo & Asia Google Dorking Engine** | Otomasi query Google Dork bertarget instansi pemerintah (`site:go.id`), perguruan tinggi (`site:ac.id`), berkas PDF SK ASN, ijazah, dan kebocoran KTP. |
| **6** | **GHunt & Google Account Profiler** | Pelacakan riwayat kontribusi & ulasan Google Maps di Indonesia, Google Drive file sharing dork, dan profil foto Google. |
| **7** | **GhostIntel & Indonesian Breach Radar** | Resolusi DNS over HTTPS, Geolocation IP, dan basis data korelasi kebocoran data nasional (Tokopedia, BPJS Kesehatan, KPU, PLN, Indihome, Ditjen Imigrasi). |

---

## 🎨 Karakteristik Antarmuka (Sesuai `ui.md`)

- **Palet Warna**: Silver `#cccccc`, Navy Blue Titlebar `#00007c`, Desktop Teal `#008080`.
- **Efek Bevel 3D**: 2px Outset (timbul) dan 2px Inset (cekung/sunken).
- **Border Radius**: Strictly `0px` (persegi klasik retro).
- **Tipografi**: `MS Sans Serif`, `Tahoma`, `Segoe UI` (bobot 400/500, tanpa teks tebal kabur).
- **Sidebar Kiri**: Navigasi explorer ala Windows 95 untuk beralih antar 7 halaman mesin.
- **Taskbar Bawah**: Tombol Start timbul, Start Menu popup, tab jendela aktif, status bar, dan jam digital live.
- **Audio Retro**: Sintesis efek suara retro PC speaker (klik, boot, alert) menggunakan Web Audio API murni.

---

## 🚀 Cara Menjalankan

### Cara 1 (Menggunakan Script Shell)
```bash
./start.sh
```

### Cara 2 (Python Langsung - Zero Dependency)
```bash
python3 backend/server.py 8080
```

### Cara 3 (NPM / Node.js)
```bash
npm start
```

Buka browser Anda di: **`http://localhost:8080`**

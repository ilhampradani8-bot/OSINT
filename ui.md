# ERP-MIJ UI Architecture & Design System Guide (Windows 90s Abu)

Dokumen ini merupakan panduan spesifikasi dan standarisasi antarmuka (Design System) untuk ERP-MIJ dengan konsep **Retro Windows 90s Abu (Classic OS Style)**. Seluruh komponen, modal, tabel, tombol, dan warna harus mengacu pada panduan ini untuk menjaga konsistensi tampilan.

---

## 1. Filosofi & Karakteristik Desain

| Dimensi | Spesifikasi | Keterangan |
| :--- | :--- | :--- |
| **Gaya Utama** | Classic Windows 95/98 Grey (`#cccccc`) | Bingkai jendela, modal, dialog, toolbar, taskbar |
| **Desktop Background** | Teal Klasik (`#008080`) | Latar belakang desktop luar |
| **Title Bar Jendela** | Navy Blue (`#00007c`) | Warna biru tua khas title bar Windows aktif |
| **Typography** | `MS Sans Serif`, `Tahoma`, `Segoe UI`, `sans-serif` | **TIDAK BOLD tebal**, rapi, tajam, dan mudah dibaca |
| **Efek 3D Border** | 2px Outset (Timbul) & 2px Inset (Cekung) | Bevel klasik retro menggunakan kombinasi `#ffffff`, `#808080`, `#000000` |
| **Border Radius** | `0px` (Strictly Rectangular) | Tidak ada sudut melengkung/pill modern |

---

## 2. Palet Warna Resmi (Color Palette)

```css
:root {
  /* Dasar Windows 90s */
  --color-silver: #cccccc;        /* Abu-abu panel / frame / button utama */
  --color-platinum: #ffffff;      /* Highlight putih untuk bevel atas/kiri */
  --color-gray: #808080;          /* Shadow abu-abu bevel bawah/kanan */
  --color-black: #000000;         /* Outline terluar bevel dan teks utama */
  
  /* Latar Belakang & Titlebar */
  --color-navy-blue: #00007c;     /* Header jendela aktif / baris terpilih */
  --color-desktop-teal: #008080;  /* Wallpaper desktop retro */
  
  /* Area Konten */
  --color-white: #ffffff;         /* Background textarea, input field, spreadsheet */
  
  /* Status Badges */
  --badge-review: #bae6fd;        /* Biru muda Windows */
  --badge-proses: #fef08a;        /* Kuning Windows */
  --badge-selesai: #bbf7d0;       /* Hijau Windows */
}
```

---

## 3. Komponen Utama (Components Specification)

### A. Window / Modal / Dialog Card
Semua modal dan container dialog wajib berbentuk jendela klasik dengan titlebar biru tua:
```html
<div class="modal-card">
  <!-- Titlebar -->
  <div class="modal-header">
    <h2>Update Details</h2>
    <button class="close-btn" type="button">×</button>
  </div>
  
  <!-- Isi Jendela -->
  <div class="modal-body">
    <!-- Konten form / tabel -->
  </div>
</div>
```
```css
.modal-card {
  background-color: #cccccc !important;
  border: 2px outset #ffffff !important;
  border-right-color: #000000 !important;
  border-bottom-color: #000000 !important;
  box-shadow: 2px 2px 0px 0px #000000 !important;
  border-radius: 0px !important;
}

.modal-header {
  background-color: #00007c !important;
  color: #ffffff !important;
  height: 26px;
  padding: 2px 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 12px;
  font-weight: 600;
  color: #ffffff !important;
  margin: 0;
}
```

---

### B. Tombol Retro Abu (`.btn`, `.os-btn`)
Tombol menggunakan abu-abu `#cccccc` dengan bevel timbul 2px. **Teks tidak boleh dibold berlebihan**:
```css
button, .btn {
  background: #cccccc !important;
  color: #000000 !important;
  font-family: 'MS Sans Serif', Tahoma, 'Segoe UI', sans-serif !important;
  font-size: 12px !important;
  font-weight: 500 !important; /* Jangan bold tebal */
  padding: 4px 14px !important;
  border-radius: 0px !important;
  border: 2px outset #ffffff !important;
  border-right-color: #000000 !important;
  border-bottom-color: #000000 !important;
  cursor: pointer !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
}

/* Hover: Sedikit lebih terang */
button:hover, .btn:hover {
  background: #e0e0e0 !important;
}

/* Active (Ditekan): Efek cekung ke dalam (Inset) */
button:active, .btn:active {
  border: 2px inset #000000 !important;
  border-right-color: #ffffff !important;
  border-bottom-color: #ffffff !important;
  transform: translate(1px, 1px) !important;
}
```

---

### C. Input, Textarea & Form Controls
Semua kolom isian harus berupa wadah putih cekung ke dalam (sunken inset) agar tampak seperti spreadsheet/form retro:
```css
input[type="text"],
input[type="password"],
input[type="date"],
input[type="time"],
select,
textarea,
.form-control {
  background-color: #ffffff !important;
  color: #000000 !important;
  border: 2px inset #000000 !important;
  border-right-color: #ffffff !important;
  border-bottom-color: #ffffff !important;
  border-radius: 0px !important;
  padding: 6px 8px !important;
  font-size: 12px !important;
  font-weight: 400 !important; /* Regular, tidak tebal */
  outline: none;
}

/* Focus: Titik-titik retro */
input:focus, select:focus, textarea:focus {
  outline: 1px dotted #000000 !important;
}
```

---

### D. Tabel Data Spreadsheet (Explorer / Details View)
Tabel menampilkan data dengan header tombol abu-abu timbul dan seleksi baris biru tua:
```css
.excel-table-container {
  background: #ffffff !important;
  border: 2px inset #000000 !important;
  border-right-color: #ffffff !important;
  border-bottom-color: #ffffff !important;
  border-radius: 0px !important;
}

.excel-table {
  width: 100% !important;
  border-collapse: collapse !important;
  font-size: 12px !important;
}

/* Header kolom seperti tombol 3D */
.excel-table th {
  background: #cccccc !important;
  color: #000000 !important;
  border: 2px outset #ffffff !important;
  border-right-color: #000000 !important;
  border-bottom-color: #000000 !important;
  font-size: 11.5px !important;
  font-weight: 600 !important;
  padding: 5px 10px !important;
  text-align: left;
}

/* Sel data */
.excel-table td {
  border: 1px solid #e0e0e0 !important;
  background-color: #ffffff !important;
  color: #000000 !important;
  padding: 5px 10px !important;
  font-weight: 400 !important;
}

/* Hover: Warna seleksi biru tua Windows */
.excel-table tr:hover td {
  background-color: #00007c !important;
  color: #ffffff !important;
}
```

---

### E. Taskbar Bawah (Windows 95 Bottom Bar)
Terletak menempel di bagian bawah layar:
- Tombol `[ ⊞ Start ]` di sebelah kiri dengan border timbul.
- Segment status server / SQLite di tengah dengan border cekung.
- Jam digital di sebelah kanan dengan border cekung.

---

## 4. Aturan Wajib untuk Pengembang
1. **Dilarang memakai border-radius lengkung** (`border-radius: 6px/8px/20px/9999px` dilarang, wajib `0px`).
2. **Dilarang memakai warna gradasi neon modern** (misal: biru ungu modern `#2563eb` atau `#6366f1`). Selalu gunakan warna dasar abu `#cccccc` dan biru tua `#00007c`.
3. **Ketebalan Teks (Font Weight)**:
   - Teks biasa (`p`, `span`, `input`, `td`, label): Wajib regular (`font-weight: 400` atau `500`).
   - Jangan gunakan `font-weight: bold` atau `700` secara menyeluruh agar tulisan tidak buram/tebal menumpuk.
4. **Link Gambar Update**:
   - Selalu dukung input link foto publik (ImgBB, Cloudinary, link drive) agar tidak mengalami kendala autentikasi Google Drive di mode klien.

/**
 * MY-OSINT 95 Frontend Application Controller
 * Menghubungkan antarmuka retro Windows 90s dengan 7 engine intelijen backend.
 */

const app = {
  activePage: "page-dashboard",
  soundEnabled: true,
  audioCtx: null,
  investigationHistory: [],

  // Metadata Halaman
  pageMeta: {
    "page-dashboard": { title: "Pusat Kendali - Penyelidikan Identitas Terpadu", icon: "🛡️" },
    "page-nik": { title: "Modul 1: NIK & KTP Demographics Decoder (Indonesia)", icon: "🪪" },
    "page-phone": { title: "Modul 2: Phone & Carrier Lookup (Asia Telco)", icon: "📞" },
    "page-email": { title: "Modul 3: Email Audit & Registration Checker (Holehe)", icon: "✉️" },
    "page-username": { title: "Modul 4: Social Username Tracker (Maigret/Sherlock)", icon: "👤" },
    "page-dork": { title: "Modul 5: Indo & Asia Google Dorking Generator", icon: "🔎" },
    "page-ghunt": { title: "Modul 6: GHunt & Google Account Profiler", icon: "🌐" },
    "page-ghostintel": { title: "Modul 7: GhostIntel & Indonesian Breach Radar", icon: "🛡️" }
  },

  init() {
    this.setupEventListeners();
    this.startClock();
    this.playRetroSound("boot");
    console.log("[MY-OSINT] Windows 95/98 Environment Initialized.");
  },

  // ==========================================
  // Web Audio API Retro Sound Effects
  // ==========================================
  playRetroSound(type) {
    if (!this.soundEnabled) return;
    try {
      if (!this.audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioCtx = new AudioContext();
      }
      if (this.audioCtx.state === "suspended") {
        this.audioCtx.resume();
      }

      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);

      const now = this.audioCtx.currentTime;

      if (type === "click") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.05);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
        osc.start(now);
        osc.stop(now + 0.05);
      } else if (type === "success") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.setValueAtTime(554.37, now + 0.08);
        osc.frequency.setValueAtTime(659.25, now + 0.16);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
        osc.start(now);
        osc.stop(now + 0.35);
      } else if (type === "boot") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(329.63, now);
        osc.frequency.setValueAtTime(493.88, now + 0.15);
        osc.frequency.setValueAtTime(659.25, now + 0.3);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.6);
        osc.start(now);
        osc.stop(now + 0.6);
      } else if (type === "error") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.setValueAtTime(120, now + 0.1);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        osc.start(now);
        osc.stop(now + 0.25);
      }
    } catch (e) {
      // Audio fallback silent
    }
  },

  toggleSound() {
    this.soundEnabled = !this.soundEnabled;
    const el = document.getElementById("sound-status");
    if (el) el.innerText = this.soundEnabled ? "AKTIF" : "NONAKTIF";
    if (this.soundEnabled) this.playRetroSound("click");
  },

  // ==========================================
  // Navigasi & Event Listeners
  // ==========================================
  setupEventListeners() {
    // Sidebar items
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        const pageId = item.getAttribute("data-page");
        if (pageId) this.switchPage(pageId);
      });
    });

    // Global Click sound
    document.addEventListener("click", (e) => {
      if (e.target.tagName === "BUTTON" || e.target.classList.contains("nav-item") || e.target.classList.contains("menu-item") || e.target.classList.contains("start-item")) {
        this.playRetroSound("click");
      }

      // Tutup start menu jika klik di luar
      const startMenu = document.getElementById("start-menu");
      const startBtn = document.getElementById("start-btn");
      if (startMenu && startBtn && !startMenu.contains(e.target) && !startBtn.contains(e.target)) {
        startMenu.classList.remove("open");
        startBtn.classList.remove("active");
      }
    });

    // Enter key listeners
    const bindEnter = (inputId, actionFn) => {
      const el = document.getElementById(inputId);
      if (el) {
        el.addEventListener("keyup", (e) => {
          if (e.key === "Enter") actionFn.call(this);
        });
      }
    };

    bindEnter("unified-query", this.runUnifiedSearch);
    bindEnter("nik-input", this.runNikDecoder);
    bindEnter("phone-input", this.runPhoneLookup);
    bindEnter("email-input", this.runEmailCheck);
    bindEnter("username-input", this.runUsernameScan);
    bindEnter("dork-target", this.runDorkGenerator);
    bindEnter("ghunt-target", this.runGhuntProfile);
    bindEnter("ghost-target", this.runGhostIntel);
  },

  switchPage(pageId) {
    this.activePage = pageId;

    // Sembunyikan semua page view
    document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
    const targetPage = document.getElementById(pageId);
    if (targetPage) targetPage.classList.add("active");

    // Update active class di sidebar
    document.querySelectorAll(".nav-item").forEach(item => {
      item.classList.toggle("active", item.getAttribute("data-page") === pageId);
    });

    // Update Titlebar & Taskbar
    const meta = this.pageMeta[pageId] || { title: "MY-OSINT 95", icon: "🛡️" };
    document.getElementById("window-title").innerText = meta.title;
    document.getElementById("window-icon").innerText = meta.icon;
    document.getElementById("taskbar-title").innerText = meta.title.split("-")[0].replace("Modul ", "");
    document.getElementById("taskbar-icon").innerText = meta.icon;

    // Tutup start menu jika terbuka
    const startMenu = document.getElementById("start-menu");
    if (startMenu) startMenu.classList.remove("open");
    const startBtn = document.getElementById("start-btn");
    if (startBtn) startBtn.classList.remove("active");
  },

  toggleStartMenu() {
    const startMenu = document.getElementById("start-menu");
    const startBtn = document.getElementById("start-btn");
    if (startMenu && startBtn) {
      const isOpen = startMenu.classList.toggle("open");
      startBtn.classList.toggle("active", isOpen);
    }
  },

  startClock() {
    const update = () => {
      const now = new Date();
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      const clockEl = document.getElementById("clock");
      if (clockEl) clockEl.innerText = `${h}:${m}:${s}`;
    };
    update();
    setInterval(update, 1000);
  },

  // ==========================================
  // HTTP API Request Helper
  // ==========================================
  async apiPost(endpoint, payload) {
    try {
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      return data;
    } catch (err) {
      this.playRetroSound("error");
      alert(`[KESALAHAN SISTEM] Gagal berkomunikasi dengan engine backend: ${err.message}`);
      return null;
    }
  },

  // ==========================================
  // MODUL 0: UNIFIED RECON (DASHBOARD)
  // ==========================================
  async runUnifiedSearch() {
    const query = document.getElementById("unified-query").value.trim();
    if (!query) {
      alert("Masukkan target penyelidikan terlebih dahulu!");
      return;
    }

    const prog = document.getElementById("unified-progress");
    if (prog) prog.style.display = "block";

    const res = await this.apiPost("/api/unified", { query });
    if (prog) prog.style.display = "none";

    if (res) {
      this.playRetroSound("success");
      this.investigationHistory.push({ time: new Date().toISOString(), type: "Unified", data: res });
      
      const container = document.getElementById("unified-results-container");
      const output = document.getElementById("unified-output");
      if (container && output) {
        container.style.display = "block";
        output.innerText = JSON.stringify(res, null, 2);
      }
    }
  },

  // ==========================================
  // MODUL 1: NIK & KTP DECODER
  // ==========================================
  loadSampleNik() {
    // Contoh NIK Jakarta Selatan
    document.getElementById("nik-input").value = "3171010508950002";
    this.runNikDecoder();
  },

  async runNikDecoder() {
    const nik = document.getElementById("nik-input").value.trim();
    if (!nik) {
      alert("Masukkan 16 digit NIK!");
      return;
    }

    const res = await this.apiPost("/api/nik", { nik });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal mendekode NIK.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "NIK", data: res });

    document.getElementById("nik-result-area").style.display = "block";
    document.getElementById("ktp-nik").innerText = res.nik;
    document.getElementById("ktp-provinsi").innerText = res.format.nama_provinsi.toUpperCase();
    document.getElementById("ktp-kabupaten").innerText = res.format.nama_kabupaten.toUpperCase();
    document.getElementById("ktp-wilayah").innerText = `${res.format.nama_kabupaten}, ${res.format.nama_provinsi}`;
    document.getElementById("ktp-kecamatan").innerText = `${res.format.nama_kecamatan} (Kode: ${res.format.kode_kecamatan})`;
    document.getElementById("ktp-tgl-lahir").innerText = res.demografi.tanggal_lahir;
    document.getElementById("ktp-usia").innerText = res.demografi.usia_detail;
    document.getElementById("ktp-gender").innerText = res.demografi.jenis_kelamin;
    document.getElementById("ktp-zodiak").innerText = res.demografi.zodiak;
    document.getElementById("ktp-shio").innerText = res.demografi.shio;
    document.getElementById("ktp-urut").innerText = `Urutan ke-${parseInt(res.format.nomor_urut, 10)} (${res.format.nomor_urut})`;
  },

  // ==========================================
  // MODUL 2: PHONE & CARRIER TRACER
  // ==========================================
  loadSamplePhone() {
    document.getElementById("phone-input").value = "081288889999";
    this.runPhoneLookup();
  },

  async runPhoneLookup() {
    const phone = document.getElementById("phone-input").value.trim();
    if (!phone) {
      alert("Masukkan nomor telepon!");
      return;
    }

    const res = await this.apiPost("/api/phone", { phone });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Nomor telepon tidak valid.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "Phone", data: res });

    const tbody = document.getElementById("phone-result-table-body");
    tbody.innerHTML = `
      <tr>
        <td><strong>Negara & Wilayah</strong></td>
        <td>${res.lokasi.bendera} ${res.lokasi.negara} (${res.lokasi.zona})</td>
        <td>Kode ISO: <b>${res.lokasi.iso}</b></td>
      </tr>
      <tr>
        <td><strong>Operator Telekomunikasi</strong></td>
        <td><span class="badge-tag badge-info">${res.telekomunikasi.operator}</span> (${res.telekomunikasi.brand})</td>
        <td>Tipe: <b>${res.telekomunikasi.layanan}</b></td>
      </tr>
      <tr>
        <td><strong>Format Internasional (E.164)</strong></td>
        <td><code style="font-weight:bold;">${res.format.e164}</code></td>
        <td>Format Nasional: <b>${res.format.national}</b></td>
      </tr>
      <tr>
        <td><strong>HLR / Wilayah Distribusi</strong></td>
        <td>${res.lokasi.hlr_regional}</td>
        <td>Standar: ITU-T E.164</td>
      </tr>
      <tr>
        <td><strong>WhatsApp Direct Chat</strong></td>
        <td>Tautan langsung tanpa simpan kontak</td>
        <td><a href="${res.osint_links.whatsapp_chat}" target="_blank" class="btn" style="padding:2px 8px !important;">💬 Buka Chat WhatsApp</a></td>
      </tr>
      <tr>
        <td><strong>Telegram Deep Link</strong></td>
        <td>Pencarian akun via Telegram</td>
        <td><a href="${res.osint_links.telegram_link}" target="_blank" class="btn" style="padding:2px 8px !important;">✈️ Buka di Telegram</a></td>
      </tr>
      <tr>
        <td><strong>Truecaller Database</strong></td>
        <td>Pelacakan Caller ID publik</td>
        <td><a href="${res.osint_links.truecaller_url}" target="_blank" class="btn" style="padding:2px 8px !important;">🔍 Cari di Truecaller</a></td>
      </tr>
      <tr>
        <td><strong>Google Dork Nomor</strong></td>
        <td><code>${res.osint_links.google_dork}</code></td>
        <td><a href="https://www.google.com/search?q=${encodeURIComponent(res.osint_links.google_dork)}" target="_blank" class="btn" style="padding:2px 8px !important;">🌐 Search Google</a></td>
      </tr>
    `;

    document.getElementById("phone-result-area").style.display = "block";
  },

  // ==========================================
  // MODUL 3: EMAIL AUDIT & HOLEHE
  // ==========================================
  loadSampleEmail() {
    document.getElementById("email-input").value = "budi_santoso@tokopedia.com";
    this.runEmailCheck();
  },

  async runEmailCheck() {
    const email = document.getElementById("email-input").value.trim();
    if (!email) {
      alert("Masukkan alamat email!");
      return;
    }

    const res = await this.apiPost("/api/email", { email });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal memeriksa email.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "Email", data: res });

    // Tampilkan Gravatar jika ada
    const gravatarCard = document.getElementById("gravatar-card");
    if (res.gravatar && res.gravatar.found && res.gravatar.profile) {
      gravatarCard.style.display = "block";
      gravatarCard.innerHTML = `
        <div style="display:flex; gap:12px; align-items:center;">
          <img src="${res.gravatar.avatar_url}" width="64" height="64" style="border:2px inset #000000;" alt="Avatar">
          <div>
            <h4 style="margin:0; color:#00007c;">Profil Gravatar Publik Ditemukan!</h4>
            <p><strong>Nama:</strong> ${res.gravatar.profile.display_name || 'N/A'}</p>
            <p><strong>Lokasi:</strong> ${res.gravatar.profile.current_location || 'N/A'}</p>
            <p><strong>Bio:</strong> ${res.gravatar.profile.about || 'N/A'}</p>
          </div>
        </div>
      `;
    } else {
      gravatarCard.style.display = "none";
    }

    // Render Table Footprint
    const tbody = document.getElementById("email-result-table-body");
    tbody.innerHTML = res.jejak_platform.map(item => `
      <tr>
        <td><strong>${item.platform}</strong></td>
        <td>${item.kategori}</td>
        <td><span class="badge-tag ${item.status.includes('Ditemukan') || item.status.includes('Terdaftar') ? 'badge-success' : 'badge-warning'}">${item.status}</span></td>
        <td><span class="badge-tag ${item.risk_level === 'Kritis' ? 'badge-danger' : (item.risk_level === 'Tinggi' ? 'badge-warning' : 'badge-info')}">${item.risk_level}</span></td>
        <td>${item.catatan}</td>
      </tr>
    `).join("");

    document.getElementById("email-result-area").style.display = "block";
  },

  // ==========================================
  // MODUL 4: USERNAME TRACKER (MAIGRET/SHERLOCK)
  // ==========================================
  loadSampleUsername() {
    document.getElementById("username-input").value = "torvalds";
    this.runUsernameScan();
  },

  async runUsernameScan() {
    const username = document.getElementById("username-input").value.trim();
    if (!username) {
      alert("Masukkan username target!");
      return;
    }

    const prog = document.getElementById("username-progress");
    if (prog) prog.style.display = "block";

    const res = await this.apiPost("/api/username", { username });
    if (prog) prog.style.display = "none";

    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal memindai username.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "Username", data: res });

    document.getElementById("user-stats-found").innerText = res.total_found;
    document.getElementById("user-stats-total").innerText = res.total_scanned;

    const tbody = document.getElementById("username-result-table-body");
    tbody.innerHTML = res.results.map(item => `
      <tr>
        <td><strong>${item.platform}</strong></td>
        <td>${item.region}</td>
        <td>${item.category}</td>
        <td><span class="badge-tag ${item.found ? 'badge-success' : 'badge-warning'}">${item.status}</span></td>
        <td><code>${item.http_code || '-'}</code></td>
        <td>${item.duration_ms} ms</td>
        <td><a href="${item.profile_url}" target="_blank">🌐 Kunjungi Profil</a></td>
      </tr>
    `).join("");

    document.getElementById("username-result-area").style.display = "block";
  },

  // ==========================================
  // MODUL 5: INDO GOOGLE DORKING GENERATOR
  // ==========================================
  async runDorkGenerator() {
    const target = document.getElementById("dork-target").value.trim();
    if (!target) {
      alert("Masukkan kata kunci target (nama, NIK, atau domain)!");
      return;
    }

    const res = await this.apiPost("/api/dorks", { target });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal membuat dorks.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "Dorks", data: res });

    const tbody = document.getElementById("dork-result-table-body");
    tbody.innerHTML = res.dorks.map((item, idx) => `
      <tr>
        <td><span class="badge-tag badge-info">${item.category}</span></td>
        <td><strong>${item.title}</strong><br><small style="color:#555;">${item.description}</small></td>
        <td><code style="background:#f4f4f4; padding:2px 4px; border:1px solid #ddd; display:block;">${item.dork}</code></td>
        <td>
          <a href="${item.google_url}" target="_blank" class="btn" style="padding:2px 8px !important; margin-right:4px;">🌐 Buka Google</a>
          <button class="btn" onclick="navigator.clipboard.writeText('${item.dork.replace(/'/g, "\\'")}'); alert('Dork disalin ke clipboard!');" style="padding:2px 6px !important;">📋 Salin</button>
        </td>
      </tr>
    `).join("");

    document.getElementById("dork-result-area").style.display = "block";
  },

  // ==========================================
  // MODUL 6: GHUNT & GOOGLE PROFILER
  // ==========================================
  async runGhuntProfile() {
    const target = document.getElementById("ghunt-target").value.trim();
    if (!target) {
      alert("Masukkan alamat Gmail atau ID Google target!");
      return;
    }

    const res = await this.apiPost("/api/ghunt", { target });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal memprofil akun Google.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "GHunt", data: res });

    const tbody = document.getElementById("ghunt-result-table-body");
    tbody.innerHTML = res.footprint_vectors.map(item => `
      <tr>
        <td><strong>${item.vector}</strong></td>
        <td><span class="badge-tag ${item.importance.includes('Kritis') ? 'badge-danger' : 'badge-warning'}">${item.importance}</span></td>
        <td>${item.keterangan}<br><code style="font-size:10.5px; color:#555;">${item.dork}</code></td>
        <td><a href="${item.action_url}" target="_blank" class="btn" style="padding:2px 8px !important;">🌐 Telusuri Jejak</a></td>
      </tr>
    `).join("");

    document.getElementById("ghunt-result-area").style.display = "block";
  },

  // ==========================================
  // MODUL 7: GHOSTINTEL & BREACH RADAR
  // ==========================================
  async runGhostIntel() {
    const target = document.getElementById("ghost-target").value.trim();
    if (!target) {
      alert("Masukkan domain, IP, atau host target!");
      return;
    }

    const res = await this.apiPost("/api/ghostintel", { target });
    if (!res || !res.valid) {
      this.playRetroSound("error");
      alert(res?.error || "Gagal menjalankan GhostIntel.");
      return;
    }

    this.playRetroSound("success");
    this.investigationHistory.push({ time: new Date().toISOString(), type: "GhostIntel", data: res });

    // Output Geolocation & DNS
    const geo = res.geolocation;
    document.getElementById("ghost-geo-output").innerHTML = `
      <div style="background:#ffffff; padding:6px; border:2px inset #000000;">
        <p><strong>IP Target:</strong> ${geo.ip} | <strong>Negara:</strong> ${geo.country} (${geo.city || 'N/A'})</p>
        <p><strong>ISP / Organisasi:</strong> ${geo.isp} (${geo.org || 'N/A'}) | <strong>ASN:</strong> ${geo.as_number || 'N/A'}</p>
        <p><strong>Koordinat Perkiraan:</strong> Lat ${geo.lat || '-'}, Lon ${geo.lon || '-'} | <strong>Zona Waktu:</strong> ${geo.timezone || 'N/A'}</p>
      </div>
    `;

    // Render Historical Leaks
    const tbody = document.getElementById("ghost-breach-table-body");
    tbody.innerHTML = res.breach_intelligence.map(item => `
      <tr>
        <td><strong>${item.insiden}</strong></td>
        <td>${item.tahun}</td>
        <td><b>${item.skala}</b></td>
        <td><code>${item.vektor_bocor}</code></td>
        <td><span class="badge-tag ${item.keparahan === 'Sangat Kritis' ? 'badge-danger' : 'badge-warning'}">${item.keparahan}</span></td>
        <td>${item.relevansi_identitas}</td>
      </tr>
    `).join("");

    document.getElementById("ghost-result-area").style.display = "block";
  },

  // ==========================================
  // Ekspor & Bantuan
  // ==========================================
  exportReport() {
    if (this.investigationHistory.length === 0) {
      alert("Belum ada data penyelidikan yang tersimpan untuk diekspor!");
      return;
    }

    const reportContent = JSON.stringify({
      generated_at: new Date().toISOString(),
      tool: "MY-OSINT 95 (Asian & Indonesian OSINT Suite)",
      investigations_count: this.investigationHistory.length,
      history: this.investigationHistory
    }, null, 2);

    const blob = new Blob([reportContent], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `LAPORAN_OSINT_${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    this.playRetroSound("success");
    alert("Laporan penyelidikan berhasil disimpan ke file JSON!");
  },

  clearCurrentForm() {
    const inputs = document.querySelectorAll("input[type='text']");
    inputs.forEach(input => input.value = "");
    this.playRetroSound("click");
    alert("Semua form isian telah dikosongkan.");
  },

  showAbout() {
    alert("MY-OSINT 95 - Asian & Indonesian Intelligence Suite\n\nDesain: Windows 95/98 Classic Retro (ui.md)\nMesin (7): NIK Decoder, Phone Tracer, Holehe Email, Username Tracker, Google Dorker, GHunt Profiler, GhostIntel.\nFokus: Indonesia & Asia (Open-Source & Free)\nArsitektur: Zero-Dependency Python REST Server.");
  }
};

window.addEventListener("DOMContentLoaded", () => {
  app.init();
});

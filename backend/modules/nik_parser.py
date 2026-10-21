"""
Modul NIK & KTP Demographics Decoder (Indonesia)
Mendekode 16 digit NIK berdasarkan format resmi Kemendagri & BPS secara offline.
Format NIK: [2 digit Prov][2 digit Kab/Kota][2 digit Kec][2 digit Tgl][2 digit Bulan][2 digit Tahun][4 digit Urut]
"""

import datetime
from typing import Dict, Any, Optional

# Database 38 Provinsi Indonesia
PROVINSI_DB = {
    "11": "Aceh",
    "12": "Sumatera Utara",
    "13": "Sumatera Barat",
    "14": "Riau",
    "15": "Jambi",
    "16": "Sumatera Selatan",
    "17": "Bengkulu",
    "18": "Lampung",
    "19": "Kepulauan Bangka Belitung",
    "21": "Kepulauan Riau",
    "31": "DKI Jakarta",
    "32": "Jawa Barat",
    "33": "Jawa Tengah",
    "34": "Daerah Istimewa Yogyakarta",
    "35": "Jawa Timur",
    "36": "Banten",
    "51": "Bali",
    "52": "Nusa Tenggara Barat",
    "53": "Nusa Tenggara Timur",
    "61": "Kalimantan Barat",
    "62": "Kalimantan Tengah",
    "63": "Kalimantan Selatan",
    "64": "Kalimantan Timur",
    "65": "Kalimantan Utara",
    "71": "Sulawesi Utara",
    "72": "Sulawesi Tengah",
    "73": "Sulawesi Selatan",
    "74": "Sulawesi Tenggara",
    "75": "Gorontalo",
    "76": "Sulawesi Barat",
    "81": "Maluku",
    "82": "Maluku Utara",
    "91": "Papua",
    "92": "Papua Barat",
    "93": "Papua Selatan",
    "94": "Papua Tengah",
    "95": "Papua Pegunungan",
    "96": "Papua Barat Daya",
}

# Database Sampel Wilayah Kabupaten / Kota Populer Indonesia
KABUPATEN_DB = {
    # DKI Jakarta (31)
    "3101": "Kabupaten Kepulauan Seribu",
    "3171": "Kota Jakarta Selatan",
    "3172": "Kota Jakarta Timur",
    "3173": "Kota Jakarta Pusat",
    "3174": "Kota Jakarta Barat",
    "3175": "Kota Jakarta Utara",

    # Jawa Barat (32)
    "3201": "Kabupaten Bogor",
    "3202": "Kabupaten Sukabumi",
    "3203": "Kabupaten Cianjur",
    "3204": "Kabupaten Bandung",
    "3205": "Kabupaten Garut",
    "3206": "Kabupaten Tasikmalaya",
    "3207": "Kabupaten Ciamis",
    "3208": "Kabupaten Kuningan",
    "3209": "Kabupaten Cirebon",
    "3210": "Kabupaten Majalengka",
    "3211": "Kabupaten Sumedang",
    "3212": "Kabupaten Indramayu",
    "3213": "Kabupaten Subang",
    "3214": "Kabupaten Purwakarta",
    "3215": "Kabupaten Karawang",
    "3216": "Kabupaten Bekasi",
    "3217": "Kabupaten Bandung Barat",
    "3218": "Kabupaten Pangandaran",
    "3271": "Kota Bogor",
    "3272": "Kota Sukabumi",
    "3273": "Kota Bandung",
    "3274": "Kota Cirebon",
    "3275": "Kota Bekasi",
    "3276": "Kota Depok",
    "3277": "Kota Cimahi",
    "3278": "Kota Tasikmalaya",
    "3279": "Kota Banjar",

    # Jawa Tengah (33)
    "3301": "Kabupaten Cilacap",
    "3302": "Kabupaten Banyumas",
    "3303": "Kabupaten Purbalingga",
    "3304": "Kabupaten Banjarnegara",
    "3305": "Kabupaten Kebumen",
    "3306": "Kabupaten Purworejo",
    "3307": "Kabupaten Wonosobo",
    "3308": "Kabupaten Magelang",
    "3309": "Kabupaten Boyolali",
    "3310": "Kabupaten Klaten",
    "3311": "Kabupaten Sukoharjo",
    "3312": "Kabupaten Wonogiri",
    "3313": "Kabupaten Karanganyar",
    "3314": "Kabupaten Sragen",
    "3315": "Kabupaten Grobogan",
    "3316": "Kabupaten Blora",
    "3317": "Kabupaten Rembang",
    "3318": "Kabupaten Pati",
    "3319": "Kabupaten Kudus",
    "3320": "Kabupaten Jepara",
    "3321": "Kabupaten Demak",
    "3322": "Kabupaten Semarang",
    "3323": "Kabupaten Temanggung",
    "3324": "Kabupaten Kendal",
    "3325": "Kabupaten Batang",
    "3326": "Kabupaten Pekalongan",
    "3327": "Kabupaten Pemalang",
    "3328": "Kabupaten Tegal",
    "3329": "Kabupaten Brebes",
    "3371": "Kota Magelang",
    "3372": "Kota Surakarta (Solo)",
    "3373": "Kota Salatiga",
    "3374": "Kota Semarang",
    "3375": "Kota Pekalongan",
    "3376": "Kota Tegal",

    # DI Yogyakarta (34)
    "3401": "Kabupaten Kulon Progo",
    "3402": "Kabupaten Bantul",
    "3403": "Kabupaten Gunungkidul",
    "3404": "Kabupaten Sleman",
    "3471": "Kota Yogyakarta",

    # Jawa Timur (35)
    "3501": "Kabupaten Pacitan",
    "3502": "Kabupaten Ponorogo",
    "3503": "Kabupaten Trenggalek",
    "3504": "Kabupaten Tulungagung",
    "3505": "Kabupaten Blitar",
    "3506": "Kabupaten Kediri",
    "3507": "Kabupaten Malang",
    "3508": "Kabupaten Lumajang",
    "3509": "Kabupaten Jember",
    "3510": "Kabupaten Banyuwangi",
    "3511": "Kabupaten Bondowoso",
    "3512": "Kabupaten Situbondo",
    "3513": "Kabupaten Probolinggo",
    "3514": "Kabupaten Pasuruan",
    "3515": "Kabupaten Sidoarjo",
    "3516": "Kabupaten Mojokerto",
    "3517": "Kabupaten Jombang",
    "3518": "Kabupaten Nganjuk",
    "3519": "Kabupaten Madiun",
    "3520": "Kabupaten Magetan",
    "3521": "Kabupaten Ngawi",
    "3522": "Kabupaten Bojonegoro",
    "3523": "Kabupaten Tuban",
    "3524": "Kabupaten Lamongan",
    "3525": "Kabupaten Gresik",
    "3526": "Kabupaten Bangkalan",
    "3527": "Kabupaten Sampang",
    "3528": "Kabupaten Pamekasan",
    "3529": "Kabupaten Sumenep",
    "3571": "Kota Kediri",
    "3572": "Kota Blitar",
    "3573": "Kota Malang",
    "3574": "Kota Probolinggo",
    "3575": "Kota Pasuruan",
    "3576": "Kota Mojokerto",
    "3577": "Kota Madiun",
    "3578": "Kota Surabaya",
    "3579": "Kota Batu",

    # Banten (36)
    "3601": "Kabupaten Pandeglang",
    "3602": "Kabupaten Lebak",
    "3603": "Kabupaten Tangerang",
    "3604": "Kabupaten Serang",
    "3671": "Kota Tangerang",
    "3672": "Kota Cilegon",
    "3673": "Kota Serang",
    "3674": "Kota Tangerang Selatan",

    # Bali (51)
    "5101": "Kabupaten Jembrana",
    "5102": "Kabupaten Tabanan",
    "5103": "Kabupaten Badung",
    "5104": "Kabupaten Gianyar",
    "5105": "Kabupaten Klungkung",
    "5106": "Kabupaten Bangli",
    "5107": "Kabupaten Karangasem",
    "5108": "Kabupaten Buleleng",
    "5171": "Kota Denpasar",

    # Sumatera Utara (12)
    "3271": "Kota Medan",
    "1271": "Kota Medan",
    "1272": "Kota Pematangsiantar",
    "1273": "Kota Sibolga",
    "1274": "Kota Tanjungbalai",
    "1275": "Kota Binjai",
    "1201": "Kabupaten Tapanuli Tengah",
    "1202": "Kabupaten Tapanuli Utara",
    "1203": "Kabupaten Tapanuli Selatan",
    "1204": "Kabupaten Nias",
    "1205": "Kabupaten Langkat",
    "1206": "Kabupaten Karo",
    "1207": "Kabupaten Deli Serdang",
    "1208": "Kabupaten Simalungun",
    "1209": "Kabupaten Asahan",

    # Sumatera Barat (13)
    "1371": "Kota Padang",
    "1372": "Kota Solok",
    "1373": "Kota Sawahlunto",
    "1374": "Kota Padang Panjang",
    "1375": "Kota Bukittinggi",
    "1376": "Kota Payakumbuh",
    "1377": "Kota Pariaman",

    # Riau (14)
    "1471": "Kota Pekanbaru",
    "1472": "Kota Dumai",

    # Sulawesi Selatan (73)
    "7371": "Kota Makassar",
    "7372": "Kota Parepare",
    "7373": "Kota Palopo",
    "7306": "Kabupaten Gowa",

    # Kalimantan Timur (64)
    "6471": "Kota Balikpapan",
    "6472": "Kota Samarinda",
    "6474": "Kota Bontang",
    "6401": "Kabupaten Paser",
    "6402": "Kabupaten Kutai Kartanegara",
    "6409": "Kabupaten Penajam Paser Utara (IKN)",
}

SHIO_ANIMALS = [
    "Tikus", "Kerbau", "Macan", "Kelinci", "Naga", "Ular",
    "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi"
]

def get_zodiac(day: int, month: int) -> str:
    dates = [
        (1, 20, "Capricorn"), (2, 19, "Aquarius"), (3, 20, "Pisces"),
        (4, 20, "Aries"), (5, 21, "Taurus"), (6, 21, "Gemini"),
        (7, 22, "Cancer"), (8, 23, "Leo"), (9, 23, "Virgo"),
        (10, 23, "Libra"), (11, 22, "Scorpio"), (12, 22, "Sagittarius"),
        (12, 31, "Capricorn")
    ]
    for m, d, sign in dates:
        if month == m and day <= d:
            return sign
        elif month == m - 1 and day > dates[m - 2][1]:
            return sign
    return "Capricorn"

def get_shio(year: int) -> str:
    # 1900 adalah tahun Tikus (indeks 0 jika basis 1900)
    idx = (year - 1900) % 12
    return SHIO_ANIMALS[idx]

def parse_nik(nik_input: str) -> Dict[str, Any]:
    nik = "".join([c for c in str(nik_input).strip() if c.isdigit()])
    
    if len(nik) != 16:
        return {
            "valid": False,
            "error": f"Panjang NIK harus tepat 16 digit angka (diterima: {len(nik)} digit)."
        }

    kode_prov = nik[0:2]
    kode_kab = nik[0:4]
    kode_kec = nik[4:6]
    raw_tgl = int(nik[6:8])
    raw_bln = int(nik[8:10])
    raw_thn = int(nik[10:12])
    nomor_urut = nik[12:16]

    # Determinasi Gender & Tanggal Lahir Riil
    if raw_tgl > 40:
        gender = "Perempuan"
        tgl_lahir = raw_tgl - 40
    else:
        gender = "Laki-laki"
        tgl_lahir = raw_tgl

    # Determinasi Tahun (Abad 20 / 21)
    current_year = datetime.date.today().year
    current_yy = current_year % 100

    if raw_thn > current_yy:
        tahun_lahir = 1900 + raw_thn
    else:
        tahun_lahir = 2000 + raw_thn

    # Validasi Tanggal
    try:
        birth_date = datetime.date(tahun_lahir, raw_bln, tgl_lahir)
        today = datetime.date.today()
        
        # Hitung Usia
        age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Detail Usia Bulan & Hari
        months = today.month - birth_date.month
        days = today.day - birth_date.day
        if days < 0:
            months -= 1
            days += 30
        if months < 0:
            months += 12
            
        birth_date_str = birth_date.strftime("%d-%m-%Y")
        zodiac = get_zodiac(tgl_lahir, raw_bln)
        shio = get_shio(tahun_lahir)
        date_valid = True
    except ValueError:
        birth_date_str = f"{tgl_lahir:02d}-{raw_bln:02d}-{tahun_lahir} (Tanggal Invalid)"
        age_years = None
        months = None
        days = None
        zodiac = "N/A"
        shio = "N/A"
        date_valid = False

    provinsi_nama = PROVINSI_DB.get(kode_prov, f"Provinsi Tidak Terdaftar (Kode: {kode_prov})")
    kabupaten_nama = KABUPATEN_DB.get(kode_kab, f"Kabupaten/Kota (Kode: {kode_kab})")
    kecamatan_nama = f"Kecamatan Wilayah {kode_kec}"

    return {
        "valid": True,
        "nik": nik,
        "format": {
            "kode_provinsi": kode_prov,
            "nama_provinsi": provinsi_nama,
            "kode_kabupaten": kode_kab,
            "nama_kabupaten": kabupaten_nama,
            "kode_kecamatan": kode_kec,
            "nama_kecamatan": kecamatan_nama,
            "nomor_urut": nomor_urut,
        },
        "demografi": {
            "jenis_kelamin": gender,
            "tanggal_lahir": birth_date_str,
            "hari": tgl_lahir,
            "bulan": raw_bln,
            "tahun": tahun_lahir,
            "usia_tahun": age_years,
            "usia_detail": f"{age_years} Tahun, {months} Bulan, {days} Hari" if age_years is not None else "N/A",
            "zodiak": zodiac,
            "shio": shio,
            "validitas_tanggal": date_valid
        },
        "analisis_intelijen": {
            "kategori_usia": "Lansia (>60)" if age_years and age_years >= 60 else ("Dewasa (18-59)" if age_years and age_years >= 18 else "Anak/Remaja (<18)"),
            "status_kemendagri": "Sesuai Standar Algoritma KTP-el Kemendagri RI",
            "catatan": "Nomor urut registrasi diterbitkan berurutan oleh Disdukcapil setempat pada tanggal lahir yang sama."
        }
    }

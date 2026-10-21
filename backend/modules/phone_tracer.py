"""
Modul Phone & Carrier Lookup (Indonesia & Asia Telco)
Mendeteksi operator telekomunikasi seluler Indonesia, prefix HLR regional,
standardisasi nomor internasional E.164 untuk Asia, dan deep-link OSINT (WhatsApp, Telegram, Truecaller).
"""

import re
from typing import Dict, Any

# Database Prefix Telco Indonesia
INDONESIA_TELCO_PREFIX = {
    # Telkomsel (Halo, Simpati, Loop, As, By.U)
    "0811": {"operator": "Telkomsel", "brand": "Kartu Halo (Pascabayar)", "tipe": "Postpaid"},
    "0812": {"operator": "Telkomsel", "brand": "simPATI / Halo", "tipe": "Prepaid/Postpaid"},
    "0813": {"operator": "Telkomsel", "brand": "simPATI", "tipe": "Prepaid"},
    "0821": {"operator": "Telkomsel", "brand": "simPATI", "tipe": "Prepaid"},
    "0822": {"operator": "Telkomsel", "brand": "simPATI / Loop", "tipe": "Prepaid"},
    "0823": {"operator": "Telkomsel", "brand": "Kartu As", "tipe": "Prepaid"},
    "0851": {"operator": "Telkomsel", "brand": "By.U / Kartu As", "tipe": "Digital Prepaid"},
    "0852": {"operator": "Telkomsel", "brand": "Kartu As", "tipe": "Prepaid"},
    "0853": {"operator": "Telkomsel", "brand": "Kartu As", "tipe": "Prepaid"},

    # Indosat Ooredoo Hutchison (IM3, Matrix, Mentari)
    "0814": {"operator": "Indosat Ooredoo", "brand": "Indosat M2 (Broadband)", "tipe": "Data Only"},
    "0815": {"operator": "Indosat Ooredoo", "brand": "Matrix / Mentari", "tipe": "Prepaid/Postpaid"},
    "0816": {"operator": "Indosat Ooredoo", "brand": "Matrix / Mentari", "tipe": "Prepaid/Postpaid"},
    "0855": {"operator": "Indosat Ooredoo", "brand": "Matrix Auto", "tipe": "Postpaid"},
    "0856": {"operator": "Indosat Ooredoo", "brand": "IM3 Ooredoo", "tipe": "Prepaid"},
    "0857": {"operator": "Indosat Ooredoo", "brand": "IM3 Ooredoo", "tipe": "Prepaid"},
    "0858": {"operator": "Indosat Ooredoo", "brand": "Mentari / IM3", "tipe": "Prepaid"},

    # XL Axiata
    "0817": {"operator": "XL Axiata", "brand": "XL Prioritas / Prabayar", "tipe": "Prepaid/Postpaid"},
    "0818": {"operator": "XL Axiata", "brand": "XL Prabayar", "tipe": "Prepaid"},
    "0819": {"operator": "XL Axiata", "brand": "XL Prabayar", "tipe": "Prepaid"},
    "0859": {"operator": "XL Axiata", "brand": "XL Prabayar", "tipe": "Prepaid"},
    "0877": {"operator": "XL Axiata", "brand": "XL Prabayar", "tipe": "Prepaid"},
    "0878": {"operator": "XL Axiata", "brand": "XL Prabayar", "tipe": "Prepaid"},

    # AXIS (XL Axiata Group)
    "0831": {"operator": "AXIS (XL Axiata)", "brand": "AXIS", "tipe": "Prepaid"},
    "0832": {"operator": "AXIS (XL Axiata)", "brand": "AXIS", "tipe": "Prepaid"},
    "0833": {"operator": "AXIS (XL Axiata)", "brand": "AXIS", "tipe": "Prepaid"},
    "0838": {"operator": "AXIS (XL Axiata)", "brand": "AXIS", "tipe": "Prepaid"},

    # Smartfren
    "0881": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0882": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0883": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0884": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0885": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0886": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0887": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0888": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},
    "0889": {"operator": "Smartfren", "brand": "Smartfren 4G LTE", "tipe": "Prepaid"},

    # Tri / 3 (Indosat Ooredoo Hutchison)
    "0895": {"operator": "Tri (IOH)", "brand": "Tri 3 Indonesia", "tipe": "Prepaid"},
    "0896": {"operator": "Tri (IOH)", "brand": "Tri 3 Indonesia", "tipe": "Prepaid"},
    "0897": {"operator": "Tri (IOH)", "brand": "Tri 3 Indonesia", "tipe": "Prepaid"},
    "0898": {"operator": "Tri (IOH)", "brand": "Tri 3 Indonesia", "tipe": "Prepaid"},
    "0899": {"operator": "Tri (IOH)", "brand": "Tri 3 Indonesia", "tipe": "Prepaid"},
}

# Direktori Kode Negara Asia
ASIA_COUNTRY_CODES = {
    "62": {"negara": "Indonesia", "iso": "ID", "bendera": "🇮🇩", "zona": "Asia Tenggara"},
    "60": {"negara": "Malaysia", "iso": "MY", "bendera": "🇲🇾", "zona": "Asia Tenggara"},
    "65": {"negara": "Singapura", "iso": "SG", "bendera": "🇸🇬", "zona": "Asia Tenggara"},
    "63": {"negara": "Filipina", "iso": "PH", "bendera": "🇵🇭", "zona": "Asia Tenggara"},
    "66": {"negara": "Thailand", "iso": "TH", "bendera": "🇹🇭", "zona": "Asia Tenggara"},
    "84": {"negara": "Vietnam", "iso": "VN", "bendera": "🇻🇳", "zona": "Asia Tenggara"},
    "81": {"negara": "Jepang", "iso": "JP", "bendera": "🇯🇵", "zona": "Asia Timur"},
    "82": {"negara": "Korea Selatan", "iso": "KR", "bendera": "🇰🇷", "zona": "Asia Timur"},
    "86": {"negara": "Tiongkok (China)", "iso": "CN", "bendera": "🇨🇳", "zona": "Asia Timur"},
    "91": {"negara": "India", "iso": "IN", "bendera": "🇮🇳", "zona": "Asia Selatan"},
    "670": {"negara": "Timor Leste", "iso": "TL", "bendera": "🇹🇱", "zona": "Asia Tenggara"},
    "852": {"negara": "Hong Kong", "iso": "HK", "bendera": "🇭🇰", "zona": "Asia Timur"},
    "886": {"negara": "Taiwan", "iso": "TW", "bendera": "🇹🇼", "zona": "Asia Timur"},
}

def analyze_phone(phone_input: str) -> Dict[str, Any]:
    cleaned = re.sub(r"[^\d+]", "", str(phone_input).strip())
    
    # Normalisasi format
    if cleaned.startswith("+"):
        raw_digits = cleaned[1:]
    else:
        raw_digits = cleaned

    if not raw_digits:
        return {"valid": False, "error": "Nomor telepon kosong atau tidak valid."}

    # Cek apakah nomor Indonesia lokal (08xx)
    is_indonesia = False
    if raw_digits.startswith("08"):
        is_indonesia = True
        e164_digits = "62" + raw_digits[1:]
        national_format = raw_digits
    elif raw_digits.startswith("62"):
        is_indonesia = True
        e164_digits = raw_digits
        national_format = "0" + raw_digits[2:]
    else:
        e164_digits = raw_digits
        national_format = raw_digits

    # Deteksi Negara Asia
    country_info = None
    for code, info in sorted(ASIA_COUNTRY_CODES.items(), key=lambda x: len(x[0]), reverse=True):
        if e164_digits.startswith(code):
            country_info = info
            country_code = code
            break

    if not country_info:
        country_info = {"negara": "Lainnya / Global", "iso": "GL", "bendera": "🌐", "zona": "Global"}
        country_code = "N/A"

    # Jika Indonesia, identifikasi operator & HLR
    operator_data = {
        "operator": "Tidak Dikenal / Global",
        "brand": "Standard Mobile",
        "tipe": "Unknown",
        "hlr_area": "Indonesia Nasional / General"
    }

    if is_indonesia:
        prefix_4 = national_format[:4]
        if prefix_4 in INDONESIA_TELCO_PREFIX:
            telco = INDONESIA_TELCO_PREFIX[prefix_4]
            operator_data["operator"] = telco["operator"]
            operator_data["brand"] = telco["brand"]
            operator_data["tipe"] = telco["tipe"]
            
            # Estimasi HLR Wilayah Indonesia
            if prefix_4 in ["0811", "0812", "0813"]:
                operator_data["hlr_area"] = "Area 2 (Jabodetabek / Jabar) & Area 1 (Sumatera) Prioritas"
            elif prefix_4 in ["0821", "0822", "0852", "0853"]:
                operator_data["hlr_area"] = "Area 3 (Jawa Tengah, DIY, Jatim, Bali) & Area 4 (Kalimantan, Sulawesi)"
            elif prefix_4.startswith("0851"):
                operator_data["hlr_area"] = "By.U Digital Mobile / Nasional Seluruh Indonesia"
            elif prefix_4.startswith("0856") or prefix_4.startswith("0857"):
                operator_data["hlr_area"] = "Indosat Seluler Regional Jabodetabek / Jawa / Sumatera"
            else:
                operator_data["hlr_area"] = "Jangkauan Nasional Indonesia"
        else:
            operator_data["operator"] = "Operator Lokal Lain / PSTN / Tidak Terdaftar"

    # Generate OSINT Deep Links
    wa_link = f"https://wa.me/{e164_digits}"
    tg_link = f"https://t.me/+{e164_digits}"
    truecaller_search = f"https://www.truecaller.com/search/{country_info.get('iso', 'id').lower()}/{national_format}"
    google_dork_phone = f'"{national_format}" OR "+{e164_digits}"'

    return {
        "valid": True,
        "raw_input": phone_input,
        "format": {
            "e164": f"+{e164_digits}",
            "e164_digits": e164_digits,
            "national": national_format,
            "country_code": country_code if country_info else "N/A"
        },
        "lokasi": {
            "negara": country_info["negara"],
            "iso": country_info["iso"],
            "bendera": country_info["bendera"],
            "zona": country_info["zona"],
            "hlr_regional": operator_data.get("hlr_area", "N/A")
        },
        "telekomunikasi": {
            "operator": operator_data["operator"],
            "brand": operator_data["brand"],
            "layanan": operator_data["tipe"],
            "status_penomoran": "Valid E.164 Standar ITU-T"
        },
        "osint_links": {
            "whatsapp_chat": wa_link,
            "whatsapp_api": f"https://api.whatsapp.com/send?phone={e164_digits}",
            "telegram_link": tg_link,
            "truecaller_url": truecaller_search,
            "google_dork": google_dork_phone
        }
    }

"""
Modul Basis Data SQL Lokal (SQLite3)
Mencatat seluruh rekaman intelijen OSINT agar tidak melakukan query daring berulang,
serta mencatat log keamanan, error WAF, dan hal berbahaya yang perlu dicatat.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "osint_archive.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabel Arsip Hasil OSINT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS osint_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_query TEXT UNIQUE NOT NULL,
        target_name TEXT,
        target_phone TEXT,
        target_location TEXT,
        candidate_count INTEGER DEFAULT 0,
        candidates_json TEXT,
        gov_registries_json TEXT,
        positive_findings_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Tabel Log Keamanan, Error WAF, & Hal Berbahaya
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL,
        source TEXT NOT NULL,
        target TEXT,
        message TEXT NOT NULL,
        details TEXT
    );
    """)

    conn.commit()
    conn.close()

def log_security_event(level: str, source: str, message: str, target: str = "", details: str = ""):
    """Mencatat error koneksi, WAF block, atau peringatan keamanan ke SQL."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO security_logs (timestamp, level, source, target, message, details)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (now_str, level.upper(), source, target, message, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Gagal mencatat security log: {e}")

def get_security_logs(level: str = "ALL", limit: int = 150) -> List[Dict[str, Any]]:
    """Mengambil log error dan keamanan terbaru dari SQL dengan filter level."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if level and level != "ALL":
            cursor.execute("SELECT * FROM security_logs WHERE level = ? ORDER BY id DESC LIMIT ?", (level, limit))
        else:
            cursor.execute("SELECT * FROM security_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        logs = []
        for r in rows:
            logs.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "level": r["level"],
                "source": r["source"],
                "target": r["target"],
                "message": r["message"],
                "details": r["details"]
            })
        conn.close()
        return logs
    except Exception as e:
        print(f"[DB ERROR] Gagal membaca security logs: {e}")
        return []

def clear_security_logs():
    """Mengosongkan tabel log."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM security_logs")
        conn.commit()
        conn.close()
    except Exception:
        pass

def save_osint_result(
    query: str,
    name: str = "",
    phone: str = "",
    location: str = "",
    candidates: List[Dict[str, Any]] = None,
    registries: List[Dict[str, Any]] = None,
    positive_findings: List[Dict[str, Any]] = None
):
    """Menyimpan arsip lengkap hasil OSINT ke SQL."""
    clean_q = (query or "").strip().lower()
    if not clean_q:
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cand_list = candidates or []
        
        cursor.execute("""
            INSERT INTO osint_records (
                target_query, target_name, target_phone, target_location,
                candidate_count, candidates_json, gov_registries_json,
                positive_findings_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(target_query) DO UPDATE SET
                target_name=excluded.target_name,
                target_phone=excluded.target_phone,
                target_location=excluded.target_location,
                candidate_count=excluded.candidate_count,
                candidates_json=excluded.candidates_json,
                gov_registries_json=excluded.gov_registries_json,
                positive_findings_json=excluded.positive_findings_json,
                updated_at=excluded.updated_at
        """, (
            clean_q,
            name,
            phone,
            location,
            len(cand_list),
            json.dumps(cand_list),
            json.dumps(registries or []),
            json.dumps(positive_findings or []),
            now_str
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Gagal menyimpan osint record: {e}")

def get_osint_result(query: str) -> Optional[Dict[str, Any]]:
    """Mengambil arsip OSINT yang sudah tersimpan di database lokal."""
    clean_q = (query or "").strip().lower()
    if not clean_q:
        return None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM osint_records WHERE target_query = ?", (clean_q,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "query": row["target_query"],
                "name": row["target_name"],
                "phone": row["target_phone"],
                "location": row["target_location"],
                "candidate_count": row["candidate_count"],
                "candidates": json.loads(row["candidates_json"] or "[]"),
                "registries": json.loads(row["gov_registries_json"] or "[]"),
                "positive_findings": json.loads(row["positive_findings_json"] or "[]"),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
    except Exception as e:
        print(f"[DB ERROR] Gagal membaca osint record: {e}")

    return None

# Otomatis inisialisasi tabel saat modul diimpor
init_db()

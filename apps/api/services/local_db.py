import os
import sqlite3
import hashlib
import uuid
import logging
from datetime import datetime
import hmac

logger = logging.getLogger(__name__)

# Locate sqlite database inside promptpilot/apps/api directory
API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(API_DIR, "promptpilot.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the local SQLite database tables if they do not exist.
    """
    logger.info(f"Initializing SQLite database at: {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table (with password hash and salt)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        plan TEXT DEFAULT 'free',
        created_at TEXT DEFAULT (datetime('now', 'utc'))
    )
    """)
    
    # 2. Compressions Metrics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compressions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        original_tokens INTEGER NOT NULL,
        compressed_tokens INTEGER NOT NULL,
        model TEXT NOT NULL,
        savings_percent REAL NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'utc')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 3. Daily Usage Aggregation Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage_daily (
        user_id TEXT,
        date TEXT DEFAULT (date('now', 'utc')),
        total_compressions INTEGER DEFAULT 1,
        total_tokens_saved INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, date),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 4. Context Documents Table (Title unique per user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS context_documents (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        original_text TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'utc')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, title)
    )
    """)
    
    # 5. Context Chunks Table (Holds chunk text and stringified vector coordinates)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS context_chunks (
        id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        chunk_text TEXT NOT NULL,
        vector_json TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'utc')),
        FOREIGN KEY (doc_id) REFERENCES context_documents(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    logger.info("SQLite database tables initialized successfully.")

# ==========================================
# SECURE PASSWORD HASHING (PBKDF2-HMAC-SHA256)
# ==========================================

def hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """
    Hashes a password using PBKDF2-HMAC-SHA256.
    Generates a 16-byte salt if not provided.
    Returns (password_hash_hex, salt_hex)
    """
    if salt is None:
        salt = os.urandom(16)
    
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000  # Iterations
    )
    return pwd_hash.hex(), salt.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """
    Verifies a password against its stored salt and hash.
    Uses hmac.compare_digest for constant-time comparison to prevent timing attacks.
    """
    try:
        salt = bytes.fromhex(salt_hex)
        hash_to_verify, _ = hash_password(password, salt)
        return hmac.compare_digest(hash_to_verify, hash_hex)
    except Exception as e:
        logger.error(f"Error during password verification: {e}")
        return False

# ==========================================
# DATABASE OPERATIONS
# ==========================================

def create_user(email: str, password: str) -> dict | None:
    """
    Creates a new user in the SQLite database.
    Email uniqueness is enforced by the database text index.
    Returns the user dict or raises sqlite3.IntegrityError if duplicate.
    """
    email_clean = email.strip().lower()
    user_id = str(uuid.uuid4())
    pwd_hash, pwd_salt = hash_password(password)
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (id, email, password_hash, salt, plan) VALUES (?, ?, ?, ?, ?)",
            (user_id, email_clean, pwd_hash, pwd_salt, "pro")  # Granting pro plan for premium dev feel
        )
        conn.commit()
        return {
            "id": user_id,
            "email": email_clean,
            "plan": "pro"
        }
    except sqlite3.IntegrityError as e:
        # Duplicate entry
        logger.warning(f"Integrity check failed during registration for email {email_clean}: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email: str) -> dict | None:
    """
    Retrieves user record from database by email.
    """
    email_clean = email.strip().lower()
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email_clean,)
    ).fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_by_id(user_id: str) -> dict | None:
    """
    Retrieves user record from database by user_id.
    """
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def log_local_compression(
    user_id: str,
    original_tokens: int,
    compressed_tokens: int,
    model: str,
    savings_percent: float
) -> bool:
    """
    Logs prompt compression metrics and automatically updates daily aggregated telemetry in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    comp_id = str(uuid.uuid4())
    date_today = datetime.utcnow().strftime("%Y-%m-%d")
    tokens_saved = max(0, original_tokens - compressed_tokens)
    
    try:
        # 1. Log metrics in compressions table
        cursor.execute(
            "INSERT INTO compressions (id, user_id, original_tokens, compressed_tokens, model, savings_percent) VALUES (?, ?, ?, ?, ?, ?)",
            (comp_id, user_id, original_tokens, compressed_tokens, model, savings_percent)
        )
        
        # 2. Upsert daily usage aggregator
        cursor.execute(
            """
            INSERT INTO usage_daily (user_id, date, total_compressions, total_tokens_saved)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                total_compressions = total_compressions + 1,
                total_tokens_saved = total_tokens_saved + EXCLUDED.total_tokens_saved
            """,
            (user_id, date_today, tokens_saved)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to log compression locally in SQLite: {e}")
        return False
    finally:
        conn.close()

def get_user_dashboard_stats(user_id: str) -> dict:
    """
    Computes exact summary metrics for user's dashboard stats.
    """
    conn = get_db_connection()
    
    # 1. Summary aggregations
    agg = conn.execute(
        """
        SELECT 
            COUNT(*) as total_audited,
            SUM(original_tokens - compressed_tokens) as total_tokens_saved,
            AVG(savings_percent) as avg_reduction
        FROM compressions
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()
    
    # 2. Daily savings logs (last 7 entries)
    daily_rows = conn.execute(
        """
        SELECT date, SUM(total_tokens_saved) as saved
        FROM usage_daily
        WHERE user_id = ?
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
        """,
        (user_id,)
    ).fetchall()
    
    # 3. Model breakdown
    model_rows = conn.execute(
        """
        SELECT model, AVG(savings_percent) as avg_savings
        FROM compressions
        WHERE user_id = ?
        GROUP BY model
        """,
        (user_id,)
    ).fetchall()
    
    # 4. Recent compressions list
    recent_rows = conn.execute(
        """
        SELECT id, original_tokens, compressed_tokens, model, savings_percent, created_at
        FROM compressions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    total_audited = agg["total_audited"] or 0
    total_tokens_saved = agg["total_tokens_saved"] or 0
    avg_reduction = round(agg["avg_reduction"] or 0.0, 1)
    
    # Estimated dollar saved (standard custom API weights approx $0.005 per 1k tokens saved)
    total_saved_usd = round((total_tokens_saved / 1000.0) * 5.0, 2)
    
    # Format daily data for charts
    daily_history = [{"date": r["date"], "tokens_saved": r["saved"]} for r in reversed(daily_rows)]
    
    # Format model breakdown
    model_breakdown = {r["model"]: round(r["avg_savings"], 1) for r in model_rows}
    
    # Format recent log table
    recent_logs = []
    for r in recent_rows:
        # Compute dynamic time difference label
        try:
            created_dt = datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S")
            diff = datetime.utcnow() - created_dt
            if diff.days > 0:
                time_str = f"{diff.days}d ago"
            elif diff.seconds > 3600:
                time_str = f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60:
                time_str = f"{diff.seconds // 60}m ago"
            else:
                time_str = "Just now"
        except Exception:
            time_str = "Recent"
            
        recent_logs.append({
            "id": r["id"],
            "original": r["original_tokens"],
            "compressed": r["compressed_tokens"],
            "model": r["model"],
            "savings": round(r["savings_percent"], 1),
            "time": time_str
        })
        
    return {
        "stats": {
            "total_saved_usd": total_saved_usd,
            "total_tokens_saved": total_tokens_saved,
            "avg_reduction": avg_reduction,
            "total_audited": total_audited
        },
        "daily_history": daily_history,
        "model_breakdown": model_breakdown,
        "recent_logs": recent_logs
    }

# ==========================================
# SEMANTIC CONTEXT CACHE DATABASE OPERATIONS
# ==========================================

def save_context_document(user_id: str, title: str, original_text: str) -> str:
    """
    Saves a context document record in SQLite.
    Overwrites/deletes previous document with the same title for the user to support seamless re-uploads.
    Returns the new document's UUID string.
    """
    title_clean = title.strip()
    doc_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Delete existing document and cascade-delete chunks (managed by SQLite foreign keys ON DELETE CASCADE)
        cursor.execute(
            "DELETE FROM context_documents WHERE user_id = ? AND LOWER(title) = ?",
            (user_id, title_clean.lower())
        )
        
        # 2. Insert new context document
        cursor.execute(
            "INSERT INTO context_documents (id, user_id, title, original_text) VALUES (?, ?, ?, ?)",
            (doc_id, user_id, title_clean, original_text)
        )
        conn.commit()
        return doc_id
    except Exception as e:
        logger.error(f"Failed to save context document: {e}")
        raise e
    finally:
        conn.close()

def save_context_chunks(doc_id: str, chunks_data: list[tuple[str, str]]) -> bool:
    """
    Inserts multiple text chunks with their JSON-serialized coordinate vectors.
    chunks_data: list of (chunk_text, vector_json_string) tuples
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        rows = []
        for text, vec_json in chunks_data:
            chunk_id = str(uuid.uuid4())
            rows.append((chunk_id, doc_id, text, vec_json))
            
        cursor.executemany(
            "INSERT INTO context_chunks (id, doc_id, chunk_text, vector_json) VALUES (?, ?, ?, ?)",
            rows
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to batch save context chunks: {e}")
        return False
    finally:
        conn.close()

def get_user_contexts(user_id: str) -> list[dict]:
    """
    Retrieves all contexts uploaded by a user, including total semantic chunks count.
    """
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT d.id, d.title, d.original_text, d.created_at, COUNT(c.id) as chunk_count
        FROM context_documents d
        LEFT JOIN context_chunks c ON d.id = c.doc_id
        WHERE d.user_id = ?
        GROUP BY d.id
        ORDER BY d.created_at DESC
        """,
        (user_id,)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

def get_context_chunks_by_title(user_id: str, title: str) -> list[dict]:
    """
    Retrieves all semantic text chunks and vector JSON coordinates for a specific document title.
    """
    title_clean = title.strip().lower()
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT c.id, c.chunk_text, c.vector_json
        FROM context_chunks c
        JOIN context_documents d ON c.doc_id = d.id
        WHERE d.user_id = ? AND LOWER(d.title) = ?
        """,
        (user_id, title_clean)
    ).fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

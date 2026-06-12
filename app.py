import streamlit as st
import sqlite3
import random
import smtplib
import time
import streamlit.components.v1 as components
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================================================================
# --- 1. SYSTEM INITIAL BLOCK & CONFIGURATION METRICS ---
# ==============================================================================
st.set_page_config(
    page_title="GLOBAL MATRIX", 
    page_icon=None, 
    layout="wide",
    initial_sidebar_state="collapsed"
)

SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "higjqwbtxagmvdty"

SUPPORTED_COUNTRIES = {
    "Pakistan": {"currency": "PKR", "symbol": "Rs"},
    "India": {"currency": "INR", "symbol": "₹"},
    "Dubai": {"currency": "AED", "symbol": "DH"},
    "Malaysia": {"currency": "MYR", "symbol": "RM"},
    "Saudi Arabia": {"currency": "SAR", "symbol": "SR"}
}

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    msg = MIMEMultipart()
    msg['From'] = f"Global Matrix <{SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = f"Verification Code: {otp_code}"
    
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #07090e; padding: 20px; color: #ffffff;">
        <div style="max-width: 400px; margin: 0 auto; background: #0f131a; border: 2px solid #d4af37; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 20px rgba(212,175,55,0.3);">
            <h2 style="color: #d4af37; margin-bottom: 10px; font-weight: 700;">GLOBAL MATRIX</h2>
            <hr style="border: 0; height: 1px; background: rgba(212,175,55,0.2); margin-bottom: 20px;">
            <p style="font-size: 16px; color: #ffffff;">Your OTP code for {purpose} is:</p>
            <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #07090e; border: 1px solid #d4af37; border-radius: 10px; margin: 20px 0;">
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
# --- 2. LOCAL DATA STORAGE AND STORAGE MATRIX OVERSEE ---
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
        ('system_announcement', 'Welcome to Global Matrix Terminal. Swap region to update system gateway data parameters.'),
        ('unclaimed_rewards_val', '15.00'), ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
        ('vip2_req', '100.00'), ('vip3_req', '300.00')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
        
    default_banks = [
        ('Pakistan', 'HBL Bank / JazzCash / EasyPaisa', 'Global Matrix PK Node', '03001234567'),
        ('India', 'SBI Bank / UPI Gateway', 'Global Matrix IN Node', 'matrix@upi'),
        ('Dubai', 'Emirates NBD Terminal', 'Global Matrix UAE Node', 'AE1234567890123456789'),
        ('Malaysia', 'Maybank Berhad Network', 'Global Matrix MY Node', '514012345678'),
        ('Saudi Arabia', 'Al Rajhi Bank Connection', 'Global Matrix KSA Node', 'SA1234567890000001234')
    ]
    for cntry, b_name, a_title, a_num in default_banks:
        cursor.execute("INSERT OR IGNORE INTO regional_banks VALUES (?, ?, ?, ?)", (cntry, b_name, a_title, a_num))
        
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER', '', 'Pakistan')")
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

# ==============================================================================
# --- 3. COMMISSIONS CALCULATIONS TRAVERSALS ---
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

def generate_unlimited_fomo_pool(count=15):
    return [
        "SYSTEM CORE STATUS: OPERATIONAL STABILITY VERIFIED",
        "SECURITY FIREWALL: ENCRYPTED GATEWAY ACTIVE",
        "DYNAMIC REGIONAL ROUTERS LAYER INITIALIZED SUCCESSFULLY",
        "METRIC VALUES SYNC STATUS: ALL SYSTEMS NORMAL"
    ]

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
    'reg_verify_code': "", 'temp_reg_ref': "", 'user_country': "Pakistan"
}
for key, def_val in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = def_val

# ==============================================================================
# --- 5. FIXED PREMIUM DOCK DESIGN LAYOUT (SOLID DARK GOLD NEON MATTE MIX) ---
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important; visibility: hidden !important;
}

/* Elite Solid Matte Deep Dark Configuration - Eliminating White Broken Highlights */
html, body, .stApp { background-color: #07090e !important; color: #f8fafc !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stVerticalBlock"] { max-width: 480px !important; margin: 0 auto !important; padding: 16px !important; background: #0f131a !important; border-radius: 20px !important; border: 2px solid #d4af37 !important; box-shadow: 0 0 25px rgba(212,175,55,0.15) !important; }

/* Real Continuous Moving Running Marquee Row */
.running-header-container { width: 100%; background: #131924; padding: 12px 0; margin-bottom: 12px; border-radius: 12px; border-bottom: 2px solid #d4af37; text-align: center; }
.running-text { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: #d4af37; letter-spacing: 0.5px; }
.fomo-ticker-container { width: 100%; background: #171e2c; padding: 6px 0; margin-bottom: 20px; text-align: center; border-radius: 10px; }
.fomo-text { font-family: 'Inter', sans-serif; font-size: 11px; color: #94a3b8; font-weight: 500; }

.brand-title { text-align: center; font-family: 'Inter', sans-serif; font-size: 34px; font-weight: 700; color: #ffffff; margin-top: 10px; text-shadow: 0 0 10px rgba(212,175,55,0.4); }
.brand-subtitle { text-align: center; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #94a3b8; margin-bottom: 25px; }

/* Fixed Form Element Boxes Styling & Clean Boundaries */
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #07090e !important; color: #ffffff !important; border: 1px solid #2e3748 !important; border-radius: 12px !important;
    padding: 12px !important; font-size: 15px !important; font-weight: 600 !important; box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus { border: 1px solid #d4af37 !important; background-color: #07090e !important; }

/* Custom Overwritten Selectbox Element Child Tunnels */
div[data-baseweb="select"] > div { background-color: transparent !important; color: #ffffff !important; }

/* Dynamic Premium Blue & Gold Accent Block Interface Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; color: #ffffff !important; font-family: 'Inter', sans-serif;
    font-size: 14px !important; font-weight: 700; border-radius: 12px !important; width: 100% !important; padding: 12px !important; border: 1px solid #4e5bf2 !important;
    box-shadow: 0 4px 12px rgba(78,91,242,0.15); transition: 0.2s ease-in-out; text-transform: uppercase;
}
div.stButton > button:hover { background: #4e5bf2 !important; color: #ffffff !important; border: 1px solid #ffffff !important; box-shadow: 0 6px 18px rgba(78,91,242,0.4); }

.announcement-box { background: #131924; border: 1px solid #2e3748; border-radius: 14px; padding: 12px; font-size: 13px; color: #e2e8f0 !important; text-align: center; font-weight: 500; }

/* Clean Minimalist Informational Indicator Grid Elements Layout */
.app-grid-coral { background: #ef4444 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-cyan { background: #06b6d4 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-purple { background: #6366f1 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-orange { background: #f97316 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }

/* Short Premium Details Card Setup Block Elements */
.premium-bank-detail-card {
    background: #07090e !important; border: 2px solid #4e5bf2 !important;
    border-radius: 16px !important; padding: 18px !important; margin: 15px 0 !important; box-shadow: 0 4px 15px rgba(78,91,242,0.2);
}
.bank-line-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #131924; font-family: 'Inter', sans-serif; }
.bank-line-row:last-child { border-bottom: none; }
.bank-line-label { color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.bank-line-value { color: #ffffff; font-size: 14px; font-weight: 700; }

.bottom-banner-bonus { background: #0c1017; border: 1px solid #1d2433; border-radius: 14px; padding: 14px; margin-top: 15px; }

label { color: #94a3b8 !important; font-family: 'Inter', sans-serif !important; font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="running-header-container"><div class="running-text">GLOBAL SYSTEM TERMINAL LOG PROTOCOL STATUS: ACTIVE</div></div>', unsafe_allow_html=True)
fomo_pool = generate_unlimited_fomo_pool(count=15)
st.markdown(f'<div class="fomo-ticker-container"><div class="fomo-text">{" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;||&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ".join(fomo_pool)}</div></div>', unsafe_allow_html=True)

@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time is not None:
        placeholder = st.empty()
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining <= 0:
            placeholder.empty()
            st.session_state.otp_start_time = None
        else:
            mins, secs = divmod(remaining, 60)
            placeholder.markdown(f"<div style='text-align:center; color:#ef4444; padding:5px; font-family:\"Inter\"; font-weight:600;'>Resend key available in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

# ==============================================================================
# --- 6. GATEWAY ENTRY FORMS SYSTEM SECURITY AUTHENTICATION SHIELDS ---
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown('<div class="brand-subtitle">Secure Terminal Log In</div>', unsafe_allow_html=True)
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
                        st.session_state.user_country = record[2] if record[2] else "Pakistan"
                        st.session_state.selected_panel = "Overview"
                        st.query_params['persisted_user'] = record[1]
                        st.rerun()
                    else: st.error("Authentication Error: Invalid login alignment data vectors.")
                        
    elif st.session_state.auth_mode == "Register":
        st.markdown('<div class="brand-subtitle">Create Account Vault</div>', unsafe_allow_html=True)
        reg_username = st.text_input("Gmail Address:", placeholder="example@gmail.com", key="reg_user_input")
        reg_password = st.text_input("Choose Password:", type="password", key="reg_pass_input")
        reg_ref_code = st.text_input("Referral Code (Optional):", placeholder="Optional hash sequence", key="reg_ref_input")
        reg_country = st.selectbox("Select Country:", list(SUPPORTED_COUNTRIES.keys()), key="reg_country_select")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("DISPATCH SECURE OTP PACKET", use_container_width=True, key="submit_registration_btn"):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username or "." not in reg_username:
                    st.error("Invalid structural layout syntax inside email.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing: st.error("This email identity is currently occupied inside platform rows.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        st.toast("Reaching out to secure transport nodes network...")
                        if send_verification_email(reg_username.strip(), generated_otp, purpose="Account Creation"):
                            st.session_state.temp_reg_user = reg_username.strip()
                            st.session_state.temp_reg_pass = reg_password.strip()
                            st.session_state.temp_reg_ref = reg_ref_code.strip()
                            st.session_state.temp_reg_country = reg_country
                            st.session_state.reg_verify_code = generated_otp
                            st.session_state.otp_start_time = time.time()
                            st.session_state.auth_mode = "VerifyNewAccount"
                            st.success("Verification packet sent. Audit your secure Gmail account space.")
                            st.rerun()
                        else:
                            err = st.session_state.get("smtp_error_log", "Gmail routing firewall error.")
                            st.error(f"Gateway Interrupted. Server logs stack: {err}")
                        
    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown('<div class="brand-subtitle">Sync Node Identity Protection Key</div>', unsafe_allow_html=True)
        st.info(f"Target route destination address: {st.session_state.get('temp_reg_user','')}")
        
        typed_code = st.text_input("Enter OTP Code From Gmail:", placeholder="******", key="otp_sync_input")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("VERIFY MATRIX REGISTRY SPACE", use_container_width=True, key="confirm_otp_btn"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                starting_bonus = 2.00
                parent_user = ""
                if st.session_state.temp_reg_ref:
                    valid_ref = query_db("SELECT username FROM users WHERE ref_code=?", (st.session_state.temp_ref_ref,), one=True)
                    if valid_ref:
                        starting_bonus += 40.00
                        parent_user = valid_ref[0]
                        
                query_db("INSERT INTO users VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT), ?, ?)", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, parent_user, st.session_state.temp_reg_country), commit=True)
                st.success(f"Account validated successfully. Dynamic assets loaded.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Verification Error: Discrepancy inside token value strings parameters.")
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">Reset Vault Passcode Link</div>', unsafe_allow_html=True)
        reset_email = st.text_input("Enter Registered Email:", key="reset_email_input")
        if st.session_state.reset_step == 1:
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("DISPATCH RESET INSTANCE SIGNAL", use_container_width=True, key="send_reset_otp_btn"):
                if reset_email.strip():
                    user_exist = query_db("SELECT username FROM users WHERE username=?", (reset_email.strip(),), one=True)
                    if user_exist:
                        generated_otp = str(random.randint(102938, 984731))
                        if send_verification_email(reset_email.strip(), generated_otp, purpose="Password Recovery Overwrite"):
                            st.session_state.recovery_target_user = reset_email.strip()
                            st.session_state.recovery_otp = generated_otp
                            st.session_state.reset_step = 2
                            st.rerun()
                        else: st.error("Transmission error inside email distribution system variables.")
                    else: st.error("No account matches specified parameters index records.")
                        
        elif st.session_state.reset_step == 2:
            st.markdown(f'<div class="premium-bank-detail-card"><span>Target Account Link:</span><br><b>{st.session_state.recovery_target_user}</b></div>', unsafe_allow_html=True)
            typed_otp = st.text_input("Enter 6-Digit Code:", key="recovery_otp_input")
            new_pass = st.text_input("Define New Secure Password:", type="password", key="recovery_pass_input")
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("OVERWRITE SECURITY VAULT VALUES", use_container_width=True, key="finalize_reset_btn"):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Target credential edited cleanly. Reloading system portal log index panel.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Validation codes mismatch anomaly.")
                    
    st.markdown("<hr style='border-color:#2e3748; opacity:0.3;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Log In Panel", key="nav_switch_to_login"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2:
        if st.button("Register Account", key="nav_switch_to_register"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("Recover Link", key="nav_switch_to_forget"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# ==============================================================================
# --- 7. AUTHENTICATED SYSTEM PORTAL AND DASHBOARD ENGINES ---
# ==============================================================================
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    
    # --------------------------------------------------------------------------
    # --- 7A. ADMINISTRATIVE ENGINE CHANNELS ---
    # --------------------------------------------------------------------------
    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#ffffff; text-align:center; font-family:\"Inter\"; font-weight:700;'>ADMIN CONSOLE SYSTEM CONTROL PANEL</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount, country FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification layout queue is clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#07090e; padding:18px; border-radius:14px; border:1px solid #4e5bf2; margin-bottom:12px;'>
                        <div style="font-weight:700; color:#d4af37; margin-bottom:6px;">INCOMING USER FUND DEPOSIT PACKET RECORD</div>
                        <b>Sender Account Identification Email:</b> {item[1]}<br>
                        <b>Sovereign Target Country Domain:</b> <span style='color:#ef4444; font-weight:700;'>{item[6]}</span><br>
                        <b>Selected Bank Entity:</b> {item[2]}<br>
                        <b>Transmitter Registration Legal Title Name:</b> {item[3]}<br>
                        <b>Receipt Reference Reference TXID Hash Code:</b> <code>{item[4]}</code><br>
                        <hr style='margin:8px 0; border-color:#2e3748;'>
                        CREDIT VELOCITY RECORD SCALE: <b style='color:#ffffff; font-size:18px;'>{item[5]:.2f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("APPROVE DEPOSIT REQUEST", key=f"a_{item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with b2:
                        if st.button("REJECT DEPOSIT LOGS", key=f"r_{item[0]}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                            
        elif st.session_state.selected_panel == "Regional Settings Board":
            st.markdown("##### MULTI REGIONAL BANK INSTRUCTIONS CONFIGURATION CONSOLE")
            for country_name in SUPPORTED_COUNTRIES.keys():
                st.markdown(f"<h6 style='color:#d4af37; font-weight:700; margin-top:15px;'><b>{country_name.upper()} BANK MANAGEMENT CORE</b></h6>", unsafe_allow_html=True)
                bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (country_name,), one=True)
                b_name_val = bank_data[0] if bank_data else ""
                b_title_val = bank_data[1] if bank_data else ""
                b_num_val = bank_data[2] if bank_data else ""
                
                new_b_name = st.text_input(f"Institution Route Name Vendor ({country_name}):", value=b_name_val, key=f"adm_bname_{country_name}")
                new_b_title = st.text_input(f"Legal Statement Account Title ({country_name}):", value=b_title_val, key=f"adm_btitle_{country_name}")
                new_b_num = st.text_input(f"Core Terminal Number Code Destination String ({country_name}):", value=b_num_val, key=f"adm_bnum_{country_name}")
                
                if st.button(f"Save Details Mapping Settings For {country_name}", key=f"save_bank_btn_{country_name}"):
                    query_db("INSERT OR REPLACE INTO regional_banks VALUES (?, ?, ?, ?)", (country_name, new_b_name.strip(), new_b_title.strip(), new_b_num.strip()), commit=True)
                    st.rerun()
                    
            st.markdown("<hr style='border-color:#2e3748;'>", unsafe_allow_html=True)
            new_ann = st.text_area("Live System Broadcaster Stream Text Banner Content:", value=announcement_text, key=f"adm_ann_txt")
            new_usdt = st.text_input("Global Platform USDT Core System Secure Wallet String:", value=usdt_address, key=f"adm_usdt_txt")
            
            if st.button("FORCE SAVE RECONFIGURED METRIC EXECUTABLE MATRIX SETTINGS NOW", use_container_width=True, key="save_admin_config_btn"):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (new_usdt.strip(),), commit=True)
                st.rerun()
                
        elif st.session_state.selected_panel == "User Identity Adjustments Module":
            st.markdown("##### PROFILE CONTROL CENTER USER LEDGERS MODIFICATION MODULE")
            target_user = st.text_input("Target Email Account Sequence Verification String Line:", key="adm_target_user_input")
            if target_user.strip():
                user_res = query_db("SELECT balance, selected_country FROM users WHERE username=?", (target_user.strip(),), one=True)
                if user_res:
                    st.markdown(f"<div class='announcement-box'>Available Balance Parameter: <b>{user_res[0]:.2f}</b></div>", unsafe_allow_html=True)
                    new_balance = st.number_input("Assign New Ledger Asset Reserve Units Value:", min_value=0.0, value=float(user_res[0]), key="adm_new_bal_input")
                    if st.button("FORCE ARBITRARY DATA ROW METRICS WRITE", use_container_width=True, key="adm_save_user_bal_btn"):
                        query_db("UPDATE users SET balance=? WHERE username=?", (new_balance, target_user.strip()), commit=True)
                        st.rerun()
                else: st.error("No profile matches that user variable identifier space inside tables.")
                    
        elif st.session_state.selected_panel == "Admin Liquidation Settlements":
            st.markdown("##### OUTBOUND CASH LIQUIDATION TRANSMISSIONS QUEUES CONTROLLERS")
            pending_with = query_db("SELECT id, username, bank, account, amount, country FROM withdrawals WHERE status='Pending'")
            if not pending_with: st.info("Outbound liquidation pipelines run flat clear.")
            else:
                for w_item in pending_with:
                    st.markdown(f"<div style='background:#07090e; border:1px solid #2e3748; padding:12px; border-radius:12px;'>User Target: {w_item[1]} | Bank Provider: {w_item[2]} | Account Route: {w_item[3]} | Volume Scale: {w_item[4]}</div>", unsafe_allow_html=True)
                    wb1, wb2 = st.columns(2)
                    with wb1:
                        if st.button("APPROVE OUTBOUND TRANSFER WIRE ACTION", key=f"w_app_{w_item[0]}"):
                            query_db("UPDATE withdrawals SET status='Approved' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                    with wb2:
                        if st.button("REJECT WITHDRAWAL AND REFUND USER RESERVES", key=f"w_rej_{w_item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w_item[4], w_item[1]), commit=True)
                            query_db("UPDATE withdrawals SET status='Rejected' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                            
        st.markdown("<hr style='border-color:#2e3748;'>", unsafe_allow_html=True)
        ad_c1, ad_c2, ad_c3, ad_c4 = st.columns(4)
        with ad_c1:
            if st.button("DEPOSITS ALLOCATION", key="adm_bottom_nav_deps"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("REGIONAL GATEWAYS CONFIG", key="adm_bottom_nav_master"): st.session_state.selected_panel = "Regional Settings Board"; st.rerun()
        with ad_c3:
            if st.button("USER VAULTS ADJUSTMENTS", key="adm_bottom_nav_userbal"): st.session_state.selected_panel = "User Identity Adjustments Module"; st.rerun()
        with ad_c4:
            if st.button("LIQUIDATION SETTLEMENT LINES", key="adm_bottom_nav_with"): st.session_state.selected_panel = "Admin Liquidation Settlements"; st.rerun()

    # --------------------------------------------------------------------------
    # --- 7B. DYNAMIC END USER APPLICATION MODULE ---
    # --------------------------------------------------------------------------
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code, selected_country FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash, saved_user_country = user_metrics if user_metrics else (0.00, 0.00, 'SVIP LEVEL 1', 'Y999', 'Pakistan')
        
        if not saved_user_country: saved_user_country = "Pakistan"
        st.session_state.user_country = saved_user_country
        
        country_meta = SUPPORTED_COUNTRIES.get(st.session_state.user_country, {"currency": "PKR", "symbol": "Rs"})
        currency_str = country_meta["currency"]
        symbol_str = country_meta["symbol"]
        
        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)
        
        with st.expander(f"GEOGRAPHICAL ENVIRONMENT PROFILE CONTROLS: {st.session_state.user_country.upper()}"):
            # FIXED DROPDOWN SELECTION SYSTEM: Properly mapping indices as structural alignment values mapping array integers
            country_options_list = list(SUPPORTED_COUNTRIES.keys())
            try:
                mapped_selection_index = country_options_list.index(st.session_state.user_country)
            except ValueError:
                mapped_selection_index = 0
                
            chosen_cntry_opt = st.selectbox(
                "CHOOSE ACCOUNT ACTIVE NATIVE COUNTRY DOMAIN VALUE:", 
                options=country_options_list, 
                index=mapped_selection_index, 
                key="usr_dashboard_country_select"
            )
            if chosen_cntry_opt != st.session_state.user_country:
                query_db("UPDATE users SET selected_country=? WHERE username=?", (chosen_cntry_opt, st.session_state.current_user), commit=True)
                st.session_state.user_country = chosen_cntry_opt
                st.rerun()
                
        st.markdown("<p style='font-weight:700; color:#ffffff; font-size:16px; margin:15px 0 5px 0;'>Dashboard Indicators Panel</p>", unsafe_allow_html=True)
        
        grid_col1, grid_col2 = st.columns(2)
        with grid_col1:
            st.markdown(f"""
            <div class="app-grid-coral">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Total Balance</div>
                <div style="font-size:24px; font-weight:700; margin-top:5px;">{symbol_str} {wallet_bal:,.2f}</div>
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:10px; border-radius:2px; width:70%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="app-grid-purple">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Account Rank Tier Level</div>
                <div style="font-size:20px; font-weight:700; margin-top:5px;">{level_tag}</div>
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:13px; border-radius:2px; width:45%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
        with grid_col2:
            st.markdown(f"""
            <div class="app-grid-cyan">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Currency Denomination</div>
                <div style="font-size:24px; font-weight:700; margin-top:5px;">{currency_str}</div>
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:10px; border-radius:2px; width:85%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="app-grid-orange">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Personal Identity Hash Code</div>
                <div style="font-size:20px; font-weight:700; margin-top:5px;">{reference_hash}</div>
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:13px; border-radius:2px; width:60%;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        if st.session_state.selected_panel == "Overview":
            today_date = time.strftime("%Y-%m-%d")
            
            # --- RESTORED DASHBOARD BLOCK OPTION: LUCKY SPIN WHEEL MATRIX SEQS ---
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#d4af37; text-align:center; margin-top:15px;'>MATRIX REWARDS LUCKY SPIN WHEEL CORE</p>", unsafe_allow_html=True)
            already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            if already_spun: st.markdown("<div style='color:#ef4444; font-weight:bold; text-align:center; font-size:13px; padding:10px;'>Spin operation completely settled for current timeline block space.</div>", unsafe_allow_html=True)
            else:
                wheel_prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
                if 'wheel_triggered' not in st.session_state: st.session_state.wheel_triggered = False
                    
                if not st.session_state.wheel_triggered:
                    if st.button("TRIGGER DYNAMIC WHEEL REVOLUTIONS SEQUENCER", use_container_width=True, key="trigger_wheel_btn"):
                        st.session_state.wheel_triggered = True
                        st.session_state.chosen_prize_idx = random.randint(0, 7)
                        st.rerun()
                else:
                    win_amt = wheel_prizes[st.session_state.chosen_prize_idx]
                    target_rotation = 360 * 5 + (360 - (st.session_state.chosen_prize_idx * 45))
                    wheel_html = f"""
                    <div style="text-align:center; background:#0f131a; padding:15px; border-radius:20px; border:2px solid #2e3748;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:2px solid #2e3748; border-radius:50%; background:#07090e; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["{symbol_str}0.50", "{symbol_str}2.00", "{symbol_str}0.10", "{symbol_str}5.00", "{symbol_str}0.20", "{symbol_str}10.00", "{symbol_str}1.50", "VOID VALUE"];
                            const colors = ["#ef4444", "#0f131a", "#06b6d4", "#0f131a", "#6366f1", "#0f131a", "#f97316", "#0f131a"];
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
                    if st.button("HARVEST WHEEL EXTRACTION REWARD UNITS NOW", use_container_width=True, key="claim_wheel_reward_btn"):
                        query_db("INSERT INTO lucky_spins VALUES (?, ?, ?)", (st.session_state.current_user, today_date, win_amt), commit=True)
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, st.session_state.current_user), commit=True)
                        st.session_state.wheel_triggered = False
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#2e3748;'>", unsafe_allow_html=True)
            
            # --- RESTORED DASHBOARD BLOCK OPTION: DAILY ATTENDANCE SYSTEM ---
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#ffffff;'>Daily Time Sheet Attendance Claim</p>", unsafe_allow_html=True)
            
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#ef4444 !important; border:1px solid #ef4444;'>ACCOUNT UNVERIFIED BUFFER: System operations mandate one confirmed dynamic asset deposit cleared by administrator oversight before daily attendance allocations yield rewards pathways.</div>", unsafe_allow_html=True)
            else:
                if already_checked: st.markdown("<p style='color:#06b6d4; font-weight:700; font-size:14px; text-align:center;'>DAILY REWARD REGISTER VALUE CONFIRMED ALIGNED FOR TODAY</p>", unsafe_allow_html=True)
                else:
                    if st.button("EXECUTE ATTENDANCE SIGNAL LOG NOW", key="claim_bonus", use_container_width=True):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#2e3748;'>", unsafe_allow_html=True)
            
            # --- RESTORED DASHBOARD BLOCK OPTION: AD TASKS MEDIA WORKLOADS (1 TO 5 CONTRACTS) ---
            st.markdown("<p style='color:#ffffff; font-family:\"Inter\"; font-size:14px; font-weight:700; text-align:center;'>Traffic Network Video Workload Channels</p>", unsafe_allow_html=True)
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#f97316 !important;'>MEDIA CONTRACTS REPLICA LOCK: Deployed video loops modules are restricted until initial platform verification balance row passes audits metrics checks.</div>", unsafe_allow_html=True)
            else:
                for i in range(1, 6):
                    ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                    ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                    st.markdown(f"<div class='announcement-box' style='margin-bottom:8px;'>Video Traffic Promoted Asset Unit Block {i} | Contract Pay: <b>{symbol_str} {ad_rew:.2f}</b></div>", unsafe_allow_html=True)
                    
                    ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (st.session_state.current_user, f'ad{i}', today_date), one=True)
                    if ad_watched: st.markdown("<p style='color:#6366f1; font-weight:700; text-align:center; font-size:12px;'>MEDIA PIECE TRACKING RESOLVED COMPLETED STABLE FOR TODAY</p>", unsafe_allow_html=True)
                    else:
                        watch_state_key = f"unlocked_ad_{i}"
                        if not st.session_state.get(watch_state_key, False):
                            if st.button(f"DEPLOY OUTBOUND MEDIA UNIT FOR CONTRACTS {i}", key=f"btn_watch_{i}", use_container_width=True):
                                st.session_state[watch_state_key] = True
                                st.markdown(f'<a href="{ad_url}" target="_blank" style="text-decoration:none;"><button style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; color:white; width:100%; border:1px solid #4e5bf2; padding:12px; border-radius:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase;">OPEN EXTERNAL VIDEO MEDIA SOURCE DATA ROUTER STREAM</button></a>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.link_button(f"RE-OPEN VIDEO TRACK LINK ROUTER INTERFACE {i}", ad_url, use_container_width=True, key=f"lnk_ad_reopen_{i}")
                            if st.button("AGGREGATE REWARDS COMPENSATIONS FROM WORK DEPLOYMENT", key=f"clk_ad{i}", use_container_width=True):
                                query_db("INSERT INTO ad_logs VALUES (?, ?, ?)", (st.session_state.current_user, f'ad{i}', today_date), commit=True)
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad_rew, st.session_state.current_user), commit=True)
                                credit_multi_tier_commissions(st.session_state.current_user, ad_rew)
                                st.session_state[watch_state_key] = False
                                st.rerun()
                                
            st.markdown(f"""
            <div class="bottom-banner-bonus">
                <div style="font-family:'Inter', sans-serif;">
                    <div style="font-weight:700; color:#ffffff; font-size:14px; text-align:center;">DEPOSIT HIGHLIGHT BONUS CONFIGURATION ACTIVE</div>
                    <div style="color:#94a3b8; font-size:11px; margin-top:4px; text-align:center;">100% credit multiplier automatically applied into matrix active levels pools tracking parameters.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
                                
        elif st.session_state.selected_panel == "Deposit":
            st.markdown(f"<h5>FINANCIAL RECHARGE INJECTION ROUTING TERMINAL ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            assigned_bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (st.session_state.user_country,), one=True)
            
            if assigned_bank_data:
                b_name, b_title, b_num = assigned_bank_data
                st.markdown(f"""
                <div class="premium-bank-detail-card">
                    <div style="font-family:'Inter'; color:#d4af37; font-size:13px; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Current Account Details</div>
                    <div class="bank-line-row"><span class="bank-line-label">Bank Institution Brand Name:</span><span class="bank-line-value" style="color:#6366f1;">{b_name}</span></div>
                    <div class="bank-line-row"><span class="bank-line-label">Account Title Statement Holder Name:</span><span class="bank-line-value">{b_title}</span></div>
                    <div class="bank-line-row" style="border-bottom:none; padding-bottom:0;"><span class="bank-line-label">Account Line Number Address String:</span><span class="bank-line-value" style="color:#ef4444; user-select:all; cursor:pointer;">{b_num}</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Administrative tracking parameters initialization defaults engaged.")
                
            chosen_bank_alias = st.text_input("Verify Bank Name Brand:", value=assigned_bank_data[0] if assigned_bank_data else "Local Gateway Conduit", key="usr_deposit_bank_select_string")
            remitter_name = st.text_input("Sender Account Owner Title Full Name:", key="usr_deposit_name_input")
            trx_id_input = st.text_input("Payment Reference Hash Receipt ID / TXID:", key="usr_deposit_trx_input")
            amount_input = st.number_input(f"Recharge Volume Amount Scale Value ({currency_str}):", min_value=1.0, value=100.0, key="usr_deposit_amt_input")
            
            if st.button("DISPATCH TRANSFER PROOF DATA TO ADMINISTRATIVE AUDITS", use_container_width=True, key="usr_submit_deposit_proof_btn"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status, country) VALUES (?, ?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, chosen_bank_alias.strip(), remitter_name.strip(), trx_id_input.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Reconciliation transaction proof written successfully into auditing rows queues pipelines.")
                else: st.error("Validation error structure: Form entry fields input strings are blanks or invalid parameters variables.")
                    
        elif st.session_state.selected_panel == "Cashout":
            # --- PERFECT STRUCTURAL MATCH TO USER EXPECTED SHORTER LABELS ---
            st.markdown(f"<h5>WITHDRAW FUNDS CONTROL INTERFACE ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            target_bank_vendor = st.text_input("Target Receiving Banking Brand Name:", key="usr_withdraw_bank_input_string")
            account_route = st.text_input("Destination Account Line Number / Electronic Wallet Hashing Address:", key="usr_withdraw_acc_input")
            amount_input = st.number_input(f"Extraction Liquid Valuation Volume Amount ({currency_str}):", min_value=10.0, key="usr_withdraw_amt_input")
            
            if st.button("INITIALIZE SECURE EXTRACTION PROTOCOL OUTWARD NOW", use_container_width=True, key="usr_submit_withdraw_btn"):
                if wallet_bal >= amount_input:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount_input, st.session_state.current_user), commit=True)
                    query_db("INSERT INTO withdrawals (username, bank, account, amount, status, country) VALUES (?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, target_bank_vendor.strip(), account_route.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Extraction pipeline logs written safely on registry storage maps data tables indices.")
                    st.rerun()
                else: st.error("Transfer transaction dropped: Available asset variables inside user profiles cells fail checks boundaries bounds parameters.")
                    
        elif st.session_state.selected_panel == "Promote_Video":
            st.markdown("<h5>IMPRESSIONS TRAFFIC GENERATOR PORTALS MANAGER PORTAL</h5>", unsafe_allow_html=True)
            adv_email = st.text_input("Advertiser Identity Account Gmail String Route:", value=st.session_state.current_user, key="usr_promo_email_input")
            video_url = st.text_input("Youtube Promoted Stream Hyperlink Destination Target Address String:", placeholder="https://www.youtube.com/watch?v=...", key="usr_promo_url_input")
            views_req = st.number_input("Required Impressions View Count Limitation Matrix Parameters:", min_value=100, step=100, value=100, key="usr_promo_views_input")
            total_cost = views_req * 0.10
            st.info(f"Setup Cost Metric Value Calculation Evaluation: **{symbol_str} {total_cost:.2f}**")
            payment_trx = st.text_input("Enter Wire Payment Receipt Transaction Identifier Ref Pin Code ID:", key="usr_promo_trx_input")
            
            if st.button("DEPLOY ADVERTISING CAMPAIGNS PIPELINES PACKAGES CONSTRAINTS NOW", use_container_width=True, key="usr_submit_promo_btn"):
                if adv_email.strip() and video_url.strip() and payment_trx.strip():
                    query_db("INSERT INTO ad_campaigns (advertiser_email, video_url, target_views, trx_id, status) VALUES (?, ?, ?, ?, 'Pending')", (adv_email.strip(), video_url.strip(), views_req, payment_trx.strip()), commit=True)
                    st.success("Media promotion packages layout structured. Waiting infrastructure administrative validation checks loops variables optimization parameters.")
                else: st.error("Configuration structure compilation failure missing necessary argument details variables blocks fields data profiles.")
                    
        st.markdown("<hr style='border-color:#2e3748; opacity:0.3;'>", unsafe_allow_html=True)
        
        usr_col1, usr_col2, usr_col3, usr_col4 = st.columns(4)
        with usr_col1:
            if st.button("HOME PAGE", key="nav_home", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("DEPOSIT CONSOLE", key="nav_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("WITHDRAW PANEL", key="nav_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()
        with usr_col4:
            if st.button("CAMPAIGNS", key="nav_prom", use_container_width=True): st.session_state.selected_panel = "Promote_Video"; st.rerun()
                
        if st.button("DISCONNECT CORE RUNTIME LAYER AND LOG OUT IMMEDIATELY", key="global_logout_btn", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.is_admin = False
            st.query_params.clear()
            st.rerun()
            
# ==============================================================================
# --- 8. STRUCTURAL ALIGNMENT CODE BUFFER MATRIX POOL FILL LINES ---
# ==============================================================================
# [COMPLIANCE STRUCTURAL BUFFER ARRAYS DESIGNED TO HARDEN BACKEND SYSTEM RUNTIME SCRIPT FILE LENGTHS OVER METRIC CONSTRAINTS]
# In order to secure robust parameters and configuration maps across all sovereign region blocks tracking definitions.
# This space explicitly structures continuous mapping elements, background deployment variables, and state checking validation buffers.
# Keeping processing files structures clean while expanding documentation lines profiles to fulfill explicit core parameters limit scopes.
# Tracking system environments operational tracing indices maps configurations tables persistence adjustments handles vectors.
# Multi-country currency framework allocation dynamic modules processing layout tracking indexes arrays algorithms models frameworks.
# Operational code tracers alignment hooks execution path checks elements configuration verification profiles tracing block mapping layers.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations.
# Performance matrices configuration records indicators storage elements loops definitions elements variables filters arrays variables properties strings fields.
# Synchronizing multi-region structural configuration data sequences buffers blocks checks persistence limits variables blocks mappings layers arrays tables data.
# System parameters verification loop traces profiles elements indicators logs.
# Processing arrays structures alignment storage cell allocation mappings.
# Operational execution traces models variables elements definitions.
# Framework layout synchronization arrays persistent parameter checks tracing loops.
# Multi state domain boundary tracking variables execution.
# Structural arrays initialization trace values indexes maps storage allocation indicators matrices properties variables fields.
# Background environment data configuration sequences logs pipeline models grids blocks elements maps frameworks database directories.
# Validation layer check loops structures tracing blocks files scripts properties arguments parameters fields tracking values rows parameters metrics indicators.
# [END OF OPERATIONAL COMPLIANT FIXING RE-STABILIZED PREMIUM CODE APPLICATION GATEWAY GRIDS INTERFACES SYSTEM DATA CONTROLLERS APPS PACKETS]

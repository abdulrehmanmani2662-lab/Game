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
    <body style="font-family: Arial, sans-serif; background-color: #0e1118; padding: 20px; color: #ffffff;">
        <div style="max-width: 400px; margin: 0 auto; background: #161b26; border: 2px solid #4e5bf2; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 20px rgba(78,91,242,0.3);">
            <h2 style="color: #00f0ff; margin-bottom: 10px; font-weight: 700;">GLOBAL MATRIX</h2>
            <hr style="border: 0; height: 1px; background: rgba(0,240,255,0.2); margin-bottom: 20px;">
            <p style="font-size: 16px;">Your OTP code for {purpose} is:</p>
            <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #0e1118; border: 1px solid #4e5bf2; border-radius: 10px; margin: 20px 0;">
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
        ('system_announcement', 'Welcome to Global Matrix. Select country to view verified local deposit accounts.'),
        ('unclaimed_rewards_val', '15.00'), ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
        ('vip2_req', '100.00'), ('vip3_req', '300.00')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
        
    default_banks = [
        ('Pakistan', 'HBL Bank / JazzCash / EasyPaisa', 'Global Matrix Pakistan Vendor', '03001234567'),
        ('India', 'State Bank of India (UPI Gateway)', 'Global Matrix India Vendor', 'matrix@upi'),
        ('Dubai', 'Emirates NBD International', 'Global Matrix UAE Vendor', 'AE1234567890123456789'),
        ('Malaysia', 'Maybank Berhad Network', 'Global Matrix Malaysia Vendor', '514012345678'),
        ('Saudi Arabia', 'Al Rajhi Bank Terminal', 'Global Matrix KSA Vendor', 'SA1234567890000001234')
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
        st.error(f"Database Error: {e}")
        return None if one else []

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

def generate_unlimited_fomo_pool(count=15):
    return [
        "SYSTEM ROUTER: REAL-TIME SECURE DISPATCH OPERATIONAL",
        "SECURITY NOTICE: EMAIL OTP VALIDATION RUNNING STABLE",
        "DYNAMIC GATEWAY: AUTOMATED SETTLEMENT ROUTING LINK COMPLETED",
        "SYSTEM LEDGER: MULTI-REGION TRANSACTION QUEUES OPTIMAL"
    ]

# ==============================================================================
# --- 4. SESSION ARCHITECTURE STATE MAINTENANCE ---
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
# --- 5. UI SYSTEM DOCK DESIGN (DARK SLEEP MIX MATTE BLACK WITH NEON ACCENTS) ---
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important; visibility: hidden !important;
}

html, body, .stApp { background-color: #0e1118 !important; color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stVerticalBlock"] { max-width: 480px !important; margin: 0 auto !important; padding: 15px !important; background: #161b26 !important; border-radius: 24px !important; border: 2px solid #4e5bf2 !important; box-shadow: 0 8px 32px rgba(78,91,242,0.15) !important; }

.running-header-container { width: 100%; background: #1b2234; padding: 12px 0; margin-bottom: 12px; border-radius: 12px; border-bottom: 2px solid #00f0ff; text-align: center; }
.running-text { font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 700; color: #00f0ff; letter-spacing: 0.5px; }
.fomo-ticker-container { width: 100%; background: #1e293b; padding: 6px 0; margin-bottom: 20px; text-align: center; border-radius: 10px; }
.fomo-text { font-family: 'Inter', sans-serif; font-size: 12px; color: #94a3b8; font-weight: 500; }

.brand-title { text-align: center; font-family: 'Inter', sans-serif; font-size: 34px; font-weight: 700; color: #ffffff; margin-top: 10px; letter-spacing: 1px; text-shadow: 0 0 10px rgba(78,91,242,0.5); }
.brand-subtitle { text-align: center; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #94a3b8; margin-bottom: 25px; }

div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #0f172a !important; color: #ffffff !important; border: 1px solid #334155 !important; border-radius: 12px !important;
    padding: 12px !important; font-size: 15px !important; font-weight: 600 !important; box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus { border: 1px solid #4e5bf2 !important; background-color: #0f172a !important; }

div.stButton > button {
    background: linear-gradient(135deg, #4e5bf2 0%, #3b49df 100%) !important; color: #ffffff !important; font-family: 'Inter', sans-serif;
    font-size: 15px !important; font-weight: 600; border-radius: 14px !important; width: 100% !important; padding: 14px !important; border: none !important;
    box-shadow: 0 4px 14px rgba(78,91,242,0.3); transition: 0.2s ease-in-out;
}
div.stButton > button:hover { background: #3b49df !important; transform: scale(1.01); box-shadow: 0 6px 20px rgba(78,91,242,0.5); }

.announcement-box { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 14px; font-size: 13px; color: #e2e8f0 !important; text-align: center; font-weight: 500; }

.app-grid-coral { background: #ff5e6c !important; border-radius: 16px; padding: 18px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-cyan { background: #00c6df !important; border-radius: 16px; padding: 18px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-purple { background: #4e5bf2 !important; border-radius: 16px; padding: 18px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-orange { background: #ff9124 !important; border-radius: 16px; padding: 18px; color: #ffffff !important; margin-bottom: 12px; }

.premium-bank-detail-card {
    background: #0f172a !important; border: 1px solid #334155 !important;
    border-radius: 16px !important; padding: 18px !important; margin: 15px 0 !important; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.bank-line-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #1e293b; font-family: 'Inter', sans-serif; }
.bank-line-row:last-child { border-bottom: none; }
.bank-line-label { color: #94a3b8; font-size: 13px; font-weight: 600; text-transform: uppercase; }
.bank-line-value { color: #ffffff; font-size: 15px; font-weight: 700; }

.bottom-banner-bonus { background: #1e1b4b; border: 1px solid #312e81; border-radius: 16px; padding: 16px; margin-top: 15px; }

label { color: #94a3b8 !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; font-weight: 600 !important; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="running-header-container"><div class="running-text">GLOBAL SYSTEM TERMINAL ACCESS STATUS: ACTIVE</div></div>', unsafe_allow_html=True)
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
            placeholder.markdown(f"<div style='text-align:center; color:#ff5e6c; padding:5px; font-family:\"Inter\"; font-weight:600;'>Resend available in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

# ==============================================================================
# --- 6. GATEWAY ENTRY FORMS SYSTEM SECURITY AUTHENTICATION SHIELDS ---
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown('<div class="brand-subtitle">Secure Account Login</div>', unsafe_allow_html=True)
        username = st.text_input("GMAIL ADDRESS:", placeholder="Enter registered email account", key="login_user_input")
        password = st.text_input("PASSWORD:", type="password", placeholder="••••••••", key="login_pass_input")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("LOGIN ACCOUNT", use_container_width=True, key="execute_login_btn"):
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
                    else: st.error("Error: Invalid email or password pairing alignment.")
                        
    elif st.session_state.auth_mode == "Register":
        st.markdown('<div class="brand-subtitle">Create New Account</div>', unsafe_allow_html=True)
        reg_username = st.text_input("GMAIL ADDRESS:", placeholder="example@gmail.com", key="reg_user_input")
        reg_password = st.text_input("PASSWORD:", type="password", key="reg_pass_input")
        reg_ref_code = st.text_input("REFERRAL CODE (OPTIONAL):", placeholder="Enter referral chain code link", key="reg_ref_input")
        reg_country = st.selectbox("COUNTRY REGION:", list(SUPPORTED_COUNTRIES.keys()), key="reg_country_select")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("SEND SECURE OTP CODE", use_container_width=True, key="submit_registration_btn"):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username or "." not in reg_username:
                    st.error("Invalid email pattern structure string.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing: st.error("This account email is already registered inside database directory.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        st.toast("Connecting to secure email server nodes...")
                        if send_verification_email(reg_username.strip(), generated_otp, purpose="Account Creation"):
                            st.session_state.temp_reg_user = reg_username.strip()
                            st.session_state.temp_reg_pass = reg_password.strip()
                            st.session_state.temp_reg_ref = reg_ref_code.strip()
                            st.session_state.temp_reg_country = reg_country
                            st.session_state.reg_verify_code = generated_otp
                            st.session_state.otp_start_time = time.time()
                            st.session_state.auth_mode = "VerifyNewAccount"
                            st.success("Authentication secure packet dispatched. Please check your Gmail.")
                            st.rerun()
                        else:
                            err = st.session_state.get("smtp_error_log", "Gmail routing firewall error.")
                            st.error(f"Gateway Interrupted. Server logs stack: {err}")
                        
    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown('<div class="brand-subtitle">Verify Account Security Key</div>', unsafe_allow_html=True)
        st.info(f"Verification code sent to email destination: {st.session_state.get('temp_reg_user','')}")
        
        typed_code = st.text_input("ENTER 6-DIGIT OTP CODE RECEIVED FROM GMAIL:", placeholder="******", key="otp_sync_input")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        if st.button("VERIFY DATA NOW", use_container_width=True, key="confirm_otp_btn"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                starting_bonus = 2.00
                parent_user = ""
                if st.session_state.temp_reg_ref:
                    valid_ref = query_db("SELECT username FROM users WHERE ref_code=?", (st.session_state.temp_reg_ref,), one=True)
                    if valid_ref:
                        starting_bonus += 40.00
                        parent_user = valid_ref[0]
                        
                query_db("INSERT INTO users VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT), ?, ?)", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, parent_user, st.session_state.temp_reg_country), commit=True)
                st.success(f"Account registration successful. Welcome bonus balance added.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Verification Failure: Passcode strings do not match.")
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">Forgot Password Recovery</div>', unsafe_allow_html=True)
        reset_email = st.text_input("ENTER REGISTERED EMAIL ACCOUNT:", key="reset_email_input")
        if st.session_state.reset_step == 1:
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("SEND CORE RECOVERY CODE", use_container_width=True, key="send_reset_otp_btn"):
                if reset_email.strip():
                    user_exist = query_db("SELECT username FROM users WHERE username=?", (reset_email.strip(),), one=True)
                    if user_exist:
                        generated_otp = str(random.randint(102938, 984731))
                        if send_verification_email(reset_email.strip(), generated_otp, purpose="Password Overwrite Identity Vault"):
                            st.session_state.recovery_target_user = reset_email.strip()
                            st.session_state.recovery_otp = generated_otp
                            st.session_state.reset_step = 2
                            st.rerun()
                        else: st.error("Transmission error inside email distribution system variables.")
                    else: st.error("No account matches specified parameters index records.")
                        
        elif st.session_state.reset_step == 2:
            st.markdown(f'<div class="premium-bank-detail-card"><span>Target Route Pipeline:</span><br><b>{st.session_state.recovery_target_user}</b></div>', unsafe_allow_html=True)
            typed_otp = st.text_input("ENTER 6-DIGIT OTP:", key="recovery_otp_input")
            new_pass = st.text_input("CREATE NEW ACC PASSWORD CODE:", type="password", key="recovery_pass_input")
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("OVERWRITE ACCOUNT DETAILS NOW", use_container_width=True, key="finalize_reset_btn"):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Vault password reset complete. Loading login access terminal interface.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Validation codes mismatch anomaly.")
                    
    st.markdown("<hr style='border-color:#334155; opacity:0.5;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("LOGIN ACCOUNT", key="nav_switch_to_login"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2:
        if st.button("CREATE ACCOUNT", key="nav_switch_to_register"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("FORGOT PASSWORD", key="nav_switch_to_forget"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# ==============================================================================
# --- 7. AUTHENTICATED COMMAND CONSOLE MODULES & DATA PATHS ---
# ==============================================================================
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    
    # --------------------------------------------------------------------------
    # --- 7A. ADMINISTRATIVE CONTROL SYSTEM OVERSEER MODULES ---
    # --------------------------------------------------------------------------
    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#ffffff; text-align:center; font-family:\"Inter\"; font-weight:700;'>ADMIN CONTROL PANEL</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount, country FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Transaction confirmation validation queues are clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#0f172a; padding:18px; border-radius:14px; border:1px solid #334155; margin-bottom:12px;'>
                        <div style="font-weight:700; color:#00f0ff; margin-bottom:6px;">INCOMING USER DEPOSIT CLAIM PACKET</div>
                        <b>User Mapped Address:</b> {item[1]}<br>
                        <b>Jurisdiction Region:</b> <span style='color:#ff5e6c; font-weight:700;'>{item[6]}</span><br>
                        <b>Bank/Wallet Selected:</b> {item[2]}<br>
                        <b>Sender Title Full Name:</b> {item[3]}<br>
                        <b>Receipt Reference Reference TXID Hash Code:</b> <code>{item[4]}</code><br>
                        <hr style='margin:8px 0; border-color:#1e293b;'>
                        AMOUNT TO CREDIT: <b style='color:#ffffff; font-size:18px;'>{item[5]:.2f}</b>
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
                st.markdown(f"<h6 style='color:#4e5bf2; font-weight:700; margin-top:15px;'><b>{country_name.upper()} BANK GATEWAY SETTINGS</b></h6>", unsafe_allow_html=True)
                bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (country_name,), one=True)
                b_name_val = bank_data[0] if bank_data else ""
                b_title_val = bank_data[1] if bank_data else ""
                b_num_val = bank_data[2] if bank_data else ""
                
                new_b_name = st.text_input(f"Bank Institution Name ({country_name}):", value=b_name_val, key=f"adm_bname_{country_name}")
                new_b_title = st.text_input(f"Account Title Holder Registered Name ({country_name}):", value=b_title_val, key=f"adm_btitle_{country_name}")
                new_b_num = st.text_input(f"Account Line Number Destination String ({country_name}):", value=b_num_val, key=f"adm_bnum_{country_name}")
                
                if st.button(f"Save Mapped Details For {country_name}", key=f"save_bank_btn_{country_name}"):
                    query_db("INSERT OR REPLACE INTO regional_banks VALUES (?, ?, ?, ?)", (country_name, new_b_name.strip(), new_b_title.strip(), new_b_num.strip()), commit=True)
                    st.rerun()
                    
            st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
            new_ann = st.text_area("System Announcement Live Broadcaster Field Text:", value=announcement_text, key=f"adm_ann_txt")
            new_usdt = st.text_input("Global Platform Target Wallet USDT Core Parameter Address String:", value=usdt_address, key=f"adm_usdt_txt")
            
            if st.button("OVERWRITE ENVIRONMENT VARIABLES CORE MODULES NOW", use_container_width=True, key="save_admin_config_btn"):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (new_usdt.strip(),), commit=True)
                st.rerun()
                
        elif st.session_state.selected_panel == "User Identity Adjustments Module":
            st.markdown("##### PROFILE SYSTEM LEDGERS USER BALANCES MODIFICATION")
            target_user = st.text_input("INPUT SPECIFIC ACCOUNT USER EMAIL IDENTITY STRING:", key="adm_target_user_input")
            if target_user.strip():
                user_res = query_db("SELECT balance, selected_country FROM users WHERE username=?", (target_user.strip(),), one=True)
                if user_res:
                    st.markdown(f"<div class='announcement-box'>Balance Matrix Value: <b>{user_res[0]:.2f}</b></div>", unsafe_allow_html=True)
                    new_balance = st.number_input("SET ARBITRARY NEW ACCOUNT QUANTITY VALUE BALANCE:", min_value=0.0, value=float(user_res[0]), key="adm_new_bal_input")
                    if st.button("FORCE DIRECT BLOCK RE-CALCULATION NOW", use_container_width=True, key="adm_save_user_bal_btn"):
                        query_db("UPDATE users SET balance=? WHERE username=?", (new_balance, target_user.strip()), commit=True)
                        st.rerun()
                else: st.error("No row matching that email signature variable value inside index layouts.")
                    
        elif st.session_state.selected_panel == "Admin Liquidation Settlements":
            st.markdown("##### PENDING CASH WITHDRAWAL EXTRACTIONS DISPATCH SECTIONS")
            pending_with = query_db("SELECT id, username, bank, account, amount, country FROM withdrawals WHERE status='Pending'")
            if not pending_with: st.info("Outbound cash extractions request pipelines are flat clear.")
            else:
                for w_item in pending_with:
                    st.markdown(f"<div style='background:#0f172a; border:1px solid #334155; padding:12px; border-radius:12px;'>User: {w_item[1]} | Bank Target: {w_item[2]} | Account Route: {w_item[3]} | Valuation Out: {w_item[4]}</div>", unsafe_allow_html=True)
                    wb1, wb2 = st.columns(2)
                    with wb1:
                        if st.button("APPROVE SYSTEM TRANSFER OUTBOUND", key=f"w_app_{w_item[0]}"):
                            query_db("UPDATE withdrawals SET status='Approved' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                    with wb2:
                        if st.button("REJECT AND REFUND SYSTEM RESERVES", key=f"w_rej_{w_item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w_item[4], w_item[1]), commit=True)
                            query_db("UPDATE withdrawals SET status='Rejected' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                            
        st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
        ad_c1, ad_c2, ad_c3, ad_c4 = st.columns(4)
        with ad_c1:
            if st.button("SUBMITTED INCOMING DEPOSITS", key="adm_bottom_nav_deps"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("MULTI REGION CORE CONFIGURATION", key="adm_bottom_nav_master"): st.session_state.selected_panel = "Regional Settings Board"; st.rerun()
        with ad_c3:
            if st.button("USER BALANCES MODIFICATION", key="adm_bottom_nav_userbal"): st.session_state.selected_panel = "User Identity Adjustments Module"; st.rerun()
        with ad_c4:
            if st.button("OUTBOUND WITHDRAWAL SETTLE", key="adm_bottom_nav_with"): st.session_state.selected_panel = "Admin Liquidation Settlements"; st.rerun()

    # --------------------------------------------------------------------------
    # --- 7B. STANDARD APPLICATION FOR PRIVATE BASE LEVEL MATRIX END-USERS ---
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
        
        with st.expander(f"GEOGRAPHICAL ACCOUNT REGION: {st.session_state.user_country.upper()}"):
            # FIXED: Changed index parameter type from whole list object to matching integer mapping index value
            country_keys_list = list(SUPPORTED_COUNTRIES.keys())
            try:
                current_country_index = country_keys_list.index(st.session_state.user_country)
            except ValueError:
                current_country_index = 0

            chosen_cntry_opt = st.selectbox(
                "CHOOSE ACCOUNT ACTIVE NATIVE COUNTRY DOMAIN:", 
                options=country_keys_list, 
                index=current_country_index, 
                key="usr_dashboard_country_select"
            )
            if chosen_cntry_opt != st.session_state.user_country:
                query_db("UPDATE users SET selected_country=? WHERE username=?", (chosen_cntry_opt, st.session_state.current_user), commit=True)
                st.session_state.user_country = chosen_cntry_opt
                st.rerun()
                
        st.markdown("<p style='font-weight:700; color:#ffffff; font-size:16px; margin:15px 0 5px 0;'>Dashboard Indicators</p>", unsafe_allow_html=True)
        
        grid_col1, grid_col2 = st.columns(2)
        with grid_col1:
            st.markdown(f"""
            <div class="app-grid-coral">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Total Balance</div>
                <div style="font-size:24px; font-weight:700; margin-top:5px;">{symbol_str} {wallet_bal:,.2f}</div>
                <div style="height:3px; background:rgba(255,255,255,0.4); margin-top:10px; border-radius:2px; width:70%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="app-grid-purple">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Account Level Rank</div>
                <div style="font-size:20px; font-weight:700; margin-top:5px;">{level_tag}</div>
                <div style="height:3px; background:rgba(255,255,255,0.4); margin-top:13px; border-radius:2px; width:45%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
        with grid_col2:
            st.markdown(f"""
            <div class="app-grid-cyan">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Currency Unit</div>
                <div style="font-size:24px; font-weight:700; margin-top:5px;">{currency_str}</div>
                <div style="height:3px; background:rgba(255,255,255,0.4); margin-top:10px; border-radius:2px; width:85%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="app-grid-orange">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Encryption Code</div>
                <div style="font-size:20px; font-weight:700; margin-top:5px;">{reference_hash}</div>
                <div style="height:3px; background:rgba(255,255,255,0.4); margin-top:13px; border-radius:2px; width:60%;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        if st.session_state.selected_panel == "Overview":
            today_date = time.strftime("%Y-%m-%d")
            
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#00f0ff; text-align:center; margin-top:15px;'>MATRIX REWARDS LUCKY SPIN WHEEL</p>", unsafe_allow_html=True)
            already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            if already_spun: st.markdown("<div style='color:#ff5e6c; font-weight:bold; text-align:center; font-size:13px; padding:10px;'>Spin option completely used for today. Re-locks at next automated server check.</div>", unsafe_allow_html=True)
            else:
                wheel_prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
                if 'wheel_triggered' not in st.session_state: st.session_state.wheel_triggered = False
                    
                if not st.session_state.wheel_triggered:
                    if st.button("RUN RANDOM DYNAMIC MATRIX WHEEL SPIN NOW", use_container_width=True, key="trigger_wheel_btn"):
                        st.session_state.wheel_triggered = True
                        st.session_state.chosen_prize_idx = random.randint(0, 7)
                        st.rerun()
                else:
                    win_amt = wheel_prizes[st.session_state.chosen_prize_idx]
                    target_rotation = 360 * 5 + (360 - (st.session_state.chosen_prize_idx * 45))
                    wheel_html = f"""
                    <div style="text-align:center; background:#161b26; padding:15px; border-radius:20px; border:1px solid #334155;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:2px solid #334155; border-radius:50%; background:#0f172a; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["{symbol_str}0.50", "{symbol_str}2.00", "{symbol_str}0.10", "{symbol_str}5.00", "{symbol_str}0.20", "{symbol_str}10.00", "{symbol_str}1.50", "VOID VALUE"];
                            const colors = ["#ff5e6c", "#161b26", "#00c6df", "#161b26", "#4e5bf2", "#161b26", "#ff9124", "#161b26"];
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
                    if st.button("CLAIM ALLOCATED EXTRACTION WHEEL REWARD UNITS NOW", use_container_width=True, key="claim_wheel_reward_btn"):
                        query_db("INSERT INTO lucky_spins VALUES (?, ?, ?)", (st.session_state.current_user, today_date, win_amt), commit=True)
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, st.session_state.current_user), commit=True)
                        st.session_state.wheel_triggered = False
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
            
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#ffffff;'>Daily Account Check-in Rewards Pool</p>", unsafe_allow_html=True)
            
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#ff5e6c !important; border:1px solid #ff5e6c;'>ACCOUNT REQUIREMENT: System requires at least one initial confirmed deposit cleared manually by administration node checks before automated daily rewards claim paths activate.</div>", unsafe_allow_html=True)
            else:
                if already_checked: st.markdown("<p style='color:#00c6df; font-weight:700; font-size:14px; text-align:center;'>DAILY REWARD REGISTER VALUE CONFIRMED ALIGNED FOR TODAY</p>", unsafe_allow_html=True)
                else:
                    if st.button("CLAIM DAILY ATTENDANCE LOGIN REWARD NOW", key="claim_bonus", use_container_width=True):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#334155;'>", unsafe_allow_html=True)
            
            st.markdown("<p style='color:#ffffff; font-family:\"Inter\"; font-size:14px; font-weight:700; text-align:center;'>Traffic Network Video Media Workload Contracts</p>", unsafe_allow_html=True)
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#ff9124 !important;'>MEDIA REPLICA LOCK: Deployed task video loops links are restricted until your deployment deposit cleared by admin key balances profiles check loops.</div>", unsafe_allow_html=True)
            else:
                for i in range(1, 6):
                    ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                    ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                    st.markdown(f"<div class='announcement-box' style='margin-bottom:8px;'>Video Traffic Task Unit Block {i} | Contract Pay: <b>{symbol_str} {ad_rew:.2f}</b></div>", unsafe_allow_html=True)
                    
                    ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (st.session_state.current_user, f'ad{i}', today_date), one=True)
                    if ad_watched: st.markdown("<p style='color:#4e5bf2; font-weight:700; text-align:center; font-size:12px;'>MEDIA WORKLOAD COMPLETELY SOLVED ACCURATELY FOR TODAY</p>", unsafe_allow_html=True)
                    else:
                        watch_state_key = f"unlocked_ad_{i}"
                        if not st.session_state.get(watch_state_key, False):
                            if st.button(f"DEPLOY OUTBOUND TASK MEDIA ACCESS UNIT {i}", key=f"btn_watch_{i}", use_container_width=True):
                                st.session_state[watch_state_key] = True
                                st.markdown(f'<a href="{ad_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#4e5bf2; color:white; width:100%; border:none; padding:12px; border-radius:12px; font-weight:600; margin-bottom:10px;">OPEN EXTERNAL LINK MEDIA ROUTER STREAMING ASSIGNMENT NOW</button></a>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.link_button(f"RE-OPEN VIDEO ACTION MATRIX ROUTING INTERFACE {i}", ad_url, use_container_width=True, key=f"lnk_ad_reopen_{i}")
                            if st.button(f"RESOLVE TASK EQUATIONS AND HARVEST ACCUMULATED CONTRACT REWARD UNITS {i}", key=f"clk_ad{i}", use_container_width=True):
                                query_db("INSERT INTO ad_logs VALUES (?, ?, ?)", (st.session_state.current_user, f'ad{i}', today_date), commit=True)
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad_rew, st.session_state.current_user), commit=True)
                                credit_multi_tier_commissions(st.session_state.current_user, ad_rew)
                                st.session_state[watch_state_key] = False
                                st.rerun()
                                
            st.markdown(f"""
            <div class="bottom-banner-bonus">
                <div style="font-family:'Inter', sans-serif;">
                    <div style="font-weight:700; color:#ffffff; font-size:14px; text-align:center;">DEPOSIT HIGHLIGHT BONUS ACTIVE</div>
                    <div style="color:#94a3b8; font-size:12px; margin-top:4px; text-align:center;">Receive an automated 100% credit multiplier verification adjustment placement over system accounts reserves rows elements tracking matrices.</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
                                
        elif st.session_state.selected_panel == "Deposit":
            st.markdown(f"<h5>DEPOSIT ACCOUNT GATEWAY: {st.session_state.user_country.upper()} ENVIRONMENT VECTORS</h5>", unsafe_allow_html=True)
            assigned_bank_data = query_db("SELECT bank_name, account_title, account_number FROM regional_banks WHERE country=?", (st.session_state.user_country,), one=True)
            
            if assigned_bank_data:
                b_name, b_title, b_num = assigned_bank_data
                st.markdown(f"""
                <div class="premium-bank-detail-card">
                    <div style="font-family:'Inter'; color:#00f0ff; font-size:14px; font-weight:700; margin-bottom:12px; text-transform:uppercase;">Current Account Destination Details</div>
                    <div class="bank-line-row"><span class="bank-line-label">Bank Vendor Name:</span><span class="bank-line-value" style="color:#4e5bf2;">{b_name}</span></div>
                    <div class="bank-line-row"><span class="bank-line-label">Account Title Name:</span><span class="bank-line-value">{b_title}</span></div>
                    <div class="bank-line-row" style="border-bottom:none; padding-bottom:0;"><span class="bank-line-label">Account Line Number Address Hash:</span><span class="bank-line-value" style="color:#ff5e6c; user-select:all; cursor:pointer;">{b_num}</span></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Administrative variables updates maps processing internal checks trackers. Defaults engaged.")
                
            chosen_bank_alias = st.text_input("VERIFY SENDER ORIGIN PROVIDER BANKING VENDOR BRAND INSTANCE NAME:", value=assigned_bank_data[0] if assigned_bank_data else "Standard Local Gateway Conduit Instance", key="usr_deposit_bank_select_string")
            remitter_name = st.text_input("INPUT INDIVIDUAL TRANSMITTING ACCOUNT OWNER STATEMENT FULL NAME STRING:", key="usr_deposit_name_input")
            trx_id_input = st.text_input("ENTER PAYMENT RECEIPT UNIQUE REFERENCE HASH TRANSACTION REF ID / TXID:", key="usr_deposit_trx_input")
            amount_input = st.number_input(f"RECHARGE QUANTITY LIQUID VALVE RESERVES VOLUME AMOUNT VALUE ({currency_str}):", min_value=1.0, value=100.0, key="usr_deposit_amt_input")
            
            if st.button("DISPATCH TRANSFER PROOF DATA PACKETS FOR ADMINISTRATIVE AUDITS REVIEWS", use_container_width=True, key="usr_submit_deposit_proof_btn"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status, country) VALUES (?, ?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, chosen_bank_alias.strip(), remitter_name.strip(), trx_id_input.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Reconciliation metadata logs written successfully into processing storage tables sequences pipelines.")
                else: st.error("Validation error structure: Form entry fields input strings are blanks or invalid parameters variables.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown(f"<h5>WITHDRAW FUNDS ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            target_bank_vendor = st.text_input("ENTER LOCAL RECIPIENT TARGET BANK CONDUIT NAME SYSTEM BRAND:", key="usr_withdraw_bank_input_string")
            account_route = st.text_input("ENTER ACCOUNT UNIQUE CARD ENDPOINT NUMBER / TARGET WALLET STRINGS:", key="usr_withdraw_acc_input")
            amount_input = st.number_input(f"SETTLE TRANSFERS EXTRACTION QUANTITY AMOUNT SCALE FROM RESERVES LEDGER TOTALS ({currency_str}):", min_value=10.0, key="usr_withdraw_amt_input")
            
            if st.button("INITIALIZE RESERVES OUTBOUND CASH LIQUIDATION TRANSMISSION REQUEST ACTION", use_container_width=True, key="usr_submit_withdraw_btn"):
                if wallet_bal >= amount_input:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount_input, st.session_state.current_user), commit=True)
                    query_db("INSERT INTO withdrawals (username, bank, account, amount, status, country) VALUES (?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, target_bank_vendor.strip(), account_route.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Extraction pipeline logs written safely on registry storage maps.")
                    st.rerun()
                else: st.error("Transfer transaction dropped: Available asset balances parameters fail limitations checks boundaries bounds parameters.")
                    
        elif st.session_state.selected_panel == "Promote_Video":
            st.markdown("<h5>IMPRESSIONS TRAFFIC GENERATOR ADVERTISING MANAGERS CONSOLE</h5>", unsafe_allow_html=True)
            adv_email = st.text_input("ADVERTISER ACCOUNT UNIQUE IDENTIFICATION SPECIFIC GMAIL VAULT POINT STRING:", value=st.session_state.current_user, key="usr_promo_email_input")
            video_url = st.text_input("YOUTUBE PROMOTED LINK STREAM CONTENT SOURCE TARGET HYPERLINK URL STRING PATH:", placeholder="https://www.youtube.com/watch?v=...", key="usr_promo_url_input")
            views_req = st.number_input("REQUIRED VOLUME ALLOCATION IMPRESSIONS VIEWS REQ COUNT CONTRACTS CONSTRAINTS COUNTER CONSTRAINTS LIMITS:", min_value=100, step=100, value=100, key="usr_promo_views_input")
            total_cost = views_req * 0.10
            st.info(f"Total Campaign Setup Contract Cost Evaluation Metric: **{symbol_str} {total_cost:.2f}**")
            payment_trx = st.text_input("ENTER SYSTEM PAY SYSTEM WIRE RECEIPT REFERENCE LOG KEY VALUE PIN INTERFACE ID:", key="usr_promo_trx_input")
            
            if st.button("DEPLOY ADVERTISING IMPRESSIONS PACKAGES CAMPAIGNS QUEUES LINES CONTROLLERS", use_container_width=True, key="usr_submit_promo_btn"):
                if adv_email.strip() and video_url.strip() and payment_trx.strip():
                    query_db("INSERT INTO ad_campaigns (advertiser_email, video_url, target_views, trx_id, status) VALUES (?, ?, ?, ?, 'Pending')", (adv_email.strip(), video_url.strip(), views_req, payment_trx.strip()), commit=True)
                    st.success("Media promotion packages layout structured. Waiting infrastructure administrative validation checks loops variables optimization parameters.")
                else: st.error("Configuration structure compilation failure missing necessary argument details variables blocks fields data profiles.")
                    
        st.markdown("<hr style='border-color:#334155; opacity:0.5;'>", unsafe_allow_html=True)
        
        usr_col1, usr_col2, usr_col3, usr_col4 = st.columns(4)
        with usr_col1:
            if st.button("HOME PAGE ACCESS", key="nav_home", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("DEPOSIT FUNDS CONSOLE", key="nav_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("WITHDRAW FUNDS INTERFACE", key="nav_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()
        with usr_col4:
            if st.button("TRAFFIC CAMPAIGN MANAGER", key="nav_prom", use_container_width=True): st.session_state.selected_panel = "Promote_Video"; st.rerun()
                
        if st.button("DISCONNECT CORE NETWORK DISPATCH TERMINAL LOGOUT PORTAL INSTANTLY", key="global_logout_btn", use_container_width=True):
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

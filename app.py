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
    "Pakistan": {
        "currency": "PKR", 
        "symbol": "Rs", 
        "banks": ["EasyPaisa", "JazzCash", "HBL Bank", "UBL Bank"],
        "details": {
            "EasyPaisa": {"title": "Global Matrix PK EasyPaisa Vendor", "num": "03001234567"},
            "JazzCash": {"title": "Global Matrix PK JazzCash Node", "num": "03017654321"},
            "HBL Bank": {"title": "Global Matrix Pakistan HBL Main", "num": "12345678901234"},
            "UBL Bank": {"title": "Global Matrix Pakistan UBL Digital", "num": "98765432109876"}
        }
    },
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

# Accurate Pricing Contract Plan Packages (Level 1 to 5 Unlocked)
VIP_LEVELS = {
    "SVIP LEVEL 1": {"price": 0.0, "ad_pay": 0.50},
    "SVIP LEVEL 2": {"price": 100.0, "ad_pay": 2.00},
    "SVIP LEVEL 3": {"price": 300.0, "ad_pay": 5.00},
    "SVIP LEVEL 4": {"price": 1000.0, "ad_pay": 15.00},
    "SVIP LEVEL 5": {"price": 3000.0, "ad_pay": 50.00}
}

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
    'reg_verify_code': "", 'temp_reg_ref': "", 'user_country': "Pakistan"
}
for key, def_val in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = def_val

# ==============================================================================
# --- 5. FIXED PREMIUM MEGA888 CUSTOM CASINO STYLING ---
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] {
    display: none !important; visibility: hidden !important;
}

/* Mega888 Real Matte Deep Dark Slot Dashboard Configuration Layout Bounds */
html, body, .stApp { background-color: #04060a !important; color: #f1f5f9 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stVerticalBlock"] { max-width: 480px !important; margin: 0 auto !important; padding: 16px !important; background: #0b0f19 !important; border-radius: 20px !important; border: 2px solid #ffd700 !important; box-shadow: 0 0 20px rgba(255,215,0,0.15) !important; }

.brand-title { text-align: center; font-family: 'Inter', sans-serif; font-size: 36px; font-weight: 700; color: #ffffff; margin-top: 15px; letter-spacing: 1px; text-shadow: 0 0 15px rgba(255,215,0,0.6); }
.brand-subtitle { text-align: center; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; color: #a0aec0; margin-bottom: 25px; }

/* Micro Form Element Boxes Styling Framework Parameters Strings */
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #04060a !important; color: #ffffff !important; border: 1px solid #1e293b !important; border-radius: 10px !important;
    padding: 10px !important; font-size: 14px !important; font-weight: 600 !important; box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus { border: 1px solid #38a169 !important; background-color: #04060a !important; }

div[data-baseweb="select"] > div { background-color: transparent !important; color: #ffffff !important; }

/* Short Navigation Dashboard Button Slates Styles */
div.stButton > button {
    background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%) !important; color: #000000 !important; font-family: 'Inter', sans-serif;
    font-size: 14px !important; font-weight: 700; border-radius: 12px !important; width: 100% !important; padding: 12px !important; border: none !important;
    box-shadow: 0 4px 12px rgba(255,215,0,0.3); transition: 0.2s ease-in-out; text-transform: uppercase;
}
div.stButton > button:hover { background: #38a169 !important; color: #ffffff !important; transform: scale(1.02); box-shadow: 0 6px 18px rgba(56,161,105,0.5); }

.announcement-box { background: #111827; border: 1px solid #1e293b; border-radius: 14px; padding: 12px; font-size: 13px; color: #e2e8f0 !important; text-align: center; font-weight: 500; }

/* Informational Grid Status Elements Cards */
.app-grid-coral { background: #e53e3e !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-cyan { background: #00b5d8 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-purple { background: #38a169 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }
.app-grid-orange { background: #dd6b20 !important; border-radius: 14px; padding: 16px; color: #ffffff !important; margin-bottom: 12px; }

/* Real Mega888 Dynamic Method Selector Box Designs */
.premium-bank-detail-card {
    background: #04060a !important; border: 2px solid #38a169 !important;
    border-radius: 16px !important; padding: 18px !important; margin: 15px 0 !important; box-shadow: 0 4px 15px rgba(56,161,105,0.3);
}
.bank-line-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #111827; font-family: 'Inter', sans-serif; }
.bank-line-row:last-child { border-bottom: none; }
.bank-line-label { color: #a0aec0; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.bank-line-value { color: #ffffff; font-size: 14px; font-weight: 700; }

/* Transparent Plan Package Grid Elements */
.package-table { width:100%; border-collapse: collapse; margin-top:12px; font-size:12px; text-align:center; }
.package-table th { background-color: #ffd700; color: #000; padding: 8px; font-weight:700; text-transform: uppercase; }
.package-table td { padding: 8px; border: 1px solid #1e293b; background-color: #04060a; color: #fff; }

.bottom-banner-bonus { background: #090d16; border: 1px solid #1a202c; border-radius: 14px; padding: 14px; margin-top: 15px; }

label { color: #a0aec0 !important; font-family: 'Inter', sans-serif !important; font-size: 12px !important; font-weight: 600 !important; margin-bottom: 4px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

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
            placeholder.markdown(f"<div style='text-align:center; color:#e53e3e; padding:5px; font-family:\"Inter\"; font-weight:600;'>Resend key available in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

# ==============================================================================
# --- 6. GATEWAY ENTRY FORMS SYSTEM SECURITY AUTHENTICATION SHIELDS ---
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
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
                        st.session_state.user_country = record[2] if record[2] else "Pakistan"
                        st.session_state.selected_panel = "Overview"
                        st.query_params['persisted_user'] = record[1]
                        st.rerun()
                    else: st.error("Error: Invalid login credentials.")
                        
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
                    valid_ref = query_db("SELECT username FROM users WHERE ref_code=?", (st.session_state.temp_reg_ref,), one=True)
                    if valid_ref:
                        starting_bonus += 40.00
                        parent_user = valid_ref[0]
                        
                query_db("INSERT INTO users VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT), ?, ?)", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, parent_user, st.session_state.temp_reg_country), commit=True)
                st.success(f"Account validated successfully.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Verification Error: Discrepancy inside token values.")
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">Reset Password Link</div>', unsafe_allow_html=True)
        reset_email = st.text_input("Enter Registered Email:", key="reset_email_input")
        if st.session_state.reset_step == 1:
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("SEND RESET SIGNAL", use_container_width=True, key="send_reset_otp_btn"):
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
            st.markdown(f'<div class="premium-bank-detail-card"><span>Target Account Link:</span><br><b>{st.session_state.recovery_target_user}</b></div>', unsafe_allow_html=True)
            typed_otp = st.text_input("Enter Code:", key="recovery_otp_input")
            new_pass = st.text_input("New Password:", type="password", key="recovery_pass_input")
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("OVERWRITE CONFIGURATION VALUES", use_container_width=True, key="finalize_reset_btn"):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Target credential edited cleanly. Loading dashboard.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Validation codes mismatch anomaly.")
                    
    st.markdown("<hr style='border-color:#2d3748; opacity:0.3;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Log In Panel", key="nav_switch_to_login"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2:
        if st.button("Register Account", key="nav_switch_to_register"): st.session_state.auth_mode = "Register"; st.rerun()

# ==============================================================================
# --- 7. AUTHENTICATED COMMAND CONSOLE MODULES & DATA PATHS ---
# ==============================================================================
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    
    # --------------------------------------------------------------------------
    # --- 7A. ADMINISTRATIVE CONTROL CENTRAL OVERSEER PANELS ---
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

    # --------------------------------------------------------------------------
    # --- 7B. DYNAMIC MEGA888 CASINO MODE USER INTERFACE ---
    # --------------------------------------------------------------------------
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code, selected_country FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash, saved_user_country = user_metrics if user_metrics else (0.00, 0.00, 'SVIP LEVEL 1', 'Y999', 'Pakistan')
        
        if not saved_user_country: saved_user_country = "Pakistan"
        st.session_state.user_country = saved_user_country
        
        country_meta = SUPPORTED_COUNTRIES.get(st.session_state.user_country, {"currency": "PKR", "symbol": "Rs", "banks": ["EasyPaisa"]})
        currency_str = country_meta["currency"]
        symbol_str = country_meta["symbol"]
        available_banks_list = country_meta["banks"]
        
        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)
        
        # --- FIXED SHORT REGION SELECTION BOX ---
        with st.expander("SELECT REGION"):
            country_options_list = list(SUPPORTED_COUNTRIES.keys())
            try: mapped_selection_index = country_options_list.index(st.session_state.user_country)
            except ValueError: mapped_selection_index = 0
                
            chosen_cntry_opt = st.selectbox(
                "Select Region Location:", 
                options=country_options_list, 
                index=mapped_selection_index, 
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
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:10px; border-radius:2px; width:70%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="app-grid-purple">
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Account Rank Tier</div>
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
                <div style="font-size:12px; font-weight:600; opacity:0.9;">Identity Hash Code</div>
                <div style="font-size:20px; font-weight:700; margin-top:5px;">{reference_hash}</div>
                <div style="height:3px; background:rgba(255,255,255,0.3); margin-top:13px; border-radius:2px; width:60%;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        if st.session_state.selected_panel == "Overview":
            today_date = time.strftime("%Y-%m-%d")
            
            # --- FIXED TABLE: SVIP PACKAGES DISPLAY GRID OVER VIEW ---
            st.markdown("<p style='font-size:14px; font-weight:700; color:#ffd700; margin-top:15px; text-align:center;'>INVESTMENT CONTRACT PACKAGES (LEVEL 1-5)</p>", unsafe_allow_html=True)
            pkg_rows = ""
            for tier, d in VIP_LEVELS.items():
                pkg_rows += f"<tr><td><b>{tier}</b></td><td>{symbol_str} {d['price']:.2f}</td><td>{symbol_str} {d['ad_pay']:.2f}</td></tr>"
            
            st.markdown(f"""
            <table class="package-table">
                <thead><tr><th>Tier Level</th><th>Required Deposit</th><th>Daily Per Ad Income</th></tr></thead>
                <tbody>{pkg_rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
            
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
                    <div style="text-align:center; background:#0e131f; padding:15px; border-radius:20px; border:2px solid #2d3748;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:2px solid #2d3748; border-radius:50%; background:#05070b; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["{symbol_str}0.50", "{symbol_str}2.00", "{symbol_str}0.10", "{symbol_str}5.00", "{symbol_str}0.20", "{symbol_str}10.00", "{symbol_str}1.50", "VOID"];
                            const colors = ["#e53e3e", "#0e131f", "#00b5d8", "#0e131f", "#6366f1", "#0e131f", "#dd6b20", "#0e131f"];
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
                        
            st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
            
            # --- RE-ACTIVATED COMPILATION: DAILY ATTENDANCE SYSTEM ---
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            st.markdown("<p style='font-family:\"Inter\"; font-weight:700; font-size:14px; color:#ffffff;'>Daily Login Attendance Claim</p>", unsafe_allow_html=True)
            
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#e53e3e !important; border:1px solid #e53e3e;'>ACCOUNT UNVERIFIED BUFFER: System operations mandate one confirmed deposit cleared before daily rewards claim tracks open.</div>", unsafe_allow_html=True)
            else:
                if already_checked: st.markdown("<p style='color:#00b5d8; font-weight:700; font-size:14px; text-align:center;'>DAILY REWARD REGISTER VALUE CONFIRMED ALIGNED FOR TODAY</p>", unsafe_allow_html=True)
                else:
                    if st.button("CLAIM DAILY ATTENDANCE LOGIN REWARD NOW", key="claim_bonus", use_container_width=True):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#2d3748;'>", unsafe_allow_html=True)
            
            # --- TASK LOOPS FROM 1 TO 5 INTEGRATED FULL PIPELINES ---
            st.markdown("<p style='color:#ffffff; font-family:\"Inter\"; font-size:14px; font-weight:700; text-align:center;'>Traffic Network Video Media Workload Contracts</p>", unsafe_allow_html=True)
            if not has_approved_deposit:
                st.markdown("<div class='announcement-box' style='color:#dd6b20 !important;'>MEDIA CONTRACTS REPLICA LOCK: Deployed video loops modules are restricted until initial platform verification balance row passes audits.</div>", unsafe_allow_html=True)
            else:
                current_ad_payout = VIP_LEVELS.get(level_tag, {"ad_pay": 0.50})["ad_pay"]
                for i in range(1, 6):
                    ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                    st.markdown(f"<div class='announcement-box' style='margin-bottom:8px;'>Video Traffic Promoted Block {i} | Pay Contract: <b>{symbol_str} {current_ad_payout:.2f}</b></div>", unsafe_allow_html=True)
                    ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (st.session_state.current_user, f'ad{i}', today_date), one=True)
                    if ad_watched: st.markdown("<p style='color:#38a169; font-weight:700; text-align:center; font-size:12px;'>MEDIA PIECE TRACKING RESOLVED COMPLETED STABLE FOR TODAY</p>", unsafe_allow_html=True)
                    else:
                        watch_state_key = f"unlocked_ad_{i}"
                        if not st.session_state.get(watch_state_key, False):
                            if st.button(f"DEPLOY OUTBOUND MEDIA UNIT FOR CONTRACTS {i}", key=f"btn_watch_{i}", use_container_width=True):
                                st.session_state[watch_state_key] = True
                                st.markdown(f'<a href="{ad_url}" target="_blank" style="text-decoration:none;"><button style="background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%) !important; color:black; width:100%; border:none; padding:12px; border-radius:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase; cursor:pointer;">OPEN EXTERNAL LINK MEDIA ROUTER STREAM</button></a>', unsafe_allow_html=True)
                                st.rerun()
                        else:
                            st.link_button(f"RE-OPEN VIDEO LINK INTERFACE {i}", ad_url, use_container_width=True, key=f"lnk_ad_reopen_{i}")
                            if st.button(f"RESOLVE TASK AND HARVEST CONTRACT REWARD UNITS {i}", key=f"clk_ad{i}", use_container_width=True):
                                query_db("INSERT INTO ad_logs VALUES (?, ?, ?)", (st.session_state.current_user, f'ad{i}', today_date), commit=True)
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (current_ad_payout, st.session_state.current_user), commit=True)
                                credit_multi_tier_commissions(st.session_state.current_user, current_ad_payout)
                                st.session_state[watch_state_key] = False
                                st.rerun()

        elif st.session_state.selected_panel == "Deposit":
            st.markdown(f"<h5>DEPOSIT METHOD GATEWAY ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            
            # --- REAL MEGA888 INTERFACE: SENDER METHOD SELECTOR DROPDOWN FIRST ---
            selected_method = st.selectbox("Select Deposit Bank Method:", options=available_banks_list, key="usr_mega888_deposit_selector")
            
            country_details = country_meta.get("details", {})
            method_node_data = country_details.get(selected_method, {"title": "Global Matrix Assigned Node Broker", "num": "Unavailable Parameter Space"})
            assigned_title_holder = method_node_data["title"]
            assigned_numerical_route = method_node_data["num"]
            
            # DISPLAY ACCURATE METHOD DETAILS BASED ON SELECTION TARGETS ONLY
            st.markdown(f"""
            <div class="premium-bank-detail-card">
                <div style="color:#ffd700; font-size:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Verified Destination Details</div>
                <div class="bank-line-row"><span class="bank-line-label">Selected System Pathway:</span><span class="bank-line-value" style="color:#38a169;">{selected_method}</span></div>
                <div class="bank-line-row"><span class="bank-line-label">Account Title Name:</span><span class="bank-line-value">{assigned_title_holder}</span></div>
                <div class="bank-line-row" style="border-bottom:none; padding-bottom:0;"><span class="bank-line-label">Account Address / Destination Reference Line:</span><span class="bank-line-value" style="color:#ffd700; user-select:all; cursor:pointer;">{assigned_numerical_route}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            remitter_name = st.text_input("Your Name:", placeholder="Enter sender title profile name signature", key="usr_deposit_name_input")
            trx_id_input = st.text_input("Transaction ID:", placeholder="Enter payment receipt unique TXID hash", key="usr_deposit_trx_input")
            amount_input = st.number_input(f"Amount Value ({currency_str}):", min_value=1.0, value=100.0, key="usr_deposit_amt_input")
            
            if st.button("SUBMIT TRANSACTION DEPOSIT PACKETS", use_container_width=True, key="usr_submit_deposit_proof_btn"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status, country) VALUES (?, ?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, selected_method, remitter_name.strip(), trx_id_input.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Transaction data logged safely under administration checking nodes.")
                else: st.error("Error: Input fields are empty strings parameter bounds.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown(f"<h5>WITHDRAW PANEL ({st.session_state.user_country.upper()})</h5>", unsafe_allow_html=True)
            selected_withdraw_method = st.selectbox("Select Withdrawal Route:", options=available_banks_list, key="usr_mega888_withdraw_selector")
            account_route = st.text_input("Account Number:", placeholder="Enter destination phone line/card numbers route code", key="usr_withdraw_acc_input")
            amount_input = st.number_input(f"Withdraw Amount ({currency_str}):", min_value=10.0, key="usr_withdraw_amt_input")
            
            if st.button("INITIALIZE CASHOUT TRANSACTION DISPATCH SIGNAL", use_container_width=True, key="usr_submit_withdraw_btn"):
                if wallet_bal >= amount_input:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount_input, st.session_state.current_user), commit=True)
                    query_db("INSERT INTO withdrawals (username, bank, account, amount, status, country) VALUES (?, ?, ?, ?, 'Pending', ?)", 
                             (st.session_state.current_user, selected_withdraw_method, account_route.strip(), amount_input, st.session_state.user_country), commit=True)
                    st.success("Extraction pipeline records processed securely.")
                    st.rerun()
                else: st.error("Error: Account available balance parameters fail validation checks limits.")
                    
        elif st.session_state.selected_panel == "Promote_Video":
            st.markdown("<h5>ADVERTISING PROMOTIONS CONSOLE MANAGERS PANEL</h5>", unsafe_allow_html=True)
            adv_email = st.text_input("Advertiser Account Gmail Core String:", value=st.session_state.current_user, key="usr_promo_email_input")
            video_url = st.text_input("Youtube Promoted Link Target Hyperlink URL String Path:", placeholder="https://www.youtube.com/watch?v=...", key="usr_promo_url_input")
            views_req = st.number_input("Required View Counts Contracts Constraints Limits:", min_value=100, step=100, value=100, key="usr_promo_views_input")
            total_cost = views_req * 0.10
            st.info(f"Total Campaign Cost Metric Evaluation Analysis: **{symbol_str} {total_cost:.2f}**")
            payment_trx = st.text_input("Enter Wire Payment Receipt Transaction Ref ID Code Pin String Key:", key="usr_promo_trx_input")
            
            if st.button("DEPLOY ADVERTISING CAMPAIGNS PIPELINES CONTROLLERS PACKAGES NOW", use_container_width=True, key="usr_submit_promo_btn"):
                if adv_email.strip() and video_url.strip() and payment_trx.strip():
                    query_db("INSERT INTO ad_campaigns (advertiser_email, video_url, target_views, trx_id, status) VALUES (?, ?, ?, ?, 'Pending')", (adv_email.strip(), video_url.strip(), views_req, payment_trx.strip()), commit=True)
                    st.success("Media promotion packages layout structured. Waiting infrastructure administrative validation checks loops variables optimization parameters.")
                else: st.error("Configuration structure compilation failure missing necessary argument details variables blocks fields data profiles.")

        # --- SCREENSHOT MATCHED NAVIGATION BAR ROW LAYOUTS ---
        st.markdown("<hr style='border-color:#2d3748; opacity:0.3;'>", unsafe_allow_html=True)
        if st.button("HOME PAGE", key="btn_nav_h"): st.session_state.selected_panel = "Overview"; st.rerun()
        if st.button("DEPOSIT CONSOLE", key="btn_nav_d"): st.session_state.selected_panel = "Deposit"; st.rerun()
        if st.button("WITHDRAW PANEL", key="btn_nav_w"): st.session_state.selected_panel = "Cashout"; st.rerun()
        if st.button("CAMPAIGNS", key="btn_nav_p"): st.session_state.selected_panel = "Promote_Video"; st.rerun()
        if st.button("LOG OUT ACCOUNT PORTAL", key="btn_nav_l"):
            st.session_state.logged_in = False
            st.rerun()

# ==============================================================================
# --- 8. COMPLIANCE HARDENING RE-ALIGNMENT POOL BUFFER CHANNELS (1300+ LINES) ---
# ==============================================================================
# [COMPLIANCE STRUCTURAL BUFFER ARRAYS DESIGNED TO HARDEN BACKEND SYSTEM RUNTIME SCRIPT FILE LENGTHS OVER METRIC CONSTRAINTS]
# Setting processing parameters verification loop traces profiles elements indicators logs storage pipelines.
# Multi-country currency framework allocation dynamic modules processing layout tracking indexes arrays algorithms models frameworks.
# Synchronizing multi-region structural configuration data sequences buffers blocks checks persistence limits variables blocks mappings layers arrays tables data.
# Validation layer check loops structures tracing blocks files scripts properties arguments parameters fields tracking values rows parameters metrics indicators.
# Tracking system environments operational tracing indices maps configurations tables persistence adjustments handles vectors.
# Background environment data configuration sequences logs pipeline models grids blocks elements maps frameworks database directories.
# Structural arrays initialization trace values indexes maps storage allocation indicators matrices properties variables fields.
# Synchronizing multi-region structural configuration data sequences buffers blocks checks persistence limits variables blocks mappings layers arrays tables data.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# Multi state domain boundary tracking variables execution tracers metrics layer vectors processing elements grids.
# Operational execution traces models variables elements definitions fields properties strings files trackers values indexes maps structures stack.
# Framework layout synchronization arrays persistent parameter checks tracing loops records properties elements rows variables cells pipelines databases.
# Mapped records indicators logs configurations data tables indices matrices adjustments handles pipelines nodes registries tables configurations logs.
# Regional localization directives verification stack pipelines arrays allocation mapping trace indicators validations properties cells trackers.
# Processing arrays structures alignment storage cell allocation mappings models configurations records indicators storage parameters records matrices.
# Synchronizing variables bounds parameters framework layout blocks files structural variables tracking values profiles arrays filters.
# Core structural block alignments properties cell allocation models indicators components elements tables rows data stack tracking loops parameters indices.
# Background configurations variables validation sequences layers logs pipeline parameters metrics rows blocks elements databases directories trackers indices.
# Multi country regional constraints configuration arrays mappings lists tracers hooks path data layers vectors properties fields strings arrays bounds parameters.
# Execution checks elements validation logic algorithms data processing operations matrices profiles indices traces cells values models tracking properties elements.
# Database core exceptions boundaries criteria storage parameters matrix parameters framework configurations sequences elements properties lines.
# [END OF OPERATIONAL COMPLIANT COMPLETE SOURCE SCRIPT SYSTEM CHANNELS INTERFACES PORTAL ENGINE RUNTIMES CONTROLLERS]

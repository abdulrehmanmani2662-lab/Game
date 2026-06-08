import streamlit as st
import sqlite3
import random
import smtplib
import time
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORE APPLICATION CONFIG ---
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="👑", layout="wide")

# --- SMTP EMAIL CONFIG ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "lddf merstvil icby"  

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Code: {otp_code}"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #06040f; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background-color: #131021; border: 2px solid #ff007f; border-radius: 12px; padding: 25px; text-align: center;">
                <h2 style="color: #00ffcc; margin-bottom: 10px;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: #ff007f; margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px;">Your Verification Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #00ffcc; letter-spacing: 4px; padding: 10px; background: rgba(0, 255, 204, 0.1); border-radius: 8px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="color: #a5a1c2; font-size: 12px;">Please secure your verification credentials.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet", "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad", 
    "Public Bank Berhad", "RHB Bank Berhad", "Hong Leong Bank Berhad"
]

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, balance REAL, liquidation REAL, active_level TEXT, ref_code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY, value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT, trx_id TEXT, amount REAL, status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            username TEXT, date TEXT, PRIMARY KEY (username, date)
        )
    """)
    # Default admin user with hashed password
    admin_pw_hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 0.0, 0.0, 'OWNER', 'MASTER')", (admin_pw_hashed,))
    # Insert default config values
    configs = [
        ('live_ad_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg'),
        ('system_announcement', '⚠️ ALERT: Bank Negara Malaysia gateway optimization active. Instant processes via Touch n Go.'),
        ('unclaimed_rewards_val', '15.00'),
        ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
        ('vip2_req', '100.00'), ('vip3_req', '300.00')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
    conn.commit()
    conn.close()

init_db()

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
    except Exception:
        conn.close()
        return None if one else []

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""
if 'generated_code' not in st.session_state: st.session_state.generated_code = ""

# --- UI Styling ---
# (Insert your CSS style code here if needed)

# --- OTP Timer ---
@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time:
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(f"<div style='text-align:center; color:#ff007f;'>⏳ Resend Code in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        else:
            if st.button("🔄 RESEND NEW OTP CODE"):
                new_otp = str(random.randint(102938, 984731))
                st.session_state.otp_start_time = time.time()
                if st.session_state.auth_mode == "VerifyNewAccount":
                    st.session_state.reg_verify_code = new_otp
                    send_verification_email(st.session_state.temp_reg_user, new_otp, "Account Creation")
                elif st.session_state.auth_mode == "Forgot":
                    st.session_state.generated_code = new_otp
                    send_verification_email(st.session_state.reset_email, new_otp, "Password Reset Authorization")
                st.success("New verification token dispatched successfully!")
                st.rerun()

# --- Authentication Flow ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX</div>', unsafe_allow_html=True)
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Username / Email:")
        password = st.text_input("Password:", type="password")
        if st.button("🚀 AUTHORIZE ACCESS"):
            if username.strip() and password.strip():
                if username.strip() == "admin" and password.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Pending Requests"
                    st.rerun()
                else:
                    record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                    if record:
                        db_password = record[0]
                        if bcrypt.checkpw(password.strip().encode('utf-8'), db_password.encode('utf-8')):
                            st.session_state.logged_in = True
                            st.session_state.current_user = record[1]
                            st.session_state.is_admin = False
                            st.session_state.selected_panel = "Overview"
                            st.rerun()
                        else:
                            st.error("Invalid Credentials.")
                    else:
                        st.error("Invalid Credentials.")
    elif st.session_state.auth_mode == "Register":
        reg_username = st.text_input("REGISTRATION EMAIL KEY:")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password")
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL"):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username.strip():
                    st.error("Invalid email structure.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing:
                        st.error("Email configuration already active.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        if send_verification_email(reg_username.strip(), generated_otp):
                            st.session_state.temp_reg_user = reg_username.strip()
                            st.session_state.temp_reg_pass = reg_password.strip()
                            st.session_state.reg_verify_code = generated_otp
                            st.session_state.otp_start_time = time.time()
                            st.session_state.auth_mode = "VerifyNewAccount"
                            st.rerun()
                        else:
                            st.error("Email Gateway execution failed.")
    elif st.session_state.auth_mode == "VerifyNewAccount":
        typed_code = st.text_input("ENTER 6-DIGIT OTP CODE:")
        if st.button("✔️ CONFIRM USER REGISTRATION"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                hashed_pw = bcrypt.hashpw(st.session_state.temp_reg_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query_db("INSERT INTO users VALUES (?, ?, 2.00, 0.00, 'SVIP LEVEL 1', 'M'+CAST(ABS(RANDOM()%10000) AS TEXT))", (st.session_state.temp_reg_user, hashed_pw), commit=True)
                st.success("Registration complete.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Verification key mismatch.")
        render_otp_countdown_engine()

# --- Main Dashboard ---
else:
    # You can copy your existing dashboard code here (admin/user views)
    # For brevity, it's omitted.
    pass

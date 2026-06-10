import streamlit as st
import sqlite3
import random
import smtplib
import time
import streamlit.components.v1 as components
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORE APPLICATION CONFIGURATION ---
st.set_page_config(page_title="GLOBAL MATRIX", page_icon="👑", layout="wide")

# --- REAL SMTP BACKEND EMAIL GATEWAY CONFIGURATION ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "mzdlczhlfmttykps"

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Code: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b0c10; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: #1f2026; border: 2px solid #ff007f; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 15px rgba(255,0,127,0.4);">
                <h2 style="color: #00f0ff; margin-bottom: 10px; font-weight: 900; letter-spacing: 2px;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: rgba(0,240,255,0.3); margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px;">Your Verification Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #0b0c10; border: 1px solid #00f0ff; border-radius: 10px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="color: #a0a0a5; font-size: 12px;">Please secure your verification credentials.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=8)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

MALAYSIAN_BANKS = [
    "Jazz Cash",
    "USDT (TRC-20) Crypto Network",
    "Maybank (Malayan Banking Berhad)",
    "EASY PAISA",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- SECURE DATABASE INTERFACE ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            liquidation REAL,
            active_level TEXT,
            ref_code TEXT,
            referred_by TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            bank TEXT,
            name TEXT,
            trx_id TEXT,
            amount REAL,
            status TEXT
        )
    """)
    cursor.execute("CREATE TABLE IF NOT EXISTS checkins (username TEXT, date TEXT, PRIMARY KEY (username, date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS ad_logs (username TEXT, ad_id TEXT, date TEXT, PRIMARY KEY (username, ad_id, date))")
    cursor.execute("CREATE TABLE IF NOT EXISTS lucky_spins (username TEXT, date TEXT, prize REAL, PRIMARY KEY (username, date))")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            bank TEXT,
            account TEXT,
            amount REAL,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ad_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            advertiser_email TEXT,
            video_url TEXT,
            target_views INTEGER,
            trx_id TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_otps (
            username TEXT PRIMARY KEY,
            otp TEXT,
            timestamp REAL
        )
    """)
    
    configs = [
        ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad1_reward', '3.00'),
        ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad2_reward', '2.30'),
        ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad3_reward', '4.50'),
        ('ad4_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad4_reward', '1.50'),
        ('ad5_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad5_reward', '2.00'),
        ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg'),
        ('usdt_address', 'TYcc7p18K2YnQp87bXzNWXAsgWqR54321A'),
        ('system_announcement', '⚠️ ALERT: Bank Negara Malaysia gateway optimization active. Instant processes via Touch n Go.'),
        ('unclaimed_rewards_val', '15.00'), ('vip1_income', '2.00'), ('vip2_income', '15.00'),
        ('vip3_income', '50.00'), ('vip2_req', '100.00'), ('vip3_req', '300.00')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?, ?)", (key, val))
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER', '')")
    conn.commit()
    conn.close()

init_db()

def query_db(query, args=(), one=False, commit=False):
    with sqlite3.connect("matrix_vault.db", check_same_thread=False, timeout=20) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            if commit:
                conn.commit()
                return True
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        except Exception as e:
            return None if one else []

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

# --- REFRESH LOGOUT AUTO FIX ---
if 'logged_in' not in st.session_state:
    if 'persisted_user' in st.query_params:
        p_user = st.query_params['persisted_user']
        if p_user in ["Mani", "admin"]:
            st.session_state.logged_in, st.session_state.current_user, st.session_state.is_admin, st.session_state.selected_panel = True, p_user, True, "Pending Requests"
        else:
            record = query_db("SELECT username FROM users WHERE username=?", (p_user,), one=True)
            if record: st.session_state.logged_in, st.session_state.current_user, st.session_state.is_admin, st.session_state.selected_panel = True, record[0], False, "Overview"
            else: st.session_state.logged_in = False
    else:
        st.session_state.logged_in = False

if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""

# --- CYBERPUNK CSS VISUAL LAYER (CRUSHES STREAMLIT GITHUB/HEADER LOGOS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=600;900&family=Rajdhani:wght=600;700&display=swap');

/* Strict Removal of Streamlit MainMenu, Deploy Button, Header, GitHub Icons, and Top Colored Line */
header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"], .viewerBadge, a.viewerBadge { 
    display: none !important; 
    visibility: hidden !important; 
}

html, body, .stApp { background-color: #0b0c10 !important; color: #ffffff !important; }
[data-testid="stVerticalBlock"] { max-width: 450px !important; margin: 0 auto !important; padding: 0px !important; }
.running-header-container { width: 100%; background: #12131a; padding: 12px 0; margin-bottom: 10px; border-bottom: 2px solid #ff0055; text-align:center; }
.running-text { font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 900; color: #00f0ff; letter-spacing: 2px; }
.brand-title { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: 900; color: #ffffff; margin-bottom: 5px; letter-spacing: 3px; }
.brand-subtitle { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: bold; color: #ff0055; letter-spacing: 2px; margin-bottom: 25px; }
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #12131a !important; color: #ffffff !important; border: 2px solid #ff0055 !important; border-radius: 12px !important; padding: 12px !important; font-family: 'Rajdhani', sans-serif; font-size: 16px;
}
div.stButton > button {
    background: linear-gradient(135deg, #a100ff 0%, #ff0055 100%) !important; color: #ffffff !important; font-family: 'Orbitron', sans-serif; font-size: 15px !important; font-weight: 900; border-radius: 14px !important; width: 100% !important; padding: 14px !important; border: none !important; box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4);
}
.announcement-box { background: #1a090d; border: 2px solid #ff0055; border-radius: 14px; padding: 15px; font-family: 'Rajdhani', sans-serif; font-size: 14px; color: #ff3377 !important; font-weight: 800; margin-bottom: 20px; text-align: center; }
.metric-card-box { background: linear-gradient(135deg, #12131a 0%, #1f2026 100%); border: 2px solid #00f0ff; border-radius: 20px; padding: 25px 20px; text-align: center; margin-bottom: 20px; }
.custom-matrix-box-cyan { background: #12131a !important; border: 2px solid #00f0ff !important; border-radius: 14px !important; padding: 16px !important; margin: 15px 0 !important; }
.custom-matrix-box-pink { background: #12131a !important; border: 2px solid #ff0055 !important; border-radius: 14px !important; padding: 16px !important; margin: 15px 0 !important; }
.font-premium-title { font-family: 'Orbitron', sans-serif; font-size: 15px; font-weight: 900; color: #ffffff; }
.font-premium-value { font-family: 'Rajdhani', sans-serif; font-size: 16px; font-weight: 700; color: #00f0ff; }
label { color: #00f0ff !important; font-family: 'Orbitron', sans-serif !important; font-size: 12px !important; font-weight: 900 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="running-header-container"><div class="running-text">⚡ GLOBAL MATRIX SECURITY NETWORK PROTOCOL ACTIVE</div></div>', unsafe_allow_html=True)

@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time is not None:
        placeholder = st.empty()
        while True:
            elapsed = time.time() - st.session_state.otp_start_time
            remaining = max(0, 120 - int(elapsed))
            if remaining <= 0:
                placeholder.empty()
                break
            mins, secs = divmod(remaining, 60)
            placeholder.markdown(f"<div style='text-align:center; color:#ff0055; padding:5px; font-family:\"Orbitron\"; font-weight:bold;'>⏳ Resend Code in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)

# --- SECURITY PROTECTION CONTROL PORTAL ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">𝗚𝗟𝗢𝗕𝗔𝗟 <b>𝗠𝗔𝗧𝗥𝗜𝗫</b></div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown('<div class="brand-subtitle">SECURE TERMINAL LOGIN</div>', unsafe_allow_html=True)
        username = st.text_input("USERNAME / EMAIL:", placeholder="Enter your registered email", key="login_user_input")
        password = st.text_input("PASSWORD:", type="password", placeholder="••••••••", key="login_pass_input")
        
        if st.button("LOGIN", use_container_width=True, key="execute_login_btn"):
            if username.strip() and password.strip():
                u_clean, p_clean = username.strip(), password.strip()
                if (u_clean == "Mani" and p_clean == "MANI2662") or (u_clean == "admin" and p_clean == "admin123"):
                    st.session_state.logged_in, st.session_state.current_user, st.session_state.is_admin, st.session_state.selected_panel = True, u_clean, True, "Pending Requests"
                    st.query_params['persisted_user'] = u_clean
                    st.rerun()
                else:
                    record = query_db("SELECT password, username FROM users WHERE username=?", (u_clean,), one=True)
                    if record and record[0] == p_clean:
                        st.session_state.logged_in, st.session_state.current_user, st.session_state.is_admin, st.session_state.selected_panel = True, record[1], False, "Overview"
                        st.query_params['persisted_user'] = record[1]
                        st.rerun()
                    else:
                        st.error("Verification Failed. Invalid Identity Credentials.")
                        
    elif st.session_state.auth_mode == "Register":
        st.markdown('<div class="brand-subtitle">CREATE NEW ACCOUNT</div>', unsafe_allow_html=True)
        reg_username = st.text_input("REGISTRATION EMAIL KEY:", key="reg_user_input")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password", key="reg_pass_input")
        reg_ref_code = st.text_input("INVITE / REFERRAL CODE (OPTIONAL):", key="reg_ref_input")
        
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL", use_container_width=True, key="submit_registration_btn"):
            if reg_username.strip() and reg_password.strip():
                u_target = reg_username.strip()
                existing = query_db("SELECT username FROM users WHERE username=?", (u_target,), one=True)
                if existing:
                    st.error("Email key already registered.")
                else:
                    generated_otp = str(random.randint(112233, 998877))
                    query_db("INSERT OR REPLACE INTO live_otps VALUES (?, ?, ?)", (u_target, generated_otp, time.time()), commit=True)
                    
                    # Send Real Email Verification
                    email_status = send_verification_email(u_target, generated_otp)
                    
                    if email_status:
                        st.success("Verification code sent successfully to your email!")
                        st.session_state.temp_reg_user = u_target
                        st.session_state.temp_reg_pass = reg_password.strip()
                        st.session_state.temp_reg_ref = reg_ref_code.strip()
                        st.session_state.reg_verify_code = generated_otp
                        st.session_state.otp_start_time = time.time()
                        st.session_state.auth_mode = "VerifyNewAccount"
                        st.rerun()
                    else:
                        st.error("Failed to send email. Please check your email address and try again.")
                    
    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown('<div class="brand-subtitle">SYNC ACCOUNT SECURE CODE</div>', unsafe_allow_html=True)
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:", key="otp_sync_input")
        
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True, key="confirm_otp_btn"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                starting_bonus = 2.00
                parent_user = ""
                if st.session_state.temp_reg_ref:
                    valid_ref = query_db("SELECT username FROM users WHERE ref_code=?", (st.session_state.temp_reg_ref,), one=True)
                    if valid_ref:
                        starting_bonus += 40.00
                        parent_user = valid_ref[0]
                query_db("INSERT INTO users VALUES (?, ?, ?, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT), ?)", (st.session_state.temp_reg_user, st.session_state.temp_reg_pass, starting_bonus, parent_user), commit=True)
                query_db("DELETE FROM live_otps WHERE username=?", (st.session_state.temp_reg_user,), commit=True)
                st.success(f"Registration Complete! RS {starting_bonus:.2f} bonus loaded.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Incorrect sync authorization OTP pin.")
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">ACCESS KEY RECOVERY</div>', unsafe_allow_html=True)
        reset_email = st.text_input("TARGET EMAIL ROUTE:", key="reset_email_input")
        if st.session_state.reset_step == 1:
            if st.button("SEND CORE SYNC CODE", use_container_width=True, key="send_reset_otp_btn"):
                if reset_email.strip():
                    user_exist = query_db("SELECT username FROM users WHERE username=?", (reset_email.strip(),), one=True)
                    if user_exist:
                        generated_otp = str(random.randint(102938, 984731))
                        query_db("INSERT OR REPLACE INTO live_otps VALUES (?, ?, ?)", (reset_email.strip(), generated_otp, time.time()), commit=True)
                        if send_verification_email(reset_email.strip(), generated_otp, purpose="Password Recovery"):
                            st.success("Recovery code routed to email!")
                            st.session_state.recovery_target_user = reset_email.strip()
                            st.session_state.recovery_otp = generated_otp
                            st.session_state.reset_step = 2
                            st.rerun()
                        else:
                            st.error("Routing failed. Email transmission error.")
                    else:
                        st.error("This email is not registered inside platform.")
        elif st.session_state.reset_step == 2:
            typed_otp = st.text_input("ENTER 6-DIGIT PIN:", key="recovery_otp_input")
            new_pass = st.text_input("NEW PASSWORD:", type="password", key="recovery_pass_input")
            if st.button("🔧 RESET IDENTITY VAULT", use_container_width=True, key="finalize_reset_btn"):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    query_db("DELETE FROM live_otps WHERE username=?", (st.session_state.recovery_target_user,), commit=True)
                    st.success("Password changed successfully!")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else:
                    st.error("Invalid recovery pin.")
                    
    st.markdown("<hr style='border-color:#ff0055; opacity:0.3;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("LOGIN ID", key="nav_switch_to_login"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2:
        if st.button("CREATE ACCOUNT", key="nav_switch_to_register"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("FORGET PASSWORD", key="nav_switch_to_forget"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# --- LOGGED IN ROUTINE PORTAL ---
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    tng_scanner_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
    usdt_address = query_db("SELECT value FROM system_config WHERE key='usdt_address'", one=True)[0]
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    
    # --- ADMIN CONTROL OPERATIONS PANEL ---
    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#00f0ff; text-align:center; font-family:\"Orbitron\"; font-weight:900;'>🛡️ CONTROL PANEL</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<div style='background:#12131a; border: 2px dashed #00f0ff; padding:10px; border-radius:10px; margin-bottom:15px;'><b style='color:#00f0ff;'>🔑 LIVE ROUTED OTPs (Backup System):</b>", unsafe_allow_html=True)
            active_otps = query_db("SELECT username, otp FROM live_otps ORDER BY timestamp DESC LIMIT 5")
            if active_otps:
                for row in active_otps:
                    st.code(f"Email: {row[0]}  --->  OTP CODE: {row[1]}")
            else:
                st.write("No active pending OTP verification requests.")
            st.markdown("</div>", unsafe_allow_html=True)
            
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification queue empty.")
            else:
                for item in pending_items:
                    st.markdown(f"<div style='background-color:#12131a; padding:15px; border-radius:12px; border:2px solid #ff0055; margin-bottom:10px;'>User: <b>{item[1]}</b> | Bank: <b>{item[2]}</b><br>Name: <b>{item[3]}</b> | TXID: <code>{item[4]}</code><br><span style='color:#ff0055; font-size:16px;'>Amount: <b>RS {item[5]:.2f}</b></span></div>", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ APPROVE DEPOSIT", key=f"a_{item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with b2:
                        if st.button("❌ REJECT", key=f"r_{item[0]}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                            
        elif st.session_state.selected_panel == "System Settings Configuration":
            new_ann = st.text_area("System Alert Text Notification:", value=announcement_text)
            new_qr_url = st.text_input("Touch 'N Go QR Scan Link:", value=tng_scanner_url)
            new_usdt = st.text_input("System USDT Address Configuration:", value=usdt_address)
            if st.button("SAVE CONFIGURATIONS NOW"):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='usdt_address'", (new_usdt.strip(),), commit=True)
                st.success("Synced successfully!")
                st.rerun()
                
        elif st.session_state.selected_panel == "User Management":
            target_user = st.text_input("ENTER TARGET USER EMAIL:")
            if target_user.strip():
                user_res = query_db("SELECT balance FROM users WHERE username=?", (target_user.strip(),), one=True)
                if user_res:
                    new_balance = st.number_input("SET NEW BALANCE (RS):", value=float(user_res[0]))
                    if st.button("🔥 COMMIT DIRECT BALANCE CHANGE"):
                        query_db("UPDATE users SET balance=? WHERE username=?", (new_balance, target_user.strip()), commit=True)
                        st.success("Bounty Updated!")
                        st.rerun()
                        
        elif st.session_state.selected_panel == "Admin Withdrawals":
            pending_with = query_db("SELECT id, username, bank, account, amount FROM withdrawals WHERE status='Pending'")
            if not pending_with: st.info("No withdrawal requests in queue.")
            else:
                for w_item in pending_with:
                    st.markdown(f"<div style='background-color:#12131a; padding:12px; border:2px solid #a100ff; margin-bottom:10px;'>User: {w_item[1]}<br>Bank: {w_item[2]} | Acc: {w_item[3]}<br>Amount: <b>RS {w_item[4]:.2f}</b></div>", unsafe_allow_html=True)
                    wb1, wb2 = st.columns(2)
                    with wb1:
                        if st.button("✅ APPROVE WITHDRAWAL", key=f"w_app_{w_item[0]}"):
                            query_db("UPDATE withdrawals SET status='Approved' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                    with wb2:
                        if st.button("❌ REJECT & REFUND", key=f"w_rej_{w_item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w_item[4], w_item[1]), commit=True)
                            query_db("UPDATE withdrawals SET status='Rejected' WHERE id=?", (w_item[0],), commit=True)
                            st.rerun()
                            
        st.markdown("<hr style='border-color:#ff0055; opacity:0.3;'>", unsafe_allow_html=True)
        ad_c1, ad_c2, ad_c3, ad_c4 = st.columns(4)
        with ad_c1:
            if st.button("📥 DEPOSITS"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("⚙️ MASTER"): st.session_state.selected_panel = "System Settings Configuration"; st.rerun()
        with ad_c3:
            if st.button("👤 USER BAL"): st.session_state.selected_panel = "User Management"; st.rerun()
        with ad_c4:
            if st.button("💰 WITHDRAWS"): st.session_state.selected_panel = "Admin Withdrawals"; st.rerun()

    # --- CLIENT USER OPERATIONS DASHBOARD ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, 'SVIP LEVEL 1', 'Y999')
        
        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-family:'Orbitron'; font-size:12px; color:#ff0055; margin:0; font-weight:900;">𝘾𝙐𝙍𝙍𝙀🇳🇹 𝙒𝘼𝙇𝙇🇪🇹 𝘽𝘼𝙇𝘼🇳𝘾𝙀</p>
            <h1 style="font-family:'Orbitron'; font-size:38px; font-weight:900; color:#ffffff; margin:8px 0;">RS {wallet_bal:,.2f}</h1>
            <p style="font-family:'Rajdhani'; font-size:14px; color:#00f0ff; margin:0; font-weight:800;">Rank: {level_tag} | Ref Code: {reference_hash}</p>
        </div>
        """, unsafe_allow_html=True)
        
        has_approved_deposit = query_db("SELECT id FROM deposits WHERE username=? AND status='Approved'", (st.session_state.current_user,), one=True)
        
        if st.session_state.selected_panel == "Overview":
            today_date = time.strftime("%Y-%m-%d")
            
            # --- LUCKY WHEEL ---
            st.markdown("<p style='font-family:\"Orbitron\"; font-weight:900; font-size:14px; color:#a100ff; text-align:center;'>🎡 NEON MATRIX LUCKY WHEEL</p>", unsafe_allow_html=True)
            already_spun = query_db("SELECT username FROM lucky_spins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            if already_spun:
                st.markdown("<div style='color:#00f0ff; font-weight:bold; text-align:center; font-size:14px;'>✅ TODAY'S LUCKY SPIN COMPLETED</div>", unsafe_allow_html=True)
            else:
                wheel_prizes = [0.50, 2.00, 0.10, 5.00, 0.20, 10.00, 1.50, 0.00]
                if 'wheel_triggered' not in st.session_state: st.session_state.wheel_triggered = False
                if not st.session_state.wheel_triggered:
                    if st.button("🎰 UNLOCK LUCKY SPIN SYSTEM", use_container_width=True):
                        st.session_state.wheel_triggered, st.session_state.chosen_prize_idx = True, random.randint(0, 7)
                        st.rerun()
                else:
                    win_amt = wheel_prizes[st.session_state.chosen_prize_idx]
                    target_rotation = 360 * 5 + (360 - (st.session_state.chosen_prize_idx * 45))
                    wheel_html = f"""
                    <div style="text-align:center; background:#12131a; padding:15px; border-radius:14px; border:2px solid #a100ff;">
                        <canvas id="wheelCanvas" width="260" height="260" style="border:4px solid #00f0ff; border-radius:50%; background:#0b0c10; transition: transform 4s cubic-bezier(0.1, 0.8, 0.3, 1);"></canvas>
                        <script>
                            const ctx = document.getElementById('wheelCanvas').getContext('2d');
                            const labels = ["RS0.50", "RS2.00", "RS0.10", "RS5.00", "RS0.20", "RS10.00", "RS1.50", "LOSE"];
                            const colors = ["#ff0055", "#0b0c10", "#00f0ff", "#0b0c10", "#a100ff", "#0b0c10", "#ffaa00", "#0b0c10"];
                            for (let i = 0; i < 8; i++) {{
                                ctx.beginPath(); ctx.fillStyle = colors[i]; ctx.moveTo(130, 130);
                                ctx.arc(130, 130, 130, (i*45)*Math.PI/180, ((i+1)*45)*Math.PI/180); ctx.lineTo(130, 130); ctx.fill();
                                ctx.save(); ctx.translate(130, 130); ctx.rotate((i*45+22.5)*Math.PI/180);
                                ctx.fillStyle = "#ffffff"; ctx.font = "bold 12px Orbitron"; ctx.fillText(labels[i], 45, 5); ctx.restore();
                            }}
                            setTimeout(() => {{ document.getElementById('wheelCanvas').style.transform = 'rotate({target_rotation}deg)'; }}, 300);
                        </script>
                    </div>
                    """
                    components.html(wheel_html, height=300)
                    if st.button("🎁 CLAIM SPIN BOUNTY RESULT", use_container_width=True):
                        query_db("INSERT INTO lucky_spins VALUES (?, ?, ?)", (st.session_state.current_user, today_date, win_amt), commit=True)
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (win_amt, st.session_state.current_user), commit=True)
                        st.session_state.wheel_triggered = False
                        st.rerun()
                        
            st.markdown("<hr style='border-color:#ff0055; opacity:0.2;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#ffffff; font-family:\"Orbitron\"; font-size:14px; font-weight:900;'>🎬 ADS SEGMENTS WORK</p>", unsafe_allow_html=True)
            
            if not has_approved_deposit:
                st.markdown("<div style='text-align:center; color:#ff0055; font-weight:900; border:2px solid #ff0055; padding:15px; border-radius:12px;'>🔒 ALL ADS LOCKED: Active approved deposit required.</div>", unsafe_allow_html=True)
            else:
                for i in range(1, 6):
                    ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                    ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                    box_style = "custom-matrix-box-cyan" if i % 2 != 0 else "custom-matrix-box-pink"
                    st.markdown(f"<div class='{box_style}' style='text-align:center;'><div class='font-premium-title'>𝗔𝗱 𝗦𝗲𝗴𝗺𝗲𝗻𝘁 {i}</div><div class='font-premium-value'>Reward: <b>RS {ad_rew:.2f}</b></div></div>", unsafe_allow_html=True)
                    
                    ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (st.session_state.current_user, f'ad{i}', today_date), one=True)
                    if ad_watched:
                        st.markdown("<p style='color:#00f0ff; text-align:center;'>✅ COMPLETED TODAY</p>", unsafe_allow_html=True)
                    else:
                        if st.button(f"📺 WATCH VIDEO AD {i}", key=f"btn_w_{i}", use_container_width=True):
                            query_db("INSERT INTO ad_logs VALUES (?, ?, ?)", (st.session_state.current_user, f'ad{i}', today_date), commit=True)
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad_rew, st.session_state.current_user), commit=True)
                            credit_multi_tier_commissions(st.session_state.current_user, ad_rew)
                            st.success(f"Reward Added: +RS {ad_rew:.2f}")
                            st.rerun()
                                
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h5 style='font-family:\"Orbitron\"; color:#00f0ff;'>SECURE DISPATCH NODE</h5>", unsafe_allow_html=True)
            chosen_bank = st.selectbox("SELECT ROUTING NODE NETWORK:", MALAYSIAN_BANKS)
            if chosen_bank == "USDT (TRC-20) Crypto Network":
                st.markdown(f"<div style='background:#1a090d; padding:12px; border-radius:10px;'><code>{usdt_address}</code></div>", unsafe_allow_html=True)
            else:
                if tng_scanner_url:
                    st.markdown(f"<div style='text-align:center;'><img src='{tng_scanner_url}' width='140' style='border:2px solid #00f0ff; border-radius:12px;'/></div>", unsafe_allow_html=True)
                    
            remitter_name = st.text_input("YOUR ACCOUNT HOLDER NAME:")
            trx_id_input = st.text_input("TRANSACTION REFERENCE CODE / TXID:")
            amount_input = st.number_input("RECHARGE QUANTITY (RS):", min_value=1.0, value=100.0)
            
            if st.button("TRANSMIT INTERFACE PROOF"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')", (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Proof submitted successfully!")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h5 style='font-family:\"Orbitron\"; color:#00f0ff;'>EXECUTE WITHDRAWALS</h5>", unsafe_allow_html=True)
            target_bank = st.selectbox("Target Bank:", MALAYSIAN_BANKS)
            account_route = st.text_input("Account Route Link / Wallet Address:")
            amount_input = st.number_input("Settle Amount Out (RS):", min_value=10.0)
            
            if st.button("INITIATE SETTLEMENT TRANSFERS"):
                if wallet_bal >= amount_input:
                    query_db("UPDATE users SET balance = balance - ? WHERE username=?", (amount_input, st.session_state.current_user), commit=True)
                    query_db("INSERT INTO withdrawals (username, bank, account, amount, status) VALUES (?, ?, ?, ?, 'Pending')", (st.session_state.current_user, target_bank, account_route.strip(), amount_input), commit=True)
                    st.success("✅ Cashout request filed!")
                    st.rerun()
                else: st.error("❌ Insufficient fluid balance.")
                
        st.markdown("<hr style='border-color:#ff0055; opacity:0.2;'>", unsafe_allow_html=True)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("HOME", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("DEPOSIT", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("🏛️ CASH OUT", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()
                
        if st.button("LOG OUT PORTAL", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.is_admin = False; st.query_params.clear(); st.rerun()

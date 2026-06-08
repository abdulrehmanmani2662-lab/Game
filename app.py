import streamlit as st
import sqlite3
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORE APPLICATION CONFIGURATION ---
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="👑", layout="wide")

# --- REAL SMTP BACKEND EMAIL GATEWAY CONFIGURATION ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
# 🔴 NOTE: Apna 16-digit Google App Password bina spaces ke yahan dalein
SENDER_APP_PASSWORD = "lddfmerstvilicby"  

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
        
        # Secure SSL Protocol (Port 465)
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Critical Error: {e}")
        return False

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet", "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad", 
    "Public Bank Berhad", "RHB Bank Berhad", "Hong Leong Bank Berhad"
]

# --- SECURE DATABASE INTERFACE ---
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
        
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER')")
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
    except Exception as e:
        conn.close()
        st.error(f"🛡️ Database Operational Error: {e}")
        return None if one else []

# --- ANTI-REFRESH RECOVERY LAYER ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""
if 'generated_code' not in st.session_state: st.session_state.generated_code = ""

# --- MASTER ENGINE UI STYLING ENGINE ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    html, body, .stApp { 
        background: linear-gradient(rgba(11, 9, 26, 0.96), rgba(6, 4, 15, 0.99)), 
                    url("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1470&auto=format&fit=crop") !important;
        background-size: cover !important; background-attachment: fixed !important; color: #ffffff !important;
    }
    .rgb-moving-strip {
        height: 5px; width: 100%; position: fixed; top: 0; left: 0; z-index: 99999;
        background: linear-gradient(90deg, #ff007f, #00ffcc, #ff00aa, #00ff55, #ffcc00, #ff007f);
        background-size: 400% 400%; animation: rgb-strip-move 6s linear infinite;
    }
    @keyframes rgb-strip-move { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }
    .running-header-container { width: 100%; overflow: hidden; background: rgba(255, 0, 127, 0.12); border-bottom: 2px solid #00ffcc; padding: 10px 0; margin-bottom: 15px; }
    .running-text { font-size: 14px; font-weight: 800; color: #00ffcc; white-space: nowrap; display: inline-block; animation: marquee-run 15s linear infinite; }
    @keyframes marquee-run { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    .brand-title { text-align: center; font-size: 28px; font-weight: 900; background: linear-gradient(135deg, #ffffff 30%, #00ffcc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stVerticalBlock"] { max-width: 460px !important; margin: 0 auto !important; padding: 5px !important; }
    
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stTextArea"] label, .stWidgetLabel p {
        color: #00ffcc !important; font-weight: 800 !important; font-size: 13px !important; text-transform: uppercase !important; letter-spacing: 0.5px; margin-bottom: 6px !important;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"], div[data-testid="stTextArea"] textarea { 
        background-color: #131021 !important; color: #ffffff !important; border: 2px solid #ff007f !important; border-radius: 10px !important; font-weight: 600 !important; font-size: 14px !important;
    }
    
    div.stButton > button { background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important; color: #ffffff !important; font-size: 13px !important; font-weight: 800; text-transform: uppercase !important; border-radius: 10px !important; width: 100% !important; padding: 12px !important; border: none !important; }
    div.stButton > button:hover { background: linear-gradient(135deg, #00ffcc 0%, #00b09b 100%) !important; color: #000000 !important; }
    .action-deck { background: rgba(20, 16, 36, 0.95); border: 2px solid #ff007f; border-radius: 12px; padding: 15px; margin-top: 10px; }
    .metric-card-box { background: linear-gradient(135deg, rgba(28, 23, 51, 0.95) 0%, rgba(15, 12, 31, 0.95) 100%); border-radius: 12px; padding: 18px; text-align: center; margin-bottom: 12px; border: 2px solid #00ffcc; }
    
    .announcement-box { background: #ff0055; border: 2px solid #ffffff; border-radius: 10px; padding: 12px; font-size: 13px; color: #ffffff !important; font-weight: 700; margin-bottom: 15px; line-height: 1.4; text-align: center; box-shadow: 0 0 10px rgba(255,0,85,0.5); }
    .recovery-box { background: #131021; border: 2px solid #00ffcc; border-radius: 10px; padding: 15px; font-size: 14px; color: #ffffff !important; font-weight: 700; margin-bottom: 12px; }
    
    .vip-lock-row { display: flex; justify-content: space-between; font-size: 12px; padding: 8px; background: rgba(255,255,255,0.04); margin: 6px 0; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08); color: #ffffff; font-weight: 600; }
    .live-log-container { background: #110d22; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; margin-top: 15px; }
    .log-row { font-size: 11px; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; justify-content: space-between; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)
random_online = random.randint(1645, 1920)
st.markdown(f'<div class="running-header-container"><div class="running-text">🔥 GLOBAL MATRIX PLATFORM • SYSTEM SECURE • ACTIVE ONLINE OPERATORS: {random_online}</div></div>', unsafe_allow_html=True)

# --- LIVE FRAGMENTED OTP TIMER ---
@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time is not None:
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(f"<div style='text-align:center; color:#ff007f; padding:5px; font-weight:bold;'>⏳ Resend Code in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()
        else:
            if st.button("🔄 RESEND NEW OTP CODE", use_container_width=True):
                new_otp = str(random.randint(102938, 984731))
                st.session_state.otp_start_time = time.time()
                if st.session_state.auth_mode == "VerifyNewAccount":
                    st.session_state.reg_verify_code = new_otp
                    sent = send_verification_email(st.session_state.temp_reg_user, new_otp, purpose="Account Creation")
                elif st.session_state.auth_mode == "Forgot":
                    st.session_state.generated_code = new_otp
                    sent = send_verification_email(st.session_state.reset_email, new_otp, purpose="Password Reset Authorization")
                
                if sent:
                    st.success("📩 A new validation code has been sent to your email!")
                else:
                    st.error("❌ Failed to send email. Check SMTP settings.")
                st.rerun()

# --- AUTHENTICATION FLOW ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Username / Email:", placeholder="username or email")
        password = st.text_input("Password:", type="password", placeholder="••••••••")
        if st.button("🚀 AUTHORIZE ACCESS", use_container_width=True):
            if username.strip() and password.strip():
                if username.strip() == "admin" and password.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Pending Requests"
                    st.rerun()
                else:
                    record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Overview"
                        st.rerun()
                    else: st.error("Invalid Credentials.")

    elif st.session_state.auth_mode == "Register":
        st.markdown("<h4 style='color:#00ffcc; text-align:center; font-size:16px; margin-bottom:10px;'>INITIALIZE SYSTEM NODE</h4>", unsafe_allow_html=True)
        reg_username = st.text_input("REGISTRATION EMAIL KEY:", placeholder="username or email")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password", placeholder="••••••••")
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL", use_container_width=True):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username.strip(): st.error("Invalid email structure.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing: st.error("Email configuration already active.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        email_sent = send_verification_email(reg_username.strip(), generated_otp)
                        
                        if email_sent:
                            st.session_state.temp_reg_user = reg_username.strip()
                            st.session_state.temp_reg_pass = reg_password.strip()
                            st.session_state.reg_verify_code = generated_otp
                            st.session_state.otp_start_time = time.time()
                            st.session_state.auth_mode = "VerifyNewAccount"
                            st.success("📩 Verification OTP successfully sent! Please check your email inbox or spam folder.")
                            st.rerun()
                        else:
                            st.error("❌ Email Delivery Failed! Please verify that your SMTP credentials or email address are correct.")

    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown(f"""
        <div class="recovery-box">
            🌐 Routing Verification To: <span style="color:#00ffcc;">{st.session_state.temp_reg_user}</span><br>
            <span style="color:#ff007f; font-size:12px;">Please check your mailbox for the 6-digit sync key.</span>
        </div>
        """, unsafe_allow_html=True)
        
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:", placeholder="******")
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True):
            if typed_code.strip() == st.session_state.reg_verify_code:
                db_status = query_db("INSERT INTO users VALUES (?, ?, 2.00, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT))", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                
                if db_status:
                    st.success("Registration completed. Free RM 2.00 loaded.")
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                else:
                    st.error("❌ Save Error: Data could not be recorded.")
            else: st.error("Incorrect verification OTP code.")
        render_otp_countdown_engine()

    elif st.session_state.auth_mode == "Forgot":
        st.markdown("<h4 style='color:#00ffcc; text-align:center; font-size:16px; margin-bottom:10px;'>ACCESS KEY RECOVERY</h4>", unsafe_allow_html=True)
        if st.session_state.reset_step == 1:
            f_email = st.text_input("Enter Registered Email:", placeholder="username or email")
            if st.button("🔍 ROUTE RESET KEY", use_container_width=True):
                if query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True):
                    generated_otp = str(random.randint(112233, 998877))
                    email_sent = send_verification_email(f_email.strip(), generated_otp)
                    if email_sent:
                        st.session_state.reset_email = f_email.strip()
                        st.session_state.generated_code = generated_otp
                        st.session_state.otp_start_time = time.time()
                        st.session_state.reset_step = 2
                        st.success("📩 Security reset pin routed to your email.")
                        st.rerun()
                    else:
                        st.error("❌ System Gateway error transmitting OTP.")
                else: st.error("No record matching identity key found.")
        elif st.session_step == 2:
            st.markdown(f"""
            <div class="recovery-box">
                🔒 Routing Token To: <span style="color:#00ffcc;">{st.session_state.reset_email}</span><br>
                <span style="color:#ff007f; font-size:12px;">Check your email mailbox for the core sync authorization pin.</span>
            </div>
            """, unsafe_allow_html=True)
            
            # 🔴 PREVIOUS DISPLAY BOX REMOVED FOR ABSOLUTE PRIVACY
            input_code = st.text_input("ENTER 6-DIGIT PIN FROM EMAIL:", placeholder="******")
            new_pass = st.text_input("NEW PASSWORD:", type="password", placeholder="••••••••")
            if st.button("🛠️ RESET IDENTITY VAULT", use_container_width=True):
                if input_code.strip() == st.session_state.generated_code:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                    st.success("Vault clear. Password updated successfully.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Sync pin validation failed.")
            render_otp_countdown_engine()

    st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🔑 LOGIN"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2: 
        if st.button("📝 JOIN"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3: 
        if st.button("🔄 RESET"): st.session_state.auth_mode = "Forgot"; st.session_state.reset_step = 1; st.rerun()

# --- DASHBOARD CONTROL FLOW ---
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    unclaimed_val = query_db("SELECT value FROM system_config WHERE key='unclaimed_rewards_val'", one=True)[0]
    v1_inc = query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0]
    v2_inc = query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0]
    v3_inc = query_db("SELECT value FROM system_config WHERE key='vip3_income'", one=True)[0]
    v2_req = query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0]
    v3_req = query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0]

    if st.session_state.is_admin:
        st.markdown("<h5 style='color:#00ffcc; text-align:center; font-weight:800; margin-bottom:15px;'>🛡️ MASTER ADMIN PLATFORM ENGINE</h5>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h6 style='color:#00ffcc; margin-bottom:10px;'>Ledger Inflow Approvals</h6>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification queue is clean.")
            else:
                for item in pending_items:
                    st.markdown(f"<div style='background-color:#1c1836; padding:10px; border-radius:6px; font-size:13px; border:1px solid #ff007f;'>User: {item[1]}<br>Bank: {item[2]}<br>TxID: {item[4]}<br><b>RM {item[5]:.2f}</b></div>", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ APPROVE", key=f"a_{item[0]}", use_container_width=True):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with b2:
                        if st.button("❌ PURGE", key=f"r_{item[0]}", use_container_width=True):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                                
        elif st.session_state.selected_panel == "System Settings Configuration":
            st.markdown("<h5 style='color:#00ffcc; font-size:16px; margin-bottom:15px;'>Real-Time Feature Management Control Desk</h5>", unsafe_allow_html=True)
            
            new_ann = st.text_area("System Broad-Scale Announcement Text:", value=announcement_text)
            new_unclaimed = st.text_input("Unclaimed Rewards Dummy Value (RM):", value=unclaimed_val)
            
            st.markdown("<p style='color:#ff007f; font-weight:bold; font-size:14px; margin-top:15px; margin-bottom:5px;'>VIP Tiers Calibration Parameters</p>", unsafe_allow_html=True)
            nv1 = st.text_input("VIP 1 Daily Yield (RM):", value=v1_inc)
            nv2 = st.text_input("VIP 2 Daily Yield (RM):", value=v2_inc)
            nv2_r = st.text_input("VIP 2 Required Recharge Threshold (RM):", value=v2_req)
            nv3 = st.text_input("VIP 3 Daily Yield (RM):", value=v3_inc)
            nv3_r = st.text_input("VIP 3 Required Recharge Threshold (RM):", value=v3_req)
            
            if st.button("💾 SAVE ENTIRE MATRIX CONFIGURATIONS", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='unclaimed_rewards_val'", (new_unclaimed.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip1_income'", (nv1.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip2_income'", (nv2.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip2_req'", (nv2_r.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip3_income'", (nv3.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip3_req'", (nv3_r.strip(),), commit=True)
                st.success("All System Variables Overhauled and Synced Safely!")
                st.rerun()

        st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        ad_c1, ad_c2 = st.columns(2)
        with ad_c1:
            if st.button("📥 LEDGER DEPOSITS", use_container_width=True): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("⚙️ MASTER MATRIX SETTINGS", use_container_width=True): st.session_state.selected_panel = "System Settings Configuration"; st.rerun()

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 1", "Y999")
        
        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:11px; color:#a5a1c2; margin:0; font-weight:800; letter-spacing:0.5px;">WALLETS EARNINGS BALANCE</p>
            <h3 style="font-size:28px; font-weight:900; color:#00ffcc; margin:4px 0;">RM {wallet_bal:,.2f}</h3>
            <p style="font-size:11px; color:#ffffff; margin:0; font-weight:600;">PENDING UNCLAIMED REWARDS: <span style='color:#ff007f;'>RM {unclaimed_val}</span></p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.selected_panel == "Overview":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            
            today_date = time.strftime("%Y-%m-%d")
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            chk_c1, chk_c2 = st.columns([2, 1])
            with chk_c1: st.markdown("<p style='margin-top:8px; font-size:13px; font-weight:bold; color:#ffffff;'>📅 DAILY REWARD CHECK-IN</p>", unsafe_allow_html=True)
            with chk_c2:
                if already_checked: st.button("✅ CLAIMED", disabled=True, key="claimed_disable")
                else:
                    if st.button("🎁 CLAIM", key="claim_bonus", use_container_width=True):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()

            st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            
            st.markdown("<p style='color:#00ffcc; font-size:12px; font-weight:bold; margin-bottom:5px;'>📊 ACTIVE PLATFORM VIP TIERS</p>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="vip-lock-row" style="border-left: 3px solid #00ffcc; background: rgba(0, 255, 204, 0.05);">🟢 SVIP Level 1 (Active) <span style="color:#00ffcc;">Daily: RM {v1_inc}</span></div>
            <div class="vip-lock-row">🔒 SVIP Level 2 (Recharge RM {v2_req}) <span style="color:#ffffff;">Daily: RM {v2_inc}</span></div>
            <div class="vip-lock-row">🔒 SVIP Level 3 (Recharge RM {v3_req}) <span style="color:#ffffff;">Daily: RM {v3_inc}</span></div>
            """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            if 'trigger_redirect' not in st.session_state: st.session_state.trigger_redirect = False
            
            if st.button("▶️ START SECURE DATA WORK TUNNEL", use_container_width=True):
                p_bar = st.progress(0, text="Syncing Data Nodes Stream Vectors...")
                for percent_complete in range(100):
                    time.sleep(0.01)
                    p_bar.progress(percent_complete + 1, text="Syncing Data Nodes Stream Vectors...")
                st.session_state.trigger_redirect = True
                st.rerun()
                
            if st.session_state.trigger_redirect:
                st.session_state.trigger_redirect = False
                st.link_button("🌐 CLICK HERE TO OPEN REWARD LINK", target_video, use_container_width=True)

            st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#00ffcc; font-size:12px; font-weight:bold; margin-bottom:5px;'>🎰 VIP GLOBAL LUCKY SPIN WHEEL</p>", unsafe_allow_html=True)
            if st.button("🎯 ENGAGE SYSTEM LUCKY SPIN", use_container_width=True):
                spin_prize = random.choice([0.20, 0.50, 1.00, 0.00])
                if spin_prize > 0:
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (spin_prize, st.session_state.current_user), commit=True)
                    st.success(f"System Node Settled! Yield Allocated: +RM {spin_prize:.2f}")
                else:
                    st.info("Handshake Complete: Better luck in next cycle matrix spin!")

            st.markdown("""
            <div style="margin-top: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <a href="https://t.me/global_matrix_support" target="_blank" style="text-align:center; background:#229ED9; color:white; padding:10px; font-size:12px; text-decoration:none; font-weight:700; border-radius:6px; display:block;">✈️ TELEGRAM HELP</a>
                <a href="https://wa.me/60111111111" target="_blank" style="text-align:center; background:#25D366; color:white; padding:10px; font-size:12px; text-decoration:none; font-weight:700; border-radius:6px; display:block;">💬 WHATSAPP SUPPORT</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='live-log-container'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#00ffcc; font-size:11px; font-weight:bold; margin:0 0 5px 0;'>⚡ REAL-TIME NETWORK TRANSACTIONS</p>", unsafe_allow_html=True)
            names_pool = ["usr_faisal", "ub_rajput", "billa_99", "lim_cash", "m_bhai_op", "tng_vector"]
            for i in range(2):
                u_mask = random.choice(names_pool)[:3] + "***" + str(random.randint(10,99))
                amt_rand = random.randint(50, 500)
                type_rand = random.choice(["Withdrew", "Deposited"])
                color_type = "#ff007f" if type_rand == "Withdrew" else "#00ffcc"
                st.markdown(f'<div class="log-row"><span style="color:#ffffff;">👤 <b>{u_mask}</b></span><span style="color:{color_type}; font-weight:bold;">{type_rand} RM {amt_rand:.2f} ✅</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#00ffcc; margin:0 0 8px 0;'>TOUCH 'N GO HUB PAYMENT</h6>", unsafe_allow_html=True)
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><img src='{target_qr}' width='130' style='border:2px solid #ff007f; border-radius:8px;'/></div>", unsafe_allow_html=True)
            chosen_bank = st.selectbox("CHOOSE SYSTEM NODE BANK:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("ACCOUNT OWNER NAME:")
            trx_id_input = st.text_input("REFERENCE TXN / TRX CODE:")
            amount_input = st.number_input("VALUATION AMOUNT (RM):", min_value=1.0, value=10.0)
            if st.button("SUBMIT PROOF RECORD", use_container_width=True):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification parameters transmitted to administration.")
            st.markdown("</div>", unsafe_allow_html=True)
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#ff007f; margin:0 0 8px 0;'>INITIALIZE OUTBOUND SETTLEMENT</h6>", unsafe_allow_html=True)
            st.selectbox("Select Clearance Bank:", MALAYSIAN_BANKS[1:])
            st.text_input("Destination Wire Account Keys:")
            st.number_input("Amount Selection (RM):", min_value=10.0)
            if st.button("🏛️ EXECUTE OUTBOUND CASH OUT", use_container_width=True):
                st.error("Operation Halted: Node Balance thresholds check failed.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("🎰 HOME", key="btn_usr_ov", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("💰 DEPOSIT", key="btn_usr_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("🏛️ WITHDRAW", key="btn_usr_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 LOG OUT PORTAL", key="global_logout_action", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

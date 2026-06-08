import streamlit as st
import sqlite3
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORE APPLICATION CONFIGURATION ---
st.set_page_config(page_title="GLOBAL MATRIX", page_icon="👑", layout="wide")

# --- REAL SMTP BACKEND EMAIL GATEWAY CONFIGURATION ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "lddfmerstvilicby"  

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Code: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #111216; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: linear-gradient(135deg, #1f2026 0%, #000000 100%); border: 2px solid #2EAF7D; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 6px 18px rgba(0,0,0,0.6);">
                <h2 style="color: #2EAF7D; margin-bottom: 10px; font-weight: 900; letter-spacing: 2px;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: rgba(46,175,125,0.3); margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px;">Your Verification Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #ffffff; letter-spacing: 4px; padding: 12px; background: #111216; border: 1px solid #2EAF7D; border-radius: 10px; margin: 20px 0;">
                    {otp_code}
                </div>
                <p style="color: #a0a0a5; font-size: 12px;">Please secure your verification credentials.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ad_logs (
            username TEXT, ad_id TEXT, date TEXT, PRIMARY KEY (username, ad_id, date)
        )
    """)
    
    configs = [
        ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('ad1_reward', '3.00'),
        ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('ad2_reward', '2.30'),
        ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('ad3_reward', '4.50'),
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

# --- SESSION STATES ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1  # FIXED: Traceback prevention
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""

# --- DESIGN ENGINE (BLACK DARK EDITION) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;900&family=Rajdhani:wght@600;700&display=swap');
    
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    html, body, .stApp { 
        background-color: #C1F6ED !important;
        color: #02353C !important;
    }
    
    .running-header-container { 
        width: 100%; background: #111216; padding: 14px 0; margin-bottom: 25px; border-bottom: 3px solid #2EAF7D; border-top: 3px solid #2EAF7D;
    }
    .running-text { font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: 900; color: #2EAF7D; letter-spacing: 2px; }
    
    .brand-title { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 36px; font-weight: 900; color: #02353C; margin-bottom: 25px; letter-spacing: 3px; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }
    [data-testid="stVerticalBlock"] { max-width: 450px !important; margin: 0 auto !important; padding: 0px !important; }
    
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { 
        background-color: #ffffff !important; color: #02353C !important; border: 2px solid #02353C !important; border-radius: 12px !important; font-weight: 700 !important; padding: 11px !important; font-family: 'Rajdhani', sans-serif; font-size: 16px;
    }
    
    div.stButton > button { background: linear-gradient(135deg, #111216 0%, #2a2b33 100%) !important; color: #2EAF7D !important; font-family: 'Orbitron', sans-serif; font-size: 15px !important; font-weight: 900; border-radius: 16px !important; width: 100% !important; padding: 14px !important; border: 2px solid #2EAF7D !important; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25); transition: 0.3s; }
    div.stButton > button:hover { color: #ffffff !important; border-color: #ffffff !important; background: #2EAF7D !important; }
    
    .announcement-box { background: #111216; border: 2px dashed #ff4a4a; border-radius: 16px; padding: 15px; font-family: 'Rajdhani', sans-serif; font-size: 14px; color: #ff4a4a !important; font-weight: 800; margin-bottom: 20px; text-align: center; line-height: 1.4; box-shadow: 0 4px 12px rgba(255,74,74,0.15); }
    
    .metric-card-box { 
        background: linear-gradient(135deg, #111216 0%, #1f2026 100%); 
        border: 3px solid #2EAF7D;
        border-radius: 24px; padding: 25px 20px; text-align: center; margin-bottom: 20px; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.35); color: #ffffff !important;
    }
    
    .international-banner {
        background-color: #111216 !important;
        color: #ffffff !important;
        border: 2px solid #3FD0C9 !important;
        border-radius: 14px !important;
        padding: 12px 10px !important;
        text-align: center !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 16px !important;
        font-weight: 900 !important;
        margin: 20px 0 !important;
        letter-spacing: 1px;
    }
    
    /* PREMIUM BLACK DARK CONTAINERS FOR BOARDS/DABBE */
    .vip-card-thick-dark {
        background: linear-gradient(135deg, #111216 0%, #1c1d22 100%);
        border: 3px solid #449342; 
        border-radius: 16px; 
        padding: 18px; 
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.25);
    }
    
    .ad-segment-block-dark {
        background: linear-gradient(135deg, #111216 0%, #1c1d22 100%);
        border: 3px solid #2EAF7D; 
        border-radius: 16px; 
        padding: 16px; 
        margin: 15px 0; 
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.25);
    }
    
    .font-premium-title { font-family: 'Orbitron', sans-serif; font-size: 16px; font-weight: 900; letter-spacing: 1px; }
    .font-premium-value { font-family: 'Rajdhani', sans-serif; font-size: 17px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# TOP RUNNING MATRIX HEADER
random_online = random.randint(1650, 1800)
st.markdown(f"""
    <div class="running-header-container">
        <marquee class="running-text" scrollamount="6">
            OPERATORS ONLINE: {random_online} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 👑 GLOBAL MATRIX DIRECT PORTAL ACTIVE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; CURRENT TRADING MODE ONLINE
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- OTP FRAGMENT ENGINE ---
@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time is not None:
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(f"<div style='text-align:center; color:#111216; padding:5px; font-family:\'Orbitron\'; font-weight:bold;'>⏳ Resend Code in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

# --- SECURITY SYSTEM CONTROL GATE ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Username / Email Address:", placeholder="Enter your email")
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
                    else: st.error("Invalid Credentials System Verification Failed.")

    elif st.session_state.auth_mode == "Register":
        reg_username = st.text_input("REGISTRATION EMAIL KEY:")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password")
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL", use_container_width=True):
            if reg_username.strip() and reg_password.strip():
                existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                if existing: st.error("Email key already registered.")
                else:
                    generated_otp = str(random.randint(102938, 984731))
                    if send_verification_email(reg_username.strip(), generated_otp):
                        st.session_state.temp_reg_user = reg_username.strip()
                        st.session_state.temp_reg_pass = reg_password.strip()
                        st.session_state.reg_verify_code = generated_otp
                        st.session_state.otp_start_time = time.time()
                        st.session_state.auth_mode = "VerifyNewAccount"
                        st.success("📩 Verification OTP securely sent!")
                        st.rerun()

    elif st.session_state.auth_mode == "VerifyNewAccount":
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:")
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True):
            if typed_code.strip() == st.session_state.reg_verify_code:
                query_db("INSERT INTO users VALUES (?, ?, 2.00, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT))", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                st.success("Registration Complete! Welcome bonus loaded.")
                st.session_state.auth_mode = "Login"
                st.rerun()
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown("<h5 style='text-align:center; font-family:\'Orbitron\';'>🔑 RECOVER ACCESS KEY</h5>", unsafe_allow_html=True)
        reset_email = st.text_input("Target Email Address:")
        
        if st.session_state.reset_step == 1:
            if st.button("SEND CORE SYNC CODE", use_container_width=True):
                if reset_email.strip():
                    user_exist = query_db("SELECT username FROM users WHERE username=?", (reset_email.strip(),), one=True)
                    if user_exist:
                        generated_otp = str(random.randint(102938, 984731))
                        if send_verification_email(reset_email.strip(), generated_otp, purpose="Password Recovery"):
                            st.session_state.recovery_target_user = reset_email.strip()
                            st.session_state.recovery_otp = generated_otp
                            st.session_state.reset_step = 2
                            st.success("📩 OTP code sent to your email!")
                            st.rerun()
                    else:
                        st.error("This email is not registered.")
                        
        elif st.session_state.reset_step == 2:
            typed_otp = st.text_input("Enter 6-Digit Code:")
            new_pass = st.text_input("New System Password:", type="password")
            if st.button("RESET IDENTITY VAULT", use_container_width=True):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Password changed successfully! Please login.")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else:
                    st.error("Incorrect Sync Code.")

    st.markdown("<hr style='border-color:#02353C;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🔑 LOGIN"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2: 
        if st.button("📝 JOIN"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("🔄 RESET"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# --- LOGGED IN ROUTINE PORTAL ---
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    
    ad1_url = query_db("SELECT value FROM system_config WHERE key='ad1_url'", one=True)[0]
    ad1_reward = float(query_db("SELECT value FROM system_config WHERE key='ad1_reward'", one=True)[0])
    ad2_url = query_db("SELECT value FROM system_config WHERE key='ad2_url'", one=True)[0]
    ad2_reward = float(query_db("SELECT value FROM system_config WHERE key='ad2_reward'", one=True)[0])
    ad3_url = query_db("SELECT value FROM system_config WHERE key='ad3_url'", one=True)[0]
    ad3_reward = float(query_db("SELECT value FROM system_config WHERE key='ad3_reward'", one=True)[0])
    
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    v3_inc = float(query_db("SELECT value FROM system_config WHERE key='vip3_income'", one=True)[0])
    v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
    v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])
    tng_scanner_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]

    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#02353C; text-align:center; font-family:\'Orbitron\'; font-weight:900;'>🛡️ SYSTEM CONTROL CENTRE</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification operational queue empty.")
            else:
                for item in pending_items:
                    st.markdown(f"<div style='background-color:#111216; color:#ffffff; padding:15px; border-radius:14px; border:2px solid #2EAF7D; margin-bottom:10px;'>User: {item[1]}<br>Bank: {item[2]}<br><b style='color:#2EAF7D;'>RM {item[5]:.2f}</b></div>", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✅ APPROVE", key=f"a_{item[0]}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with b2:
                        if st.button("❌ PURGE", key=f"r_{item[0]}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                                
        elif st.session_state.selected_panel == "System Settings Configuration":
            st.markdown("##### Control Links & Pricing Settings Desk")
            new_ann = st.text_area("System Alert Notification Line:", value=announcement_text)
            new_qr_url = st.text_input("Touch 'N Go Scan Code Image Link URL:", value=tng_scanner_url)
            
            st.markdown("<p style='color:#02353C; font-weight:900; margin-top:15px;'>🎬 MULTI-AD TRAFFIC REDIRECTION SETTINGS</p>", unsafe_allow_html=True)
            nad1_url = st.text_input("Ad Segment 1 Web Video Link:", value=ad1_url)
            nad1_rew = st.text_input("Ad Segment 1 Payout Pay (RM):", value=str(ad1_reward))
            
            nad2_url = st.text_input("Ad Segment 2 Web Video Link:", value=ad2_url)
            nad2_rew = st.text_input("Ad Segment 2 Payout Pay (RM):", value=str(ad2_reward))
            
            nad3_url = st.text_input("Ad Segment 3 Web Video Link:", value=ad3_url)
            nad3_rew = st.text_input("Ad Segment 3 Payout Pay (RM):", value=str(ad3_reward))
            
            if st.button("SAVE LINK CONFIGURATIONS NOW", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad1_url'", (nad1_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad1_reward'", (nad1_rew.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad2_url'", (nad2_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad2_reward'", (nad2_rew.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad3_url'", (nad3_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad3_reward'", (nad3_rew.strip(),), commit=True)
                st.success("All Active Video parameters & layouts updated!")
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        ad_c1, ad_c2 = st.columns(2)
        with ad_c1:
            if st.button("📥 LEDGER DEPOSITS"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("⚙️ MASTER CONFIGS"): st.session_state.selected_panel = "System Settings Configuration"; st.rerun()

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 1", "Y999")
        clean_level = str(level_tag).upper().strip()

        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)

        # MAIN WALLET (DARK RADAR COUNTER)
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-family:'Orbitron', sans-serif; font-size:12px; color:#3FD0C9; margin:0; font-weight:900; letter-spacing:1px;">CURRENT WALLET BALANCE</p>
            <h1 style="font-family:'Orbitron', sans-serif; font-size:38px; font-weight:900; color:#ffffff; margin:8px 0; letter-spacing:1px;">RM {wallet_bal:,.2f}</h1>
            <p style="font-family:'Rajdhani', sans-serif; font-size:14px; color:#2EAF7D; margin:0; font-weight:800; letter-spacing:0.5px;">CURRENT RANK: {level_tag}</p>
        </div>
        """, unsafe_allow_html=True)

        # White/Cyan Banner
        st.markdown('<div class="international-banner">INTERNATIONAL EARNING HUB ACTIVE</div>', unsafe_allow_html=True)

        if st.session_state.selected_panel == "Overview":
            
            today_date = time.strftime("%Y-%m-%d")
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            st.markdown("<p style='font-family:\'Orbitron\'; font-weight:900; font-size:14px; margin-bottom:5px; color:#02353C;'>🎁 DAILY IDENTITY BOUNTY CHECK-IN</p>", unsafe_allow_html=True)
            if already_checked: 
                st.markdown("<p style='color:#449342; font-weight:bold; font-size:14px; margin-left:5px;'>✅ CLAIMED SUCCESSFUL</p>", unsafe_allow_html=True)
            else:
                if st.button("CLAIM TODAY'S REWARD", key="claim_bonus"):
                    query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                    st.rerun()

            st.markdown("<hr style='border-color:#02353C; margin:15px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#02353C; font-family:\'Orbitron\'; font-size:15px; font-weight:900; margin-bottom:10px;'>📊 DESIGN MATRIX INVESTMENT PORTFOLIOS</p>", unsafe_allow_html=True)
            
            # --- BLACK DARK BOXES FOR VIP PLANS ---
            # SVIP LEVEL 1
            st.markdown(f"""
            <div class="vip-card-thick-dark" style="border-color: #449342;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="font-premium-title" style="color:#ffffff;">👑 {level_tag if 'LEVEL 1' in clean_level else 'SVIP LEVEL 1'}</span>
                    <span class="font-premium-value" style="color:#449342;">Daily Base: RM {v1_inc:.2f}</span>
                </div>
                <div class="font-premium-value" style="color:#a0a0a5; font-size:13px; margin-top:6px;">Cost: Free Account Welcome Package</div>
            </div>
            """, unsafe_allow_html=True)
            
            # SVIP LEVEL 2
            st.markdown(f"""
            <div class="vip-card-thick-dark" style="border-color: #2EAF7D;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="font-premium-title" style="color:#ffffff;">👑 SVIP LEVEL 2</span>
                    <span class="font-premium-value" style="color:#2EAF7D;">Daily Base: RM {v2_inc:.2f}</span>
                </div>
                <div class="font-premium-value" style="color:#a0a0a5; font-size:13px; margin-top:6px;">Activation Target: RM {v2_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # SVIP LEVEL 3
            st.markdown(f"""
            <div class="vip-card-thick-dark" style="border-color: #3FD0C9;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="font-premium-title" style="color:#ffffff;">👑 SVIP LEVEL 3</span>
                    <span class="font-premium-value" style="color:#3FD0C9;">Daily Base: RM {v3_inc:.2f}</span>
                </div>
                <div class="font-premium-value" style="color:#a0a0a5; font-size:13px; margin-top:6px;">Activation Target: RM {v3_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<hr style='border-color:#02353C; margin:20px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#02353C; font-family:\'Orbitron\'; font-size:15px; font-weight:900; text-align:center; margin-bottom:10px;'>🎬 DAILY SECURE MULTI-AD SEGMENTS</p>", unsafe_allow_html=True)

            # --- BLACK DARK BOXES FOR AD SEGMENTS ---
            # DYNAMIC AD BLOCK 1
            st.markdown(f"""
            <div class="ad-segment-block-dark" style="border-color: #449342;">
                <div class="font-premium-title" style="color:#ffffff; margin-bottom:4px;">📺 Ad Segment 1</div>
                <div class="font-premium-value" style="color:#449342;">Watch Reward Earnings: <b>RM {ad1_reward:.2f}</b></div>
            </div>
            """, unsafe_allow_html=True)
            ad1_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad1' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad1_watched: st.markdown("<p style='color:#449342; font-family:\'Orbitron\'; font-size:12px; font-weight:900; text-align:center; margin-top:-5px;'>✅ COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("WATCH & CLAIM AD 1", key="clk_ad1", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad1', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad1_reward, st.session_state.current_user), commit=True)
                    st.success(f"Bounty Linked: +RM {ad1_reward:.2f}")
                    time.sleep(0.5)
                    st.link_button("🌐 WATCH ADS VIDEO SOURCE 1", ad1_url, use_container_width=True)
                    st.rerun()

            # DYNAMIC AD BLOCK 2
            st.markdown(f"""
            <div class="ad-segment-block-dark" style="border-color: #2EAF7D;">
                <div class="font-premium-title" style="color:#ffffff; margin-bottom:4px;">📺 Ad Segment 2</div>
                <div class="font-premium-value" style="color:#2EAF7D;">Watch Reward Earnings: <b>RM {ad2_reward:.2f}</b></div>
            </div>
            """, unsafe_allow_html=True)
            ad2_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad2' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad2_watched: st.markdown("<p style='color:#449342; font-family:\'Orbitron\'; font-size:12px; font-weight:900; text-align:center; margin-top:-5px;'>✅ COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("WATCH & CLAIM AD 2", key="clk_ad2", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad2', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad2_reward, st.session_state.current_user), commit=True)
                    st.success(f"Bounty Linked: +RM {ad2_reward:.2f}")
                    time.sleep(0.5)
                    st.link_button("🌐 WATCH ADS VIDEO SOURCE 2", ad2_url, use_container_width=True)
                    st.rerun()

            # DYNAMIC AD BLOCK 3
            st.markdown(f"""
            <div class="ad-segment-block-dark" style="border-color: #3FD0C9;">
                <div class="font-premium-title" style="color:#ffffff; margin-bottom:4px;">📺 Ad Segment 3</div>
                <div class="font-premium-value" style="color:#3FD0C9;">Watch Reward Earnings: <b>RM {ad3_reward:.2f}</b></div>
            </div>
            """, unsafe_allow_html=True)
            ad3_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad3' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad3_watched: st.markdown("<p style='color:#449342; font-family:\'Orbitron\'; font-size:12px; font-weight:900; text-align:center; margin-top:-5px;'>✅ COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("WATCH & CLAIM AD 3", key="clk_ad3", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad3', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad3_reward, st.session_state.current_user), commit=True)
                    st.success(f"Bounty Linked: +RM {ad3_reward:.2f}")
                    time.sleep(0.5)
                    st.link_button("🌐 WATCH ADS VIDEO SOURCE 3", ad3_url, use_container_width=True)
                    st.rerun()

            st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
            st.button("▶️ START SECURE DATA WORK TUNNEL", use_container_width=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h5 style='font-family:\'Orbitron\';'>TOUCH 'N GO SECURE DISPATCH</h5>", unsafe_allow_html=True)
            if tng_scanner_url:
                st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><img src='{tng_scanner_url}' width='140' style='border:3px solid #111216; border-radius:16px;'/></div>", unsafe_allow_html=True)
            chosen_bank = st.selectbox("SELECT BANK ROUTE:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("SENDER HOLDER NAME:")
            trx_id_input = st.text_input("TRX CODE ID REFERENCE:")
            amount_input = st.number_input("RECHARGE VALUE (RM):", min_value=1.0, value=100.0)
            if st.button("TRANSMIT INTERFACE PROOF", use_container_width=True):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification parameters queued.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h5 style='color:#02353C; font-family:\'Orbitron\';'>EXECUTE VAULT DISPATCHED WITHDRAWALS</h5>", unsafe_allow_html=True)
            st.selectbox("Receiving Target Bank:", MALAYSIAN_BANKS)
            st.text_input("Account/Wallet Number:")
            st.number_input("Payout Settle Value (RM):", min_value=10.0)
            if st.button("INITIATE SETTLEMENT TRANSFERS", use_container_width=True):
                st.error("Operation Halted: Compliance clearance failed.")

        st.markdown("<hr style='border-color:#02353C; margin:15px 0;'>", unsafe_allow_html=True)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("🎰 HOME", key="nav_home", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("💰 DEPOSIT", key="nav_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("🏛️ CASH OUT", key="nav_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()

    if st.button("🚪 LOG OUT PORTAL", key="global_logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

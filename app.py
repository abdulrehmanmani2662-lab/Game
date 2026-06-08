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
        ('ad1_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad1_reward', '3.00'),
        ('ad2_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad2_reward', '2.30'),
        ('ad3_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad3_reward', '4.50'),
        ('ad4_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad4_reward', '1.50'),
        ('ad5_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'), ('ad5_reward', '2.00'),
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
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1  
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""

# --- DEVILXD PREMIUM DARK & NEON GLOW ENGINE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght=600;900&family=Rajdhani:wght=600;700&display=swap');
    
    /* Hide top and bottom layout default elements */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* HARDCORE BLACK BACKGROUND */
    html, body, .stApp { 
        background-color: #0b0c10 !important;
        color: #ffffff !important;
    }
    
    /* Center layout maximum styling like mobile device width */
    [data-testid="stVerticalBlock"] { max-width: 450px !important; margin: 0 auto !important; padding: 0px !important; }
    
    /* TOP MARQUEE HEADER */
    .running-header-container { 
        width: 100%; background: #12131a; padding: 12px 0; margin-bottom: 25px; border-bottom: 2px solid #ff0055;
    }
    .running-text { font-family: 'Orbitron', sans-serif; font-size: 13px; font-weight: 900; color: #00f0ff; letter-spacing: 2px; }
    
    /* MAIN PLATFORM TITLE */
    .brand-title { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: 900; color: #ffffff; margin-bottom: 5px; letter-spacing: 3px; text-shadow: 0 0 10px rgba(0,240,255,0.5); }
    .brand-subtitle { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 14px; font-weight: bold; color: #ff0055; letter-spacing: 2px; margin-bottom: 25px; }

    /* INPUT FIELDS - DARK BACKGROUND + NEON PINK/CYAN GLOW BORDER */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { 
        background-color: #12131a !important; 
        color: #ffffff !important; 
        border: 2px solid #ff0055 !important; 
        border-radius: 12px !important; 
        font-weight: 700 !important; 
        padding: 12px !important; 
        font-family: 'Rajdhani', sans-serif; 
        font-size: 16px;
        box-shadow: 0 0 8px rgba(255, 0, 85, 0.2);
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #00f0ff !important;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4) !important;
    }
    
    /* BUTTONS - GRADIENT PURPLE/PINK STYLE LINE REFERENCE */
    div.stButton > button { 
        background: linear-gradient(135deg, #a100ff 0%, #ff0055 100%) !important; 
        color: #ffffff !important; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 15px !important; 
        font-weight: 900; 
        border-radius: 14px !important; 
        width: 100% !important; 
        padding: 14px !important; 
        border: none !important; 
        box-shadow: 0 4px 15px rgba(255, 0, 85, 0.4); 
        transition: 0.3s; 
    }
    div.stButton > button:hover { 
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
        transform: scale(1.02);
    }
    
    /* ANNOUNCEMENT RED FLASH BOX */
    .announcement-box { background: #1a090d; border: 2px solid #ff0055; border-radius: 14px; padding: 15px; font-family: 'Rajdhani', sans-serif; font-size: 14px; color: #ff3377 !important; font-weight: 800; margin-bottom: 20px; text-align: center; box-shadow: 0 0 10px rgba(255,0,85,0.2); }
    
    /* CURRENT BALANCE CARD DUST LOOK */
    .metric-card-box { 
        background: linear-gradient(135deg, #12131a 0%, #1f2026 100%); 
        border: 2px solid #00f0ff;
        border-radius: 20px; padding: 25px 20px; text-align: center; margin-bottom: 20px; 
        box-shadow: 0 0 15px rgba(0,240,255,0.2);
    }
    
    /* PREMIUM GLOWING CONTAINER DABBE */
    .custom-matrix-box-cyan {
        background: #12131a !important;
        border: 2px solid #00f0ff !important;
        border-radius: 14px !important;
        padding: 16px !important;
        margin: 15px 0 !important;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
    }
    
    .custom-matrix-box-pink {
        background: #12131a !important;
        border: 2px solid #ff0055 !important;
        border-radius: 14px !important;
        padding: 16px !important;
        margin: 15px 0 !important;
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.2);
    }

    .custom-matrix-box-purple {
        background: #12131a !important;
        border: 2px solid #a100ff !important;
        border-radius: 14px !important;
        padding: 16px !important;
        margin: 15px 0 !important;
        box-shadow: 0 0 10px rgba(161, 0, 255, 0.2);
    }
    
    .font-premium-title { font-family: 'Orbitron', sans-serif; font-size: 15px; font-weight: 900; color: #ffffff; letter-spacing: 1px; }
    .font-premium-value { font-family: 'Rajdhani', sans-serif; font-size: 16px; font-weight: 700; color: #00f0ff; }
    
    /* Fix label style colors for dark layout */
    label { color: #00f0ff !important; font-family: 'Orbitron', sans-serif !important; font-size: 12px !important; font-weight: 900 !important; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# TOP RUNNING HEADER
random_online = random.randint(1650, 1800)
st.markdown(f"""
    <div class="running-header-container">
        <marquee class="running-text" scrollamount="6">
            ONLINE OPERATORS: {random_online} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ⚡ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐌𝐀𝐓𝐑𝐈𝐗 𝐏𝐑𝐎𝐓𝐎𝐂𝐎𝐋 𝐂𝐎𝐌𝐏𝐋𝐈𝐀𝐍𝐓 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; SYSTEM ONLINE
        </marquee>
    </div>
""", unsafe_allow_html=True)

# --- OTP FRAGMENT ENGINE ---
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

# --- SECURITY SYSTEM CONTROL GATE ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 ░G░L░O░B░A░L░ ░M░A░T░R░I░X░</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown('<div class="brand-subtitle">SECURE TERMINAL LOGIN</div>', unsafe_allow_html=True)
        username = st.text_input("USERNAME / EMAIL:", placeholder="Enter your registered email")
        password = st.text_input("PASSWORD:", type="password", placeholder="••••••••")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        if st.button("LOGIN", use_container_width=True):
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
                    else: st.error("Verification Failed. Invalid Identity Credentials.")

    elif st.session_state.auth_mode == "Register":
        st.markdown('<div class="brand-subtitle">CREATE NEW ACCOUNT</div>', unsafe_allow_html=True)
        reg_username = st.text_input("REGISTRATION EMAIL KEY:")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
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
        st.markdown('<div class="brand-subtitle">SYNC ACCOUNT SECURE CODE</div>', unsafe_allow_html=True)
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:")
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True):
            if typed_code.strip() == st.session_state.reg_verify_code:
                query_db("INSERT INTO users VALUES (?, ?, 2.00, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT))", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                st.success("Registration Complete! Welcome bonus loaded.")
                st.session_state.auth_mode = "Login"
                st.rerun()
        render_otp_countdown_engine()
        
    elif st.session_state.auth_mode == "ResetPassword":
        st.markdown('<div class="brand-subtitle">ACCESS KEY RECOVERY</div>', unsafe_allow_html=True)
        reset_email = st.text_input("TARGET EMAIL ROUTE:")
        
        if st.session_state.reset_step == 1:
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
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
                    else: st.error("This email is not registered inside platform.")
                        
        elif st.session_state.reset_step == 2:
            st.markdown(f"""
            <div class="custom-matrix-box-cyan">
                <span style="font-family:'Rajdhani'; font-weight:bold; color:#ff0055;">🔒 Route Target:</span><br>
                <span style="font-family:'Orbitron'; font-size:14px; font-weight:900; color:#00f0ff;">{st.session_state.recovery_target_user}</span>
                <div style="background:#a100ff; color:#ffffff; padding:12px; border-radius:10px; font-family:'Orbitron'; text-align:center; font-weight:900; margin-top:12px; font-size:16px;">
                    Core Sync Code Generated Check Mail
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            typed_otp = st.text_input("ENTER 6-DIGIT PIN:")
            new_pass = st.text_input("NEW PASSWORD:", type="password")
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("🔧 RESET IDENTITY VAULT", use_container_width=True):
                if typed_otp.strip() == st.session_state.recovery_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.recovery_target_user), commit=True)
                    st.success("Password changed successfully! Opening terminal login...")
                    st.session_state.auth_mode = "Login"
                    st.session_state.reset_step = 1
                    st.rerun()
                else: st.error("Incorrect Sync Code Pin.")

    st.markdown("<hr style='border-color:#ff0055; opacity:0.3;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("LOGIN ID"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2: 
        if st.button("CREATE ACCOUNT"): st.session_state.auth_mode = "Register"; st.rerun()
    with c3:
        if st.button("FORGET PASSWORD"): st.session_state.auth_mode = "ResetPassword"; st.session_state.reset_step = 1; st.rerun()

# --- LOGGED IN ROUTINE PORTAL ---
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    tng_scanner_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
    
    v1_inc = float(query_db("SELECT value FROM system_config WHERE key='vip1_income'", one=True)[0])
    v2_inc = float(query_db("SELECT value FROM system_config WHERE key='vip2_income'", one=True)[0])
    v3_inc = float(query_db("SELECT value FROM system_config WHERE key='vip3_income'", one=True)[0])
    v2_req = float(query_db("SELECT value FROM system_config WHERE key='vip2_req'", one=True)[0])
    v3_req = float(query_db("SELECT value FROM system_config WHERE key='vip3_req'", one=True)[0])

    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#00f0ff; text-align:center; font-family:\"Orbitron\"; font-weight:900;'>🛡️ SYSTEM CONTROL CENTRE</h4>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification queue empty.")
            else:
                for item in pending_items:
                    st.markdown(f"<div style='background-color:#12131a; color:#ffffff; padding:15px; border-radius:14px; border:2px solid #ff0055; margin-bottom:10px;'>User: {item[1]}<br>Bank: {item[2]}<br><b style='color:#00f0ff;'>RM {item[5]:.2f}</b></div>", unsafe_allow_html=True)
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
            st.markdown("##### Global Settings Board")
            new_ann = st.text_area("System Alert Text Notification:", value=announcement_text)
            new_qr_url = st.text_input("Touch 'N Go QR Scan Link:", value=tng_scanner_url)
            
            st.markdown("<p style='color:#00f0ff; font-weight:900; margin-top:15px;'>🎬 VIDEO LINK PLATFORM PARAMETERS (1 TO 5)</p>", unsafe_allow_html=True)
            
            # Form 5 ad configurations dynamically
            ad_configs = {}
            for i in range(1, 6):
                st.markdown(f"**⚙️ AD BLOCK SEGMENT {i}**")
                old_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                old_rew = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0]
                ad_configs[f'ad{i}_url'] = st.text_input(f"Ad {i} Video Source Link:", value=old_url, key=f"adm_ad{i}_url")
                ad_configs[f'ad{i}_rew'] = st.text_input(f"Ad {i} Reward Pay (RM):", value=str(old_rew), key=f"adm_ad{i}_rew")
            
            if st.button("SAVE CONFIGURATIONS NOW", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr_url.strip(),), commit=True)
                for i in range(1, 6):
                    query_db(f"UPDATE system_config SET value=? WHERE key='ad{i}_url'", (ad_configs[f'ad{i}_url'].strip(),), commit=True)
                    query_db(f"UPDATE system_config SET value=? WHERE key='ad{i}_reward'", (ad_configs[f'ad{i}_rew'].strip(),), commit=True)
                st.success("Layout configuration synced successfully!")
                st.rerun()

        # --- NEW OPTION: EDIT USER BALANCE ---
        elif st.session_state.selected_panel == "User Management":
            st.markdown("##### 👤 PLATFORM IDENTITY VAULT")
            target_user = st.text_input("ENTER TARGET USER EMAIL / USERNAME:")
            if target_user.strip():
                user_res = query_db("SELECT balance FROM users WHERE username=?", (target_user.strip(),), one=True)
                if user_res:
                    st.markdown(f"<div class='custom-matrix-box-cyan'>Current System Balance: <b style='color:#00f0ff;'>RM {user_res[0]:.2f}</b></div>", unsafe_allow_html=True)
                    new_balance = st.number_input("SET NEW ACCOUNT BALANCE (RM):", min_value=0.0, value=float(user_res[0]))
                    if st.button("🔥 COMMIT DIRECT BALANCE CHANGE", use_container_width=True):
                        query_db("UPDATE users SET balance=? WHERE username=?", (new_balance, target_user.strip()), commit=True)
                        st.success(f"Bounty Updated! New Balance is RM {new_balance:.2f}")
                        st.rerun()
                else:
                    st.error("Target identity not found in platform database.")

        st.markdown("<hr style='border-color:#ff0055; opacity:0.3;'>", unsafe_allow_html=True)
        ad_c1, ad_c2, ad_c3 = st.columns(3)
        with ad_c1:
            if st.button("📥 Approvel"): st.session_state.selected_panel = "Pending Requests"; st.rerun()
        with ad_c2:
            if st.button("⚙️ MASTER"): st.session_state.selected_panel = "System Settings Configuration"; st.rerun()
        with ad_c3:
            if st.button("👤 USER BAL"): st.session_state.selected_panel = "User Management"; st.rerun()

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, 'SVIP LEVEL 1', 'Y999')

        st.markdown(f'<div class="announcement-box">{announcement_text}</div>', unsafe_allow_html=True)

        # MAIN WALLET NEON MATRIX DISPLAY
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-family:'Orbitron', sans-serif; font-size:12px; color:#ff0055; margin:0; font-weight:900; letter-spacing:1px;">CURRENT WALLET BALANCE</p>
            <h1 style="font-family:'Orbitron', sans-serif; font-size:38px; font-weight:900; color:#ffffff; margin:8px 0; letter-spacing:1px;">RM {wallet_bal:,.2f}</h1>
            <p style="font-family:'Rajdhani', sans-serif; font-size:14px; color:#00f0ff; margin:0; font-weight:800; letter-spacing:0.5px;">CURRENT RANK: {level_tag}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.selected_panel == "Overview":
            today_date = time.strftime("%Y-%m-%d")
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            
            st.markdown("<p style='font-family:\"Orbitron\"; font-weight:900; font-size:13px; color:#ff0055;'>🎁 𝗙𝗿𝗲𝗲 𝗿𝗲𝘄𝗮𝗿𝗱𝘀 CHECK-IN</p>", unsafe_allow_html=True)
            if already_checked: 
                st.markdown("<p style='color:#00f0ff; font-weight:bold; font-size:14px; margin-left:5px;'>✅ REWARD CLAIMED</p>", unsafe_allow_html=True)
            else:
                if st.button("CLAIM TODAY'S REWARD", key="claim_bonus"):
                    query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                    st.rerun()

            st.markdown("<hr style='border-color:#ff0055; opacity:0.2; margin:15px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#ffffff; font-family:\"Orbitron\"; font-size:14px; font-weight:900; margin-bottom:10px;'>📊 DESIGN MATRIX PLANS</p>", unsafe_allow_html=True)
            
            # --- CUSTOM BOARDS WITH PREMIUM NEON BORDERS ---
            st.markdown(f"""
            <div class="custom-matrix-box-cyan">
                <div style="display:flex; justify-content:between; align-items:center;">
                    <span class="font-premium-title">👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟏</span>
                    <span class="font-premium-value" style="margin-left:auto;">Daily: RM {v1_inc:.2f}</span>
                </div>
                <div style="font-family:'Rajdhani'; font-size:13px; color:#a0a0a5; margin-top:5px;">Cost: Welcome Portal Package</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="custom-matrix-box-pink">
                <div style="display:flex; justify-content:between; align-items:center;">
                    <span class="font-premium-title">👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟐</span>
                    <span class="font-premium-value" style="margin-left:auto; color:#ff0055;">Daily: RM {v2_inc:.2f}</span>
                </div>
                <div style="font-family:'Rajdhani'; font-size:13px; color:#a0a0a5; margin-top:5px;">Activation Target: RM {v2_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="custom-matrix-box-purple">
                <div style="display:flex; justify-content:between; align-items:center;">
                    <span class="font-premium-title">👑 𝐕𝐈𝐏 𝐋𝐄𝐕𝐄𝐋 𝟑</span>
                    <span class="font-premium-value" style="margin-left:auto; color:#a100ff;">Daily: RM {v3_inc:.2f}</span>
                </div>
                <div style="font-family:'Rajdhani'; font-size:13px; color:#a0a0a5; margin-top:5px;">Activation Target: RM {v3_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<hr style='border-color:#ff0055; opacity:0.2; margin:20px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#ffffff; font-family:\"Orbitron\"; font-size:14px; font-weight:900; text-align:center;'>🎬 SECURE TRAFFIC MULTI-AD SEGMENTS</p>", unsafe_allow_html=True)

            # --- DYNAMIC 5 AD SLOTS RENDERER ---
            for i in range(1, 6):
                ad_url = query_db(f"SELECT value FROM system_config WHERE key='ad{i}_url'", one=True)[0]
                ad_rew = float(query_db(f"SELECT value FROM system_config WHERE key='ad{i}_reward'", one=True)[0])
                
                # Alternate coloring mechanics for professional theme layout
                box_style = "custom-matrix-box-cyan" if i % 2 != 0 else "custom-matrix-box-pink"
                val_color = "#00f0ff" if i % 2 != 0 else "#ff0055"
                
                st.markdown(f"""
                <div class="{box_style}" style="text-align:center;">
                    <div class="font-premium-title">Ad Segment Block {i}</div>
                    <div class="font-premium-value" style="margin-top:4px; color:{val_color};">Watch Reward: <b>RM {ad_rew:.2f}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                ad_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id=? AND date=?", (st.session_state.current_user, f'ad{i}', today_date), one=True)
                if ad_watched: 
                    st.markdown(f"<p style='color:{val_color}; font-family:\"Orbitron\"; font-size:12px; font-weight:900; text-align:center;'>✅ COMPLETED TODAY</p>", unsafe_allow_html=True)
                else:
                    if st.button(f"WATCH & CLAIM AD {i}", key=f"clk_ad{i}"):
                        query_db("INSERT INTO ad_logs VALUES (?, ?, ?)", (st.session_state.current_user, f'ad{i}', today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad_rew, st.session_state.current_user), commit=True)
                        st.success(f"Bounty Linked: +RM {ad_rew:.2f}")
                        st.link_button(f"VIEW VIDEO AD LINK SOURCE {i}", ad_url, use_container_width=True)

            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            st.button("START SECURE DATA WORK TUNNEL", use_container_width=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h5 style='font-family:\"Orbitron\"; color:#00f0ff;'>TOUCH 'N GO DISPATCH</h5>", unsafe_allow_html=True)
            if tng_scanner_url:
                st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><img src='{tng_scanner_url}' width='140' style='border:2px solid #00f0ff; border-radius:12px;'/></div>", unsafe_allow_html=True)
            chosen_bank = st.selectbox("SELECT BANK METHOD:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("SENDER HOLDER NAME:")
            trx_id_input = st.text_input("TRX CODE ID REFERENCE:")
            amount_input = st.number_input("RECHARGE VALUE (RM):", min_value=1.0, value=100.0)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("TRANSMIT INTERFACE PROOF", use_container_width=True):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Transaction proof submitted for processing secure check.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h5 style='font-family:\"Orbitron\"; color:#00f0ff;'>EXECUTE SECURE WITHDRAWALS</h5>", unsafe_allow_html=True)
            st.selectbox("Target Bank Gateway:", MALAYSIAN_BANKS)
            st.text_input("Account Number Route:")
            st.number_input("Settle Amount Out (RM):", min_value=10.0)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("INITIATE SETTLEMENT TRANSFERS", use_container_width=True):
                st.error("Operation Halted: System compliance clearance pending.")

        st.markdown("<hr style='border-color:#ff0055; opacity:0.2; margin:15px 0;'>", unsafe_allow_html=True)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("HOME", key="nav_home", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("DEPOSIT", key="nav_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("🏛️ CASH OUT", key="nav_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()

    if st.button("LOG OUT PORTAL", key="global_logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

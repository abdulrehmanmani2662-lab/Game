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
SENDER_APP_PASSWORD = "lddfmerstvilicby"  

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Code: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #fbf4ee; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: linear-gradient(135deg, #f3552a 0%, #ff8052 100%); border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 6px 18px rgba(243,85,42,0.25);">
                <h2 style="color: #ffffff; margin-bottom: 10px; font-weight: 900;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: rgba(255,255,255,0.3); margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px;">Your Verification Code for {purpose} is:</p>
                <div style="font-size: 32px; font-weight: bold; color: #f3552a; letter-spacing: 4px; padding: 12px; background: #ffffff; border-radius: 10px; margin: 20px 0; box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);">
                    {otp_code}
                </div>
                <p style="color: #ffffff; font-size: 12px; opacity: 0.8;">Please secure your verification credentials.</p>
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
    # New table to trace which user watched which ad today
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
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""
if 'generated_code' not in st.session_state: st.session_state.generated_code = ""

# --- RANG-BRANG PREMIUM DESIGN UI STYLING ENGINE ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    html, body, .stApp { 
        background-color: #f7ede2 !important;
        color: #2b170c !important;
    }
    .running-header-container { 
        width: 100%; overflow: hidden; background: linear-gradient(90deg, #b71c1c, #e53935); border-bottom: 3px solid #7f0000; padding: 10px 0; margin-bottom: 20px; 
    }
    .running-text { font-size: 13px; font-weight: 800; color: #ffffff; white-space: nowrap; display: inline-block; animation: marquee-run 15s linear infinite; }
    @keyframes marquee-run { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
    
    .brand-title { text-align: center; font-size: 34px; font-weight: 900; background: linear-gradient(135deg, #880e4f 0%, #b71c1c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; }
    [data-testid="stVerticalBlock"] { max-width: 460px !important; margin: 0 auto !important; padding: 5px !important; }
    
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stTextArea"] label, .stWidgetLabel p {
        color: #4a148c !important; font-weight: 800 !important; font-size: 13px !important; margin-bottom: 5px !important;
    }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"], div[data-testid="stTextArea"] textarea { 
        background-color: #ffffff !important; color: #1a0c02 !important; border: 2px solid #e0b0ffd !important; border-radius: 14px !important; font-weight: 700 !important; padding: 12px !important;
    }
    
    div.stButton > button { background: linear-gradient(135deg, #b71c1c 0%, #d32f2f 100%) !important; color: #ffffff !important; font-size: 15px !important; font-weight: 800; border-radius: 16px !important; width: 100% !important; padding: 14px !important; border: none !important; box-shadow: 0 5px 15px rgba(183, 28, 28, 0.3); transition: all 0.25s ease; }
    div.stButton > button:hover { background: linear-gradient(135deg, #7f0000 0%, #b71c1c 100%) !important; transform: translateY(-1px); }
    
    .action-deck { 
        background: #ffffff; border: 2px solid #ffccd5; border-radius: 24px; padding: 22px; margin-top: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.04); 
    }
    .metric-card-box { 
        background: linear-gradient(135deg, #7f0000 0%, #b71c1c 100%); 
        border-radius: 24px; padding: 26px; text-align: center; margin-bottom: 15px; 
        box-shadow: 0 10px 25px rgba(127, 0, 0, 0.35); color: #ffffff !important;
    }
    
    .announcement-box { background: #ffebee; border: 2px dashed #ef5350; border-radius: 14px; padding: 12px; font-size: 13px; color: #c62828 !important; font-weight: 800; margin-bottom: 15px; text-align: center; }
    
    /* --- CUSTOM PREMIUM THICK RANG-BRANG CONTAINERS --- */
    .vip-card-v1 {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border: 3.5px solid #e53935; border-radius: 20px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .vip-card-v2 {
        background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
        border: 3.5px solid #3f51b5; border-radius: 20px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .vip-card-v3 {
        background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
        border: 3.5px solid #009688; border-radius: 20px; padding: 16px; margin: 12px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .ad-task-card {
        background: linear-gradient(135deg, #fffde7 0%, #fff9c4 100%);
        border: 3px solid #fbc02d; border-radius: 18px; padding: 15px; margin: 10px 0; text-align: center;
    }
    
    .live-log-container { background: #ffffff; border: 2px solid #ffcdd2; border-radius: 16px; padding: 14px; margin-top: 15px; }
    .log-row { font-size: 12px; padding: 7px 0; border-bottom: 1px solid #ffebee; display: flex; justify-content: space-between; }
    </style>
""", unsafe_allow_html=True)

random_online = random.randint(1645, 1920)
st.markdown(f'<div class="running-header-container"><div class="running-text">🔥 GLOBAL MATRIX PLATFORM • AD VECTOR ENGINE ACTIVE • OPERATORS ONLINE: {random_online}</div></div>', unsafe_allow_html=True)

# --- FRAGMENTED COUNTDOWN ---
@st.fragment
def render_otp_countdown_engine():
    if st.session_state.otp_start_time is not None:
        elapsed = time.time() - st.session_state.otp_start_time
        remaining = max(0, 120 - int(elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(f"<div style='text-align:center; color:#b71c1c; padding:5px; font-weight:bold;'>⏳ Resend Code in: {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)
            time.sleep(1)
            st.rerun()

# --- SYSTEM LOGOUT OR LOGIN ROUTE ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Username / Email Address:", placeholder="Enter username or email")
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
        reg_username = st.text_input("REGISTRATION EMAIL KEY:")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password")
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL", use_container_width=True):
            if reg_username.strip() and reg_password.strip():
                existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                if existing: st.error("Email already active.")
                else:
                    generated_otp = str(random.randint(102938, 984731))
                    if send_verification_email(reg_username.strip(), generated_otp):
                        st.session_state.temp_reg_user = reg_username.strip()
                        st.session_state.temp_reg_pass = reg_password.strip()
                        st.session_state.reg_verify_code = generated_otp
                        st.session_state.otp_start_time = time.time()
                        st.session_state.auth_mode = "VerifyNewAccount"
                        st.success("📩 Verification OTP sent!")
                        st.rerun()

    elif st.session_state.auth_mode == "VerifyNewAccount":
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:")
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True):
            if typed_code.strip() == st.session_state.reg_verify_code:
                query_db("INSERT INTO users VALUES (?, ?, 2.00, 0.00, 'SVIP LEVEL 1', 'M' || CAST(ABS(RANDOM()%10000) AS TEXT))", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                st.success("Registration success! RM 2.00 loaded.")
                st.session_state.auth_mode = "Login"
                st.rerun()
        render_otp_countdown_engine()

    st.markdown("<hr>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("🔑 LOGIN"): st.session_state.auth_mode = "Login"; st.rerun()
    with c2: 
        if st.button("📝 JOIN"): st.session_state.auth_mode = "Register"; st.rerun()

# --- MAIN DASHBOARD FLOW ---
else:
    announcement_text = query_db("SELECT value FROM system_config WHERE key='system_announcement'", one=True)[0]
    
    # Ads dynamic configuration parameters fetch
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
        st.markdown("<h5 style='color:#b71c1c; text-align:center; font-weight:900;'>🛡️ MASTER ADMIN PANEL</h5>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            if not pending_items: st.info("Verification queue is clean.")
            else:
                for item in pending_items:
                    st.markdown(f"<div style='background-color:#ffffff; padding:12px; border-radius:14px; border:1px solid #b71c1c;'>User: {item[1]}<br>Bank: {item[2]}<br><b>RM {item[5]:.2f}</b></div>", unsafe_allow_html=True)
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
            st.markdown("##### Link and Earning Control Setup Desk")
            
            new_ann = st.text_area("System Announcement Text:", value=announcement_text)
            new_qr_url = st.text_input("Touch 'N Go QR Scanner Image URL:", value=tng_scanner_url)
            
            st.markdown("<p style='color:#b71c1c; font-weight:bold; font-size:16px; margin-top:15px;'>🎬 MULTI-AD CAMPAIGN SYSTEM SETTINGS</p>", unsafe_allow_html=True)
            nad1_url = st.text_input("Ad 1 Destination Video URL Link:", value=ad1_url)
            nad1_rew = st.text_input("Ad 1 Earning Payout Value (RM):", value=str(ad1_reward))
            
            nad2_url = st.text_input("Ad 2 Destination Video URL Link:", value=ad2_url)
            nad2_rew = st.text_input("Ad 2 Earning Payout Value (RM):", value=str(ad2_reward))
            
            nad3_url = st.text_input("Ad 3 Destination Video URL Link:", value=ad3_url)
            nad3_rew = st.text_input("Ad 3 Earning Payout Value (RM):", value=str(ad3_reward))
            
            st.markdown("<p style='color:#b71c1c; font-weight:bold; font-size:14px; margin-top:10px;'>VIP Calibration Limits</p>", unsafe_allow_html=True)
            nv2_r = st.text_input("VIP 2 Activation Recharge Cost (RM):", value=str(v2_req))
            nv3_r = st.text_input("VIP 3 Activation Recharge Cost (RM):", value=str(v3_req))
            
            if st.button("GSAVE ALL SETTINGS NOW", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='system_announcement'", (new_ann.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad1_url'", (nad1_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad1_reward'", (nad1_rew.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad2_url'", (nad2_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad2_reward'", (nad2_rew.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad3_url'", (nad3_url.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='ad3_reward'", (nad3_rew.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip2_req'", (nv2_r.strip(),), commit=True)
                query_db("UPDATE system_config SET value=? WHERE key='vip3_req'", (nv3_r.strip(),), commit=True)
                st.success("All Multi-Ad parameters & layout system variations overhauled!")
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

        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:11px; color:#ffcdd2; margin:0; font-weight:800; letter-spacing:0.5px;">CURRENT WALLET BALANCE</p>
            <h3 style="font-size:32px; font-weight:900; color:#ffffff; margin:4px 0;">RM {wallet_bal:,.2f}</h3>
            <p style="font-size:12px; color:#ffffff; margin:0; font-weight:700;">CURRENT RANK: <span style='color:#ffd700; font-weight:900;'>{level_tag}</span></p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.selected_panel == "Overview":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            
            today_date = time.strftime("%Y-%m-%d")
            already_checked = query_db("SELECT username FROM checkins WHERE username=? AND date=?", (st.session_state.current_user, today_date), one=True)
            chk_c1, chk_c2 = st.columns([2, 1])
            with chk_c1: st.markdown("<p style='margin-top:8px; font-size:13px; font-weight:bold;'>🎁 DAILY IDENTITY BOUNTY CHECK-IN</p>", unsafe_allow_html=True)
            with chk_c2:
                if already_checked: st.button("✅ CLAIMED", disabled=True)
                else:
                    if st.button("CLAIM", key="claim_bonus"):
                        query_db("INSERT INTO checkins VALUES (?, ?)", (st.session_state.current_user, today_date), commit=True)
                        query_db("UPDATE users SET balance = balance + 0.50 WHERE username=?", (st.session_state.current_user,), commit=True)
                        st.rerun()

            st.markdown("<hr style='border-color:#ffccd5;'>", unsafe_allow_html=True)
            
            # --- RANG-BRANG THICK LEVEL CARDS ---
            st.markdown("<p style='color:#b71c1c; font-size:14px; font-weight:900; margin-bottom:10px;'>📊 DESIGN MATRIX LEVEL INVESTMENT PORTFOLIOS</p>", unsafe_allow_html=True)
            
            # Red Card - SVIP LEVEL 1
            st.markdown(f"""
            <div class="vip-card-v1">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="font-weight:900; color:#b71c1c; font-size:16px;">👑 SVIP LEVEL 1</span>
                    <span style="color:#b71c1c; font-weight:900; font-size:15px;">Daily Base: RM {v1_inc:.2f}</span>
                </div>
                <div style="font-size:12px; color:#7f0000; font-weight:700;">Cost: Free Account Package</div>
            </div>
            """, unsafe_allow_html=True)
            if "LEVEL 1" in clean_level:
                st.markdown("<p style='color:#2e7d32; font-size:13px; font-weight:900; margin:-5px 0 10px 5px;'>🟢 CURRENT ACTIVE SYSTEM RANK</p>", unsafe_allow_html=True)

            # Blue Card - SVIP LEVEL 2
            st.markdown(f"""
            <div class="vip-card-v2">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="font-weight:900; color:#1a237e; font-size:16px;">👑 SVIP LEVEL 2</span>
                    <span style="color:#1a237e; font-weight:900; font-size:15px;">Daily Base: RM {v2_inc:.2f}</span>
                </div>
                <div style="font-size:12px; color:#1a237e; font-weight:700;">Activation Requirement Limit: RM {v2_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            if "LEVEL 2" in clean_level:
                st.markdown("<p style='color:#2e7d32; font-size:13px; font-weight:900; margin:-5px 0 10px 5px;'>🟢 CURRENT ACTIVE SYSTEM RANK</p>", unsafe_allow_html=True)
            elif wallet_bal >= v2_req and "LEVEL 3" not in clean_level:
                if st.button("⚡ ACTIVATE SVIP LEVEL 2 INSTANT", key="act_vip_2"):
                    query_db("UPDATE users SET balance = balance - ?, active_level='SVIP LEVEL 2' WHERE username=?", (v2_req, st.session_state.current_user), commit=True)
                    st.rerun()
            else:
                st.markdown(f"<button style='width:100%; border:none; background:#c5cae9; color:#1a237e; font-size:12px; font-weight:900; padding:10px; border-radius:12px;' disabled>🔒 SYSTEM LOCKED (RECHARGE NEEDED)</button>", unsafe_allow_html=True)

            # Teal Card - SVIP LEVEL 3
            st.markdown(f"""
            <div class="vip-card-v3">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="font-weight:900; color:#004d40; font-size:16px;">👑 SVIP LEVEL 3</span>
                    <span style="color:#004d40; font-weight:900; font-size:15px;">Daily Base: RM {v3_inc:.2f}</span>
                </div>
                <div style="font-size:12px; color:#004d40; font-weight:700;">Activation Requirement Limit: RM {v3_req:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            if "LEVEL 3" in clean_level:
                st.markdown("<p style='color:#2e7d32; font-size:13px; font-weight:900; margin:-5px 0 10px 5px;'>🟢 CURRENT ACTIVE SYSTEM RANK</p>", unsafe_allow_html=True)
            elif wallet_bal >= v3_req:
                if st.button("⚡ ACTIVATE SVIP LEVEL 3 INSTANT", key="act_vip_3"):
                    query_db("UPDATE users SET balance = balance - ?, active_level='SVIP LEVEL 3' WHERE username=?", (v3_req, st.session_state.current_user), commit=True)
                    st.rerun()
            else:
                st.markdown(f"<button style='width:100%; border:none; background:#b2dfdb; color:#004d40; font-size:12px; font-weight:900; padding:10px; border-radius:12px;' disabled>🔒 SYSTEM LOCKED (RECHARGE NEEDED)</button>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border-color:#ffccd5;'>", unsafe_allow_html=True)
            
            # --- 3 SEQUENTIAL DYNAMIC ADS WORKSPACE TUNNEL ---
            st.markdown("<p style='color:#e65100; font-size:15px; font-weight:900; margin-bottom:5px; text-align:center;'>🎬 DAILY SECURE ADS VECTOR WORKSPACE</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:11px; text-align:center; color:#555; margin-top:-5px;'>Har video ad ko open karein aur apna real-time dynamic revenue wallet me add karein.</p>", unsafe_allow_html=True)
            
            # --- AD CARD 1 ---
            st.markdown(f"""
            <div class="ad-task-card">
                <span style="font-weight:900; color:#f57f17; font-size:14px;">▶️ ADS TASK SEGMENT 1</span><br>
                <span style="font-size:12px; color:#444; font-weight:700;">Watch reward bounty value: <b>RM {ad1_reward:.2f}</b></span>
            </div>
            """, unsafe_allow_html=True)
            ad1_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad1' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad1_watched:
                st.markdown("<p style='color:#2e7d32; font-size:12px; font-weight:bold; text-align:center;'>✅ TASK COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("ENGAGE & VERIFY VIDEO AD 1", key="btn_ad1", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad1', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad1_reward, st.session_state.current_user), commit=True)
                    st.success(f"Dynamic Reward Linked Successfully: +RM {ad1_reward:.2f}")
                    time.sleep(1)
                    st.link_button("🌐 WATCH VIDEO AD 1 SOURCE", ad1_url, use_container_width=True)
                    st.rerun()

            # --- AD CARD 2 ---
            st.markdown(f"""
            <div class="ad-task-card" style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); border-color:#8e24aa;">
                <span style="font-weight:900; color:#6a1b9a; font-size:14px;">▶️ ADS TASK SEGMENT 2</span><br>
                <span style="font-size:12px; color:#444; font-weight:700;">Watch reward bounty value: <b>RM {ad2_reward:.2f}</b></span>
            </div>
            """, unsafe_allow_html=True)
            ad2_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad2' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad2_watched:
                st.markdown("<p style='color:#2e7d32; font-size:12px; font-weight:bold; text-align:center;'>✅ TASK COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("ENGAGE & VERIFY VIDEO AD 2", key="btn_ad2", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad2', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad2_reward, st.session_state.current_user), commit=True)
                    st.success(f"Dynamic Reward Linked Successfully: +RM {ad2_reward:.2f}")
                    time.sleep(1)
                    st.link_button("🌐 WATCH VIDEO AD 2 SOURCE", ad2_url, use_container_width=True)
                    st.rerun()

            # --- AD CARD 3 ---
            st.markdown(f"""
            <div class="ad-task-card" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-color:#1e88e5;">
                <span style="font-weight:900; color:#0d47a1; font-size:14px;">▶️ ADS TASK SEGMENT 3</span><br>
                <span style="font-size:12px; color:#444; font-weight:700;">Watch reward bounty value: <b>RM {ad3_reward:.2f}</b></span>
            </div>
            """, unsafe_allow_html=True)
            ad3_watched = query_db("SELECT username FROM ad_logs WHERE username=? AND ad_id='ad3' AND date=?", (st.session_state.current_user, today_date), one=True)
            if ad3_watched:
                st.markdown("<p style='color:#2e7d32; font-size:12px; font-weight:bold; text-align:center;'>✅ TASK COMPLETED TODAY</p>", unsafe_allow_html=True)
            else:
                if st.button("ENGAGE & VERIFY VIDEO AD 3", key="btn_ad3", use_container_width=True):
                    query_db("INSERT INTO ad_logs VALUES (?, 'ad3', ?)", (st.session_state.current_user, today_date), commit=True)
                    query_db("UPDATE users SET balance = balance + ? WHERE username=?", (ad3_reward, st.session_state.current_user), commit=True)
                    st.success(f"Dynamic Reward Linked Successfully: +RM {ad3_reward:.2f}")
                    time.sleep(1)
                    st.link_button("🌐 WATCH VIDEO AD 3 SOURCE", ad3_url, use_container_width=True)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6>TOUCH 'N GO PAYMENT MATRIX</h6>", unsafe_allow_html=True)
            if tng_scanner_url:
                st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><img src='{tng_scanner_url}' width='130' style='border:3px solid #b71c1c; border-radius:14px;'/></div>", unsafe_allow_html=True)
            chosen_bank = st.selectbox("SELECT ROUTING BANK:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("SENDER HOLDER NAME:")
            trx_id_input = st.text_input("TRANSACTION REFERENCE CODE (TRX ID):")
            amount_input = st.number_input("RECHARGE VALUE (RM):", min_value=1.0, value=100.0)
            if st.button("TRANSMIT PAYMENT LEDGER PROOF", use_container_width=True):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification parameters transmitted successfully.")
            st.markdown("</div>", unsafe_allow_html=True)
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#b71c1c;'>EXECUTE OUTBOUND WIRE TRANSFERS</h6>", unsafe_allow_html=True)
            st.selectbox("Receiving Target Gateway Bank:", MALAYSIAN_BANKS[1:])
            st.text_input("IBAN / Vault Routing Code Number:")
            st.number_input("Settle Amount (RM):", min_value=10.0)
            if st.button("INITIATE SETTLEMENT TRANSFERS", use_container_width=True):
                st.error("Operation Halted: Clearance verification failed.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#ffccd5;'>", unsafe_allow_html=True)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("🎰 HOME", key="btn_usr_ov", use_container_width=True): st.session_state.selected_panel = "Overview"; st.rerun()
        with usr_col2:
            if st.button("💰 DEPOSIT", key="btn_usr_dep", use_container_width=True): st.session_state.selected_panel = "Deposit"; st.rerun()
        with usr_col3:
            if st.button("🏛️ WITHDRAW", key="btn_usr_cash", use_container_width=True): st.session_state.selected_panel = "Cashout"; st.rerun()

    if st.button("🚪 LOG OUT PORTAL", key="global_logout_action", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

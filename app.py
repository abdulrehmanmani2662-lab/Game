import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- REAL EMAIL DISTRIBUTION PIPELINE (SMTP AUTHENTICATED) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "Salmanveerm@gmail.com"  # Aapki real email linkage  
SENDER_PASSWORD = "syjawmpyvdnokasn"     # Aapka real 16-digit App Password set ho gaya hai

def send_real_verification_email(receiver_email, otp_code, user_name):
    """Sends a completely real security token to the user's authentic inbox"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Matrix Secure Protocol <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🛡️ SECURITY LOCK: {otp_code} - Identity Verification"
        
        body = f"""
        Hello {user_name},
        
        Your request to initialize an investment node has triggered our identity validation phase.
        
        Your 6-Digit Secure Verification Token is:
        👉 {otp_code}
        
        If you did not initiate this system handshake, please ignore this log sequence.
        
        Regards,
        Matrix Secure Engine
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP CRITICAL FAILURE]: {e}")
        return False

# --- DATABASE INTEGRITY MANAGEMENT (COMPLETE RESET & FIX) ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Dono tables ko completely safe reset karte hain taake koi structural error na bache
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS deposits")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            balance REAL,
            active_level TEXT,
            referred_by TEXT,
            ref_code TEXT,
            full_name TEXT,
            dob TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            level TEXT,
            amount REAL,
            method TEXT,
            holder_name TEXT,
            trx_id TEXT,
            status TEXT
        )
    """)
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
        print(f"[DB ERROR]: {e}")
        return None if one else []

# --- PREMIUM VISUAL STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght=500;800&family=Poppins:wght=400;600;800&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #030712 !important; }
    .main .block-container { padding-top: 5px !important; padding-bottom: 110px !important; max-width: 430px !important; margin: 0 auto; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Poppins', sans-serif !important; }
    
    .ticker-wrap {
        background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 15px; font-size: 12px; color: #f87171; font-weight: 600;
    }
    label, [data-testid="stWidgetLabel"] p { color: #9ca3af !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
    .stTextInput input, .stNumberInput input, .stDateInput input, div[data-baseweb="select"] { color: #ffffff !important; background-color: #0b0f19 !important; border: 1px solid #374151 !important; border-radius: 10px !important; padding: 10px !important; }
    .app-title-bar { text-align: center; font-size: 22px; color: #ffffff; font-family: 'Orbitron', sans-serif !important; font-weight: 800; letter-spacing: 2px; margin-bottom: 15px; background: linear-gradient(to right, #ef4444, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .balance-box { background: linear-gradient(135deg, #111827 0%, #030712 100%); padding: 25px; border-radius: 20px; border: 1px solid #1f2937; margin-bottom: 20px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    .section-label { font-size: 13px; color: #9ca3af; margin-top: 20px; margin-bottom: 10px; font-weight: 600; text-transform: uppercase; }
    .level-container { background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 15px; margin-bottom: 12px; }
    .google-verification-card { background: #ffffff !important; color: #1f2937 !important; border-radius: 16px; padding: 25px; text-align: center; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.4); }
    
    .stButton>button { font-weight: 600 !important; font-size: 13px !important; border-radius: 10px !important; padding: 10px 0 !important; background: linear-gradient(90deg, #1f2937 0%, #111827 100%) !important; color: #ffffff !important; border: 1px solid #374151 !important; }
    .stButton>button:hover { border-color: #ef4444 !important; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2) !important; }
    .action-btn-hub .stButton>button { background: linear-gradient(90deg, #ef4444 0%, #b91c1c 100%) !important; border: none !important; }
    .google-btn-hub .stButton>button { background: #ffffff !important; color: #1f2937 !important; border: 1px solid #dadce0 !important; }
    .video-holder-box { background: #000000; border: 1px solid #1f2937; border-radius: 14px; padding: 6px; margin-bottom: 15px; }
    .bottom-nav-holder { position: fixed; bottom: 0; left: 0; right: 0; background-color: #0b0f19; border-top: 1px solid #1f2937; padding: 12px 10px; z-index: 999999; max-width: 430px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Session State Hooks
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'google_screen_active' not in st.session_state: st.session_state.google_screen_active = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

# Live ticker metrics
fake_users = ["ali_***", "mian_***", "tan_***", "lim_***", "raj_***", "zain_***"]
fake_actions = ["just withdrew RM 700.00 successfully!", "activated VIP LEVEL 3 node pipeline."]
st.markdown(f'<div class="ticker-wrap">⚡ LIVE FEED: User {random.choice(fake_users)} {random.choice(fake_actions)}</div>', unsafe_allow_html=True)

st.markdown('<div class="app-title-bar">MATRIX PORTFOLIO</div>', unsafe_allow_html=True)

# --- GATEWAY MANAGEMENT INTERFACE ---
if not st.session_state.logged_in:
    
    if st.session_state.google_screen_active:
        st.markdown("""
        <div class="google-verification-card">
            <h3 style="color:#202124; margin:0 0 8px 0; font-size:20px; font-weight:400; text-align:center;">Sign in</h3>
            <p style="color:#5f6368; font-size:14px; margin:0 0 25px 0; text-align:center;">To continue to Matrix Streamlit Protocol</p>
        </div>
        """, unsafe_allow_html=True)
        
        real_g_email = st.text_input("EMAIL REGISTERED ID / PHONE LINKAGE:", placeholder="salmanveerm@gmail.com")
        real_g_pass = st.text_input("SECURE NETWORK KEYCODE ENTRY:", type="password", placeholder="••••••••")
        
        st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
        if st.button("UNLOCK PROTOCOL ARCHITECTURE", use_container_width=True):
            if "@" in real_g_email:
                user_exists = query_db("SELECT * FROM users WHERE username=?", (real_g_email.strip(),), one=True)
                if not user_exists:
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (real_g_email.strip(), 5.00, "None", "727", str(random.randint(1000,9999)), "Verified Agent", "2000-01-01"), commit=True)
                st.session_state.logged_in = True
                st.session_state.google_screen_active = False
                st.session_state.current_user = real_g_email.strip()
                st.session_state.current_app_tab = "home"
                st.rerun()
            else:
                st.error("Please insert a valid identity structure.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("ABORT PROFILE SYNC", use_container_width=True):
            st.session_state.google_screen_active = False
            st.rerun()
            
    elif st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_verification_form"):
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 12px; padding: 15px; text-align: center;">
                <p style="color: #60a5fa; font-size: 13px; margin: 0; font-weight: 600;">📧 SECURITY PASSCODE DISPATCHED</p>
                <p style="color: #ffffff; font-size: 12px; margin: 4px 0 0 0;">Check your inbox for code sync verification:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            user_otp_input = st.text_input("ENTER SYSTEM KEY TOKEN:", max_chars=6)
            
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            verify_submit = st.form_submit_button("VALIDATE KEY HANDSHAKE", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if verify_submit:
                if user_otp_input.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (t_data['email'], 5.00, "None", "727", str(random.randint(1000,9999)), t_data['name'], "2000-01-01"), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else:
                    st.error("Trace token mismatch!")
                    
    else:
        st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
        if st.button("OAUTH FAST SECURE SIGN IN", use_container_width=True):
            st.session_state.google_screen_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("manual_entry_form"):
            st.markdown("<p style='font-size:11px; text-align:center; color:#6b7280;'>OR ALTERNATIVE ACCESS INTERFACE</p>", unsafe_allow_html=True)
            reg_name = st.text_input("USER IDENTITY NAME:")
            reg_email = st.text_input("USER LOGIN ID (EMAIL):")
            reg_pass = st.text_input("SECURE PASSPHRASE KEYCODE:", type="password")
            
            if st.form_submit_button("ENTER ACCOUNT MATRIX", use_container_width=True):
                u_email_clean = reg_email.strip()
                if u_email_clean == "admin" and reg_pass == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                elif "@" in u_email_clean:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"name": reg_name.strip(), "email": u_email_clean}
                    
                    with st.spinner("Firing core routing engines..."):
                        send_real_verification_email(u_email_clean, st.session_state.generated_otp, reg_name.strip())
                    
                    st.session_state.verification_stage = "awaiting_otp"
                    st.rerun()

# --- ADMIN DISPATCH CONSOLE ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#ef4444;'>👑 MATRIX CONTROL FRAME</h4>", unsafe_allow_html=True)
    st.session_state.admin_video_url = st.text_input("VIDEO STREAM SOURCE URL:", value=st.session_state.admin_video_url)
    
    reqs = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    if reqs:
        for req in reqs:
            st.markdown(f"<div class='level-container'>USER: {req[1]} | RM {req[3]}<br>TRX: <code>{req[6]}</code></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("APPROVE", key=f"a_{req[0]}"):
                    query_db("UPDATE users SET active_level=? WHERE username=?", (req[2], req[1]), commit=True)
                    query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()
            with c2:
                if st.button("REJECT", key=f"r_{req[0]}"):
                    query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()

    if st.button("SHUTDOWN DISPATCH HUB", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- LIVE USER INTERFACE ---
else:
    u_row = query_db("SELECT balance, active_level, ref_code, full_name FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    if u_row:
        curr_balance, curr_level, user_code, full_name = u_row[0], u_row[1], u_row[2], u_row[3]
    else:
        curr_balance, curr_level, user_code, full_name = 5.00, "None", "0000", "Guest Node"

    if st.session_state.current_app_tab == "home":
        st.markdown(f"""
        <div class="balance-box">
            <div style="color:#6b7280; font-size:11px; margin-bottom:4px;">USER CLUSTER NODE ID: {st.session_state.current_user}</div>
            <div style="color:#6b7280; font-size:12px; margin-bottom:4px;">ACCOUNT HOLDER: <span style="color:#ffffff; font-weight:600;">{full_name}</span></div>
            <div style="color:#ef4444; font-size:11px; font-weight:600;">STATUS: {curr_level}</div>
            <div style="font-size:32px; font-family:'Orbitron', sans-serif !important; color:#ffffff; font-weight:800; margin-top:8px;">RM {curr_balance:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-label">💎 ACCOUNT ACTIVE VIP PLANS</div>', unsafe_allow_html=True)
        for l_name, l_details in LEVELS_CONF.items():
            st.markdown(f"""
            <div class="level-container">
                <div style="font-size:14px; font-weight:600; color:#ffffff;">{l_name}</div>
                <div style="color:#9ca3af; font-size:11px;">DAILY RETRO BONUS: <span style="color:#10b981; font-weight:600;">RM {l_details['daily_reward']:.2f}</span></div>
                <div style="color:#9ca3af; font-size:11px;">ACTIVATION QUANTITY: <span style="color:#f59e0b; font-weight:600;">RM {l_details['cost']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="section-label"></div>', unsafe_allow_html=True)
        with st.form("deposit_verification_hub"):
            h_name = st.text_input("SOURCE SENDER NAME ACCOUNT HOLDER:")
            t_id = st.text_input("SERIAL REFERENCE RECEIPT TRX TRANSACTION ID:")
            if st.form_submit_button("SUBMIT DEPOSIT PROOF"):
                if h_name and t_id:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (st.session_state.current_user, "VIP LEVEL 1", 50.0, "Touch n Go", h_name, t_id, "PENDING"), commit=True)
                    st.success("Proof queued! Waiting for Admin authorization.")
                else:
                    st.error("Fill all data entries.")

    elif st.session_state.current_app_tab == "task":
        st.markdown('<div class="video-holder-box">', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("CONSOLIDATE VERIFIED ENGAGEMENT REWARDS", use_container_width=True):
            payout = 5.00 if curr_level == "None" else float(LEVELS_CONF[curr_level]["daily_reward"])
            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (payout, st.session_state.current_user), commit=True)
            st.success(f"Added RM {payout:.2f} to your live balance.")
            st.session_state.current_app_tab = "home"
            st.rerun()

    # Sticky Footer Setup
    st.markdown('<div class="bottom-nav-holder">', unsafe_allow_html=True)
    c_h, c_t, c_l = st.columns(3)
    with c_h:
        if st.button("🏠 REFRESH HOME", use_container_width=True): st.session_state.current_app_tab = "home"; st.rerun()
    with c_t:
        if st.button("📺 CLAIM TASK (+5)", use_container_width=True): st.session_state.current_app_tab = "task"; st.rerun()
    with c_l:
        if st.button("🚪 LOGOUT SECURE", use_container_width=True): st.session_state.logged_in = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- REAL EMAIL DISTRIBUTION PIPELINE ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "Salmanveerm@gmail.com"  
SENDER_PASSWORD = "syjawmpyvdnokasn"     

def send_real_verification_email(receiver_email, otp_code, user_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Security Verification <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"Verification Code: {otp_code}"
        
        body = f"Hello {user_name},\n\nYour 6-digit verification code is: {otp_code}\n\nRegards,\nGlobal Matrix Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP ERROR]: {e}")
        return False

# --- DATABASE MANAGEMENT WITH REFERRALS ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            balance REAL,
            active_level TEXT,
            referred_by TEXT,
            ref_code TEXT,
            full_name TEXT,
            dob TEXT,
            last_claim_timestamp INTEGER DEFAULT 0
        )
    """)
    
    # Structural upgrades check
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'last_claim_timestamp' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN last_claim_timestamp INTEGER DEFAULT 0")
        
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
        return None if one else []

# --- PREMIUM VISUAL STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #0d1117 !important; }
    .main .block-container { padding-top: 15px !important; padding-bottom: 120px !important; max-width: 420px !important; margin: 0 auto; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Poppins', sans-serif !important; }
    
    .app-title-bar { text-align: center; font-size: 24px; color: #ffffff; font-weight: 700; letter-spacing: 1px; margin-bottom: 25px; }
    
    .balance-box { 
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
        padding: 22px; 
        border-radius: 16px; 
        border: 1px solid #30363d; 
        margin-bottom: 25px; 
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .section-label { font-size: 14px; color: #8b949e; margin-top: 25px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    
    .level-container { 
        background: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 16px; 
        margin-bottom: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .invite-box {
        background: rgba(88, 166, 255, 0.05);
        border: 1px dashed #58a6ff;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    label, [data-testid="stWidgetLabel"] p { color: #8b949e !important; font-size: 12px !important; font-weight: 500 !important; margin-bottom: 6px !important; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { color: #ffffff !important; background-color: #0d1117 !important; border: 1px solid #30363d !important; border-radius: 8px !important; padding: 10px !important; }
    
    .stButton>button { font-weight: 600 !important; font-size: 14px !important; border-radius: 8px !important; padding: 12px 0 !important; background: #21262d !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; }
    .stButton>button:hover { border-color: #58a6ff !important; color: #ffffff !important; }
    
    .action-btn-hub .stButton>button { background: #238636 !important; color: #ffffff !important; border: none !important; }
    .action-btn-hub .stButton>button:hover { background: #2ea043 !important; }
    
    .lock-btn-hub .stButton>button { background: #30363d !important; color: #8b949e !important; border: 1px solid #21262d !important; cursor: not-allowed !important; }
    
    .bottom-nav-holder { position: fixed; bottom: 0; left: 0; right: 0; background-color: #161b22; border-top: 1px solid #30363d; padding: 12px 10px; z-index: 999999; max-width: 420px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Session States
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

st.markdown('<div class="app-title-bar">Global Matrix Investment</div>', unsafe_allow_html=True)

# --- LOGIN / SIGNUP INTERFACE ---
if not st.session_state.logged_in:
    if st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_form"):
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <p style="color: #ffffff; font-size: 14px; margin: 0;">Enter verification code sent to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>
            </div>
            """, unsafe_allow_html=True)
            user_otp_input = st.text_input("Verification Code:", max_chars=6)
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            verify_submit = st.form_submit_button("Verify & Login", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if verify_submit:
                if user_otp_input.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    my_ref_code = "MX" + str(random.randint(1000, 9999))
                    
                    # Insert new user data
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                             (t_data['email'], 0.00, "None", t_data['ref_by'], my_ref_code, t_data['name'], "2000-01-01", 0), commit=True)
                    
                    # Reward the inviter if code matches
                    if t_data['ref_by'] != "None":
                        query_db("UPDATE users SET balance = balance + 10.00 WHERE ref_code=?", (t_data['ref_by'],), commit=True)
                        
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else:
                    st.error("Invalid verification code!")
                    
    else:
        with st.form("login_entry_form"):
            st.markdown("<p style='font-size:16px; text-align:center; color:#ffffff; font-weight:600; margin-bottom:15px;'>Account Authentication</p>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name (For New Users):")
            reg_email = st.text_input("Email Address:")
            reg_pass = st.text_input("Password:", type="password")
            reg_invite_code = st.text_input("Referral Code (Optional):")
            
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Login / Register", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit_btn:
                u_email_clean = reg_email.strip()
                if u_email_clean == "admin" and reg_pass == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "ADMIN_PANEL"
                    st.rerun()
                elif "@" in u_email_clean:
                    user_exists = query_db("SELECT * FROM users WHERE username=?", (u_email_clean,), one=True)
                    if user_exists:
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_email_clean
                        st.session_state.current_app_tab = "home"
                        st.rerun()
                    else:
                        if not reg_name.strip():
                            st.error("Please enter your Full Name to register.")
                        else:
                            final_ref_by = "None"
                            if reg_invite_code.strip():
                                check_code = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                if check_code:
                                    final_ref_by = reg_invite_code.strip()
                                else:
                                    st.warning("Referral code not found. Continuing without referral.")
                                    
                            st.session_state.generated_otp = str(random.randint(100000, 999999))
                            st.session_state.temp_register_data = {
                                "name": reg_name.strip(), 
                                "email": u_email_clean,
                                "ref_by": final_ref_by
                            }
                            with st.spinner("Sending verification code..."):
                                send_real_verification_email(u_email_clean, st.session_state.generated_otp, reg_name.strip())
                            st.session_state.verification_stage = "awaiting_otp"
                            st.rerun()

# --- ADMIN PANEL ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#ffffff; margin-bottom:20px;'>Admin Control Dashboard</h4>", unsafe_allow_html=True)
    st.session_state.admin_video_url = st.text_input("Update Task Video URL:", value=st.session_state.admin_video_url)
    
    st.markdown('<div class="section-label">Pending Deposit Approvals</div>', unsafe_allow_html=True)
    reqs = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    if reqs:
        for req in reqs:
            st.markdown(f"""
            <div style="background:#161b22; border:1px solid #30363d; padding:12px; border-radius:8px; margin-bottom:10px;">
                <b>User:</b> {req[1]}<br>
                <b>Plan:</b> {req[2]} | <b>Amount:</b> RM {req[3]}<br>
                <b>Trx ID:</b> <code>{req[6]}</code>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve", key=f"a_{req[0]}", use_container_width=True):
                    query_db("UPDATE users SET active_level=? WHERE username=?", (req[2], req[1]), commit=True)
                    query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()
            with c2:
                if st.button("Reject", key=f"r_{req[0]}", use_container_width=True):
                    query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (req[0],), commit=True)
                    st.rerun()
    else:
        st.info("No pending deposits.")

    if st.button("Logout From Admin", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- USER DASHBOARD ---
else:
    u_row = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    if u_row:
        curr_balance, curr_level, user_code, full_name, last_claim = u_row[0], u_row[1], u_row[2], u_row[3], u_row[4]
    else:
        curr_balance, curr_level, user_code, full_name, last_claim = 0.00, "None", "MX0000", "User", 0

    if st.session_state.current_app_tab == "home":
        st.markdown(f"""
        <div class="balance-box">
            <div style="color:#8b949e; font-size:12px;">Welcome Back</div>
            <div style="color:#ffffff; font-size:18px; font-weight:600; margin-bottom:8px;">{full_name}</div>
            <div style="color:#58a6ff; font-size:12px; font-weight:600; text-transform:uppercase;">Plan: {curr_level}</div>
            <div style="font-size:36px; color:#ffffff; font-weight:700; margin-top:10px;">RM {curr_balance:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Invite Friend Module Visual Layout
        st.markdown(f"""
        <div class="invite-box">
            <p style="color:#58a6ff; margin:0; font-size:13px; font-weight:600;">📢 INVITE FRIENDS & EARN MULTIPLIER</p>
            <p style="color:#8b949e; margin:4px 0 10px 0; font-size:11px;">Share code with friends. Get RM 10.00 instant on registration!</p>
            <div style="background:#0d1117; border:1px solid #30363d; border-radius:6px; padding:8px; font-family:monospace; color:#ffffff; font-size:15px; font-weight:700; letter-spacing:1px;">
                {user_code}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-label">Available Investment Plans</div>', unsafe_allow_html=True)
        for l_name, l_details in LEVELS_CONF.items():
            st.markdown(f"""
            <div class="level-container">
                <div>
                    <div style="font-size:15px; font-weight:600; color:#ffffff;">{l_name}</div>
                    <div style="color:#8b949e; font-size:12px;">Daily Income: <span style="color:#2ea043; font-weight:600;">RM {l_details['daily_reward']:.2f}</span></div>
                </div>
                <div style="font-size:16px; font-weight:700; color:#58a6ff;">RM {l_details['cost']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="section-label">Submit Deposit Proof</div>', unsafe_allow_html=True)
        with st.form("deposit_form"):
            h_name = st.text_input("Account Holder Name:")
            t_id = st.text_input("Transaction ID (Trx ID):")
            selected_plan = st.selectbox("Select Plan to Activate:", list(LEVELS_CONF.keys()))
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            submit_proof = st.form_submit_button("Submit Proof", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit_proof:
                if h_name and t_id:
                    cost_amount = LEVELS_CONF[selected_plan]["cost"]
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                             (st.session_state.current_user, selected_plan, cost_amount, "Touch n Go", h_name, t_id, "PENDING"), commit=True)
                    st.success("Deposit proof submitted successfully!")
                else:
                    st.error("Please fill all details.")

    elif st.session_state.current_app_tab == "task":
        st.markdown('<div class="section-label">Daily Video Task</div>', unsafe_allow_html=True)
        st.markdown('<div class="video-holder-box">', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        st.markdown('</div>', unsafe_allow_html=True)
        
        current_time = int(time.time())
        time_passed = current_time - last_claim
        one_day_seconds = 86400
        
        if time_passed < one_day_seconds:
            seconds_left = one_day_seconds - time_passed
            hours_left = seconds_left // 3600
            minutes_left = (seconds_left % 3600) // 60
            
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 15px;">
                <p style="color: #f87171; font-size: 13px; margin: 0; font-weight: 500;">
                    🔒 Next claim available in <b>{hours_left}h {minutes_left}m</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="lock-btn-hub">', unsafe_allow_html=True)
            st.button("Claim Daily Reward (Locked)", disabled=True, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            if st.button("Claim Daily Reward", use_container_width=True):
                payout = 5.00 if curr_level == "None" else float(LEVELS_CONF[curr_level]["daily_reward"])
                query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", 
                         (payout, current_time, st.session_state.current_user), commit=True)
                st.success(f"RM {payout:.2f} added to your balance!")
                st.session_state.current_app_tab = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Sticky Footer Navigation
    st.markdown('<div class="bottom-nav-holder">', unsafe_allow_html=True)
    c_h, c_t, c_l = st.columns(3)
    with c_h:
        if st.button("🏠 Home", use_container_width=True): st.session_state.current_app_tab = "home"; st.rerun()
    with c_t:
        if st.button("📺 Tasks", use_container_width=True): st.session_state.current_app_tab = "task"; st.rerun()
    with c_l:
        if st.button("🚪 Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

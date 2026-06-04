import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Force layout config natively
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="wide")

# --- DATABASE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            active_level TEXT,
            referred_by TEXT,
            ref_code TEXT,
            full_name TEXT,
            dob TEXT,
            last_claim_timestamp INTEGER DEFAULT 0
        )
    """)
    # Structural safety fallback column sync
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'password' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password TEXT DEFAULT '123456'")
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            amount REAL,
            wallet_details TEXT,
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

# --- SECURE REAL EMAIL GATEWAY ---
def send_real_verification_email(receiver_email, otp_code, user_name, subject_title="Verification Code"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Support <Salmanveerm@gmail.com>"
        msg['To'] = receiver_email
        msg['Subject'] = f"{subject_title}: {otp_code}"
        body = f"Hello {user_name},\n\nYour security execution verification code token is: {otp_code}\n\nRegards,\nGlobal Matrix Investment Team"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("Salmanveerm@gmail.com", "syjawmpyvdnokasn")
        server.sendmail("Salmanveerm@gmail.com", receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# Persistent Application Core State Variables Router
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"

# --- CSS OVERRIDES UI ENGINE ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f4f6f9 !important; }
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    
    .app-brand-header {
        background: linear-gradient(135deg, #111827, #1f2937) !important;
        padding: 18px !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 15px !important;
        text-align: center !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    .clean-auth-card {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 20px !important;
        padding: 26px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 15px;
    }
    
    .stButton>button {
        background: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        padding: 10px 5px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background: #2563eb !important;
        color: #ffffff !important;
        border-color: #2563eb !important;
    }

    /* PREMIUM MOBILE WALLET OVERRIDES MATCHING SCREENSHOT 2 EXACTLY */
    .earnwise-main-card {
        background: #0f172a !important;
        border-radius: 16px !important;
        padding: 20px !important;
        color: #ffffff !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15) !important;
    }
    .card-top-title { font-size: 13px !important; color: #94a3b8 !important; font-weight: 600; }
    .card-sub-banner { font-size: 11px !important; color: #fbbf24 !important; font-weight: 700; margin-top: 4px; margin-bottom: 16px; }
    
    .wallet-row-container {
        display: flex !important;
        justify-content: space-between !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        margin-top: 6px;
        margin-bottom: 14px !important;
    }
    .wallet-box { width: 48%; }
    .wallet-lbl { font-size: 10px !important; color: #94a3b8 !important; text-transform: uppercase; font-weight: 700; letter-spacing: 0.3px; }
    .wallet-val { font-size: 16px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 2px; }

    .action-btn-row {
        display: flex !important;
        justify-content: space-between !important;
        gap: 10px !important;
        margin-top: 10px;
    }
    .action-btn-half {
        flex: 1 !important;
        text-align: center !important;
        padding: 10px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    .bg-blue { background: #1e75e5 !important; }
    .bg-green { background: #10b981 !important; }

    .premium-widget-box {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 16px !important;
        padding: 18px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
    }
    .widget-title-head { 
        font-size: 13px !important; 
        font-weight: 700 !important; 
        color: #1f2937 !important; 
        margin-bottom: 12px !important; 
        border-left: 4px solid #2563eb;
        padding-left: 8px;
    }
    
    .history-item-flex {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 12px 0 !important;
        border-bottom: 1px solid #f3f4f6 !important;
        font-size: 13px !important;
    }
    .status-badge { font-size: 10px !important; font-weight: 700 !important; padding: 3px 8px !important; border-radius: 6px; text-transform: uppercase; }
    .s-success { background: #dcfce7 !important; color: #166534 !important; }
    .s-alert { background: #fef3c7 !important; color: #92400e !important; }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# --- UNIFIED IDENTITY GATEWAYS (AUTH) ---
if not st.session_state.logged_in:
    st.markdown('<div class="app-brand-header" style="margin-top:20px;">🔱 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    # A. SIGN UP VERIFICATION STAGE (OTP)
    if st.session_state.verification_stage == "awaiting_otp":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("secure_otp_form"):
            st.markdown(f"<h4 style='text-align:center;'>Verify Account Registration</h4><p style='font-size:12px; color:#6b7280; text-align:center;'>Security code dispatched to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
            u_otp = st.text_input("Enter 6-Digit Code Verification Token", max_chars=6)
            if st.form_submit_button("Verify Code Token", use_container_width=True):
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                             (t_data['email'], t_data['password'], 10.00, "None", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    if t_data['ref_by'] != "None":
                        query_db("UPDATE users SET balance = balance + 10.00 WHERE ref_code=?", (t_data['ref_by'],), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.active_sidebar_tab = "Dashboard"
                    st.rerun()
                else: st.error("Verification string token mismatch.")
        st.markdown('</div>', unsafe_allow_html=True)

    # B. FORGOT PASSWORD REQUEST GATEWAY
    elif st.session_state.auth_view == "forgot_password_request":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("forgot_password_email_pipeline"):
            st.markdown("<h4 style='text-align:center; font-weight:700;'>Recover Passwords Account</h4>", unsafe_allow_html=True)
            reset_email = st.text_input("Your Registered Email Address Account:")
            if st.form_submit_button("Generate Reset Token Code Link", use_container_width=True):
                clean_email = reset_email.strip()
                match_user = query_db("SELECT full_name FROM users WHERE username=?", (clean_email,), one=True)
                if match_user:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"email": clean_email, "name": match_user[0]}
                    send_real_verification_email(clean_email, st.session_state.generated_otp, match_user[0], "Password Recovery Reset Token Code")
                    st.session_state.auth_view = "forgot_password_verification"
                    st.success("Recovery verification token code generated successfully to target channel.")
                    st.rerun()
                else: st.error("No verified user entries registered with this tracking node email.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Abort and Back to Login"):
            st.session_state.auth_view = "login"
            st.rerun()

    # C. FORGOT PASSWORD VERIFICATION EXECUTION STAGE
    elif st.session_state.auth_view == "forgot_password_verification":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("password_reset_override_terminal"):
            st.markdown(f"<h4 style='text-align:center;'>Reset Credential Configuration</h4><p style='font-size:12px; text-align:center; color:#6b7280;'>Targeting: <b>{st.session_state.temp_register_data.get('email')}</b></p>", unsafe_allow_html=True)
            input_token = st.text_input("6-Digit Recovery Token Code String:", max_chars=6)
            new_secure_password = st.text_input("Configure New Account Passwords Input String:", type="password")
            if st.form_submit_button("Overwrite Cryptographic Key Node Passwords", use_container_width=True):
                if input_token.strip() == st.session_state.generated_otp:
                    if len(new_secure_password.strip()) >= 4:
                        query_db("UPDATE users SET password=? WHERE username=?", (new_secure_password.strip(), st.session_state.temp_register_data.get('email')), commit=True)
                        st.success("Security keys modified successfully! Re-routing back to basic execution login panels.")
                        st.session_state.auth_view = "login"
                        st.rerun()
                    else: st.error("Password string density parameters error.")
                else: st.error("Invalid dynamic token recovery mismatch logs.")
        st.markdown('</div>', unsafe_allow_html=True)

    # D. APPLICATION BASE SIGNUP HUB
    elif st.session_state.auth_view == "signup":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("identity_register_gateway"):
            st.markdown("<h4 style='text-align:center; font-weight:700;'>Create Account</h4>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Password", type="password")
            reg_invite_code = st.text_input("Invitation Code (Optional)")
            if st.form_submit_button("Register Now", use_container_width=True):
                em_clean = reg_email.strip()
                pass_clean = reg_pass.strip()
                if "@" in em_clean:
                    existing = query_db("SELECT * FROM users WHERE username=?", (em_clean,), one=True)
                    if existing: st.error("Email already registered.")
                    elif not reg_name.strip() or not pass_clean: st.error("Fields cannot be empty.")
                    else:
                        f_ref = "None"
                        if reg_invite_code.strip():
                            match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                            if match: f_ref = reg_invite_code.strip()
                        st.session_state.generated_otp = str(random.randint(100000, 999999))
                        st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "password": pass_clean, "ref_by": f_ref}
                        send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                        st.session_state.verification_stage = "awaiting_otp"
                        st.rerun()
                else: st.error("Invalid email.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Have an account? Log In Instead", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()

    # E. APPLICATION BASE SIGNIN HUB (WITH FORGOT PASSWORD TRIGGER LINK)
    elif st.session_state.auth_view == "login":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("identity_login_gateway"):
            st.markdown("<h4 style='text-align:center; font-weight:700;'>Welcome Back Log In</h4>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address")
            login_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In Secure Authenticator", use_container_width=True):
                em_clean = login_email.strip()
                pass_clean = login_pass.strip()
                if em_clean == "admin" and pass_clean == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "MATRIX_ADMIN"
                    st.rerun()
                elif "@" in em_clean:
                    user_record = query_db("SELECT password FROM users WHERE username=?", (em_clean,), one=True)
                    if user_record and user_record[0] == pass_clean:
                        st.session_state.logged_in = True
                        st.session_state.current_user = em_clean
                        st.session_state.active_sidebar_tab = "Dashboard"
                        st.rerun()
                    else: st.error("Incorrect credentials configuration log matrix matching error.")
                else: st.error("Invalid tracking route email patterns format.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Dual Navigation Help Grid Structure below login box
        help_c1, help_c2 = st.columns(2)
        with help_c1:
            if st.button("New Account Registry"):
                st.session_state.auth_view = "signup"
                st.rerun()
        with help_c2:
            if st.button("🔑 Forgot Passwords?"):
                st.session_state.auth_view = "forgot_password_request"
                st.rerun()

# --- MAIN APPLICATION WORKSPACE CONTROLLER ---
else:
    st.markdown('<div class="app-brand-header">GLOBAL MATRIX INVESTMENT PLATFORM</div>', unsafe_allow_html=True)
    
    # Responsive Grid Navigation Core System Top Bar Row 1
    nav_c1, nav_c2, nav_c3 = st.columns(3)
    with nav_c1:
        if st.button("🏠 Dashboard", use_container_width=True): st.session_state.active_sidebar_tab = "Dashboard"
    with nav_c2:
        if st.button("📺 View Tasks", use_container_width=True): st.session_state.active_sidebar_tab = "Tasks"
    with nav_c3:
        if st.button("📜 Log History", use_container_width=True): st.session_state.active_sidebar_tab = "History"

    # Responsive Grid Navigation Core System Top Bar Row 2
    nav_c4, nav_c5, nav_c6 = st.columns(3)
    with nav_c4:
        if st.button("➕ Deposit", use_container_width=True): st.session_state.active_sidebar_tab = "Deposit"
    with nav_c5:
        if st.button("📤 Cashout", use_container_width=True): st.session_state.active_sidebar_tab = "Withdrawal"
    with nav_c6:
        if st.button("🚪 Leave App", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)

    # --- ROUTING SYSTEM LOGIC VIEWS ---
    if st.session_state.is_admin:
        st.markdown("### Admin Configuration Pipeline Logs")
        st.session_state.admin_video_url = st.text_input("Active Live Stream URL:", value=st.session_state.admin_video_url)
        deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
        for d in deps:
            st.markdown(f"<div style='background:#fff; border:1px solid #cbd5e1; padding:10px; border-radius:6px; margin-bottom:10px;'>User: {d[1]} | Plan: <b>{d[2]}</b> | Trx: <code>{d[6]}</code></div>", unsafe_allow_html=True)
            if st.button("Approve System Node", key=f"ad_{d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()

    else:
        u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", "Matrix User", 0)
        
        ready_withdrawal = bal * 0.70 
        
        # ACTIVE ROUTER VIEW: DASHBOARD
        if st.session_state.active_sidebar_tab == "Dashboard":
            # PERFECT COMPILATION RENDERING WITHOUT STR CORRUPTIONS (unsafe_allow_html=True explicitly tracked)
            st.markdown(f"""
            <div class="earnwise-main-card">
                <div class="card-top-title">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
                <div class="card-sub-banner">Pelan VIP/SVIP &amp; Tugasan Media Sosial Diperkenalkan!</div>
                
                <div style="font-size: 11px; color:#cbd5e1; margin-bottom: 2px;">💼 Dompet Perolehan Saya (My Earnings Wallet)</div>
                <div class="wallet-row-container">
                    <div class="wallet-box">
                        <div class="wallet-lbl">Current Balance</div>
                        <div class="wallet-val">RM {bal:,.2f}</div>
                    </div>
                    <div class="wallet-box" style="border-left: 1px solid rgba(255,255,255,0.15); padding-left: 12px;">
                        <div class="wallet-lbl">Ready For Cashout</div>
                        <div class="wallet-val" style="color: #10b981;">RM {ready_withdrawal:,.2f}</div>
                    </div>
                </div>
                
                <div class="action-btn-row">
                    <div class="action-btn-half bg-blue">📥 Deposit Dana</div>
                    <div class="action-btn-half bg-green">📤 Tarik Perolehan</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="premium-widget-box">
                <div class="widget-title-head">Pusat Tugasan YouTube &amp; Media (Active Tier)</div>
                <p style="font-size:13px; color:#4b5563; margin:0;">Your tier node status code is: <b style="color:#2563eb;">{lvl}</b></p>
                <p style="font-size:12px; color:#6b7280; margin-top:4px;">Invitation link activation tracking ID token: <b>{code}</b></p>
            </div>
            """, unsafe_allow_html=True)

        # ACTIVE ROUTER VIEW: TASKS
        elif st.session_state.active_sidebar_tab == "Tasks":
            st.markdown('<div class="premium-widget-box"><div class="widget-title-head">Tonton Video &amp; Menang</div>', unsafe_allow_html=True)
            st.video(st.session_state.admin_video_url)
            
            c_time = int(time.time())
            if (c_time - claim_stamp) < 86400:
                rem = 86400 - (c_time - claim_stamp)
                st.markdown(f"<div style='background:#fee2e2; padding:12px; border-radius:8px; color:#991b1b; font-size:13px; text-align:center; font-weight:600;'>🔒 Tasks locked. Cool down active. Next claim in: {rem//3600}h {(rem%3600)//60}m</div>", unsafe_allow_html=True)
            else:
                if st.button("Tonton &amp; Peroleh Reward Now", use_container_width=True):
                    bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                    query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                    st.success(f"Success! Credited +RM {bonus:.2f} to your secure stream vault.")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ACTIVE ROUTER VIEW: DEPOSIT
        elif st.session_state.active_sidebar_tab == "Deposit":
            st.markdown('<div class="premium-widget-box"><div class="widget-title-head">Submit Secure Payment Slip Gateway</div>', unsafe_allow_html=True)
            with st.form("deposit_confirmation_hub"):
                holder = st.text_input("Account Holder Verified Name:")
                tx_str = st.text_input("Transaction Identification Reference (Trx ID):")
                p_select = st.selectbox("Select Target Investment Plan Node:", list(LEVELS_CONF.keys()))
                if st.form_submit_button("Hantar Slip Deposit", use_container_width=True):
                    if holder and tx_str:
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                 (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "Bank Transfer", holder, tx_str, "PENDING"), commit=True)
                        st.success("Verification receipt logged into tracking databases pipeline node.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ACTIVE ROUTER VIEW: WITHDRAWAL
        elif st.session_state.active_sidebar_tab == "Withdrawal":
            st.markdown('<div class="premium-widget-box"><div class="widget-title-head">Tarik Perolehan Outflow Terminal</div>', unsafe_allow_html=True)
            with st.form("withdrawal_request_terminal"):
                w_val = st.number_input("Liquidation Settlement Sum (RM):", min_value=10.0, step=5.0)
                w_net = st.text_input("Destination Bank System Credentials / Wallet Routing Link:")
                if st.form_submit_button("Launch Cashout Request", use_container_width=True):
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Asset payout initialization pipeline has been built.")
                            st.rerun()
                        else: st.error("Please explicitly write target account details data.")
                    else: st.error("Out of bound index allocation error. Account balance status shortfall.")
            st.markdown('</div>', unsafe_allow_html=True)

        # ACTIVE ROUTER VIEW: HISTORY
        elif st.session_state.active_sidebar_tab == "History":
            st.markdown('<div class="premium-widget-box"><div class="widget-title-head">Sejarah Transaksi Terkini</div>', unsafe_allow_html=True)
            all_deps = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            if not all_deps:
                st.markdown("<p style='font-size:13px; color:#6b7280; text-align:center; padding:10px;'>Logs are clean. No transaction footprints captured.</p>", unsafe_allow_html=True)
            for dl in all_deps:
                b_style = "s-success" if dl[2]=="APPROVED" else "s-alert"
                st.markdown(f"""
                <div class="history-item-flex">
                    <div>Investment Node Tier: <b>{dl[0]}</b></div>
                    <div style="text-align:right;">
                        <b>RM {dl[1]:,.2f}</b><br>
                        <span class="status-badge {b_style}">{dl[2]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

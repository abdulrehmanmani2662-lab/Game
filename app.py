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

# --- REAL EMAIL SYSTEM ---
def send_real_verification_email(receiver_email, otp_code, user_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Support <Salmanveerm@gmail.com>"
        msg['To'] = receiver_email
        msg['Subject'] = f"Verification Code: {otp_code}"
        body = f"Hello {user_name},\n\nYour verification code is: {otp_code}\n\nRegards,\nGlobal Matrix Investment Team"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("Salmanveerm@gmail.com", "syjawmpyvdnokasn")
        server.sendmail("Salmanveerm@gmail.com", receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# Persistent State Management Routing
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "signup"

# --- MOBILE STYLING OVERHAUL ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f8fafc !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Inter', sans-serif !important; }
    
    .master-top-streamer {
        background: #0f172a !important;
        padding: 14px 16px !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 16px !important;
        text-align: center !important;
    }
    
    .clean-auth-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
    }
    
    label, [data-testid="stWidgetLabel"] p { 
        color: #334155 !important; 
        font-size: 13px !important; 
        font-weight: 500 !important; 
        margin-bottom: 4px !important;
    }
    
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { 
        background-color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important; 
        border-radius: 8px !important; 
        color: #0f172a !important;
        padding: 8px 12px !important;
    }
    
    .form-execution-btn .stButton>button {
        background: #1e75e5 !important;
        color: #ffffff !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 0 !important;
        border-radius: 8px !important;
        width: 100% !important;
    }

    /* PREMIUM MOBILE WALLET OVERRIDES */
    .premium-navy-wallet-card {
        background: #0f172a !important;
        border-radius: 14px !important;
        padding: 20px !important;
        color: #ffffff !important;
        margin-bottom: 16px !important;
    }
    .wallet-header-caption { font-size: 11px !important; color: #94a3b8 !important; font-weight: 500; text-transform: uppercase; }
    .wallet-user-title { font-size: 20px !important; font-weight: 700 !important; color: #ffffff !important; margin-top: 2px; margin-bottom: 14px; }
    
    .wallet-data-split-flex {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding-top: 12px !important;
    }
    .wallet-data-chunk { flex: 1; }
    .chunk-title-lbl { font-size: 10px !important; color: #94a3b8 !important; text-transform: uppercase; }
    .chunk-amount-val { font-size: 18px !important; font-weight: 700 !important; color: #ffffff !important; }
    
    .clean-white-card-widget {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    .card-widget-header { font-size: 13px !important; font-weight: 700 !important; color: #0f172a !important; margin-bottom: 10px !important; text-transform: uppercase; }
    
    .history-row-item {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 10px 0 !important;
        border-bottom: 1px solid #f1f5f9 !important;
        font-size: 12px !important;
    }
    .clean-badge-capsule { font-size: 9px !important; font-weight: 700 !important; padding: 2px 6px !important; border-radius: 4px; text-transform: uppercase; }
    .c-approved { background: #dcfce7 !important; color: #15803d !important; }
    .c-pending { background: #fef3c7 !important; color: #b45309 !important; }
    .c-rejected { background: #fee2e2 !important; color: #b91c1c !important; }

    /* MOBILE NAVIGATION SYSTEM BAR */
    .mobile-nav-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        background: #ffffff;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }
    .mobile-nav-container .stButton>button {
        padding: 8px 4px !important;
        font-size: 11px !important;
        text-align: center !important;
        justify-content: center !important;
        background: #f1f5f9 !important;
        color: #334155 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    .mobile-nav-container .stButton>button:hover {
        background: #1e75e5 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# --- UNIFIED AUTH VIEWS ---
if not st.session_state.logged_in:
    st.markdown('<div class="master-top-streamer" style="margin-top:20px;">🔱 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    # 1. OTP SCREEN
    if st.session_state.verification_stage == "awaiting_otp":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("secure_otp_form"):
            st.markdown(f"<h4 style='text-align:center; color:#0f172a;'>Verify Your Email</h4><p style='font-size:12px; color:#64748b; text-align:center;'>Code sent to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
            u_otp = st.text_input("Enter 6-Digit Code", max_chars=6)
            st.markdown('<div class="form-execution-btn" style="margin-top:10px;">', unsafe_allow_html=True)
            btn_v = st.form_submit_button("Verify Code", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if btn_v:
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
                else:
                    st.error("Invalid code.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. SIGN UP VIEW
    elif st.session_state.auth_view == "signup":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("identity_register_gateway"):
            st.markdown("<h4 style='font-weight:700; color:#0f172a; text-align:center; margin-bottom:15px;'>Create Account</h4>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name")
            reg_email = st.text_input("Email Address")
            reg_pass = st.text_input("Password", type="password")
            reg_invite_code = st.text_input("Invitation Code (Optional)")
            
            st.markdown('<div class="form-execution-btn" style="margin-top:15px;">', unsafe_allow_html=True)
            register_submit = st.form_submit_button("Register Now", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if register_submit:
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

    # 3. SIGN IN VIEW
    elif st.session_state.auth_view == "login":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("identity_login_gateway"):
            st.markdown("<h4 style='font-weight:700; color:#0f172a; text-align:center; margin-bottom:15px;'>Welcome Back</h4>", unsafe_allow_html=True)
            login_email = st.text_input("Email Address")
            login_pass = st.text_input("Password", type="password")
            
            st.markdown('<div class="form-execution-btn" style="margin-top:15px;">', unsafe_allow_html=True)
            login_submit = st.form_submit_button("Sign In", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if login_submit:
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
                    else: st.error("Incorrect credentials.")
                else: st.error("Invalid email pattern.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("New here? Create an Account", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()

# --- MAIN RESPONSIVE CONTENT CONTROLLER ---
else:
    st.markdown('<div class="master-top-streamer">GLOBAL MATRIX INVESTMENT PLATFORM</div>', unsafe_allow_html=True)
    
    # Grid System for Top Horizontal Navigation Bar on Mobile
    st.markdown('<div class="mobile-nav-container">', unsafe_allow_html=True)
    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
    with nav_c1:
        if st.button("🏠 Home", use_container_width=True): st.session_state.active_sidebar_tab = "Dashboard"
    with nav_c2:
        if st.button("📺 Tasks", use_container_width=True): st.session_state.active_sidebar_tab = "Tasks"
    with nav_c3:
        if st.button("💰 Deposit", use_container_width=True): st.session_state.active_sidebar_tab = "Deposit"
    with nav_c4:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Secondary Utilities Link Grid 
    util_c1, util_c2 = st.columns(2)
    with util_c1:
        if st.button("📜 History Ledger", use_container_width=True): st.session_state.active_sidebar_tab = "History"
    with util_c2:
        if st.button("📥 Withdrawal", use_container_width=True): st.session_state.active_sidebar_tab = "Withdrawal"

    st.markdown('<hr style="border-color:#e2e8f0; margin:15px 0;">', unsafe_allow_html=True)

    # --- ROUTING SCREENS ---
    if st.session_state.is_admin:
        st.markdown("### Admin Dashboard Panel")
        st.session_state.admin_video_url = st.text_input("Active Live Stream URL:", value=st.session_state.admin_video_url)
        deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
        for d in deps:
            st.markdown(f"<div style='background:#fff; border:1px solid #cbd5e1; padding:10px; border-radius:6px; margin-bottom:10px; font-size:12px;'>User: {d[1]} | Plan: <b>{d[2]}</b> | Trx: <code>{d[6]}</code></div>", unsafe_allow_html=True)
            if st.button("Approve System Node", key=f"ad_{d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()

    else:
        u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", "Matrix User", 0)
        
        if st.session_state.active_sidebar_tab == "Dashboard":
            # RE-ENGINEERED RENDERING FOR CLEAN STYLING WITHOUT BUGGING RAW STRINGS
            st.markdown(f"""
            <div class="premium-navy-wallet-card">
                <div class="wallet-header-caption">EarnWise Accounts Dashboard (MY)</div>
                <div class="wallet-user-title">User: {title}</div>
                <div class="wallet-data-split-flex">
                    <div class="wallet-data-chunk">
                        <div class="chunk-title-lbl">Current Balance</div>
                        <div class="chunk-amount-val">RM {bal:.2f}</div>
                    </div>
                    <div class="wallet-data-chunk" style="text-align: right;">
                        <div class="chunk-title-lbl">Active Plan Node</div>
                        <div class="chunk-amount-val" style="color: #f59e0b; font-size:14px;">{lvl}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="clean-white-card-widget">
                <div class="card-widget-header">Referral Code Network</div>
                <p style="font-size:12px; color:#475569; margin:0;">Share your link node to claim instant RM 10.00 reward:</p>
                <div style="background:#f8fafc; padding:8px; border-radius:6px; font-family:monospace; font-weight:700; text-align:center; color:#1e75e5; margin-top:8px; border:1px dashed #cbd5e1;">{code}</div>
            </div>
            """, unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Tasks":
            st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Daily Video Stream Tasks</div>', unsafe_allow_html=True)
            st.video(st.session_state.admin_video_url)
            
            c_time = int(time.time())
            if (c_time - claim_stamp) < 86400:
                rem = 86400 - (c_time - claim_stamp)
                st.markdown(f"<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:6px; padding:10px; color:#b91c1c; font-size:12px; text-align:center;'>🔒 Lock Active. Available in: {rem//3600}h {(rem%3600)//60}m</div>", unsafe_allow_html=True)
            else:
                st.markdown('<div class="form-execution-btn" style="margin-top:10px;">', unsafe_allow_html=True)
                if st.button("Claim Daily Reward Plan Link", use_container_width=True):
                    bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                    query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                    st.success(f"Claimed successfully: +RM {bonus:.2f}")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Deposit":
            st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Submit Deposit Gateway Proof</div>', unsafe_allow_html=True)
            with st.form("deposit_confirmation_hub"):
                holder = st.text_input("Sender Account Verification Name:")
                tx_str = st.text_input("Transaction reference Hash (Trx ID):")
                p_select = st.selectbox("Choose Target Plan Node Tier:", list(LEVELS_CONF.keys()))
                st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                btn_d = st.form_submit_button("Hantar Slip Deposit Now", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_d and holder and tx_str:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                             (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "Bank Transfer", holder, tx_str, "PENDING"), commit=True)
                    st.success("Receipt node queued! Waiting for admin asset synchronization pipeline logs.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Withdrawal":
            st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Request Cashout Payout</div>', unsafe_allow_html=True)
            with st.form("withdrawal_request_terminal"):
                w_val = st.number_input("Payout Outflow Amount (RM):", min_value=10.0, step=5.0)
                w_net = st.text_input("Target Bank Information / Wallet Details:")
                st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                btn_w = st.form_submit_button("Launch Withdrawal Settlement", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_w:
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Liquidation pipelines successfully established.")
                            st.rerun()
                        else: st.error("Please insert banking target credentials channels.")
                    else: st.error("Threshold limits breakdown. Insufficient credit balance allocation.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "History":
            st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Transaction Records Storage</div>', unsafe_allow_html=True)
            all_deps = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            if not all_deps:
                st.markdown("<p style='font-size:12px; color:#64748b; text-align:center;'>Sejarah Transaksi Terkini Empty.</p>", unsafe_allow_html=True)
            for dl in all_deps:
                c_badge = "c-approved" if dl[2]=="APPROVED" else "c-pending" if dl[2]=="PENDING" else "c-rejected"
                st.markdown(f'<div class="history-row-item"><div><b>Deposit Proof Tier: {dl[0]}</b></div><div style="text-align:right;"><b>RM {dl[1]:.2f}</b><br><span class="clean-badge-capsule {c_badge}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

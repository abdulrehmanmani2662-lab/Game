import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Forced app structure setup globally
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="wide")

# --- DATABASE ENGINE ---
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

# --- SECURE EMAIL SYSTEM ---
def send_real_verification_email(receiver_email, otp_code, user_name, subject_title="Verification Code"):
    try:
        msg = MIMEMultipart()
        msg['From'] = "Global Matrix Support <Salmanveerm@gmail.com>"
        msg['To'] = receiver_email
        msg['Subject'] = f"{subject_title}: {otp_code}"
        body = f"Hello {user_name},\n\nYour security token code is: {otp_code}\n\nRegards,\nGlobal Matrix Team"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("Salmanveerm@gmail.com", "syjawmpyvdnokasn")
        server.sendmail("Salmanveerm@gmail.com", receiver_email, msg.as_string())
        server.quit()
        return True
    except:
        return False

# Session management router states
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"

# --- URL PARAMETERS DETECTOR FOR CUSTOM DABBEY CLICKS ---
st_params = st.query_params
if "nav" in st_params:
    nav_val = st_params["nav"]
    if nav_val in ["Dashboard", "Tasks", "Deposit", "Withdrawal", "History", "Logout"]:
        if nav_val == "Logout":
            st.session_state.logged_in = False
            st.session_state.auth_view = "login"
        else:
            st.session_state.active_sidebar_tab = nav_val

# --- ADVANCED PREMIUM INJECTION CSS ENGINE ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2 family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
    [data-testid="stSidebar"], footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f8fafc !important; }
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    
    .app-brand-header {
        background: #0f172a !important;
        padding: 14px !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        text-align: center !important;
        margin-bottom: 12px !important;
    }

    .clean-auth-card {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        max-width: 450px;
        margin: 35px auto !important;
    }

    /* PREMIUM BALANCE BANNER (SCREENSHOT MATCH) */
    .earnwise-main-card {
        background: #0d1e3d !important;
        border-radius: 14px !important;
        padding: 18px !important;
        color: #ffffff !important;
        margin-bottom: 16px !important;
    }
    .card-top-title { font-size: 14px !important; color: #94a3b8 !important; font-weight: 600; }
    .card-sub-banner { font-size: 11px !important; color: #fbbf24 !important; font-weight: 700; margin-top: 2px; margin-bottom: 12px; }
    
    .wallet-grid {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    .wallet-box { width: 49% !important; }
    .wallet-lbl { font-size: 10px !important; color: #94a3b8 !important; text-transform: uppercase; font-weight: 700; line-height: 1.2; }
    .wallet-val { font-size: 18px !important; font-weight: 800 !important; color: #ffffff !important; margin-top: 4px; }

    /* LEFT-ALIGNED VERTICAL DASHBOARD NAVIGATION DABBA ENGINE */
    .v-dabba-container {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        margin-bottom: 20px !important;
        width: 100% !important;
    }
    .custom-dabba-link {
        display: block !important;
        width: 100% !important;
        padding: 14px 16px !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        text-align: left !important;  /* Strict Left Alignment Line */
        text-decoration: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04) !important;
        transition: transform 0.2s, opacity 0.2s !important;
    }
    .custom-dabba-link:active { transform: scale(0.98); opacity: 0.9; }
    
    /* Dynamic Color Mappings based on Screenshot 1000048025.jpg spec */
    .db-blue-color { background: #1e62d0 !important; }
    .db-green-color { background: #10b981 !important; }
    .db-orange-color { background: #f97316 !important; }
    .db-purple-color { background: #8b5cf6 !important; }
    .db-slate-color { background: #475569 !important; }
    .db-red-color { background: #ef4444 !important; }

    .premium-widget-box {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
    }
    .widget-title-head { font-size: 14px !important; font-weight: 700 !important; color: #1e293b !important; margin-bottom: 8px !important; }
    
    .form-wrapper-box {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px !important;
    }

    .history-row {
        display: flex !important; justify-content: space-between !important; align-items: center !important;
        padding: 10px 0 !important; border-bottom: 1px solid #f1f5f9 !important; font-size: 13px !important;
    }
    .badge { font-size: 11px !important; font-weight: 700 !important; padding: 2px 6px !important; border-radius: 4px; }
    .b-success { background: #dcfce7 !important; color: #15803d !important; }
    .b-pending { background: #fef3c7 !important; color: #b45309 !important; }
    </style>
""", unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# --- AUTH PANELS PIPELINE ---
if not st.session_state.logged_in:
    st.markdown('<div class="app-brand-header">🔱 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    if st.session_state.verification_stage == "awaiting_otp":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("otp_verify_form"):
            st.markdown("<h3>Verify Account</h3>", unsafe_allow_html=True)
            u_otp = st.text_input("6-Digit Token")
            if st.form_submit_button("Submit Token", use_container_width=True):
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                             (t_data['email'], t_data['password'], 10.00, "None", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.rerun()
                else: st.error("Token invalid.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_view == "forgot_password_request":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("forgot_form"):
            st.markdown("<h3>Reset Password Configuration</h3>", unsafe_allow_html=True)
            r_email = st.text_input("Enter Registered Email Account")
            if st.form_submit_button("Send Password Recovery OTP Token", use_container_width=True):
                user_match = query_db("SELECT full_name FROM users WHERE username=?", (r_email.strip(),), one=True)
                if user_match:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"email": r_email.strip(), "name": user_match[0]}
                    send_real_verification_email(r_email.strip(), st.session_state.generated_otp, user_match[0], "Password Recovery Code")
                    st.session_state.auth_view = "forgot_password_verification"
                    st.rerun()
                else: st.error("Target email node sequence not registered.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Abort and Return to Sign In"):
            st.session_state.auth_view = "login"
            st.rerun()

    elif st.session_state.auth_view == "forgot_password_verification":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("reset_finalize_form"):
            st.markdown("<h3>Input Recovery Verification Code</h3>", unsafe_allow_html=True)
            input_token = st.text_input("6-Digit Token Code Received", max_chars=6)
            new_pass = st.text_input("Configure Secure Password", type="password")
            if st.form_submit_button("Rewrite Security Profile", use_container_width=True):
                if input_token.strip() == st.session_state.generated_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.temp_register_data['email']), commit=True)
                    st.success("Credentials updated successfully.")
                    st.session_state.auth_view = "login"
                    st.rerun()
                else: st.error("Token verification hash mismatched.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_view == "signup":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("reg_form"):
            st.markdown("<h3>Create Platform Profile</h3>", unsafe_allow_html=True)
            reg_name = st.text_input("Name")
            reg_email = st.text_input("Email")
            reg_pass = st.text_input("Password", type="password")
            reg_inv = st.text_input("Invite Token (Optional)")
            if st.form_submit_button("Register Account Node", use_container_width=True):
                if "@" in reg_email:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"name": reg_name.strip(), "email": reg_email.strip(), "password": reg_pass.strip(), "ref_by": reg_inv.strip() or "None"}
                    send_real_verification_email(reg_email.strip(), st.session_state.generated_otp, reg_name.strip())
                    st.session_state.verification_stage = "awaiting_otp"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Existing Profile? Log In"):
            st.session_state.auth_view = "login"
            st.rerun()

    elif st.session_state.auth_view == "login":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h3>Secure Portal Gateway</h3>", unsafe_allow_html=True)
            login_email = st.text_input("Registered Email Address")
            login_pass = st.text_input("Account Secret Password", type="password")
            if st.form_submit_button("Authorize Workspace Connection", use_container_width=True):
                if login_email.strip() == "admin" and login_pass.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    user_record = query_db("SELECT password FROM users WHERE username=?", (login_email.strip(),), one=True)
                    if user_record and user_record[0] == login_pass.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_email.strip()
                        st.session_state.active_sidebar_tab = "Dashboard"
                        st.rerun()
                    else: st.error("Credentials database identification fault.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enroll Profile"): st.session_state.auth_view = "signup"; st.rerun()
        with c2:
            if st.button("🔑 Forgot Passwords?"): st.session_state.auth_view = "forgot_password_request"; st.rerun()

# --- MAIN DASHBOARD INTERFACE TERMINAL ---
else:
    st.markdown('<div class="app-brand-header">👑 GLOBAL MATRIX PREMIUM SYSTEM</div>', unsafe_allow_html=True)
    
    if st.session_state.is_admin:
        st.markdown("## Admin Matrix Controller Terminal")
        st.session_state.admin_video_url = st.text_input("Video URL Target Link:", value=st.session_state.admin_video_url)
        if st.button("Logout Admin Interface Context", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
        for d in deps:
            st.markdown(f"User: {d[1]} | Plan Tier: {d[2]} | Code Hash: {d[6]}")
            if st.button(f"Approve Sequence ID {d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()
                
    else:
        u_data = query_db("SELECT balance, active_level, ref_code, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", 0)
        ready_withdrawal = bal * 0.70

        # --- PREMIUM WALLET HEAD CARD ---
        st.markdown(f"""
        <div class="earnwise-main-card">
            <div class="card-top-title">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
            <div class="card-sub-banner">Pelan VIP/SVIP &amp; Tugasan Media Sosial Diperkenalkan!</div>
            <div class="wallet-grid">
                <div class="wallet-box">
                    <div class="wallet-lbl">💼 DOMPET PEROLEHAN SAYA (CURRENT BALANCE)</div>
                    <div class="wallet-val">RM {bal:,.2f}</div>
                </div>
                <div class="wallet-box" style="border-left: 1px solid rgba(255,255,255,0.15); padding-left:15px;">
                    <div class="wallet-lbl">📤 READY FOR CASHOUT OUTFLOW</div>
                    <div class="wallet-val" style="color: #10b981;">RM {ready_withdrawal:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- ⚡ 100% LEFT SIDEBAR LINE DASHBOARD DABBA MENU ⚡ ---
        # Saare buttons ab left align aur screenshot ke premium dabba format me vertical line me hain
        st.markdown("""
        <div class="v-dabba-container">
            <a href="?nav=Dashboard" target="_self" class="custom-dabba-link db-blue-color">🔹 Deposit Dana / Dashboard Hub</a>
            <a href="?nav=Tasks" target="_self" class="custom-dabba-link db-green-color">🟢 Tarik Perolehan / Play Video Tasks</a>
            <a href="?nav=Deposit" target="_self" class="custom-dabba-link db-orange-color">➕ Fund Wallets Add Balance</a>
            <a href="?nav=Withdrawal" target="_self" class="custom-dabba-link db-purple-color">📤 Cashout System Settlement Node</a>
            <a href="?nav=History" target="_self" class="custom-dabba-link db-slate-color">📜 Ledger History Account Statement</a>
            <a href="?nav=Logout" target="_self" class="custom-dabba-link db-red-color">🚪 Disconnect Secure Portal Connection</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- DYNAMIC ACTIVE SUB-PANELS CONTENT VIEWPORT ---
        if st.session_state.active_sidebar_tab == "Dashboard":
            st.markdown("### Profile Meta Allocation Nodes Overview")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("""
                <div class="premium-widget-box" style="height:120px;">
                    <div class="widget-title-head">Tugasan Tontonan &amp; Bonus Module</div>
                    <p style="font-size:13px; color:#4b5563; margin:0;">Watch streamed sequence loops inside the task panels to instantly unlock matrix allocation balances daily into secure nodes.</p>
                </div>
                """, unsafe_allow_html=True)
            with col_r:
                st.markdown(f"""
                <div class="premium-widget-box" style="height:120px;">
                    <div class="widget-title-head">Pusat Tugasan YouTube &amp; Media (Active Tier)</div>
                    <p style="font-size:13px; color:#4b5563; margin:0;">Active Operational Node Tier Status: <b style="color:#2563eb;">{lvl}</b></p>
                    <p style="font-size:12px; color:#64748b; margin-top:5px;">Unique Invitation Hash Tracking ID Code Token: <b>{code}</b></p>
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Tasks":
            st.markdown("<div class='form-wrapper-box'><h4>Tonton Video &amp; Menang Rewards Workspace</h4>", unsafe_allow_html=True)
            st.video(st.session_state.admin_video_url)
            
            c_time = int(time.time())
            if (c_time - claim_stamp) < 86400:
                rem = 86400 - (c_time - claim_stamp)
                st.error(f"Cooldown active sequence constraint lock block. Time remaining: {rem//3600}h {(rem%3600)//60}m")
            else:
                if st.button("Claim Daily Stream Settlement Token Now", use_container_width=True):
                    bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                    query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                    st.success(f"Execution tracking settlement bonus logged successfully: +RM {bonus:.2f}")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Deposit":
            st.markdown("<div class='form-wrapper-box'><h4>Submit Deposit Verification Payment Slip</h4>", unsafe_allow_html=True)
            with st.form("dep_form_hub"):
                holder = st.text_input("Sender Account Holder Full Title Reference:")
                tx_str = st.text_input("Bank System Verification Transaction Code Token (Trx ID):")
                p_select = st.selectbox("Select Target Deployment Nodes Plan Tier Configuration:", list(LEVELS_CONF.keys()))
                if st.form_submit_button("Hantar Slip Proof Verification Sequence", use_container_width=True):
                    if holder and tx_str:
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                 (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "Bank Transfer", holder, tx_str, "PENDING"), commit=True)
                        st.success("Log submission cached into tracking pipelines.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Withdrawal":
            st.markdown("<div class='form-wrapper-box'><h4>Launch Liquidation Outflow Settlement Connection Terminal</h4>", unsafe_allow_html=True)
            with st.form("with_form_hub"):
                w_val = st.number_input("Value Sum Liquidation Size (RM Units):", min_value=10.0, step=5.0)
                w_net = st.text_input("Destination Routing Accounts / Wallet Matrix Information Data String:")
                if st.form_submit_button("Execute Outflow Cashout Command Link", use_container_width=True):
                    if w_val <= bal:
                        query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                        query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                        st.success("Outflow pipelines execution complete.")
                        st.rerun()
                    else: st.error("Shortfall allocation index bounds error. Insufficient current balance.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "History":
            st.markdown("<div class='form-wrapper-box'><h4>Sejarah Transaksi Terkini Accounts Nodes Tracker</h4>", unsafe_allow_html=True)
            all_deps = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            if not all_deps: st.markdown("<p style='color:#64748b; text-align:center;'>No structural logging transaction steps traced.</p>", unsafe_allow_html=True)
            for dl in all_deps:
                badge_cls = "b-success" if dl[2] == "APPROVED" else "b-pending"
                st.markdown(f"""
                <div class="history-row">
                    <div>Node Level Tier Config Model: <b>{dl[0]}</b></div>
                    <div style="text-align: right;">
                        <b>RM {dl[1]:,.2f}</b><br><span class="badge {badge_cls}">{dl[2]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Global app setting
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="wide")

# --- MALAYSIAN BANKS LIST CONFIGURATION ---
MALAYSIAN_BANKS = [
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad",
    "AmBank (M) Berhad",
    "UOB (United Overseas Bank Malaysia)",
    "Bank Islam Malaysia Berhad",
    "Affin Bank Berhad",
    "Alliance Bank Malaysia Berhad",
    "Standard Chartered Bank Malaysia",
    "HSBC Bank Malaysia Berhad",
    "Bank Muamalat Malaysia Berhad"
]

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

# Session routers state engine (PERSISTENT IN-MEMORY ROUTING)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"

# --- ADVANCED PREMIUM INJECTION CSS ENGINE (EXTRA BOLD FONTS) ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&display=swap" rel="stylesheet">
    
    <style>
    [data-testid="stSidebar"], footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f8fafc !important; }
    
    /* Global Motay Fonts Style */
    * { 
        font-family: 'Plus Jakarta Sans', sans-serif !important; 
        font-weight: 700 !important; 
    }
    
    .app-brand-header {
        background: #0f172a !important;
        padding: 16px !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-align: center !important;
        margin-bottom: 14px !important;
        text-transform: uppercase;
    }

    .clean-auth-card {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 16px !important;
        padding: 26px !important;
        max-width: 450px;
        margin: 35px auto !important;
    }

    /* PREMIUM BALANCE BANNER COMPONENT */
    .earnwise-main-card {
        background: #0d1e3d !important;
        border-radius: 14px !important;
        padding: 20px !important;
        color: #ffffff !important;
        margin-bottom: 18px !important;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .card-top-title { font-size: 15px !important; color: #cbd5e1 !important; font-weight: 800 !important; }
    .card-sub-banner { font-size: 12px !important; color: #fbbf24 !important; font-weight: 900 !important; margin-top: 4px; margin-bottom: 14px; }
    
    .wallet-grid {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        background: rgba(255, 255, 255, 0.07) !important;
        border: 2px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        padding: 14px !important;
    }
    .wallet-box { width: 49% !important; }
    .wallet-lbl { font-size: 11px !important; color: #94a3b8 !important; text-transform: uppercase; font-weight: 800 !important; line-height: 1.3; }
    .wallet-val { font-size: 20px !important; font-weight: 900 !important; color: #ffffff !important; margin-top: 5px; }

    /* DYNAMIC ACTION BUTTON DABBA ELEMENT FOR STREAMLIT INTERNAL BINDING */
    div.stButton > button {
        display: block !important;
        width: 100% !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        text-align: left !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06) !important;
        transition: transform 0.1s ease !important;
        margin-bottom: -10px !important;
    }
    div.stButton > button:hover { color: #ffffff !important; transform: scale(1.01); }
    div.stButton > button:active { transform: scale(0.99); }
    
    /* Pure CSS Overrides for Button Dabba Mappings Verbatim to 1000048041.jpg */
    .btn-blue button { background: #1e62d0 !important; }
    .btn-green button { background: #10b981 !important; }
    .btn-orange button { background: #f97316 !important; }
    .btn-purple button { background: #8b5cf6 !important; }
    .btn-slate button { background: #475569 !important; }
    .btn-red button { background: #ef4444 !important; }

    .premium-widget-box {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 14px !important;
    }
    .widget-title-head { font-size: 15px !important; font-weight: 800 !important; color: #0f172a !important; margin-bottom: 10px !important; }
    
    .form-wrapper-box {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 20px !important;
    }

    .history-row {
        display: flex !important; justify-content: space-between !important; align-items: center !important;
        padding: 12px 0 !important; border-bottom: 2px solid #f1f5f9 !important; font-size: 14px !important;
    }
    .badge { font-size: 12px !important; font-weight: 800 !important; padding: 4px 8px !important; border-radius: 6px; }
    .b-success { background: #dcfce7 !important; color: #15803d !important; }
    .b-pending { background: #fef3c7 !important; color: #b45309 !important; }
    
    /* Make Form labels thicker */
    label p { font-weight: 800 !important; font-size: 14px !important; color: #1e293b !important; }
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
            st.markdown("### Verify Account", unsafe_allow_html=True)
            u_otp = st.text_input("Enter 6-Digit Token")
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
                else: st.error("Token verification invalid.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_view == "forgot_password_request":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("forgot_form"):
            st.markdown("### Reset Password Account", unsafe_allow_html=True)
            r_email = st.text_input("Enter Registered Email Address")
            if st.form_submit_button("Send Recovery Token Code", use_container_width=True):
                user_match = query_db("SELECT full_name FROM users WHERE username=?", (r_email.strip(),), one=True)
                if user_match:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"email": r_email.strip(), "name": user_match[0]}
                    send_real_verification_email(r_email.strip(), st.session_state.generated_otp, user_match[0], "Password Recovery Code")
                    st.session_state.auth_view = "forgot_password_verification"
                    st.rerun()
                else: st.error("Target email layout node not found in system storage.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Back to Sign In Login Portal"):
            st.session_state.auth_view = "login"
            st.rerun()

    elif st.session_state.auth_view == "forgot_password_verification":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("reset_finalize_form"):
            st.markdown("### Enter Recovery Security Token", unsafe_allow_html=True)
            input_token = st.text_input("6-Digit Token Code", max_chars=6)
            new_pass = st.text_input("New Secure Access Password", type="password")
            if st.form_submit_button("Overwrite Security Credentials", use_container_width=True):
                if input_token.strip() == st.session_state.generated_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.temp_register_data['email']), commit=True)
                    st.success("Password overwritten! Proceed to sign-in setup.")
                    st.session_state.auth_view = "login"
                    st.rerun()
                else: st.error("Token validation index misaligned.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.auth_view == "signup":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("reg_form"):
            st.markdown("### Create Platform Node Profile", unsafe_allow_html=True)
            reg_name = st.text_input("Full Profile Name")
            reg_email = st.text_input("Valid Email Address")
            reg_pass = st.text_input("Secure Account Password", type="password")
            reg_inv = st.text_input("Invitation Hash Tracking Code (Optional)")
            if st.form_submit_button("Register Account Credentials", use_container_width=True):
                if "@" in reg_email:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"name": reg_name.strip(), "email": reg_email.strip(), "password": reg_pass.strip(), "ref_by": reg_inv.strip() or "None"}
                    send_real_verification_email(reg_email.strip(), st.session_state.generated_otp, reg_name.strip())
                    st.session_state.verification_stage = "awaiting_otp"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("Already have an account? Access Portal"):
            st.session_state.auth_view = "login"
            st.rerun()

    elif st.session_state.auth_view == "login":
        st.markdown('<div class="clean-auth-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### Account Login Entry Hub", unsafe_allow_html=True)
            login_email = st.text_input("Registered Account Email")
            login_pass = st.text_input("System Security Password", type="password")
            if st.form_submit_button("Authorize Secure Access", use_container_width=True):
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
                    else: st.error("Credentials security pairing failed database matching.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create Profile Account"): st.session_state.auth_view = "signup"; st.rerun()
        with c2:
            if st.button("🔑 Forgot Passwords?"): st.session_state.auth_view = "forgot_password_request"; st.rerun()

# --- MAIN WORKSPACE INTERFACE ---
else:
    st.markdown('<div class="app-brand-header">👑 GLOBAL MATRIX PREMIUM SYSTEM</div>', unsafe_allow_html=True)
    
    if st.session_state.is_admin:
        st.markdown("## Admin Matrix Controller Terminal")
        st.session_state.admin_video_url = st.text_input("Video URL Target Link Configuration:", value=st.session_state.admin_video_url)
        if st.button("Logout Admin Workspace Instance", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
        for d in deps:
            st.markdown(f"User: {d[1]} | Plan Tier Target: {d[2]} | Verification Trx ID: {d[6]}")
            if st.button(f"Approve Sequence Processing Allocation ID {d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()
                
    else:
        u_data = query_db("SELECT balance, active_level, ref_code, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", 0)
        ready_withdrawal = bal * 0.70

        # --- PREMIUM WALLET CARD BANNER ---
        st.markdown(f"""
        <div class="earnwise-main-card">
            <div class="card-top-title">EarnWise: Your Earnings Overview Hub Dashboard (MY)</div>
            <div class="card-sub-banner">VIP/SVIP Tiers &amp; Social Video Streams Active Tasks Systems Live!</div>
            <div class="wallet-grid">
                <div class="wallet-box">
                    <div class="wallet-lbl">💼 MY EARNINGS WALLET NODE (CURRENT BALANCE)</div>
                    <div class="wallet-val">RM {bal:,.2f}</div>
                </div>
                <div class="wallet-box" style="border-left: 1px solid rgba(255,255,255,0.15); padding-left:15px;">
                    <div class="wallet-lbl">📤 READY FOR CASHOUT LIQUIDATION OUTFLOW</div>
                    <div class="wallet-val" style="color: #10b981;">RM {ready_withdrawal:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- ⚡ 100% SECURE STATE-BASED MENU (NO LOGOUT BUG) ⚡ ---
        # Query Strings ko click handlers me badal diya hai taake memory lock safe rahe.
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        if st.button("🔹 Fund Deposit / Dashboard Overview", key="nav_dash"):
            st.session_state.active_sidebar_tab = "Dashboard"
            st.rerun()
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        if st.button("🟢 Claim Revenue / Stream Video Tasks", key="nav_tasks"):
            st.session_state.active_sidebar_tab = "Tasks"
            st.rerun()
        st.markdown('</div><div class="btn-orange">', unsafe_allow_html=True)
        if st.button("➕ Add Wallet Funds Balance Node", key="nav_dep"):
            st.session_state.active_sidebar_tab = "Deposit"
            st.rerun()
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        if st.button("📤 Bank Cashout Liquidation Settlement", key="nav_with"):
            st.session_state.active_sidebar_tab = "Withdrawal"
            st.rerun()
        st.markdown('</div><div class="btn-slate">', unsafe_allow_html=True)
        if st.button("📜 Ledger Statements Account Logs", key="nav_hist"):
            st.session_state.active_sidebar_tab = "History"
            st.rerun()
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        if st.button("🚪 Disconnect Secure Portal Access", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # --- DYNAMIC ACTION VIEWS HOOK PANEL MODULES ---
        if st.session_state.active_sidebar_tab == "Dashboard":
            st.markdown("### Profile Meta Allocation Nodes Overview")
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("""
                <div class="premium-widget-box" style="height:140px;">
                    <div class="widget-title-head">Video Stream Engine &amp; Daily Rewards Module</div>
                    <p style="font-size:13px; color:#4b5563; margin:0; font-weight:700;">Watch allocated video stream loop playback logs within the interface tasks workspace to unlock cloud matrix balances instantly into tracking pipelines.</p>
                </div>
                """, unsafe_allow_html=True)
            with col_r:
                st.markdown(f"""
                <div class="premium-widget-box" style="height:140px;">
                    <div class="widget-title-head">YouTube Streams Tasks Core Center (Active Tier)</div>
                    <p style="font-size:13px; color:#4b5563; margin:0; font-weight:700;">Active Functional Node Profile Level Status: <b style="color:#2563eb;">{lvl}</b></p>
                    <p style="font-size:13px; color:#64748b; margin-top:5px; font-weight:700;">Unique Invitation Hash Tracking Identification Token ID: <b>{code}</b></p>
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Tasks":
            st.markdown("<div class='form-wrapper-box'><h4>Stream Video Playback &amp; Earn Matrix Settlement Tokens</h4>", unsafe_allow_html=True)
            st.video(st.session_state.admin_video_url)
            
            c_time = int(time.time())
            if (c_time - claim_stamp) < 86400:
                rem = 86400 - (c_time - claim_stamp)
                st.error(f"Daily system stream task cooldown lock active. Time remaining execution segment: {rem//3600}h {(rem%3600)//60}m")
            else:
                if st.button("Claim Daily Video Processing Reward Yield Allocation Now", use_container_width=True):
                    bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                    query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                    st.success(f"Execution tracking settlement stream balance assigned logged: +RM {bonus:.2f}")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Deposit":
            st.markdown("<div class='form-wrapper-box'><h4>Submit Local Malaysian Bank Transfer Deposit Proof Slip</h4>", unsafe_allow_html=True)
            with st.form("dep_form_hub"):
                deposit_bank = st.selectbox("Select Your Malaysian Bank Node Used for Deposit Transfer:", MALAYSIAN_BANKS)
                holder = st.text_input("Sender Account Holder Name/Title:")
                tx_str = st.text_input("Bank System Payment Verification Transaction Reference Number (Trx ID):")
                p_select = st.selectbox("Select Target Active Investment Nodes Deployment Level Configuration:", list(LEVELS_CONF.keys()))
                if st.form_submit_button("Submit Deposit Proof Payment Slip Metadata", use_container_width=True):
                    if holder and tx_str:
                        method_string = f"Bank Transfer ({deposit_bank})"
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                 (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], method_string, holder, tx_str, "PENDING"), commit=True)
                        st.success("Log submission payment confirmation pending admin verification check.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "Withdrawal":
            st.markdown("<div class='form-wrapper-box'><h4>Configure Bank Liquidation Cashout Outflow Node Connection</h4>", unsafe_allow_html=True)
            with st.form("with_form_hub"):
                withdrawal_bank = st.selectbox("Select Target Malaysian Bank Destination Node Account Receive:", MALAYSIAN_BANKS)
                w_acc_num = st.text_input("Receiver Bank Account Number:")
                w_acc_title = st.text_input("Receiver Bank Account Title/Full Name:")
                w_val = st.number_input("Value Sum Cashout Size (RM Units):", min_value=10.0, step=5.0)
                if st.form_submit_button("Execute Outflow Cashout Command Authorization Pipeline", use_container_width=True):
                    if w_val <= bal:
                        routing_string = f"Bank: {withdrawal_bank} | Acc Num: {w_acc_num} | Title: {w_acc_title}"
                        query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                        query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, routing_string, "PENDING"), commit=True)
                        st.success("Outflow pipeline cache registration entry recorded. Settlement updates follow processing blocks.")
                        st.rerun()
                    else: st.error("Shortfall tracking allocation index limits. Insufficient current balance index funds.")
            st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.active_sidebar_tab == "History":
            st.markdown("<div class='form-wrapper-box'><h4>Recent Account Nodes Transaction History Statements Ledger</h4>", unsafe_allow_html=True)
            all_deps = query_db("SELECT level, amount, status, method FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            if not all_deps: st.markdown("<p style='color:#64748b; text-align:center;'>No structural ledger transactions traced in data pipelines.</p>", unsafe_allow_html=True)
            for dl in all_deps:
                badge_cls = "b-success" if dl[2] == "APPROVED" else "b-pending"
                st.markdown(f"""
                <div class="history-row">
                    <div>Node Model: <b style="font-weight:900 !important;">{dl[0]}</b><br><small style="color:#64748b;">Source: {dl[3]}</small></div>
                    <div style="text-align: right;">
                        <b style="font-weight:900 !important;">RM {dl[1]:,.2f}</b><br><span class="badge {badge_cls}">{dl[2]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

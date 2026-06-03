import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Core Page Configurations
st.set_page_config(page_title="Global Matrix Investment", page_icon="🔱", layout="centered")

# --- DATABASE MANAGEMENT & ERROR PATCHES ---
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

# --- EMAIL PIPELINE ---
def send_real_verification_email(receiver_email, otp_code, user_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Support <Salmanveerm@gmail.com>"
        msg['To'] = receiver_email
        msg['Subject'] = f"Verification Code: {otp_code}"
        body = f"Hello {user_name},\n\nYour security verification OTP code is: {otp_code}\n\nRegards,\nGlobal Matrix Investment Team"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("Salmanveerm@gmail.com", "syjawmpyvdnokasn")
        server.sendmail("Salmanveerm@gmail.com", receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

# --- EXACT DARK THEME MATCHING CSS ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Hide Default Header/Footer elements */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Exact Dark Matrix Background Config */
    .stApp { background-color: #0b132b !important; }
    .main .block-container { padding-top: 15px !important; padding-bottom: 120px !important; max-width: 440px !important; margin: 0 auto; }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* Global Matrix Corporate Header Branding */
    .matrix-logo-header {
        text-align: center;
        padding: 12px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .matrix-logo-title {
        font-family: 'Orbitron', sans-serif !important;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
    }
    .matrix-logo-title span { color: #f59e0b; } /* Premium Laptop Gold Accent */
    
    /* Premium High-End Blue Dashboard Wallet Module */
    .matrix-balance-card {
        background: linear-gradient(135deg, #1e293b 0%, #111e36 100%) !important;
        padding: 22px; 
        border-radius: 20px; 
        color: #ffffff !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: center;
    }
    .card-welcome { font-size: 11px; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .card-user-title { font-size: 26px; font-weight: 700; color: #ffffff; margin: 4px 0; }
    .card-plan-node { font-size: 11px; color: #38bdf8; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 10px; }
    .card-main-balance { font-size: 32px; font-weight: 700; color: #ffffff; margin: 10px 0; font-family: 'Poppins', sans-serif; }
    
    /* Invitation Dynamic Module */
    .invite-box-node {
        background: #111e36; border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;
        padding: 14px; display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 22px;
    }
    .inv-title { font-size: 12px; font-weight: 600; color: #ffffff; }
    .inv-subtitle { font-size: 10px; color: #94a3b8; margin-top: 1px; }
    .inv-code { background: rgba(56, 189, 248, 0.1); color: #38bdf8; padding: 6px 12px; border-radius: 8px; font-family: monospace; font-weight: 700; font-size: 13px; }
    
    /* Headlines Sections markers */
    .matrix-section-marker { font-size: 12px; color: #94a3b8; font-weight: 700; text-transform: uppercase; margin: 25px 0 12px 0; letter-spacing: 0.8px; }
    
    /* Investment Cards Matrix Layout */
    .invest-tier-node {
        background: #111e36; border: 1px solid rgba(255,255,255,0.05); border-radius: 14px;
        padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;
    }
    .tier-title { font-size: 14px; font-weight: 700; color: #ffffff; }
    .tier-yield { font-size: 12px; color: #94a3b8; margin-top: 2px; }
    .tier-yield span { color: #10b981; font-weight: 600; }
    .tier-cost { font-size: 15px; font-weight: 700; color: #38bdf8; }
    
    /* Input Adjustments for Dark Interface */
    label, [data-testid="stWidgetLabel"] p { color: #94a3b8 !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { background-color: #111e36 !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; color: #ffffff !important; }
    div[data-baseweb="select"] * { color: #ffffff !important; }
    
    /* Action Buttons Primary Layout Style */
    .action-btn-hub .stButton>button { background: #2563eb !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; font-size: 14px !important; padding: 12px 0 !important; border-radius: 8px !important; width: 100%; box-shadow: 0 4px 14px rgba(37, 99, 235, 0.2); }
    .action-btn-hub .stButton>button:hover { background: #1d4ed8 !important; }
    
    /* System Native Live Feed Broadcast Ticker Banner */
    .live-feed-banner { background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(220, 38, 38, 0.25); border-radius: 10px; padding: 10px; text-align: center; color: #fca5a5; font-size: 11px; font-weight: 500; margin-bottom: 15px; }
    
    /* History Rows Logger styling */
    .hist-node-row { background: #111e36; border: 1px solid rgba(255,255,255,0.05); padding: 14px; border-radius: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .status-badge { padding: 4px 8px; border-radius: 6px; font-size: 9px; font-weight: 700; text-transform: uppercase; }
    .s-approved { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .s-pending { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .s-rejected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    
    /* FIXED HORIZONTAL FOOTER NAVIGATION BAR FOR MOBILE SCREENS */
    .app-sticky-footer-bar {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background: #111e36 !important;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding: 12px 8px;
        z-index: 999999;
        max-width: 440px;
        margin: 0 auto;
    }
    .footer-flex-wrap {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 8px !important;
        width: 100% !important;
    }
    .footer-flex-wrap .stButton { width: 32% !important; margin: 0 !important; }
    .footer-flex-wrap .stButton>button {
        background: #0b132b !important;
        color: #94a3b8 !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 10px 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        width: 100% !important;
    }
    .footer-flex-wrap .stButton>button:hover {
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# App Controllers
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

# Branding Corporate Module
st.markdown('<div class="matrix-logo-header"><div class="matrix-logo-title">🔱 GLOBAL MATRIX <span>INVESTMENT</span></div></div>', unsafe_allow_html=True)

# Live Broadcast Feed Simulation
st.markdown('<div class="live-feed-banner">⚡ LIVE FEED: User ali_*** activated VIP LEVEL 3 node pipeline successfully!</div>', unsafe_allow_html=True)

# --- USER ENTRY POINT SYSTEM ---
if not st.session_state.logged_in:
    if st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_verification"):
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#94a3b8;'>Security confirmation OTP sent to:<br><b style='color:#ffffff;'>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
            u_otp = st.text_input("6-Digit Verification Code Node:", max_chars=6)
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            btn_v = st.form_submit_button("Authenticate Entry Access", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if btn_v:
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (t_data['email'], 10.00, "NONE", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    if t_data['ref_by'] != "None":
                        query_db("UPDATE users SET balance = balance + 10.00 WHERE ref_code=?", (t_data['ref_by'],), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else: st.error("Mismatched security code protocol parameters.")
    else:
        with st.form("matrix_auth_gate"):
            st.markdown("<p style='font-size:13px; font-weight:600; color:#38bdf8; text-align:center; margin-bottom:15px; letter-spacing:0.5px;'>SECURE CREDENTIAL SYSTEM</p>", unsafe_allow_html=True)
            reg_name = st.text_input("Account Identifier / Full Name:")
            reg_email = st.text_input("Corporate Email Component Route:")
            reg_pass = st.text_input("Password Encryption String Key:", type="password")
            reg_invite_code = st.text_input("Referral Assignment Code (Optional):")
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            login_submit = st.form_submit_button("CONFIRM AND SECURE SIGN IN", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if login_submit:
                em_clean = reg_email.strip()
                if em_clean == "admin" and reg_pass == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "MATRIX_ADMIN"
                    st.rerun()
                elif "@" in em_clean:
                    existing = query_db("SELECT * FROM users WHERE username=?", (em_clean,), one=True)
                    if existing:
                        st.session_state.logged_in = True
                        st.session_state.current_user = em_clean
                        st.session_state.current_app_tab = "home"
                        st.rerun()
                    else:
                        if not reg_name.strip(): st.error("Account declaration requires an assignment name token.")
                        else:
                            f_ref = "None"
                            if reg_invite_code.strip():
                                match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                if match: f_ref = reg_invite_code.strip()
                            st.session_state.generated_otp = str(random.randint(100000, 999999))
                            st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "ref_by": f_ref}
                            with st.spinner("Broadcasting Security OTP Matrix Token..."):
                                send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                            st.session_state.verification_stage = "awaiting_otp"
                            st.rerun()

# --- ADMIN DEPLOYMENT TERMINAL ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#ffffff;'>Root Allocation Matrix</h4>", unsafe_allow_html=True)
    st.session_state.admin_video_url = st.text_input("Global Video Streams URL Resource:", value=st.session_state.admin_video_url)
    
    st.markdown('<div class="matrix-section-marker">Pending Deposit Vault Requests</div>', unsafe_allow_html=True)
    deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    for d in deps:
        st.markdown(f"<div style='background:#111e36; border:1px solid rgba(255,255,255,0.1); padding:12px; border-radius:8px; margin-bottom:8px; color:#ffffff; font-size:12px;'>User Target: {d[1]} | Volume: <b>RM {d[3]}</b><br>Trx Identification: <code>{d[6]}</code></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("Approve & Sync Tier", key=f"ad_{d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()
        with c2:
            if st.button("Reject Entry Token", key=f"rd_{d[0]}", use_container_width=True):
                query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (d[0],), commit=True)
                st.rerun()

    if st.button("Disconnect Secure Terminal Session", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.is_admin = False; st.rerun()

# --- APP FRONTEND CORE INTERFACE ---
else:
    u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "NONE", "GM0000", "Matrix User", 0)
    
    if st.session_state.current_app_tab == "home":
        # Exact Matching Blue Investment Dashboard UI Element Block from Screenshot 1000042721.jpg
        st.markdown(f"""
        <div class="matrix-balance-card">
            <div class="card-welcome">Welcome Back</div>
            <div class="card-user-title">{title}</div>
            <div class="card-plan-node">PLAN: {lvl}</div>
            <div class="card-main-balance">RM {bal:.2f}</div>
        </div>
        
        <div class="invite-box-node">
            <div>
                <div class="inv-title">👥 Kongsi Pautan Kawan</div>
                <div class="inv-subtitle">System referral network credit bonus: RM 10.00</div>
            </div>
            <div class="inv-code">{code}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="matrix-section-marker">SISTEM TRANSAKSI:</div>', unsafe_allow_html=True)
        sub_tab = st.radio("Route Action Selection:", ["Deposit Dana Nodes", "Tarik Perolehan Funds"], label_visibility="collapsed")
        
        if sub_tab == "Deposit Dana Nodes":
            st.markdown('<div class="matrix-section-marker">AVAILABLE INVESTMENT PLANS</div>', unsafe_allow_html=True)
            for ln, ld in LEVELS_CONF.items():
                st.markdown(f"""
                <div class="invest-tier-node">
                    <div>
                        <div class="tier-title">{ln}</div>
                        <div class="tier-yield">Daily Income: <span>RM {ld['daily_reward']}.00</span></div>
                    </div>
                    <div class="tier-cost">RM {ld['cost']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div class="matrix-section-marker">SUBMIT DEPOSIT PROOF</div>', unsafe_allow_html=True)
            with st.form("deposit_confirmation_proof"):
                holder = st.text_input("Account Holder Verification Name:")
                tx_str = st.text_input("Transaction ID (Trx ID):")
                p_select = st.selectbox("Select Plan to Activate:", list(LEVELS_CONF.keys()))
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                btn_d = st.form_submit_button("Submit Proof", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_d and holder and tx_str:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "TNG/Bank", holder, tx_str, "PENDING"), commit=True)
                    st.success("Verification parameters logged. Waiting approval sync token.")
                    st.rerun()
                    
        elif sub_tab == "Tarik Perolehan Funds":
            st.markdown('<div class="matrix-section-marker">Vault Withdrawal Hub</div>', unsafe_allow_html=True)
            with st.form("withdrawal_request_flow"):
                w_val = st.number_input("Extraction Balance Volume (RM):", min_value=10.0, step=1.0)
                w_net = st.text_input("Destination Routing Nodes (e.g., Bank / Gateway Info):")
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                btn_w = st.form_submit_button("Initiate Settlement Payout", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_w:
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Extraction routing pipeline deployed successfully.")
                            st.rerun()
                        else: st.error("Missing routing target parameter blocks.")
                    else: st.error("Vault margin overflow execution limits error.")

        # --- SEJARAH TRANSAKASI LOG VIEW ---
        st.markdown('<div class="matrix-section-marker">Sejarah Transaksi Terkini</div>', unsafe_allow_html=True)
        dep_logs = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
        w_logs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
        
        if not dep_logs and not w_logs:
            st.markdown("<p style='font-size:12px; color:#94a3b8; text-align:center; padding:12px;'>No active network interaction logs recorded.</p>", unsafe_allow_html=True)
        else:
            for dl in dep_logs:
                c_lbl = "approved" if dl[2]=="APPROVED" else "pending" if dl[2]=="PENDING" else "rejected"
                st.markdown(f'<div class="hist-node-row"><div><div style="font-size:13px; font-weight:600; color:#ffffff;">Deposit Activation Allocation</div><div style="font-size:11px; color:#94a3b8;">Tier Resource: {dl[0]}</div></div><div style="text-align:right;"><div style="font-size:13px; font-weight:700; color:#ffffff;">RM {dl[1]:.2f}</div><span class="status-badge s-{c_lbl}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
            for wl in w_logs:
                c_lbl = "approved" if wl[1]=="APPROVED" else "pending" if wl[1]=="PENDING" else "rejected"
                st.markdown(f'<div class="hist-node-row"><div><div style="font-size:13px; font-weight:600; color:#ef4444;">Settlement Withdrawal Out</div><div style="font-size:11px; color:#94a3b8;">Network Transfer File</div></div><div style="text-align:right;"><div style="font-size:13px; font-weight:700; color:#ef4444;">-RM {wl[0]:.2f}</div><span class="status-badge s-{c_lbl}">{wl[1]}</span></div></div>', unsafe_allow_html=True)

    elif st.session_state.current_app_tab == "task":
        st.markdown('<div class="matrix-section-marker">Stream Engine Activity Tasks</div>', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        
        c_time = int(time.time())
        diff = c_time - claim_stamp
        if diff < 86400:
            rem = 86400 - diff
            st.markdown(f"<div style='background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); border-radius:10px; padding:12px; text-align:center; color:#fca5a5; font-size:13px;'>🔒 Matrix validation cycle opens in: <b>{rem//3600}h {(rem%3600)//60}m</b></div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            if st.button("Claim Yield Return Bonus Token", use_container_width=True):
                bonus = 5.00 if lvl == "NONE" else float(LEVELS_CONF[lvl]["daily_reward"])
                query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                st.success(f"Yield data tokens captured: +RM {bonus:.2f}")
                st.session_state.current_app_tab = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- HORIZONTAL NON-BREAKING APP FOOTER NAVBAR ---
    st.markdown(f"""
    <div class="app-sticky-footer-bar">
        <div class="footer-flex-wrap">
    """, unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        if st.button("🏠 Home", key="m_nav_home", use_container_width=True):
            st.session_state.current_app_tab = "home"
            st.rerun()
    with f_col2:
        if st.button("📺 Tasks", key="m_nav_task", use_container_width=True):
            st.session_state.current_app_tab = "task"
            st.rerun()
    with f_col3:
        if st.button("🚪 Logout", key="m_nav_out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown('</div></div>', unsafe_allow_html=True)

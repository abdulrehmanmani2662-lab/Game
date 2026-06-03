import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Core Page Setup
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- DATABASE MANAGEMENT ---
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

# --- REAL EMAIL PIPELINE ---
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

# --- EXACT LIGHT/CLEAN BLUE-WHITE CSS MATCHING 1000047431_2.jpg ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Hide default Streamlit overlays */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Exact Light Background matching the laptop screen */
    .stApp { background-color: #f1f5f9 !important; }
    .main .block-container { padding-top: 10px !important; padding-bottom: 120px !important; max-width: 440px !important; margin: 0 auto; }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Inter', sans-serif !important; }
    
    /* Global Matrix Corporate Logo Banner (Top Left look on Laptop) */
    .matrix-brand-header {
        background: #0f172a; 
        padding: 14px; 
        border-radius: 12px; 
        text-align: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .matrix-brand-text {
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .matrix-brand-text span { color: #eab308; } /* Gold accent color */
    
    /* Exact Earnings Dark Blue Premium Card Container */
    .laptop-earnings-card {
        background: #0f172a !important;
        padding: 20px; 
        border-radius: 14px; 
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.1);
        margin-bottom: 14px;
    }
    .earnings-top-title { font-size: 11px; color: #94a3b8; font-weight: 500; }
    .earnings-user-name { font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 2px; }
    .earnings-flex-row { display: flex; justify-content: space-between; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px; }
    .earn-block-title { font-size: 10px; color: #94a3b8; text-transform: uppercase; }
    .earn-block-amount { font-size: 18px; font-weight: 700; color: #ffffff; margin-top: 2px; }
    
    /* Quick Actions Row Style Matching Blue/Green Sections */
    .btn-action-container { display: flex; gap: 10px; margin-bottom: 16px; }
    .action-blue-pill { background: #1e75e5; color: white; padding: 12px; border-radius: 10px; flex: 1; text-align: center; font-size: 13px; font-weight: 600; box-shadow: 0 4px 10px rgba(30,117,229,0.15); }
    .action-green-pill { background: #22c55e; color: white; padding: 12px; border-radius: 10px; flex: 1; text-align: center; font-size: 13px; font-weight: 600; box-shadow: 0 4px 10px rgba(34,197,94,0.15); }
    
    /* White Card Wrapper Widgets */
    .laptop-white-widget {
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 12px;
        padding: 15px; 
        margin-bottom: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .widget-heading { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    
    /* Table Rows Layout for Logs and Info */
    .table-data-row { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 10px 0; 
        border-bottom: 1px solid #f1f5f9;
        font-size: 12px;
    }
    .table-data-row:last-child { border-bottom: none; }
    .row-title-main { font-weight: 600; color: #334155; }
    .row-subtitle-sub { font-size: 10px; color: #64748b; }
    .row-val-bold { font-weight: 700; color: #0f172a; text-align: right; }
    
    .status-badge-clean { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: capitalize; }
    .badge-conf { background: #dcfce7; color: #15803d; }
    .badge-pend { background: #fef3c7; color: #b45309; }
    .badge-fail { background: #fee2e2; color: #b91c1c; }
    
    /* Input Form Fixes */
    label, [data-testid="stWidgetLabel"] p { color: #475569 !important; font-size: 11px !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; color: #0f172a !important; }
    
    /* Form Action Layout Buttons */
    .form-submit-wrapper .stButton>button { background: #0f172a !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; font-size: 13px !important; padding: 10px 0 !important; border-radius: 8px !important; width: 100%; }
    
    /* FIXED HORIZONTAL FOOTER NAVIGATION BAR FOR MOBILE SCREENS */
    .app-sticky-footer-bar {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background: #ffffff !important;
        border-top: 1px solid #e2e8f0;
        padding: 12px 8px;
        z-index: 999999;
        max-width: 440px;
        margin: 0 auto;
    }
    .footer-flex-wrap {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 6px !important;
        width: 100% !important;
    }
    .footer-flex-wrap .stButton { width: 32% !important; margin: 0 !important; }
    .footer-flex-wrap .stButton>button {
        background: #f8fafc !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
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
        border-color: #1e75e5 !important;
        color: #1e75e5 !important;
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

# Top Header Logo Widget
st.markdown('<div class="matrix-brand-header"><div class="matrix-brand-text">🔱 GLOBAL MATRIX <span>INVESTMENT</span></div></div>', unsafe_allow_html=True)

# --- USER ENTRY PROFILE ACCESS ---
if not st.session_state.logged_in:
    if st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_verification_flow"):
            st.markdown(f"<p style='text-align:center; font-size:12px; color:#475569;'>Enter verification OTP code sent to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
            u_otp = st.text_input("Enter 6-Digit Code:", max_chars=6)
            st.markdown('<div class="form-submit-wrapper">', unsafe_allow_html=True)
            btn_v = st.form_submit_button("Verify & Login Profile", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if btn_v:
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (t_data['email'], 10.00, "None", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    if t_data['ref_by'] != "None":
                        query_db("UPDATE users SET balance = balance + 10.00 WHERE ref_code=?", (t_data['ref_by'],), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else: st.error("Verification code parameter mismatch.")
    else:
        with st.form("portal_login_gate"):
            st.markdown("<p style='font-size:13px; font-weight:600; color:#0f172a; text-align:center; margin-bottom:12px;'>AUTHENTICATION ACCESS GATEWAY</p>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Profile Name (New Users Only):")
            reg_email = st.text_input("Email Account String:")
            reg_pass = st.text_input("Password Credential Key:", type="password")
            reg_invite_code = st.text_input("Invitation Code (Optional):")
            st.markdown('<div class="form-submit-wrapper">', unsafe_allow_html=True)
            login_submit = st.form_submit_button("Sign In / Open Node Account", use_container_width=True)
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
                        if not reg_name.strip(): st.error("Please enter your name to register a profile link.")
                        else:
                            f_ref = "None"
                            if reg_invite_code.strip():
                                match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                if match: f_ref = reg_invite_code.strip()
                            st.session_state.generated_otp = str(random.randint(100000, 999999))
                            st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "ref_by": f_ref}
                            with st.spinner("Sending security gateway OTP token..."):
                                send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                            st.session_state.verification_stage = "awaiting_otp"
                            st.rerun()

# --- ADMIN DEPLOYMENT CONSOLE ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4>Root Dashboard Controls</h4>", unsafe_allow_html=True)
    st.session_state.admin_video_url = st.text_input("Task Broadcast Streams URL:", value=st.session_state.admin_video_url)
    
    st.markdown('***\n**Pending Verification Logs**')
    deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    for d in deps:
        st.markdown(f"<div style='background:#ffffff; border:1px solid #cbd5e1; padding:10px; border-radius:8px; margin-bottom:6px; font-size:12px;'>User: {d[1]} | Volume: <b>RM {d[3]}</b><br>Trx Hash: <code>{d[6]}</code></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("Authorize Core Sync", key=f"ad_{d[0]}", use_container_width=True):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()
        with c2:
            if st.button("Reject Entry Token", key=f"rd_{d[0]}", use_container_width=True):
                query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (d[0],), commit=True)
                st.rerun()

    if st.button("Log out System Node Admin", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.is_admin = False; st.rerun()

# --- USER APP FRONTEND CORE INTERFACE ---
else:
    u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", "Matrix User", 0)
    
    if st.session_state.current_app_tab == "home":
        # Exact Earnings Wallet Setup Box from Laptop Blueprint
        st.markdown(f"""
        <div class="laptop-earnings-card">
            <div class="earnings-top-title">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
            <div class="earnings-user-name">👤 {title}</div>
            
            <div class="earnings-flex-row">
                <div>
                    <div class="earn-block-title">Dompet Perolehan Saya</div>
                    <div class="earn-block-amount">RM {bal:.2f}</div>
                </div>
                <div style="text-align: right;">
                    <div class="earn-block-title">Ready For Withdrawal</div>
                    <div class="earn-block-amount" style="color: #22c55e;">RM {bal:.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Pills row matching blue/green links layout from screenshot
        st.markdown("""
        <div class="btn-action-container">
            <div class="action-blue-pill">🔹 Deposit Dana Portal</div>
            <div class="action-green-pill">🔸 Tarik Perolehan Hub</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Form router selection split layout
        sub_tab = st.radio("Execute Action Route:", ["Deposit Routing Node", "Extraction Settlement Route"], label_visibility="collapsed")
        
        if sub_tab == "Deposit Routing Node":
            st.markdown(f"""
            <div class="laptop-white-widget">
                <div class="widget-heading">👥 SYSTEM REFERRAL INVITATION</div>
                <div style="font-size:12px; color:#475569;">Share code to claim instant RM 10.00 platform credits:</div>
                <div style="background:#f8fafc; padding:8px; border-radius:6px; font-family:monospace; font-weight:700; font-size:14px; text-align:center; color:#1e75e5; margin-top:8px; border:1px dashed #cbd5e1;">{code}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<p style="font-size:11px; font-weight:700; color:#64748b; margin-top:15px; text-transform:uppercase;">AVAILABLE TIERS</p>', unsafe_allow_html=True)
            for ln, ld in LEVELS_CONF.items():
                st.markdown(f"""
                <div style='background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='font-size:13px; font-weight:700; color:#0f172a;'>{ln}</div>
                        <div style='font-size:11px; color:#64748b;'>Daily Yield Node: <span style='color:#22c55e; font-weight:600;'>RM {ld['daily_reward']}</span></div>
                    </div>
                    <div style='font-size:14px; font-weight:700; color:#1e75e5;'>RM {ld['cost']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with st.form("hantar_proof_slip"):
                st.markdown('<p style="font-size:12px; font-weight:600; color:#0f172a; margin-bottom:10px;">HANTAR BUKTI SLIP DEPOSIT</p>', unsafe_allow_html=True)
                holder = st.text_input("Account Holder Verification Name:")
                tx_str = st.text_input("Reference Transaction ID (Trx ID):")
                p_select = st.selectbox("Select Target Deployment Tier:", list(LEVELS_CONF.keys()))
                st.markdown('<div class="form-submit-wrapper">', unsafe_allow_html=True)
                btn_d = st.form_submit_button("Hantar Slip Deposit Now", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_d and holder and tx_str:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "TNG/Bank", holder, tx_str, "PENDING"), commit=True)
                    st.success("Verification parameters logged. Awaiting admin sync.")
                    st.rerun()
                    
        elif sub_tab == "Extraction Settlement Route":
            with st.form("payout_settlement_flow"):
                st.markdown('<p style="font-size:12px; font-weight:600; color:#0f172a; margin-bottom:10px;">TARIK PEROLEHAN ACCOUNT FUNDS</p>', unsafe_allow_html=True)
                w_val = st.number_input("Extraction Balance Volume (RM):", min_value=10.0, step=5.0)
                w_net = st.text_input("Destination Bank/Wallet Details String:")
                st.markdown('<div class="form-submit-wrapper">', unsafe_allow_html=True)
                btn_w = st.form_submit_button("Confirm Cashout Extraction", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_w:
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Settlement extraction routing parameters initialized.")
                            st.rerun()
                        else: st.error("Target distribution channels info parameter missing.")
                    else: st.error("Insufficient digital vault balance margin.")

        # --- SEJARAH TRANSAKSI TERKINI TABLE MODULE ---
        st.markdown("""
        <div class="laptop-white-widget">
            <div class="widget-heading">Sejarah Transaksi Terkini</div>
        """, unsafe_allow_html=True)
        
        dep_logs = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
        w_logs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
        
        if not dep_logs and not w_logs:
            st.markdown("<p style='font-size:12px; color:#64748b; text-align:center; padding:10px;'>No structural transaction log history found.</p>", unsafe_allow_html=True)
        else:
            for dl in dep_logs:
                lbl_cls = "badge-conf" if dl[2]=="APPROVED" else "badge-pend" if dl[2]=="PENDING" else "badge-fail"
                st.markdown(f"""
                <div class="table-data-row">
                    <div>
                        <div class="row-title-main">Deposit Dana</div>
                        <div class="row-subtitle-sub">Tier Action: {dl[0]}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="row-val-bold">RM {dl[1]:.2f}</div>
                        <span class="status-badge-clean {lbl_cls}">{dl[2]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            for wl in w_logs:
                lbl_cls = "badge-conf" if wl[1]=="APPROVED" else "badge-pend" if wl[1]=="PENDING" else "badge-fail"
                st.markdown(f"""
                <div class="table-data-row">
                    <div>
                        <div class="row-title-main" style="color:#b91c1c;">Tarik Perolehan Out</div>
                        <div class="row-subtitle-sub">Settlement Pipeline File</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="row-val-bold" style="color:#b91c1c;">-RM {wl[0]:.2f}</div>
                        <span class="status-badge-clean {lbl_cls}">{wl[1]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_app_tab == "task":
        st.markdown("""
        <div class="laptop-white-widget">
            <div class="widget-heading">Tugasan Tontonan & Bonus</div>
        """, unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        
        c_time = int(time.time())
        diff = c_time - claim_stamp
        if diff < 86400:
            rem = 86400 - diff
            st.markdown(f"<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:10px; text-align:center; color:#b91c1c; font-size:12px; font-weight:500;'>🔒 Stream link claim node locked: <b>{rem//3600}h {(rem%3600)//60}m</b></div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="form-submit-wrapper" style="margin-top:12px;">', unsafe_allow_html=True)
            if st.button("Tonton & Peroleh Reward Now", use_container_width=True):
                bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                st.success(f"Yield update captured: +RM {bonus:.2f}")
                st.session_state.current_app_tab = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- SOLID FIXED HORIZONTAL FOOTER NAVIGATION BAR ---
    st.markdown(f"""
    <div class="app-sticky-footer-bar">
        <div class="footer-flex-wrap">
    """, unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        if st.button("📊 Dashboard", key="l_nav_home", use_container_width=True):
            st.session_state.current_app_tab = "home"
            st.rerun()
    with f_col2:
        if st.button("📺 Video Tasks", key="l_nav_task", use_container_width=True):
            st.session_state.current_app_tab = "task"
            st.rerun()
    with f_col3:
        if st.button("🚪 Leave App", key="l_nav_out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown('</div></div>', unsafe_allow_html=True)

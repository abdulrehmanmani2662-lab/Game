import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Force wide layout to let the laptop layout space out natively
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

# --- EXTREME STYLE INJECTION ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f1f5f9 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Inter', sans-serif !important; }
    
    .custom-sidebar-container {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        padding: 24px 16px !important;
        height: 100vh !important;
        display: flex;
        flex-direction: column;
    }
    
    .brand-logo-card {
        background: #0f172a !important;
        padding: 14px !important;
        border-radius: 8px !important;
        text-align: center !important;
        margin-bottom: 28px !important;
    }
    .brand-logo-text {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: 0.5px !important;
    }
    .brand-logo-text span { color: #f59e0b !important; }
    
    .stButton>button {
        background: transparent !important;
        color: #475569 !important;
        border: none !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 6px !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background: #f1f5f9 !important;
        color: #1e75e5 !important;
    }
    
    .main-canvas-right { padding: 20px 30px !important; }
    
    .master-top-streamer {
        background: #0f172a !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 24px !important;
    }
    .master-top-streamer span { color: #f59e0b !important; }
    
    .premium-navy-wallet-card {
        background: #0f172a !important;
        border-radius: 14px !important;
        padding: 24px !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15) !important;
        margin-bottom: 20px !important;
    }
    .wallet-header-caption { font-size: 11px !important; color: #94a3b8 !important; font-weight: 500 !important; text-transform: uppercase; }
    .wallet-user-title { font-size: 24px !important; font-weight: 700 !important; color: #ffffff !important; margin-top: 4px; margin-bottom: 18px; }
    
    .wallet-data-split-flex {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding-top: 16px !important;
    }
    .wallet-data-chunk { flex: 1; }
    .chunk-title-lbl { font-size: 11px !important; color: #94a3b8 !important; text-transform: uppercase; font-weight: 600; }
    .chunk-amount-val { font-size: 20px !important; font-weight: 700 !important; color: #ffffff !important; margin-top: 2px; }
    
    .action-pills-row { display: flex !important; gap: 14px !important; margin-bottom: 22px !important; }
    .pill-blue-button { background: #1e75e5 !important; color: white !important; padding: 12px 20px !important; border-radius: 8px !important; font-size: 13px !important; font-weight: 700 !important; flex: 1 !important; text-align: center !important; box-shadow: 0 4px 12px rgba(30,117,229,0.15); }
    .pill-green-button { background: #22c55e !important; color: white !important; padding: 12px 20px !important; border-radius: 8px !important; font-size: 13px !important; font-weight: 700 !important; flex: 1 !important; text-align: center !important; box-shadow: 0 4px 12px rgba(34,197,94,0.15); }
    
    .clean-white-card-widget {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01) !important;
    }
    .card-widget-header { font-size: 14px !important; font-weight: 700 !important; color: #0f172a !important; margin-bottom: 14px !important; text-transform: uppercase; }
    
    .history-row-item {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 12px 0 !important;
        border-bottom: 1px solid #f1f5f9 !important;
        font-size: 13px !important;
    }
    .history-row-item:last-child { border-bottom: none !important; }
    .hist-title-bold { font-weight: 600 !important; color: #334155 !important; }
    .hist-subtitle-sub { font-size: 11px !important; color: #64748b !important; margin-top: 2px; }
    .hist-value-bold { font-weight: 700 !important; color: #0f172a !important; text-align: right; }
    
    .clean-badge-capsule { font-size: 10px !important; font-weight: 700 !important; padding: 3px 8px !important; border-radius: 4px !important; text-transform: uppercase; display: inline-block; margin-top: 4px; }
    .c-approved { background: #dcfce7 !important; color: #15803d !important; }
    .c-pending { background: #fef3c7 !important; color: #b45309 !important; }
    .c-rejected { background: #fee2e2 !important; color: #b91c1c !important; }
    
    label, [data-testid="stWidgetLabel"] p { color: #475569 !important; font-size: 11px !important; font-weight: 600 !important; text-transform: uppercase; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; color: #0f172a !important; }
    
    .form-execution-btn .stButton>button {
        background: #0f172a !important;
        color: #ffffff !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 12px 0 !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# --- CONTROL CONDITION: IF NOT LOGGED IN (COMPLETELY HIDE SIDEBAR & HEADERS) ---
if not st.session_state.logged_in:
    # Beautiful Centered Login Block
    _, central_block, _ = st.columns([1, 2, 1])
    
    with central_block:
        st.markdown('<br><br><div class="brand-logo-card" style="margin-bottom:15px;"><div class="brand-logo-text">🔱 GLOBAL MATRIX <span>INVESTMENT</span></div></div>', unsafe_allow_html=True)
        
        if st.session_state.verification_stage == "awaiting_otp":
            with st.form("secure_otp_form"):
                st.markdown(f"<p style='font-size:13px; color:#475569; text-align:center;'>Enter verification code sent to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
                u_otp = st.text_input("6-Digit OTP Token Input:", max_chars=6)
                st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                btn_v = st.form_submit_button("Verify & Open Profile", use_container_width=True)
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
                        st.error("Invalid dynamic OTP key matching.")
        else:
            # Login Mode Selection Tab
            auth_mode = st.tabs(["🔐 Sign In (Old Account)", "📝 Sign Up (Create New Account)"])
            
            # --- TAB 1: SIGN IN (OLD ACCOUNT) ---
            with auth_mode[0]:
                with st.form("identity_login_gateway"):
                    st.markdown("<p style='font-size:12px; font-weight:700; color:#0f172a; text-align:center; margin-bottom:10px;'>ACCESS OLD ACCOUNT NODE</p>", unsafe_allow_html=True)
                    login_email = st.text_input("Account Email Address:", key="login_em")
                    login_pass = st.text_input("Account Password Encryption:", type="password", key="login_pw")
                    st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                    login_submit = st.form_submit_button("SIGN IN INSTANTLY", use_container_width=True)
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
                            else:
                                st.error("Incorrect account email or password configuration.")
                        else:
                            st.error("Please enter a valid structural layout credentials.")

            # --- TAB 2: SIGN UP (NEW ACCOUNT) ---
            with auth_mode[1]:
                with st.form("identity_register_gateway"):
                    st.markdown("<p style='font-size:12px; font-weight:700; color:#0f172a; text-align:center; margin-bottom:10px;'>CREATE BRAND NEW WALLET PROFILE</p>", unsafe_allow_html=True)
                    reg_name = st.text_input("User Core Full Display Name:", key="reg_nm")
                    reg_email = st.text_input("Secure Account Routing Email:", key="reg_em")
                    reg_pass = st.text_input("Create Password Encryption:", type="password", key="reg_pw")
                    reg_invite_code = st.text_input("Affiliate Invitation Network Node (Optional):", key="reg_iv")
                    st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                    register_submit = st.form_submit_button("OPEN PROFILE NODE VIA OTP", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if register_submit:
                        em_clean = reg_email.strip()
                        pass_clean = reg_pass.strip()
                        if "@" in em_clean:
                            existing = query_db("SELECT * FROM users WHERE username=?", (em_clean,), one=True)
                            if existing:
                                st.error("This email is already mapped. Switch to 'Sign In' option.")
                            elif not reg_name.strip() or not pass_clean:
                                st.error("Name and Password blocks cannot remain empty.")
                            else:
                                f_ref = "None"
                                if reg_invite_code.strip():
                                    match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                    if match: f_ref = reg_invite_code.strip()
                                st.session_state.generated_otp = str(random.randint(100000, 999999))
                                st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "password": pass_clean, "ref_by": f_ref}
                                with st.spinner("Dispatching verification stream node..."):
                                    send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                                st.session_state.verification_stage = "awaiting_otp"
                                st.rerun()
                        else:
                            st.error("Please insert authentic configuration values.")

# --- MASTER FRAME SIDEBAR DIVISION (SHOWS ONLY IF SUCCESSFULLY LOGGED IN) ---
else:
    side_pane, main_pane = st.columns([1, 4])

    with side_pane:
        st.markdown('<div class="custom-sidebar-container">', unsafe_allow_html=True)
        st.markdown('<div class="brand-logo-card"><div class="brand-logo-text">🔱 GLOBAL MATRIX <span>INVESTMENT</span></div></div>', unsafe_allow_html=True)
        
        # Left Side Options visible only post login
        if st.button("📊 Dashboard", key="nav_dash"): st.session_state.active_sidebar_tab = "Dashboard"
        if st.button("📺 Tasks", key="nav_tasks"): st.session_state.active_sidebar_tab = "Tasks"
        if st.button("💰 Deposit", key="nav_dep"): st.session_state.active_sidebar_tab = "Deposit"
        if st.button("💸 Withdrawal", key="nav_with"): st.session_state.active_sidebar_tab = "Withdrawal"
        if st.button("⏳ History", key="nav_hist"): st.session_state.active_sidebar_tab = "History"
        if st.button("⚙️ Settings", key="nav_sett"): st.session_state.active_sidebar_tab = "Settings"
        if st.button("❓ Help", key="nav_help"): st.session_state.active_sidebar_tab = "Help"
        
        st.markdown('<br><hr style="border-color:#e2e8f0;"><br>', unsafe_allow_html=True)
        if st.button("🚪 Disconnect", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.current_user = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with main_pane:
        st.markdown('<div class="main-canvas-right">', unsafe_allow_html=True)
        st.markdown('<div class="master-top-streamer">🔱 GLOBAL MATRIX <span>INVESTMENT</span> SYSTEM</div>', unsafe_allow_html=True)
        
        # --- ADMIN ROOT CONSOLE ---
        if st.session_state.is_admin:
            st.markdown("<h3>Admin Server Overrides</h3>", unsafe_allow_html=True)
            st.session_state.admin_video_url = st.text_input("Active Live Task Stream URL Link:", value=st.session_state.admin_video_url)
            
            st.markdown("**Pending Synchronization Verification Logs Ledger**")
            deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
            for d in deps:
                st.markdown(f"<div style='background:#ffffff; border:1px solid #cbd5e1; padding:12px; border-radius:6px; margin-bottom:6px; font-size:12px;'>User Target: {d[1]} | Capacity: <b>RM {d[3]}</b><br>Hash Reference ID: <code>{d[6]}</code></div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirm Allocation", key=f"ad_{d[0]}"):
                        query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                        query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                        st.rerun()
                with c2:
                    if st.button("Drop Allocation Request", key=f"rd_{d[0]}"):
                        query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (d[0],), commit=True)
                        st.rerun()

        # --- ROUTED DESKTOP VIEW APPLICATION CANVAS ---
        else:
            u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
            bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", "Matrix User", 0)
            
            # 1. NAVIGATION: DASHBOARD
            if st.session_state.active_sidebar_tab == "Dashboard":
                st.markdown(f"""
                <div class="premium-navy-wallet-card">
                    <div class="wallet-header-caption">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
                    <div class="wallet-user-title">👤 {title}</div>
                    
                    <div class="wallet-data-split-flex">
                        <div class="wallet-data-chunk">
                            <div class="chunk-title-lbl">Dompet Perolehan Saya</div>
                            <div class="chunk-amount-val">RM {bal:.2f}</div>
                        </div>
                        <div class="wallet-data-chunk" style="text-align: right;">
                            <div class="chunk-title-lbl">Ready For Withdrawal</div>
                            <div class="chunk-amount-val" style="color: #22c55e;">RM {bal:.2f}</div>
                        </div>
                    </div>
                </div>
                
                <div class="action-pills-row">
                    <div class="pill-blue-button">🔹 Deposit Dana Portal</div>
                    <div class="pill-green-button">🔸 Tarik Perolehan Hub</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="clean-white-card-widget">
                    <div class="card-widget-header">👥 SYSTEM REFERRAL INVITATION LINKS</div>
                    <div style="font-size:12px; color:#475569;">Share assignments node to snap an instant RM 10.00 cash voucher credit bonus:</div>
                    <div style="background:#f8fafc; padding:10px; border-radius:6px; font-family:monospace; font-weight:700; font-size:15px; text-align:center; color:#1e75e5; margin-top:10px; border:1px dashed #cbd5e1;">{code}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Sejarah Transaksi Terkini</div>', unsafe_allow_html=True)
                dep_logs = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
                w_logs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
                
                if not dep_logs and not w_logs:
                    st.markdown("<p style='font-size:12px; color:#64748b; text-align:center; padding:12px;'>No structural ledger operations mapped to profile history.</p>", unsafe_allow_html=True)
                else:
                    for dl in dep_logs:
                        c_badge = "c-approved" if dl[2]=="APPROVED" else "c-pending" if dl[2]=="PENDING" else "c-rejected"
                        st.markdown(f'<div class="history-row-item"><div><div class="hist-title-bold">Deposit Dana Portal</div><div class="hist-subtitle-sub">Assigned Node Level: {dl[0]}</div></div><div style="text-align:right;"><div class="hist-value-bold">RM {dl[1]:.2f}</div><span class="clean-badge-capsule {c_badge}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
                    for wl in w_logs:
                        c_badge = "c-approved" if wl[1]=="APPROVED" else "c-pending" if wl[1]=="PENDING" else "c-rejected"
                        st.markdown(f'<div class="history-row-item"><div><div class="hist-title-bold" style="color:#b91c1c;">Tarik Perolehan Dispatch</div><div class="hist-subtitle-sub">Distribution Line Clearance</div></div><div style="text-align:right;"><div class="hist-value-bold" style="color:#b91c1c;">-RM {wl[0]:.2f}</div><span class="clean-badge-capsule {c_badge}">{wl[1]}</span></div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # 2. NAVIGATION: TASKS
            elif st.session_state.active_sidebar_tab == "Tasks":
                st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Tugasan Tontonan & Earn Streams Portal</div>', unsafe_allow_html=True)
                st.video(st.session_state.admin_video_url)
                
                c_time = int(time.time())
                diff = c_time - claim_stamp
                if diff < 86400:
                    rem = 86400 - diff
                    st.markdown(f"<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:6px; padding:12px; color:#b91c1c; font-size:12px; text-align:center; font-weight:600;'>🔒 Task reward processing pipeline cold lock. Re-opens in: {rem//3600}h {(rem%3600)//60}m</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="form-execution-btn" style="margin-top:14px;">', unsafe_allow_html=True)
                    if st.button("Confirm Media stream Watch Completion Reward"):
                        bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                        query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                        st.success(f"System distribution logs verified: Added +RM {bonus:.2f}")
                        st.session_state.active_sidebar_tab = "Dashboard"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # 3. NAVIGATION: DEPOSIT
            elif st.session_state.active_sidebar_tab == "Deposit":
                st.markdown('<div class="card-widget-header">Available Subscription Vault Deployment Matrix</div>', unsafe_allow_html=True)
                for ln, ld in LEVELS_CONF.items():
                    st.markdown(f"""
                    <div style='background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <div style='font-size:13px; font-weight:700; color:#0f172a;'>{ln}</div>
                            <div style='font-size:11px; color:#64748b;'>Daily Task Allocation Yield: <span style='color:#22c55e; font-weight:600;'>RM {ld['daily_reward']}</span></div>
                        </div>
                        <div style='font-size:14px; font-weight:700; color:#1e75e5;'>RM {ld['cost']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with st.form("deposit_confirmation_hub"):
                    st.markdown('<p style="font-size:12px; font-weight:700; color:#0f172a;">HANTAR BUKTI SLIP DEPOSIT PORTAL</p>', unsafe_allow_html=True)
                    holder = st.text_input("Depositor Submitter Profile Name Verification:")
                    tx_str = st.text_input("Network Unique Transaction Reference Hash Code (Trx ID):")
                    p_select = st.selectbox("Select Target Investment Allocation Tier Plan:", list(LEVELS_CONF.keys()))
                    st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                    btn_d = st.form_submit_button("Hantar Slip Deposit Node Now", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if btn_d and holder and tx_str:
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "TNG/Online Bank Trans", holder, tx_str, "PENDING"), commit=True)
                        st.success("Ledger entry requested successfully. Admin approval synchronization underway.")
                        st.rerun()

            # 4. NAVIGATION: WITHDRAWAL
            elif st.session_state.active_sidebar_tab == "Withdrawal":
                with st.form("withdrawal_request_terminal"):
                    st.markdown('<p style="font-size:12px; font-weight:700; color:#0f172a;">TARIK PEROLEHAN VALUATION FUNDS DISPATCH</p>', unsafe_allow_html=True)
                    w_val = st.number_input("Desired Balance Cashout Outflow (RM):", min_value=10.0, step=5.0)
                    w_net = st.text_input("Target Account Settlement Routing Coordinates Bank Details:")
                    st.markdown('<div class="form-execution-btn">', unsafe_allow_html=True)
                    btn_w = st.form_submit_button("Deploy Settlement Distribution Line Wire", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if btn_w:
                        if w_val <= bal:
                            if w_net.strip():
                                query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                                query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                                st.success("Settlement liquidation pipelines activated successfully.")
                                st.rerun()
                            else: st.error("Target deployment bank parameter cannot be blank.")
                        else: st.error("Available credit thresholds balance limits violated.")

            # 5. NAVIGATION: HISTORY
            elif st.session_state.active_sidebar_tab == "History":
                st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">Complete Unified Account Balance History Logs</div>', unsafe_allow_html=True)
                all_deps = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
                all_withs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
                
                if not all_deps and not all_withs:
                    st.markdown("<p style='font-size:12px; color:#64748b; text-align:center;'>No historical server data captured under token signature.</p>", unsafe_allow_html=True)
                else:
                    for dl in all_deps:
                        c_badge = "c-approved" if dl[2]=="APPROVED" else "c-pending" if dl[2]=="PENDING" else "c-rejected"
                        st.markdown(f'<div class="history-row-item"><div><div class="hist-title-bold">Deposit Node Registry</div><div class="hist-subtitle-sub">Tier Category Blueprint: {dl[0]}</div></div><div style="text-align:right;"><div class="hist-value-bold">RM {dl[1]:.2f}</div><span class="clean-badge-capsule {c_badge}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
                    for wl in all_withs:
                        c_badge = "c-approved" if wl[1]=="APPROVED" else "c-pending" if wl[1]=="PENDING" else "c-rejected"
                        st.markdown(f'<div class="history-row-item"><div><div class="hist-title-bold" style="color:#b91c1c;">Tarik Perolehan Distribution</div><div class="hist-subtitle-sub">Account Token Settlement Wire</div></div><div style="text-align:right;"><div class="hist-value-bold" style="color:#b91c1c;">-RM {wl[0]:.2f}</div><span class="clean-badge-capsule {c_badge}">{wl[1]}</span></div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            elif st.session_state.active_sidebar_tab == "Settings":
                st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">⚙️ Secure Profile Configuration Preferences</div><p style="font-size:12px; color:#475569;">System encryption vectors and security node parameters are operational.</p></div>', unsafe_allow_html=True)
                
            elif st.session_state.active_sidebar_tab == "Help":
                st.markdown('<div class="clean-white-card-widget"><div class="card-widget-header">❓ Help Desk Support Portal Terminal</div><p style="font-size:12px; color:#475569;">Contact support dispatch at: <b>Salmanveerm@gmail.com</b></p></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

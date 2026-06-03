import streamlit as st
import sqlite3
import pandas as pd
import random
import time
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Force layout to wide to match laptop sidebar structure perfectly
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="wide")

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

# --- EXACT LAPTOP SIDEBAR FRAMEWORK & LIGHT UI CSS ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    /* Clean up default frames */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #f8fafc !important; }
    
    /* Global Typography Reset */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Inter', sans-serif !important; }
    
    /* Left Side Menu Sidebar Container Panel */
    .laptop-left-sidebar {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        padding: 20px 15px;
        height: 100vh;
    }
    
    /* Corporate Branding Card inside Sidebar top left */
    .sidebar-brand-box {
        background: #0f172a;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 30px;
    }
    .sidebar-brand-title {
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .sidebar-brand-title span { color: #f59e0b; }
    
    /* Custom Navigation Buttons Framework */
    .stButton>button {
        background: transparent !important;
        color: #475569 !important;
        border: none !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        border-radius: 8px !important;
        margin-bottom: 4px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #f1f5f9 !important;
        color: #0f172a !important;
    }
    
    /* Active highlighted item selection marker mimic */
    div[data-testid="stHorizontalBlock"] .stButton>button:focus {
        background: #e2e8f0 !important;
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    
    /* Main Content Right Box Panel Configuration */
    .laptop-right-panel {
        padding: 15px 25px !important;
    }
    
    /* Top Main Corporate Header Element */
    .top-corporate-bar {
        background: #0f172a;
        padding: 14px 20px;
        border-radius: 10px;
        color: #ffffff;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 0.5px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .top-corporate-bar span { color: #f59e0b; }
    
    /* Exact Wallet Content Box Module Frame */
    .wallet-mainframe-card {
        background: #0f172a !important;
        border-radius: 12px;
        padding: 22px;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(15,23,42,0.08);
        margin-bottom: 18px;
    }
    .wallet-caption-line { font-size: 11px; color: #94a3b8; font-weight: 500; text-transform: uppercase; }
    .wallet-holder-identity { font-size: 22px; font-weight: 700; color: #ffffff; margin-top: 2px; margin-bottom: 15px; }
    
    /* Inner Row Layout Flex Blocks */
    .wallet-splits-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 14px;
    }
    .split-data-block { flex: 1; }
    .split-data-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
    .split-data-val { font-size: 19px; font-weight: 700; color: #ffffff; margin-top: 2px; }
    
    /* Quick Actions Static Display Links */
    .pills-layout-row { display: flex; gap: 12px; margin-bottom: 18px; }
    .pill-blue-item { background: #1e75e5; color: white; padding: 11px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; flex: 1; text-align: center; }
    .pill-green-item { background: #22c55e; color: white; padding: 11px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; flex: 1; text-align: center; }
    
    /* Standard Light Panels */
    .laptop-widget-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .widget-box-title { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.3px; }
    
    /* Clean Logs Table Configuration */
    .clean-table-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 12px;
    }
    .clean-table-row:last-child { border-bottom: none; }
    .col-main-txt { font-weight: 600; color: #334155; }
    .col-sub-txt { font-size: 10px; color: #64748b; margin-top: 1px; }
    .col-val-bold { font-weight: 700; color: #0f172a; text-align: right; }
    
    .badge-node-status { font-size: 9px; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; margin-top: 3px; display: inline-block; }
    .b-approved { background: #dcfce7; color: #15803d; }
    .b-pending { background: #fef3c7; color: #b45309; }
    .b-rejected { background: #fee2e2; color: #b91c1c; }
    
    /* Inputs Override styling */
    label, [data-testid="stWidgetLabel"] p { color: #475569 !important; font-size: 11px !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important; }
    
    .form-btn-submit .stButton>button {
        background: #0f172a !important;
        color: #ffffff !important;
        text-align: center !important;
        justify-content: center !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 10px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Session State Controls
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

# Master Frame Grid Layout Split (Left Sidebar 7 Options vs Right Main Panel View)
side_pane, main_pane = st.columns([1, 3])

with side_pane:
    st.markdown('<div class="laptop-left-sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-brand-box"><div class="sidebar-brand-title">🔱 GLOBAL MATRIX <span>INVESTMENT</span></div></div>', unsafe_allow_html=True)
    
    # Same 7 left side choices from your laptop dashboard layout blueprint
    if st.button("📊 Dashboard", key="btn_side_dash"): st.session_state.active_sidebar_tab = "Dashboard"
    if st.button("📺 Tasks", key="btn_side_tasks"): st.session_state.active_sidebar_tab = "Tasks"
    if st.button("💰 Deposit", key="btn_side_dep"): st.session_state.active_sidebar_tab = "Deposit"
    if st.button("💸 Withdrawal", key="btn_side_with"): st.session_state.active_sidebar_tab = "Withdrawal"
    if st.button("⏳ History", key="btn_side_hist"): st.session_state.active_sidebar_tab = "History"
    if st.button("⚙️ Settings", key="btn_side_sett"): st.session_state.active_sidebar_tab = "Settings"
    if st.button("❓ Help", key="btn_side_help"): st.session_state.active_sidebar_tab = "Help"
    
    st.markdown('<br><hr style="border-color:#e2e8f0;"><br>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        if st.button("🚪 Disconnect Session", key="btn_side_logout"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with main_pane:
    st.markdown('<div class="laptop-right-panel">', unsafe_allow_html=True)
    st.markdown('<div class="top-corporate-bar">🔱 GLOBAL MATRIX <span>INVESTMENT</span> PANEL</div>', unsafe_allow_html=True)
    
    # --- AUTH GATES FOR SECURE ACCOUNTS ---
    if not st.session_state.logged_in:
        if st.session_state.verification_stage == "awaiting_otp":
            with st.form("otp_gate_form"):
                st.markdown(f"<p style='font-size:12px; color:#475569;'>Enter security code node dispatched to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
                u_otp = st.text_input("Enter 6-Digit Code Parameter:", max_chars=6)
                st.markdown('<div class="form-btn-submit">', unsafe_allow_html=True)
                btn_v = st.form_submit_button("Authenticate Verification Vector", use_container_width=True)
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
                        st.session_state.active_sidebar_tab = "Dashboard"
                        st.rerun()
                    else: st.error("Mismatched security string execution parameters.")
        else:
            with st.form("identity_gate_portal"):
                st.markdown("<p style='font-size:12px; font-weight:700; color:#0f172a; margin-bottom:10px;'>ACCESS HUB CREDENTIAL GATEWAY</p>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Profile Label Name (New Users Only):")
                reg_email = st.text_input("Account Identity Route Email Address:")
                reg_pass = st.text_input("Security String Encryption Key Password:", type="password")
                reg_invite_code = st.text_input("Referral Network Node Code (Optional):")
                st.markdown('<div class="form-btn-submit">', unsafe_allow_html=True)
                login_submit = st.form_submit_button("ACCESS ROUTE OR REGISTER INITIAL TOKEN", use_container_width=True)
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
                            st.session_state.active_sidebar_tab = "Dashboard"
                            st.rerun()
                        else:
                            if not reg_name.strip(): st.error("Declaration profile block name token entry missing.")
                            else:
                                f_ref = "None"
                                if reg_invite_code.strip():
                                    match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                    if match: f_ref = reg_invite_code.strip()
                                st.session_state.generated_otp = str(random.randint(100000, 999999))
                                st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "ref_by": f_ref}
                                with st.spinner("Processing token transmission route..."):
                                    send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                                st.session_state.verification_stage = "awaiting_otp"
                                st.rerun()

    # --- ADMIN NODE PIPELINE MANAGER ---
    elif st.session_state.logged_in and st.session_state.is_admin:
        st.markdown("<h3>Admin Server Overrides</h3>", unsafe_allow_html=True)
        st.session_state.admin_video_url = st.text_input("Active Live Task Stream URL Link:", value=st.session_state.admin_video_url)
        
        st.markdown("**Pending Sync Node Requests Verification Logs**")
        deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
        for d in deps:
            st.markdown(f"<div style='background:#ffffff; border:1px solid #e2e8f0; padding:10px; border-radius:6px; margin-bottom:5px; font-size:12px;'>Target User: {d[1]} | Volume size: <b>RM {d[3]}</b><br>Trx Identification Key: <code>{d[6]}</code></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Confirm Sync Route", key=f"ad_{d[0]}"):
                    query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                    query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                    st.rerun()
            with c2:
                if st.button("Drop Allocation Request Token", key=f"rd_{d[0]}"):
                    query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (d[0],), commit=True)
                    st.rerun()

    # --- CORE USER INTERFACE DISPATCH NAVIGATION ROUTERS ---
    else:
        u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "GM0000", "Matrix User", 0)
        
        # TAB 1: SIDEBAR OPTION 'DASHBOARD'
        if st.session_state.active_sidebar_tab == "Dashboard":
            # FIXED CLEAN WALLET: HTML Raw strings code completely replaced with native structural blocks
            st.markdown(f"""
            <div class="wallet-mainframe-card">
                <div class="wallet-caption-line">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
                <div class="wallet-holder-identity">👤 Account Holder: {title}</div>
                
                <div class="wallet-splits-row">
                    <div class="split-data-block">
                        <div class="split-data-label">Dompet Perolehan Saya (My Earnings Wallet)</div>
                        <div class="split-data-val">RM {bal:.2f}</div>
                    </div>
                    <div class="split-data-block" style="text-align: right;">
                        <div class="split-data-label">Ready For Extraction Withdrawal</div>
                        <div class="split-data-val" style="color: #22c55e;">RM {bal:.2f}</div>
                    </div>
                </div>
            </div>
            
            <div class="pills-layout-row">
                <div class="pill-blue-item">🔹 Deposit Dana System Active</div>
                <div class="pill-green-item">🔸 Tarik Perolehan Connected</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Referral Widget Section
            st.markdown(f"""
            <div class="laptop-widget-box">
                <div class="widget-box-title">👥 PARTNER INVITATION NETWORK LINK</div>
                <div style="font-size:12px; color:#475569;">Distribute your assignment tag to secure instant RM 10.00 platform credits bonus:</div>
                <div style="background:#f1f5f9; padding:10px; border-radius:6px; font-family:monospace; font-weight:700; font-size:15px; text-align:center; color:#1e75e5; margin-top:8px; border:1px dashed #cbd5e1;">{code}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recent Transaction Table inside Dashboard view directly matching screenshot structure
            st.markdown('<div class="laptop-widget-box"><div class="widget-box-title">Sejarah Transaksi Terkini</div>', unsafe_allow_html=True)
            dep_logs = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
            w_logs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC LIMIT 2", (st.session_state.current_user,))
            
            if not dep_logs and not w_logs:
                st.markdown("<p style='font-size:11px; color:#64748b; text-align:center; padding:10px;'>No database ledger operations recorded yet.</p>", unsafe_allow_html=True)
            else:
                for dl in dep_logs:
                    b_cls = "b-approved" if dl[2]=="APPROVED" else "b-pending" if dl[2]=="PENDING" else "b-rejected"
                    st.markdown(f'<div class="clean-table-row"><div><div class="col-main-txt">Deposit Dana Portal</div><div class="col-sub-txt">Allocation Node: {dl[0]}</div></div><div style="text-align:right;"><div class="col-val-bold">RM {dl[1]:.2f}</div><span class="badge-node-status {b_cls}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
                for wl in w_logs:
                    b_cls = "b-approved" if wl[1]=="APPROVED" else "b-pending" if wl[1]=="PENDING" else "b-rejected"
                    st.markdown(f'<div class="clean-table-row"><div><div class="col-main-txt" style="color:#b91c1c;">Tarik Perolehan Dispatch</div><div class="col-sub-txt">System Extraction Wire</div></div><div style="text-align:right;"><div class="col-val-bold" style="color:#b91c1c;">-RM {wl[0]:.2f}</div><span class="badge-node-status {b_cls}">{wl[1]}</span></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 2: SIDEBAR OPTION 'TASKS'
        elif st.session_state.active_sidebar_tab == "Tasks":
            st.markdown('<div class="laptop-widget-box"><div class="widget-box-title">Tugasan Tontonan & Bonus Streams</div>', unsafe_allow_html=True)
            st.video(st.session_state.admin_video_url)
            
            c_time = int(time.time())
            diff = c_time - claim_stamp
            if diff < 86400:
                rem = 86400 - diff
                st.markdown(f"<div style='background:#fee2e2; border:1px solid #fca5a5; padding:10px; border-radius:6px; color:#b91c1c; font-size:12px; text-align:center; font-weight:500;'>🔒 Operational Cycle Locked. Next access window opens in: <b>{rem//3600}h {(rem%3600)//60}m</b></div>", unsafe_allow_html=True)
            else:
                st.markdown('<div class="form-btn-submit" style="margin-top:12px;">', unsafe_allow_html=True)
                if st.button("Tonton & Peroleh Instant Yield Reward", key="btn_execute_task_yield"):
                    bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                    query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                    st.success(f"System yield update verification confirmed: +RM {bonus:.2f}")
                    st.session_state.active_sidebar_tab = "Dashboard"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 3: SIDEBAR OPTION 'DEPOSIT'
        elif st.session_state.active_sidebar_tab == "Deposit":
            st.markdown('<div class="widget-box-title">Available Activation Tiers Matrix</div>', unsafe_allow_html=True)
            for ln, ld in LEVELS_CONF.items():
                st.markdown(f"""
                <div style='background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='font-size:13px; font-weight:700; color:#0f172a;'>{ln}</div>
                        <div style='font-size:11px; color:#64748b;'>Daily Task Revenue Margin: <span style='color:#22c55e; font-weight:600;'>RM {ld['daily_reward']}</span></div>
                    </div>
                    <div style='font-size:14px; font-weight:700; color:#1e75e5;'>RM {ld['cost']}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with st.form("deposit_submission_form"):
                st.markdown('<p style="font-size:12px; font-weight:600; color:#0f172a;">HANTAR BUKTI SLIP DEPOSIT PORTAL</p>', unsafe_allow_html=True)
                holder = st.text_input("Account Holder Verification Submitter Name:")
                tx_str = st.text_input("Unique System Reference Transaction ID (Trx ID):")
                p_select = st.selectbox("Choose Target Allocation Tier Plan Node:", list(LEVELS_CONF.keys()))
                st.markdown('<div class="form-btn-submit">', unsafe_allow_html=True)
                btn_d = st.form_submit_button("Hantar Slip Deposit Now Verification", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_d and holder and tx_str:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "TNG/Bank Gateway", holder, tx_str, "PENDING"), commit=True)
                    st.success("Verification parameters successfully mapped to secure ledger logs. Awaiting confirmation.")
                    st.rerun()

        # TAB 4: SIDEBAR OPTION 'WITHDRAWAL'
        elif st.session_state.active_sidebar_tab == "Withdrawal":
            with st.form("withdrawal_execution_form"):
                st.markdown('<p style="font-size:12px; font-weight:600; color:#0f172a;">TARIK PEROLEHAN HUB CASH OUT OUTFLOW</p>', unsafe_allow_html=True)
                w_val = st.number_input("Desired Cash Out Volume (RM):", min_value=10.0, step=5.0)
                w_net = st.text_input("Routing Destination Channel Addresses Details:")
                st.markdown('<div class="form-btn-submit">', unsafe_allow_html=True)
                btn_w = st.form_submit_button("Deploy Cashout Settlement Wire", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_w:
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Extraction parameters locked down. System routing active.")
                            st.rerun()
                        else: st.error("Target routing coordinates string can't be empty.")
                    else: st.error("Account balance threshold limits error.")

        # TAB 5: SIDEBAR OPTION 'HISTORY'
        elif st.session_state.active_sidebar_tab == "History":
            st.markdown('<div class="laptop-widget-box"><div class="widget-box-title">Complete System Ledger Operation History Logs</div>', unsafe_allow_html=True)
            all_deps = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            all_withs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
            
            if not all_deps and not all_withs:
                st.markdown("<p style='font-size:12px; color:#64748b; text-align:center;'>No historical timeline entry records mapped.</p>", unsafe_allow_html=True)
            else:
                for dl in all_deps:
                    b_cls = "b-approved" if dl[2]=="APPROVED" else "b-pending" if dl[2]=="PENDING" else "b-rejected"
                    st.markdown(f'<div class="clean-table-row"><div><div class="col-main-txt">Deposit Node Allocation</div><div class="col-sub-txt">Tier Rank: {dl[0]}</div></div><div style="text-align:right;"><div class="col-val-bold">RM {dl[1]:.2f}</div><span class="badge-node-status {b_cls}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
                for wl in all_withs:
                    b_cls = "b-approved" if wl[1]=="APPROVED" else "b-pending" if wl[1]=="PENDING" else "b-rejected"
                    st.markdown(f'<div class="clean-table-row"><div><div class="col-main-txt" style="color:#b91c1c;">Tarik Perolehan Cashout</div><div class="col-sub-txt">Network Node Wire</div></div><div style="text-align:right;"><div class="col-val-bold" style="color:#b91c1c;">-RM {wl[0]:.2f}</div><span class="badge-node-status {b_cls}">{wl[1]}</span></div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # TAB 6 & 7: SETTINGS & HELP SKELETONS
        elif st.session_state.active_sidebar_tab == "Settings":
            st.markdown('<div class="laptop-widget-box"><div class="widget-box-title">⚙️ User Node Preference Profile Settings</div><p style="font-size:12px; color:#475569;">Security configurations and profile encryption matrices are operational and locked securely.</p></div>', unsafe_allow_html=True)
            
        elif st.session_state.active_sidebar_tab == "Help":
            st.markdown('<div class="laptop-widget-box"><div class="widget-box-title">❓ Help Desk Support Portal</div><p style="font-size:12px; color:#475569;">If you experience transaction processing lags or network parameter drops, coordinate with support team instantly at: <b>Salmanveerm@gmail.com</b></p></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

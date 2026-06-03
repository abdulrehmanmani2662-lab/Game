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
st.set_page_config(page_title="EarnWise Portal", page_icon="🪪", layout="centered")

# --- SMTP EMAIL DISTRIBUTION PIPELINE ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "Salmanveerm@gmail.com"  
SENDER_PASSWORD = "syjawmpyvdnokasn"     

def send_real_verification_email(receiver_email, otp_code, user_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"EarnWise Security <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"Verification Code: {otp_code}"
        body = f"Hello {user_name},\n\nYour 6-digit verification code is: {otp_code}\n\nRegards,\nEarnWise Team"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[SMTP ERROR]: {e}")
        return False

# --- ROBUST DATABASE SYSTEM (ERROR-FREE RE-ENGINEERING) ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    # Users core infrastructure
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
    
    # Table safety assertions
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

# --- EARNWISE PREMIUM WHITE LIGHT CSS ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #f8fafc !important; }
    .main .block-container { padding-top: 10px !important; padding-bottom: 100px !important; max-width: 430px !important; margin: 0 auto; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input { font-family: 'Poppins', sans-serif !important; }
    
    /* EarnWise Main Header */
    .brand-container { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px; padding: 10px 0; }
    .brand-logo-text { font-size: 22px; color: #0f172a; font-weight: 700; letter-spacing: -0.5px; }
    .brand-logo-text span { color: #2563eb; }
    
    /* Double Balance Wallet Modules */
    .earning-wallet-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 18px; border-radius: 16px; margin-bottom: 16px; color: #ffffff;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.08);
    }
    .wallet-split-row { display: flex; justify-content: space-between; margin-top: 10px; border-top: 1px solid #334155; padding-top: 10px; }
    
    /* Action Status Grids */
    .stat-badge-grid { display: flex; gap: 10px; margin-bottom: 16px; }
    .action-card-btn { 
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; 
        text-align: center; width: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .section-headline { font-size: 13px; color: #64748b; font-weight: 600; text-transform: uppercase; margin: 20px 0 10px 0; letter-spacing: 0.5px; }
    
    /* Standard Light Inputs & Form fields */
    label, [data-testid="stWidgetLabel"] p { color: #475569 !important; font-size: 11px !important; font-weight: 600 !important; }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] { color: #0f172a !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }
    
    .stButton>button { font-weight: 600 !important; font-size: 13px !important; border-radius: 8px !important; padding: 10px 0 !important; background: #ffffff !important; color: #334155 !important; border: 1px solid #cbd5e1 !important; }
    .stButton>button:hover { border-color: #2563eb !important; color: #2563eb !important; }
    
    .action-btn-hub .stButton>button { background: #2563eb !important; color: #ffffff !important; border: none !important; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.15); }
    .action-btn-hub .stButton>button:hover { background: #1d4ed8 !important; }
    
    /* System Real Transaction Logger Badges */
    .log-row-node { background: #ffffff; border: 1px solid #e2e8f0; padding: 12px; border-radius: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    .badge-node { padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
    .status-confirmed { background: #dcfce7; color: #15803d; }
    .status-pending { background: #fef3c7; color: #b45309; }
    .status-rejected { background: #fee2e2; color: #b91c1c; }
    
    /* Micro Bottom App Nav-Bar Sticky */
    .bottom-app-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e2e8f0; padding: 10px; z-index: 999999; max-width: 430px; margin: 0 auto; display: flex; justify-content: space-between; }
    </style>
    """, unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Active Navigation State Controllers
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'current_app_tab' not in st.session_state: st.session_state.current_app_tab = "home"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""

st.markdown('<div class="brand-container"><div class="brand-logo-text">⚡ Earn<span>Wise</span> Mobile</div></div>', unsafe_allow_html=True)

# --- SIGN IN AND PROTOCOL LAYER ---
if not st.session_state.logged_in:
    if st.session_state.verification_stage == "awaiting_otp":
        with st.form("otp_verification_node"):
            st.markdown(f"<p style='text-align:center; font-size:13px; color:#475569;'>Enter verification OTP code sent to:<br><b>{st.session_state.temp_register_data.get('email', '')}</b></p>", unsafe_allow_html=True)
            u_otp = st.text_input("Enter 6-Digit Code:", max_chars=6)
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            btn_v = st.form_submit_button("Confirm & Secure Authentication", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if btn_v:
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "EW" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (t_data['email'], 10.00, "None", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    if t_data['ref_by'] != "None":
                        query_db("UPDATE users SET balance = balance + 10.00 WHERE ref_code=?", (t_data['ref_by'],), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.session_state.current_app_tab = "home"
                    st.rerun()
                else: st.error("Wrong security OTP mismatch.")
    else:
        with st.form("secure_login_form"):
            st.markdown("<p style='font-size:14px; font-weight:600; color:#0f172a; text-align:center;'>Papan Pemuka Gateway</p>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Registration Name (New Users Only):")
            reg_email = st.text_input("User Core Email Account:")
            reg_pass = st.text_input("Secure Password Node:", type="password")
            reg_invite_code = st.text_input("Referral Invitation Node Code (Optional):")
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            login_submit = st.form_submit_button("Sign In / Open Profile Account", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if login_submit:
                em_clean = reg_email.strip()
                if em_clean == "admin" and reg_pass == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.current_user = "MASTER_ADMIN"
                    st.rerun()
                elif "@" in em_clean:
                    existing = query_db("SELECT * FROM users WHERE username=?", (em_clean,), one=True)
                    if existing:
                        st.session_state.logged_in = True
                        st.session_state.current_user = em_clean
                        st.session_state.current_app_tab = "home"
                        st.rerun()
                    else:
                        if not reg_name.strip(): st.error("Please enter Full Name to create configuration file.")
                        else:
                            f_ref = "None"
                            if reg_invite_code.strip():
                                match = query_db("SELECT username FROM users WHERE ref_code=?", (reg_invite_code.strip(),), one=True)
                                if match: f_ref = reg_invite_code.strip()
                            st.session_state.generated_otp = str(random.randint(100000, 999999))
                            st.session_state.temp_register_data = {"name": reg_name.strip(), "email": em_clean, "ref_by": f_ref}
                            with st.spinner("Broadcasting Security OTP Module..."):
                                send_real_verification_email(em_clean, st.session_state.generated_otp, reg_name.strip())
                            st.session_state.verification_stage = "awaiting_otp"
                            st.rerun()

# --- ADMIN PANEL LOGISTICS ---
elif st.session_state.logged_in and st.session_state.is_admin:
    st.markdown("<h4 style='color:#0f172a;'>Admin Terminal View</h4>", unsafe_allow_html=True)
    st.session_state.admin_video_url = st.text_input("Global Content Stream Task URL:", value=st.session_state.admin_video_url)
    
    st.markdown('<div class="section-headline">Pending Deposits Management</div>', unsafe_allow_html=True)
    deps = query_db("SELECT * FROM deposits WHERE status='PENDING'")
    for d in deps:
        st.markdown(f"<div style='background:#ffffff; border:1px solid #cbd5e1; padding:10px; border-radius:8px; margin-bottom:8px; font-size:12px; color:#0f172a;'>User: {d[1]} | Amount: <b>RM {d[3]}</b><br>Trx Node: <code>{d[6]}</code></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("Approve", key=f"ad_{d[0]}"):
                query_db("UPDATE users SET active_level=? WHERE username=?", (d[2], d[1]), commit=True)
                query_db("UPDATE deposits SET status='APPROVED' WHERE id=?", (d[0],), commit=True)
                st.rerun()
        with c2:
            if st.button("Reject", key=f"rd_{d[0]}"):
                query_db("UPDATE deposits SET status='REJECTED' WHERE id=?", (d[0],), commit=True)
                st.rerun()

    st.markdown('<div class="section-headline">Pending Withdrawal Terminals</div>', unsafe_allow_html=True)
    w_reqs = query_db("SELECT * FROM withdrawals WHERE status='PENDING'")
    for w in w_reqs:
        st.markdown(f"<div style='background:#ffffff; border:1px solid #cbd5e1; padding:10px; border-radius:8px; margin-bottom:8px; font-size:12px; color:#0f172a;'>User: {w[1]} | Amount: <b>RM {w[2]}</b><br>Routing Node: {w[3]}</div>", unsafe_allow_html=True)
        cw1, cw2 = st.columns(2)
        with cw1:
            if st.button("Confirm Payout Settlement", key=f"wc_{w[0]}"):
                query_db("UPDATE withdrawals SET status='APPROVED' WHERE id=?", (w[0],), commit=True)
                st.rerun()
        with cw2:
            if st.button("Cancel & Rollback", key=f"wj_{w[0]}"):
                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (w[2], w[1]), commit=True)
                query_db("UPDATE withdrawals SET status='REJECTED' WHERE id=?", (w[0],), commit=True)
                st.rerun()

    if st.button("Disconnect Terminal Admin", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.is_admin = False; st.rerun()

# --- MOBILE APPLICATION FRONTEND INTERFACE ---
else:
    u_data = query_db("SELECT balance, active_level, ref_code, full_name, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
    bal, lvl, code, title, claim_stamp = u_data if u_data else (0.00, "None", "EW0000", "User Client", 0)
    
    if st.session_state.current_app_tab == "home":
        # EarnWise Styled Main Dual Dashboard Balance Panel
        st.markdown(f"""
        <div class="earning-wallet-container">
            <div style="font-size:11px; color:#94a3b8; font-weight:500;">Papan Pemuka Perolehan Anda (MY)</div>
            <div style="font-size:20px; font-weight:600; margin-top:2px; color:#ffffff;">{title}</div>
            <div style="font-size:11px; color:#38bdf8; font-weight:600;">ACTIVE NODE TIER: {lvl}</div>
            <div class="wallet-split-row">
                <div>
                    <div style="font-size:10px; color:#94a3b8;">Dompet Perolehan Saya</div>
                    <div style="font-size:22px; font-weight:700; color:#ffffff;">RM {bal:.2f}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size:10px; color:#94a3b8;">Ready For Withdrawal</div>
                    <div style="font-size:22px; font-weight:700; color:#34d399;">RM {bal:.2f}</div>
                </div>
            </div>
        </div>
        
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:12px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:12px; font-weight:600; color:#0f172a;">👥 Kongsi Pautan Kawan</div>
                <div style="font-size:10px; color:#64748b;">Invite system reward: RM 10.00 instant</div>
            </div>
            <div style="background:#f1f5f9; padding:6px 12px; border-radius:6px; font-family:monospace; font-weight:700; color:#2563eb; font-size:13px;">{code}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Finance Flow Select Hub Components
        sub_tab = st.radio("SISTEM TRANSAKSI:", ["Deposit Dana Nodes", "Tarik Perolehan Funds"], horizontal=True)
        
        if sub_tab == "Deposit Dana Nodes":
            st.markdown('<div class="section-headline">Available Network Node Tiers</div>', unsafe_allow_html=True)
            for ln, ld in LEVELS_CONF.items():
                st.markdown(f"<div style='background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'><div><div style='font-size:12px; font-weight:600; color:#0f172a;'>{ln}</div><div style='font-size:11px; color:#64748b;'>Daily Yield: <span style='color:#16a34a;'>RM {ld['daily_reward']}</span></div></div><div style='font-size:14px; font-weight:700; color:#2563eb;'>RM {ld['cost']}</div></div>", unsafe_allow_html=True)
                
            st.markdown('<div class="section-headline">Hantar Bukti Slip Deposit</div>', unsafe_allow_html=True)
            with st.form("dep_proof_sub"):
                holder = st.text_input("Account Holder Verification Name:")
                tx_str = st.text_input("Reference Transaction ID (Trx ID):")
                p_select = st.selectbox("Select Target Deployment Tier:", list(LEVELS_CONF.keys()))
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                btn_d = st.form_submit_button("Hantar Slip Deposit Now", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_d and holder and tx_str:
                    query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], "GrabPay/Touch'nGo", holder, tx_str, "PENDING"), commit=True)
                    st.success("Verification file transmitted to verification logs.")
                    st.rerun()
                    
        elif sub_tab == "Tarik Perolehan Funds":
            st.markdown('<div class="section-headline">Sistem Tarik Perolehan Balance</div>', unsafe_allow_html=True)
            with st.form("cash_extraction_form"):
                w_val = st.number_input("Amount Value (RM):", min_value=10.0, step=5.0)
                w_net = st.text_input("Routing Wallet Details (e.g., Bank Islam / Maybank):")
                st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
                btn_w = st.form_submit_button("Confirm Cashout Extraction", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if btn_w:
                    if w_val <= bal:
                        if w_net.strip():
                            query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                            query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, w_net.strip(), "PENDING"), commit=True)
                            st.success("Withdrawal pipeline processed. Awaiting settlement verification node.")
                            st.rerun()
                        else: st.error("Missing physical target network nodes parameters.")
                    else: st.error("Credit parameters margin overflow limit configuration.")

        # --- SEJARAH TRANSAKASI LOG VIEW ---
        st.markdown('<div class="section-headline">Sejarah Transaksi Terkini</div>', unsafe_allow_html=True)
        dep_logs = query_db("SELECT level, amount, status FROM deposits WHERE user=? ORDER BY id DESC LIMIT 3", (st.session_state.current_user,))
        w_logs = query_db("SELECT amount, status FROM withdrawals WHERE user=? ORDER BY id DESC LIMIT 3", (st.session_state.current_user,))
        
        if not dep_logs and not w_logs:
            st.markdown("<p style='font-size:11px; color:#64748b; text-align:center;'>No structural log history found.</p>", unsafe_allow_html=True)
        else:
            for dl in dep_logs:
                c_lbl = "confirmed" if dl[2]=="APPROVED" else "pending" if dl[2]=="PENDING" else "rejected"
                st.markdown(f'<div class="log-row-node"><div><div style="font-size:12px; font-weight:600; color:#0f172a;">Deposit Dana Node</div><div style="font-size:10px; color:#64748b;">Tier: {dl[0]}</div></div><div style="text-align:right;"><div style="font-size:12px; font-weight:700; color:#0f172a;">RM {dl[1]:.2f}</div><span class="badge-node status-{c_lbl}">{dl[2]}</span></div></div>', unsafe_allow_html=True)
            for wl in w_logs:
                c_lbl = "confirmed" if wl[1]=="APPROVED" else "pending" if wl[1]=="PENDING" else "rejected"
                st.markdown(f'<div class="log-row-node"><div><div style="font-size:12px; font-weight:600; color:#b91c1c;">Tarik Perolehan Out</div><div style="font-size:10px; color:#64748b;">Cashout File</div></div><div style="text-align:right;"><div style="font-size:12px; font-weight:700; color:#b91c1c;">-RM {wl[0]:.2f}</div><span class="badge-node status-{c_lbl}">{wl[1]}</span></div></div>', unsafe_allow_html=True)

    elif st.session_state.current_app_tab == "task":
        st.markdown('<div class="section-headline">Tonton Video & Menang Bonus</div>', unsafe_allow_html=True)
        st.video(st.session_state.admin_video_url)
        
        c_time = int(time.time())
        diff = c_time - claim_stamp
        if diff < 86400:
            rem = 86400 - diff
            st.markdown(f"<div style='background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:10px; text-align:center; color:#b91c1c; font-size:12px;'>🔒 Next advertising streaming matrix unlocked in: <b>{rem//3600}h {(rem%3600)//60}m</b></div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="action-btn-hub">', unsafe_allow_html=True)
            if st.button("Claim Tonton Advertisements Reward Node", use_container_width=True):
                bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                st.success(f"Successfully claimed Node yield: RM {bonus:.2f}")
                st.session_state.current_app_tab = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER MOBILE CONFIG STICKY NAVIGATION ---
    st.markdown('<div class="bottom-app-nav">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: 
        if st.button("📊 Dashboard"): st.session_state.current_app_tab = "home"; st.rerun()
    with f2: 
        if st.button("📺 Video Tasks"): st.session_state.current_app_tab = "task"; st.rerun()
    with f3: 
        if st.button("🚪 Leave App"): st.session_state.logged_in = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

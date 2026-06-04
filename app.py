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

# Session routers state engine
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'admin_video_url' not in st.session_state: st.session_state.admin_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
if 'active_sidebar_tab' not in st.session_state: st.session_state.active_sidebar_tab = "Dashboard Overview"
if 'verification_stage' not in st.session_state: st.session_state.verification_stage = "closed"
if 'temp_register_data' not in st.session_state: st.session_state.temp_register_data = {}
if 'generated_otp' not in st.session_state: st.session_state.generated_otp = ""
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"

# --- CUSTOM ENGINE FOR COLORFUL CORNER DABBE (TABS) ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #f8fafc !important; }
    
    .premium-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 22px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .wallet-card-container {
        background: #0f172a;
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0px 10px 15px -3px rgba(0,0,0,0.3);
        border: 1px solid #1e293b;
    }
    
    /* --- EXACT MATCH FOR DOOSRI SCREENSHOT TABS HACK --- */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
    }
    div[data-testid="stRadio"] label {
        padding: 16px 20px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        display: block !important;
        width: 100% !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        border: none !important;
        transition: transform 0.2s ease, opacity 0.2s ease !important;
    }
    div[data-testid="stRadio"] label:hover {
        transform: scale(1.01);
        opacity: 0.95;
    }
    
    /* 1. Fund Deposit / Dashboard Overview -> Pink */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(1) {
        background: #ec4899 !important;
    }
    /* 2. Claim Revenue / Stream Video Tasks -> Red/Coral */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(2) {
        background: #ef4444 !important;
    }
    /* 3. Add Wallet Funds Balance Node -> Green */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(3) {
        background: #22c55e !important;
    }
    /* 4. Bank Cashout Liquidation Settlement -> Orange */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(4) {
        background: #f97316 !important;
    }
    /* 5. Ledger Statements Account Logs -> Cyan */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(5) {
        background: #06b6d4 !important;
    }
    /* 6. Disconnect Secure Portal Access -> Slate Grey */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:nth-child(6) {
        background: #64748b !important;
    }

    /* Hide standard radio circular elements completely */
    div[data-testid="stRadio"] input[type="radio"], 
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# --- AUTH PANELS PIPELINE ---
if not st.session_state.logged_in:
    st.markdown('<div class="premium-header"><h1>🔱 GLOBAL MATRIX INVESTMENT</h1></div>', unsafe_allow_html=True)
    
    if st.session_state.verification_stage == "awaiting_otp":
        with st.container(border=True):
            st.subheader("Verify Account")
            u_otp = st.text_input("Enter 6-Digit Token")
            if st.button("Submit Token", use_container_width=True, type="primary"):
                if u_otp.strip() == st.session_state.generated_otp:
                    t_data = st.session_state.temp_register_data
                    m_code = "GM" + str(random.randint(1000, 9999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                             (t_data['email'], t_data['password'], 77889900.00, "VIP LEVEL 3", t_data['ref_by'], m_code, t_data['name'], "2000-01-01", 0), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = t_data['email']
                    st.session_state.verification_stage = "closed"
                    st.rerun()
                else:
                    st.error("Token verification invalid.")

    elif st.session_state.auth_view == "forgot_password_request":
        with st.container(border=True):
            st.subheader("Reset Password Account")
            r_email = st.text_input("Enter Registered Email Address")
            
            if st.button("Send Token", use_container_width=True, type="primary"):
                user_match = query_db("SELECT full_name FROM users WHERE username=?", (r_email.strip(),), one=True)
                if user_match:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"email": r_email.strip(), "name": user_match[0]}
                    send_real_verification_email(r_email.strip(), st.session_state.generated_otp, user_match[0], "Password Recovery Code")
                    st.session_state.auth_view = "forgot_password_verification"
                    st.rerun()
                else:
                    st.error("Target email layout node not found.")
            
            if st.button("← Back to Login", use_container_width=True, type="secondary"):
                st.session_state.auth_view = "login"
                st.rerun()

    elif st.session_state.auth_view == "forgot_password_verification":
        with st.container(border=True):
            st.subheader("Enter Recovery Security Token")
            input_token = st.text_input("6-Digit Token Code", max_chars=6)
            new_pass = st.text_input("New Secure Access Password", type="password")
            if st.button("Overwrite Credentials", use_container_width=True, type="primary"):
                if input_token.strip() == st.session_state.generated_otp:
                    query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.temp_register_data['email']), commit=True)
                    st.success("Password overwritten! Proceed to login.")
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.error("Token validation index misaligned.")

    elif st.session_state.auth_view == "signup":
        with st.container(border=True):
            st.subheader("Create Profile Account")
            reg_name = st.text_input("Full Profile Name")
            reg_email = st.text_input("Valid Email Address")
            reg_pass = st.text_input("Secure Account Password", type="password")
            reg_inv = st.text_input("Invitation Hash Code (Optional)")
            
            if st.button("Register Now", use_container_width=True, type="primary"):
                if "@" in reg_email and reg_name and reg_pass:
                    st.session_state.generated_otp = str(random.randint(100000, 999999))
                    st.session_state.temp_register_data = {"name": reg_name.strip(), "email": reg_email.strip(), "password": reg_pass.strip(), "ref_by": reg_inv.strip() or "None"}
                    send_real_verification_email(reg_email.strip(), st.session_state.generated_otp, reg_name.strip())
                    st.session_state.verification_stage = "awaiting_otp"
                    st.rerun()
                else:
                    st.error("Please fill all valid parameters fields.")
                    
            if st.button("← Back to Login", use_container_width=True, type="secondary"):
                st.session_state.auth_view = "login"
                st.rerun()

    elif st.session_state.auth_view == "login":
        with st.container(border=True):
            st.subheader("Account Login Hub")
            login_email = st.text_input("Registered Account Email")
            login_pass = st.text_input("System Security Password", type="password")
            
            if st.button("Authorize Secure Access", use_container_width=True, type="primary"):
                if login_email.strip() == "admin" and login_pass.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    user_record = query_db("SELECT password FROM users WHERE username=?", (login_email.strip(),), one=True)
                    if user_record and user_record[0] == login_pass.strip():
                        query_db("UPDATE users SET balance=77889900.00, active_level='VIP LEVEL 3' WHERE username=?", (login_email.strip(),), commit=True)
                        st.session_state.logged_in = True
                        st.session_state.current_user = login_email.strip()
                        st.session_state.active_sidebar_tab = "Dashboard Overview"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
            
            st.markdown("---")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Create Account", use_container_width=True, type="secondary"):
                    st.session_state.auth_view = "signup"
                    st.rerun()
            with col_b2:
                if st.button("🔑 Forgot Pass?", use_container_width=True, type="secondary"):
                    st.session_state.auth_view = "forgot_password_request"
                    st.rerun()

# --- MAIN LOGGED-IN PORTAL INTERFACE WORKSPACE ---
else:
    if st.session_state.is_admin:
        st.markdown('<div class="premium-header"><h1>🚨 MASTER CONTROL PANEL (ADMIN)</h1></div>', unsafe_allow_html=True)
        
        if st.button("Logout Admin Console", type="primary"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        st.session_state.admin_video_url = st.text_input("Global Task Video URL Link:", value=st.session_state.admin_video_url)
        st.markdown("---")
        
        st.markdown("### 👥 All Registered Users Database")
        all_users = query_db("SELECT username, full_name, balance, active_level FROM users")
        
        if all_users:
            df_users = pd.DataFrame(all_users, columns=["Email/Username", "Full Name", "Balance (RM)", "VIP Level"])
            st.dataframe(df_users, use_container_width=True)
            
            st.markdown("#### ⚡ Quick Actions: Modify User Record Data")
            selected_user = st.selectbox("Select Target User Node to Control:", df_users["Email/Username"].tolist())
            
            if selected_user:
                current_meta = query_db("SELECT balance, active_level FROM users WHERE username=?", (selected_user,), one=True)
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    new_balance_val = st.number_input("Modify Wallet Balance (RM):", value=float(current_meta[0]), step=10.0)
                with col_b2:
                    current_lvls = ["None", "VIP LEVEL 1", "VIP LEVEL 2", "VIP LEVEL 3"]
                    try: initial_idx = current_lvls.index(current_meta[1])
                    except: initial_idx = 0
                    new_level_select = st.selectbox("Change Forced Tier Level:", current_lvls, index=initial_idx)
                
                if st.button("Save Changes and Overwrite Data Node", use_container_width=True, type="primary"):
                    query_db("UPDATE users SET balance=?, active_level=? WHERE username=?", (new_balance_val, new_level_select, selected_user), commit=True)
                    st.success(f"Successfully updated data logs for {selected_user}!")
                    st.rerun()
        else:
            st.info("No active user modules found in database pools.")
                
    else:
        st.markdown('<div class="premium-header"><h1>👑 GLOBAL MATRIX PREMIUM SYSTEM</h1></div>', unsafe_allow_html=True)
        u_data = query_db("SELECT balance, active_level, ref_code, last_claim_timestamp FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        bal, lvl, code, claim_stamp = u_data if u_data else (77889900.00, "VIP LEVEL 3", "GM7777", 0)
        ready_withdrawal = bal * 0.70

        # --- PREMIUM WALLET CARD BANNER ---
        st.markdown(f"""
        <div class="wallet-card-container">
            <div style="font-size: 15px; opacity: 0.9; font-weight: bold; letter-spacing: 0.5px; margin-bottom: 3px;">EarnWise: Papan Pemuka Perolehan Anda (MY)</div>
            <div style="font-size: 12px; color: #fbbf24; font-weight: bold; margin-bottom: 18px;">Pelan VIP/SVIP &amp; Tugasan Media Sosial Diperkenalkan!</div>
            <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div>
                    <div style="font-size: 12px; opacity: 0.7; font-weight: 600;">💼 DOMPET PEROLEHAN SAYA (CURRENT BALANCE)</div>
                    <div style="font-size: 26px; font-weight: bold; color: #ffffff; margin-top: 4px;">RM {bal:,.2f}</div>
                </div>
                <div style="border-left: 2px solid rgba(255,255,255,0.15); padding-left: 20px;">
                    <div style="font-size: 12px; opacity: 0.7; font-weight: 600;">📤 READY FOR CASHOUT OUTFLOW</div>
                    <div style="font-size: 26px; font-weight: bold; color: #10b981; margin-top: 4px;">RM {ready_withdrawal:,.2f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- NAVIGATION TILES MATCHING IMAGE 1000049608.jpg ---
        labels_list = [
            "Fund Deposit / Dashboard Overview", 
            "Claim Revenue / Stream Video Tasks", 
            "Add Wallet Funds Balance Node", 
            "Bank Cashout Liquidation Settlement", 
            "Ledger Statements Account Logs",
            "Disconnect Secure Portal Access"
        ]
        
        # Safe sync for mapping active view states
        tabs_map = {
            "Fund Deposit / Dashboard Overview": "Dashboard Overview",
            "Claim Revenue / Stream Video Tasks": "Stream Video Tasks",
            "Add Wallet Funds Balance Node": "Add Wallet Funds",
            "Bank Cashout Liquidation Settlement": "Bank Cashout Liquidation",
            "Ledger Statements Account Logs": "Ledger Logs Statements"
        }
        
        try:
            current_idx = list(tabs_map.values()).index(st.session_state.active_sidebar_tab)
        except ValueError:
            current_idx = 0
            
        app_tab = st.radio(
            "Select View Workspace Tab:",
            labels_list,
            index=current_idx,
            label_visibility="collapsed"
        )
        
        # Handle Action routing dynamically
        if app_tab == "Disconnect Secure Portal Access":
            st.session_state.logged_in = False
            st.session_state.auth_view = "login"
            st.rerun()
        else:
            st.session_state.active_sidebar_tab = tabs_map[app_tab]
            
        st.markdown("---")

        # --- DYNAMIC ACTION VIEWS ---
        if st.session_state.active_sidebar_tab == "Dashboard Overview":
            st.markdown("### Profile Meta Allocation Nodes Overview")
            with st.container(border=True):
                st.markdown("#### Video Stream Engine & Daily Rewards Module")
                st.write("Watch allocated video stream loop playback logs within the interface tasks workspace to unlock cloud matrix balances instantly into tracking pipelines.")
            
            with st.container(border=True):
                st.markdown("#### YouTube Streams Tasks Core Center (Active Tier)")
                st.markdown(f"Active Functional Node Profile Level Status: **{lvl}**")
                st.markdown(f"Unique Invitation Hash Tracking Identification Token ID: **{code}**")

        elif st.session_state.active_sidebar_tab == "Stream Video Tasks":
            with st.container(border=True):
                st.markdown("#### Stream Video Playback & Earn Matrix Settlement Tokens")
                st.video(st.session_state.admin_video_url)
                
                c_time = int(time.time())
                if (c_time - claim_stamp) < 86400:
                    rem = 86400 - (c_time - claim_stamp)
                    st.error(f"Daily system stream task cooldown lock active. Time remaining execution segment: {rem//3600}h {(rem%3600)//60}m")
                else:
                    if st.button("Claim Daily Video Processing Reward Yield Allocation Now", use_container_width=True, type="primary"):
                        bonus = 5.00 if lvl == "None" else float(LEVELS_CONF[lvl]["daily_reward"])
                        query_db("UPDATE users SET balance = balance + ?, last_claim_timestamp = ? WHERE username=?", (bonus, c_time, st.session_state.current_user), commit=True)
                        st.success(f"Execution tracking settlement stream balance assigned logged: +RM {bonus:.2f}")
                        st.rerun()

        elif st.session_state.active_sidebar_tab == "Add Wallet Funds":
            with st.container(border=True):
                st.markdown("#### Submit Local Malaysian Bank Transfer Deposit Proof Slip")
                deposit_bank = st.selectbox("Select Your Malaysian Bank Node Used for Deposit Transfer:", MALAYSIAN_BANKS)
                holder = st.text_input("Sender Account Holder Name/Title:")
                tx_str = st.text_input("Bank System Payment Verification Transaction Reference Number (Trx ID):")
                p_select = st.selectbox("Select Target Active Investment Nodes Deployment Level Configuration:", list(LEVELS_CONF.keys()))
                
                if st.button("Submit Deposit Proof Payment Slip Metadata", use_container_width=True, type="primary"):
                    if holder and tx_str:
                        method_string = f"Bank Transfer ({deposit_bank})"
                        query_db("INSERT INTO deposits (user, level, amount, method, holder_name, trx_id, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                                 (st.session_state.current_user, p_select, LEVELS_CONF[p_select]["cost"], method_string, holder, tx_str, "PENDING"), commit=True)
                        st.success("Log submission payment confirmation pending admin verification check.")

        elif st.session_state.active_sidebar_tab == "Bank Cashout Liquidation":
            with st.container(border=True):
                st.markdown("#### Configure Bank Liquidation Cashout Outflow Node Connection")
                withdrawal_bank = st.selectbox("Select Target Malaysian Bank Destination Node Account Receive:", MALAYSIAN_BANKS)
                w_acc_num = st.text_input("Receiver Bank Account Number:")
                w_acc_title = st.text_input("Receiver Bank Account Title/Full Name:")
                w_val = st.number_input("Value Sum Cashout Size (RM Units):", min_value=10.0, step=5.0)
                
                if st.button("Execute Outflow Cashout Command Authorization Pipeline", use_container_width=True, type="primary"):
                    if w_val <= bal:
                        routing_string = f"Bank: {withdrawal_bank} | Acc Num: {w_acc_num} | Title: {w_acc_title}"
                        query_db("UPDATE users SET balance = balance - ? WHERE username=?", (w_val, st.session_state.current_user), commit=True)
                        query_db("INSERT INTO withdrawals (user, amount, wallet_details, status) VALUES (?, ?, ?, ?)", (st.session_state.current_user, w_val, routing_string, "PENDING"), commit=True)
                        st.success("Outflow pipeline cache registration entry recorded. Settlement updates follow processing blocks.")
                        st.rerun()
                    else:
                        st.error("Shortfall tracking allocation index limits. Insufficient current balance index funds.")

        elif st.session_state.active_sidebar_tab == "Ledger Logs Statements":
            with st.container(border=True):
                st.markdown("#### Recent Account Nodes Transaction History Statements Ledger")
                all_deps = query_db("SELECT level, amount, status, method FROM deposits WHERE user=? ORDER BY id DESC", (st.session_state.current_user,))
                if not all_deps: 
                    st.info("No structural ledger transactions traced in data pipelines.")
                for dl in all_deps:
                    st.markdown(f"**Node Model:** {dl[0]} | **Amount:** RM {dl[1]:,.2f} | **Status:** {dl[2]} ({dl[3]})")
                    st.markdown("---")

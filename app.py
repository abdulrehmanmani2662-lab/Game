import streamlit as st
import sqlite3
import random

# Global application frame config
st.set_page_config(page_title="Y999 Matrix System", page_icon="🎰", layout="wide")

# --- MALAYSIAN CORE BANKS CONFIG ---
MALAYSIAN_BANKS = [
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad",
    "AmBank (M) Berhad"
]

# --- LIGHTWEIGHT LOCAL STORAGE DB WITH ADMIN EXTRAS ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            balance REAL,
            liquidation REAL,
            active_level TEXT,
            ref_code TEXT
        )
    """)
    # Live Ads Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # Deposit Requests Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            bank TEXT,
            name TEXT,
            trx_id TEXT,
            amount REAL,
            status TEXT
        )
    """)
    
    # Default Configs set karna agar pehle se na hon
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('live_ad_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg')")
    
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

# System Route Handlers
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'auth_view' not in st.session_state: st.session_state.auth_view = "login"
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Dashboard Overview"

# --- INJECTING PREMIUM FONTS & THEME ENGINE ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    html, body, .stApp { 
        background: linear-gradient(135deg, #0a0a1a 0%, #0d0d2b 40%, #1a0a2e 70%, #0a1a2e 100%) !important;
        color: #e0e0ff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 10, 40, 0.85) !important;
        border: 1px solid rgba(255, 105, 180, 0.3) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 0 40px rgba(255,105,180,0.15), 0 0 80px rgba(135,206,235,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    label, p, span, li {
        color: rgba(135,206,235,0.8) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 1px !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
    }
    
    .shimmer-logo {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #ff69b4, #87ceeb, #ff1493, #00bfff);
        background-size: 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s linear infinite;
        letter-spacing: 3px;
        margin-bottom: 5px;
    }
    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* Input Fields Fixes */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background: #ffffff !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: 1px solid rgba(255,105,180,0.4) !important;
        border-radius: 10px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stTextInput"] input::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
    }
    
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff1493, #ff69b4) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(255,20,147,0.4) !important;
        width: 100% !important;
    }
    
    .nav-container div.stButton > button {
        background: rgba(15, 10, 40, 0.6) !important;
        color: #e0e0ff !important;
        border: 1px solid rgba(135,206,235,0.3) !important;
        box-shadow: none !important;
    }
    
    .balance-card-container { display: flex; gap: 15px; margin-bottom: 25px; }
    .balance-box { flex: 1; background: rgba(15, 10, 40, 0.7); border: 1px solid rgba(255, 105, 180, 0.25); border-radius: 14px; padding: 16px; text-align: center; }
    .balance-value { font-family: 'Orbitron', sans-serif; font-size: 20px; font-weight: 900; color: #ff69b4 !important; }
    .balance-value-sky { font-family: 'Orbitron', sans-serif; font-size: 20px; font-weight: 900; color: #87ceeb !important; }
    .promo-banner { background: rgba(255,105,180,0.05); border: 1px dashed rgba(255,105,180,0.3); padding: 12px; border-radius: 12px; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- AUTH LAYER ---
if not st.session_state.logged_in:
    st.markdown("<div class='shimmer-logo'> 💵 ONLINE EARNINGS</div>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_view == "login":
            st.markdown("<h3 style='font-size:16px; color:#ff69b4;'>LOGIN TO ACCOUNT</h3>", unsafe_allow_html=True)
            user_input = st.text_input("Registered Phone number / Email Address", placeholder="Please enter Phone/Email")
            pass_input = st.text_input("System Security Password", type="password", placeholder="Enter password")
            
            if st.button("Verify"):
                # HARDCODED MASTER ADMIN LOGIN Check
                if user_input.strip() == "admin" and pass_input.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Admin Panel"
                    st.rerun()
                
                elif user_input.strip() and pass_input.strip():
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        m_code = "Y" + str(random.randint(100, 999))
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                 (user_input.strip(), pass_input.strip(), 0.0, 0.0, "SVIP LEVEL 1", m_code), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Dashboard Overview"
                        st.rerun()
            
            if st.button("Create Profile Account"):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        else:
            st.markdown("<h3 style='font-size:16px; color:#ff69b4;'>REGISTER SECURE PROFILE</h3>", unsafe_allow_html=True)
            reg_user = st.text_input("Account Phone number / Email", placeholder="Please enter Phone/Email")
            reg_pass = st.text_input("Setup Password security", type="password", placeholder="Enter password")
            
            if st.button("Confirm Registration"):
                if reg_user.strip() and reg_pass.strip():
                    m_code = "Y" + str(random.randint(100, 999))
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                             (reg_user.strip(), reg_pass.strip(), 0.0, 0.0, "SVIP LEVEL 1", m_code), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_user.strip()
                    st.session_state.is_admin = False
                    st.session_state.selected_panel = "Dashboard Overview"
                    st.rerun()
            
            if st.button("Back to Login Hub"):
                st.session_state.auth_view = "login"
                st.rerun()

# --- PANEL LAYER (IF LOGGED IN) ---
else:
    # --- ADMIN INTERFACE PANEL ---
    if st.session_state.is_admin:
        st.markdown("<h2 style='color:#ff69b4; text-align:center;'>🎛️ MASTER ADMIN CONTROL PANEL</h2>", unsafe_allow_html=True)
        
        if st.button("🚪 Logout Admin Session"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        st.write("---")
        
        # 1. LIVE VIDEO AD CONTROLLER
        st.markdown("### 🎥 1. Update Live Video Task Link")
        current_ad = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)[0]
        new_ad_link = st.text_input("Paste YouTube Video URL Here:", value=current_ad)
        if st.button("Update Live Video"):
            query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_ad_link.strip(),), commit=True)
            st.success("Live Video ad link updated successfully!")
            st.rerun()
            
        st.write("---")
        
        # 2. TOUCH 'N GO SCANNER IMAGE CONTROLLER
        st.markdown("### 💳 2. Update Touch 'n Go Scanner Link")
        current_tng = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
        new_tng_link = st.text_input("Paste TNG Scanner Image URL Here:", value=current_tng)
        if st.button("Update TNG Scanner Image"):
            query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_tng_link.strip(),), commit=True)
            st.success("Touch 'n Go Scanner image updated successfully!")
            st.rerun()
            
        st.write("---")
        
        # 3. PENDING DEPOSIT NOTIFICATIONS & APPROVAL
        st.markdown("### 🔔 3. Live Deposit Requests Notifications")
        pending_deposits = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
        
        if not pending_deposits:
            st.info("No pending deposit alerts right now.")
        else:
            for dep in pending_deposits:
                dep_id, dep_user, dep_bank, dep_name, dep_trx, dep_amount = dep
                with st.expander(f"⚠️ REQUEST: {dep_user} wants to deposit RM {dep_amount}"):
                    st.write(f"**User Account:** {dep_user}")
                    st.write(f"**Bank:** {dep_bank} | **Remitter Name:** {dep_name}")
                    st.write(f"**Transaction ID (Trx ID):** {dep_trx}")
                    
                    # Direct Admin Override Amount Entry
                    final_amount = st.number_input(f"Verify / Edit Amount to Add (RM) for Request #{dep_id}:", value=float(dep_amount), key=f"amt_{dep_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Approve & Add RM {final_amount}", key=f"app_{dep_id}"):
                            # Update user balance in DB
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (final_amount, dep_user), commit=True)
                            # Update status to Approved
                            query_db("UPDATE deposits SET status='Approved', amount=? WHERE id=?", (final_amount, dep_id), commit=True)
                            st.success(f"Approved! RM {final_amount} added to {dep_user}")
                            st.rerun()
                    with col2:
                        if st.button(f"❌ Reject Request", key=f"rej_{dep_id}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (dep_id,), commit=True)
                            st.error("Deposit request rejected.")
                            st.rerun()

    # --- USER INTERFACE PANEL ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.0, 0.0, "SVIP LEVEL 1", "Y999")
        
        st.markdown(f"""
        <div class="balance-card-container">
            <div class="balance-box">
                <div class="balance-title">My Earnings Balance</div>
                <div class="balance-value">RM {wallet_bal:,.2f}</div>
            </div>
            <div class="balance-box">
                <div class="balance-title"> Ready For Cashout</div>
                <div class="balance-value-sky">RM {liquid_bal:,.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='font-size:12px; color:rgba(135,206,235,0.6) !important;'>🧭 SYSTEM NAVIGATION INDEX</h4>", unsafe_allow_html=True)
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        
        if st.button("🎰 Fund Deposit / Overview Hub"): st.session_state.selected_panel = "Dashboard Overview"; st.rerun()
        if st.button("🎥 Claim Revenue / Video Task Node"): st.session_state.selected_panel = "Stream Video Tasks"; st.rerun()
        if st.button("💰 Add Wallet Balance Node"): st.session_state.selected_panel = "Add Wallet Funds"; st.rerun()
        if st.button("🏛️ Bank Cashout Liquidation Protocol"): st.session_state.selected_panel = "Bank Cashout"; st.rerun()
        if st.button("🚪 Disconnect Secure Session"): st.session_state.logged_in = False; st.rerun()
        
        st.markdown('</div><br>', unsafe_allow_html=True)
        st.markdown("<div style='background: rgba(15,10,40,0.85); padding:20px; border-radius:14px; border:1px solid rgba(255,105,180,0.2);'>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Dashboard Overview":
            st.markdown("<h3 style='font-size:18px; color:#ff69b4;'>Active Workspace Tracker</h3>", unsafe_allow_html=True)
            st.write(f"Account Profile Level Rank: {level_tag}")
            st.write(f"Unique Master Invitation Link Code: {reference_hash}")
            st.info("System Engine operational. All tracking nodes are online.")
            
        elif st.session_state.selected_panel == "Stream Video Tasks":
            st.markdown("<h3 style='font-size:18px; color:#ff69b4;'>Video Streams Premium Rewards</h3>", unsafe_allow_html=True)
            # Fetch Live Link from Database Set by Admin
            live_video_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)[0]
            st.video(live_video_url)
            
            if st.button("Process & Collect Task Revenue Distribution"):
                query_db("UPDATE users SET balance = balance + 250.00 WHERE username=?", (st.session_state.current_user,), commit=True)
                st.success("Reward allocated successfully! +RM 250.00")
                st.rerun()
                
        elif st.session_state.selected_panel == "Add Wallet Funds":
            st.markdown("<h3 style='font-size:18px; color:#ff69b4;'>Deposit via Touch 'n Go Scanner</h3>", unsafe_allow_html=True)
            
            # Fetch Live TNG Scanner Image from DB
            tng_img = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)[0]
            
            st.write("Scan this code to complete deposit payment:")
            st.image(tng_img, width=250)
            
            st.write("---")
            st.markdown("#### Submit Payment Proof Details")
            chosen_bank = st.selectbox("Select Network Bank Node:", ["Touch 'n Go eWallet"] + MALAYSIAN_BANKS)
            remitter_name = st.text_input("Remitter / Account Holder Full Name:")
            trx_id_input = st.text_input("Unique Transaction Reference ID (Trx ID / Ref No):")
            amount_input = st.number_input("Enter Amount Deposited (RM):", min_value=1.0, value=10.0)
            
            if st.button("File Proof Settlement Entry"):
                if remitter_name.strip() and trx_id_input.strip():
                    # Insert request as 'Pending' notification for Admin
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification notification sent to admin vault! Waiting for clearance approval.")
                else:
                    st.error("Please fill all fields properly.")
                    
        elif st.session_state.selected_panel == "Bank Cashout":
            st.markdown("<h3 style='font-size:18px; color:#ff69b4;'>Configure Outflow Liquidation Settlement</h3>", unsafe_allow_html=True)
            st.selectbox("Select Bank Infrastructure Module:", MALAYSIAN_BANKS)
            st.text_input("Target Clearing Bank Account Number:")
            st.number_input("Liquidation Inflow Allocation Volume (RM):", min_value=10.0)
            if st.button("Initialize Instant Cashout Framework"):
                st.error("Operation failed. Core balance limit constraints reached.")
                
        st.markdown("</div>", unsafe_allow_html=True)

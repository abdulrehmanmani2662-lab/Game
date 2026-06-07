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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
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
if 'cloud_deposits' not in st.session_state: st.session_state.cloud_deposits = []

# --- INJECTING PREMIUM FONTS & DESIGN UNIFICATION ENGINE ---
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
        box-shadow: 0 0 40px rgba(255,105,180,0.25), 0 0 80px rgba(135,206,235,0.1) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    label, p, span, li {
        color: #ff69b4 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: 2px !important;
        color: #ffffff !important;
    }
    
    /* INPUT FIELDS PREMIUM UNIFICATION - REPLACING PLAIN WHITE */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background: rgba(20, 15, 45, 0.9) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #ff1493 !important;
        border-radius: 12px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        box-shadow: 0 0 15px rgba(255, 20, 147, 0.2) !important;
    }
    
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        -webkit-text-fill-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* UNIFIED BUTTON DESIGN LIKE OUTER REGISTRATION HUB */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff1493, #ff69b4) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        box-shadow: 0 4px 25px rgba(255,20,147,0.5) !important;
        width: 100% !important;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(255,20,147,0.7) !important;
    }
    
    .balance-container-box {
        background: rgba(10, 5, 30, 0.9);
        border: 2px solid #ff69b4;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 30px rgba(255,105,180,0.3);
        margin-bottom: 25px;
    }
    
    .balance-display-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 36px;
        font-weight: 900;
        color: #00ffcc !important;
        text-shadow: 0 0 20px rgba(0,255,204,0.6);
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH LAYER ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#ff69b4; font-size:32px;'>🎰 GLOBAL MATRIX INVESTMENT</h1>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_view == "login":
            st.markdown("### ACCOUNT LOGIN HUB")
            user_input = st.text_input("Registered Phone number / Email Address", placeholder="Please enter Phone/Email")
            pass_input = st.text_input("System Security Password", type="password", placeholder="Enter password")
            
            if st.button("Authorize Secure Access"):
                if user_input.strip() == "admin" and pass_input.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Admin Panel"
                    st.rerun()
                
                elif user_input.strip() and pass_input.strip():
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        m_code = "Y999"
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                 (user_input.strip(), pass_input.strip(), 10.0, 7.0, "SVIP LEVEL 9", m_code), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Dashboard Overview"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
            
            if st.button("Create Account Profile"):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        else:
            st.markdown("### REGISTER SECURE PROFILE")
            reg_user = st.text_input("Account Phone number / Email", placeholder="Please enter Phone/Email")
            reg_pass = st.text_input("Setup Password security", type="password", placeholder="Enter password")
            
            if st.button("Confirm Registration"):
                if reg_user.strip() and reg_pass.strip():
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                             (reg_user.strip(), reg_pass.strip(), 10.0, 7.0, "SVIP LEVEL 9", "Y999"), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_user.strip()
                    st.session_state.is_admin = False
                    st.session_state.selected_panel = "Dashboard Overview"
                    st.rerun()

# --- PANEL LAYER (IF LOGGED IN) ---
else:
    if st.session_state.is_admin:
        st.markdown("<h2 style='color:#ff1493; text-align:center;'>🎛️ MASTER CONTROL SECURITY VAULT</h2>", unsafe_allow_html=True)
        if st.button("🚪 Disconnect Session Module"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        st.write("---")
        
        # 1. LIVE NOTIFICATIONS MANAGEMENT (STATE + BACKUP DB)
        st.markdown("### 🔔 Pending Income Deposit Alerts")
        
        # Pulling from state fallback & DB merge
        active_requests = st.session_state.cloud_deposits
        
        if not active_requests:
            st.info("No incoming deposit payloads detected at the current timestamp.")
        else:
            for idx, req in enumerate(active_requests):
                if req['status'] == 'Pending':
                    with st.container():
                        st.markdown(f"""
                        <div style='background:rgba(255,20,147,0.1); border:1px solid #ff1493; padding:15px; border-radius:10px; margin-bottom:10px;'>
                            <h4>Request from Account: {req['username']}</h4>
                            <p><b>Bank Selected:</b> {req['bank']}</p>
                            <p><b>Remitter Name:</b> {req['name']}</p>
                            <p><b>Transaction Reference Ref ID:</b> {req['trx_id']}</p>
                            <p style='color:#00ffcc !important; font-size:18px;'><b>Amount Filed: RM {req['amount']:.2f}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        override_amt = st.number_input(f"Verify / Re-allocate System Balance Load (RM):", value=float(req['amount']), key=f"or_{idx}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Authorize Load RM {override_amt}", key=f"auth_{idx}"):
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (override_amt, req['username']), commit=True)
                                st.session_state.cloud_deposits[idx]['status'] = 'Approved'
                                st.success(f"Successfully processed allocation node for {req['username']}")
                                st.rerun()
                        with col2:
                            if st.button(f"❌ Deny Framework Entry", key=f"deny_{idx}"):
                                st.session_state.cloud_deposits[idx]['status'] = 'Rejected'
                                st.error("Transaction vector rejected and logged.")
                                st.rerun()

    else:
        # --- USER INTERFACE PANEL ---
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.0, 7.0, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="balance-container-box">
            <div style="font-family:'Orbitron'; font-weight:700; color:#ff69b4; letter-spacing:1px;">DOMPET PEROLEHAN SAYA (CURRENT BALANCE)</div>
            <div class="balance-display-value">RM {wallet_bal:,.2f}</div>
            <div style="margin-top:10px; color:rgba(255,255,255,0.6) !important; font-size:14px;">READY FOR CASHOUT OUTFLOW: <span style="color:#00ffcc;">RM {liquid_bal:,.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 APPLICATION NAVIGATION ENGINE")
        
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("🎰 Fund Deposit / Overview"): st.session_state.selected_panel = "Dashboard Overview"; st.rerun()
            if st.button("🎥 Claim Revenue / Video Tasks"): st.session_state.selected_panel = "Stream Video Tasks"; st.rerun()
            if st.button("💰 Add Wallet Balance Node"): st.session_state.selected_panel = "Add Wallet Funds"; st.rerun()
        with col_nav2:
            if st.button("🏛️ Bank Cashout Liquidation"): st.session_state.selected_panel = "Bank Cashout"; st.rerun()
            if st.button("📊 Ledger Account Logs"): st.session_state.selected_panel = "Ledger"; st.rerun()
            if st.button("🚪 Disconnect Secure Session"): st.session_state.logged_in = False; st.rerun()
            
        st.write("---")
        
        if st.session_state.selected_panel == "Dashboard Overview":
            st.markdown("### Active Workspace Tracker")
            st.write(f"Account Profile Level Rank: **{level_tag}**")
            st.write(f"Unique Master Invitation Link Code: **{reference_hash}**")
            st.info("System Engine operational. All tracking nodes are online.")
            
        elif st.session_state.selected_panel == "Add Wallet Funds":
            st.markdown("### Deposit via Touch 'n Go Scanner")
            st.markdown("<div style='text-align:center;'><img src='https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg' width='220' style='border:3px solid #ff1493; border-radius:10px; box-shadow:0 0 20px #ff1493;'/></div>", unsafe_allow_html=True)
            
            st.write("---")
            st.markdown("#### Submit Payment Proof Details")
            chosen_bank = st.selectbox("Select Network Bank Node:", ["Touch 'n Go eWallet"] + MALAYSIAN_BANKS)
            remitter_name = st.text_input("Remitter / Account Holder Full Name:")
            trx_id_input = st.text_input("Unique Transaction Reference ID (Trx ID / Ref No):")
            amount_input = st.number_input("Enter Amount Deposited (RM):", min_value=1.0, value=10.0)
            
            if st.button("File Proof Settlement Entry"):
                if remitter_name.strip() and trx_id_input.strip():
                    payload = {
                        "username": st.session_state.current_user,
                        "bank": chosen_bank,
                        "name": remitter_name.strip(),
                        "trx_id": trx_id_input.strip(),
                        "amount": amount_input,
                        "status": "Pending"
                    }
                    st.session_state.cloud_deposits.append(payload)
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification payload sent to admin workspace vault! Awaiting node clearance approval.")
                else:
                    st.error("Data verification criteria unfulfilled. Fill all input spaces.")

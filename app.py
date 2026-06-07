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

# --- LIGHTWEIGHT DATABASE PERSISTENCE INITIALIZATION ---
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

# --- SYSTEM INTEGRITY RUNTIME MEMORY PERSISTENCE LINK ---
if 'persisted_deposits' not in st.session_state:
    st.session_state.persisted_deposits = []

# --- HIGH RESOLUTION HIGH-CONTRAST CASINO THEME ENGINE ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
    
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    html, body, .stApp { 
        background: #060314 !important;
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #0d0a21 !important;
        border: 2px solid #ff1493 !important;
        border-radius: 16px !important;
        padding: 25px !important;
        box-shadow: 0 0 25px rgba(255, 20, 147, 0.4) !important;
    }
    
    /* INPUT LABELS READABILITY FIX */
    label, p, span, li {
        color: #00ffcc !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 17px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
    }
    
    /* INPUT COMPONENT DYNAMIC CONTRAST */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 2px solid #ff1493 !important;
        border-radius: 8px !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }
    
    /* PREMIUM SOLID CASINO FLUID ACTION BUTTONS */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff1493 0%, #c71585 100%) !important;
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        border-radius: 10px !important;
        border: 2px solid #ffffff !important;
        padding: 14px 20px !important;
        box-shadow: 0 5px 20px rgba(255, 20, 147, 0.6) !important;
        width: 100% !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .balance-container-box {
        background: #120e2e;
        border: 3px solid #00ffcc;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.3);
        margin-bottom: 20px;
    }
    
    .balance-display-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 38px;
        font-weight: 900;
        color: #ff1493 !important;
        text-shadow: 0 0 15px rgba(255, 20, 147, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH LAYER ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#ff1493;'>🎰 MATRIX LEAGUE</h1>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_view == "login":
            st.markdown("### SECURITY CREDENTIALS ACCESS")
            user_input = st.text_input("Registered ID (Phone/Email):", placeholder="Enter profile user tracking node")
            pass_input = st.text_input("Security Access Code:", type="password", placeholder="Enter keycode")
            
            if st.button("Authorize Core Profile"):
                if user_input.strip() == "admin" and pass_input.strip() == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.current_user = "admin"
                    st.session_state.is_admin = True
                    st.session_state.selected_panel = "Admin Panel"
                    st.rerun()
                
                elif user_input.strip() and pass_input.strip():
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                                 (user_input.strip(), pass_input.strip(), 10.00, 7.00, "SVIP LEVEL 9", "Y999"), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Dashboard Overview"
                        st.rerun()
                    else:
                        st.error("Authentication configuration match failed inside core database storage.")
            
            if st.button("Register Access Gateway"):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        else:
            st.markdown("### ACCOUNT PROFILE INITIALIZATION")
            reg_user = st.text_input("Setup Registered Account Node:")
            reg_pass = st.text_input("Configure Structural Password:", type="password")
            
            if st.button("Establish Node Connection"):
                if reg_user.strip() and reg_pass.strip():
                    query_db("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                             (reg_user.strip(), reg_pass.strip(), 10.00, 7.00, "SVIP LEVEL 9", "Y999"), commit=True)
                    st.session_state.logged_in = True
                    st.session_state.current_user = reg_user.strip()
                    st.session_state.is_admin = False
                    st.session_state.selected_panel = "Dashboard Overview"
                    st.rerun()

# --- SECURITY SYSTEM CONTROL ROUTER ---
else:
    if st.session_state.is_admin:
        st.markdown("<h2 style='color:#00ffcc; text-align:center;'>🎛️ MASTER ADMINISTRATIVE MODULE</h2>", unsafe_allow_html=True)
        if st.button("🚪 Terminate Session Connection"):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
            
        st.write("---")
        
        st.markdown("### 🔔 Pending Settlement Pipeline Inflows")
        
        # Persistent UI loop check over DB structural frames
        db_pending = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
        
        # Merge both DB entries and runtime allocations safely
        combined_requests = []
        seen_trx = set()
        
        for item in st.session_state.persisted_deposits:
            if item['status'] == 'Pending' and item['trx_id'] not in seen_trx:
                combined_requests.append(item)
                seen_trx.add(item['trx_id'])
                
        for item in db_pending:
            if item[4] not in seen_trx:
                combined_requests.append({
                    "id": item[0], "username": item[1], "bank": item[2],
                    "name": item[3], "trx_id": item[4], "amount": item[5], "status": "Pending"
                })
        
        if not combined_requests:
            st.info("No actionable verification entries found in validation pipelines.")
        else:
            for idx, req in enumerate(combined_requests):
                with st.container():
                    st.markdown(f"""
                    <div style='background:#14112e; border:2px solid #ff1493; padding:15px; border-radius:8px; margin-bottom:12px;'>
                        <h4 style='color:#ffffff;'>REQUEST payload FROM user: {req['username']}</h4>
                        <p style='color:#00ffcc !important; margin:3px 0;'><b>TRANSFERRED VIA:</b> {req['bank']}</p>
                        <p style='color:#00ffcc !important; margin:3px 0;'><b>SENDER NAME:</b> {req['name']}</p>
                        <p style='color:#00ffcc !important; margin:3px 0;'><b>REFERENCE TRX ID:</b> {req['trx_id']}</p>
                        <h3 style='color:#ffff00 !important; margin-top:5px;'>AMOUNT SUBMITTED: RM {req['amount']:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    adjusted_credit = st.number_input("Verify Allocation Payload Load Limit (RM):", value=float(req['amount']), key=f"adj_{req['trx_id']}_{idx}")
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"✅ Approve Payload Asset", key=f"val_app_{req['trx_id']}_{idx}"):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (adjusted_credit, req['username']), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE trx_id=?", (req['trx_id'],), commit=True)
                            
                            # Clean runtime storage status context
                            for s_item in st.session_state.persisted_deposits:
                                if s_item['trx_id'] == req['trx_id']: s_item['status'] = 'Approved'
                                
                            st.success(f"Asset node authorization complete for {req['username']}")
                            st.rerun()
                    with btn_col2:
                        if st.button(f"❌ Drop System Payload Entry", key=f"val_rej_{req['trx_id']}_{idx}"):
                            query_db("UPDATE deposits SET status='Rejected' WHERE trx_id=?", (req['trx_id'],), commit=True)
                            for s_item in st.session_state.persisted_deposits:
                                if s_item['trx_id'] == req['trx_id']: s_item['status'] = 'Rejected'
                            st.error("Request payload dropped out of verification pipelines.")
                            st.rerun()

    else:
        # --- USER INTERFACE MODULE ---
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.00, 7.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="balance-container-box">
            <div style="font-family:'Orbitron'; font-weight:700; color:#00ffcc;">DOMPET PEROLEHAN SAYA (MAIN WALLET)</div>
            <div class="balance-display-value">RM {wallet_bal:,.2f}</div>
            <div style="margin-top:5px; color:#ffffff !important; font-size:15px; font-weight:700;">READY FOR CASHOUT TRANSFER MODULE: <span style="color:#00ffcc;">RM {liquid_bal:,.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 INTERFACE CONTROL NODE INDEX")
        
        nav_matrix_1, nav_matrix_2 = st.columns(2)
        with nav_matrix_1:
            if st.button("🎰 SYSTEM TRACKING METRICS OVERVIEW"): st.session_state.selected_panel = "Dashboard Overview"; st.rerun()
            if st.button("💰 ADD DOMPET ACCOUNT SYSTEM FUNDS"): st.session_state.selected_panel = "Add Wallet Funds"; st.rerun()
        with nav_matrix_2:
            if st.button("🏛️ CASHOUT SETTLEMENT CLEARING PROTOCOL"): st.session_state.selected_panel = "Bank Cashout"; st.rerun()
            if st.button("🚪 DISCONNECT PORTAL SYSTEM ACCESS"): st.session_state.logged_in = False; st.rerun()
            
        st.write("---")
        
        if st.session_state.selected_panel == "Dashboard Overview":
            st.markdown("### SYSTEM RUNTIME OPERATIONS OVERVIEW")
            st.write(f"Account Infrastructure Matrix Level: **{level_tag}**")
            st.write(f"Unique Master Reference Affiliate Hash: **{reference_hash}**")
            st.info("Dynamic analytical tracking structures show zero active latency drops inside current workspace channels.")
            
        elif st.session_state.selected_panel == "Add Wallet Funds":
            st.markdown("### MULTI-BANK PAYLOAD INFLOW VIA TOUCH 'N GO")
            st.markdown("<div style='text-align:center; padding:10px;'><img src='https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg' width='220' style='border:4px solid #ff1493; border-radius:12px; box-shadow:0 0 25px #ff1493;'/></div>", unsafe_allow_html=True)
            
            st.write("---")
            st.markdown("#### SUBMIT SETTLEMENT INPUT DETAILS")
            chosen_bank = st.selectbox("Select Target Banking Inflow Node:", ["Touch 'n Go eWallet"] + MALAYSIAN_BANKS)
            remitter_name = st.text_input("Sender Remitter / Registrant Account Name:")
            trx_id_input = st.text_input("System Reference Ref-ID / Trx Transaction Number:")
            amount_input = st.number_input("Inflow Valuation Volume Amount (RM):", min_value=1.0, value=10.0)
            
            if st.button("EXECUTE SUBMISSION DISPATCH LOGS"):
                if remitter_name.strip() and trx_id_input.strip():
                    new_payload = {
                        "username": st.session_state.current_user,
                        "bank": chosen_bank,
                        "name": remitter_name.strip(),
                        "trx_id": trx_id_input.strip(),
                        "amount": amount_input,
                        "status": "Pending"
                    }
                    # Save both locally inside isolated runtime slots & backup database instances
                    st.session_state.persisted_deposits.append(new_payload)
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification framework transaction dispatched successfully. Validation updates are logged inside admin channels.")
                else:
                    st.error("Submission input criteria incomplete. Please fill all alpha-numeric field spaces.")
                    
        elif st.session_state.selected_panel == "Bank Cashout":
            st.markdown("### CONFIGURE CASHOUT TRANSACTIONS PROTOCOLS")
            st.selectbox("Target Core Clearing Bank Node:", MALAYSIAN_BANKS)
            st.text_input("Target Account System Number Registry:")
            st.number_input("Volume Inflow Framework Target (RM):", min_value=10.0)
            if st.button("AUTHORIZE CASHOUT PROCESS NODE"):
                st.error("System structural validation drop error. Main balance threshold index mismatch.")

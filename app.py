import streamlit as st
import sqlite3

# App config
st.set_page_config(page_title="Matrix Dashboard Engine", page_icon="🎰", layout="wide")

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password TEXT, balance REAL, liquidation REAL, active_level TEXT, ref_code TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            key TEXT PRIMARY KEY, value TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT, trx_id TEXT, amount REAL, status TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('live_ad_url', 'https://www.youtube.com')")
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg')")
    # Default Admin Account
    cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 0.0, 0.0, 'OWNER', 'MASTER')")
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

# Session Management 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Dashboard Hub"

# --- HIGH READABILITY CLEAN NEON UI (FIXED LIGHTS & FONTS) ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    html, body, .stApp { 
        background-color: #0b091a !important;
        color: #ffffff !important;
    }
    
    /* Input Form Container Clear Box */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #121026 !important;
        border: 2px solid #00ffcc !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* INPUT LABELS READABILITY FIX - NO HIGH BLINDING GLOW */
    label, p, span, li, [data-testid="stMarkdownContainer"] p {
        color: #00ffcc !important;
        font-weight: bold !important;
        font-size: 16px !important;
        text-transform: uppercase !important;
        text-shadow: none !important;
    }
    
    /* INPUT FIELDS TEXT & BACKGROUND COLOR FIX */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background-color: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        border: 2px solid #ff007f !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    /* PREMIUM SOLID READABLE BUTTONS - NO OVERLAPPING TEXT SHADOWS */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff007f 0%, #bc005b 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0px 4px 10px rgba(255, 0, 127, 0.3) !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: #ff007f !important;
        color: #ffffff !important;
    }

    .balance-box {
        background: #17143a;
        border: 2px solid #00ffcc;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION DECOUPLER LOGIC ---
def switch_panel(panel_name):
    st.session_state.selected_panel = panel_name
    st.rerun()

# --- ENTRY CONTROL LAYER ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#ff007f;'>🎰 CORE ACCESS GATEWAY</h1>", unsafe_allow_html=True)
    
    with st.container():
        user_input = st.text_input("Username / Registered Node Email:", placeholder="Enter account registration key")
        pass_input = st.text_input("System Security Password:", type="password", placeholder="Enter authorization credential")
        
        col_login, col_reg = st.columns(2)
        with col_login:
            if st.button("Authorize Connection Portal"):
                if user_input.strip() == "admin" or "@" not in user_input:
                    # Check database for entry
                    record = query_db("SELECT password, username FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if record and record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = (record[1] == "admin")
                        st.session_state.selected_panel = "Admin Hub" if st.session_state.is_admin else "Dashboard Hub"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
                else:
                    record = query_db("SELECT password FROM users WHERE username=?", (user_input.strip(),), one=True)
                    if not record:
                        query_db("INSERT INTO users VALUES (?, ?, 10.00, 7.00, 'SVIP LEVEL 9', 'Y999')", (user_input.strip(), pass_input.strip()), commit=True)
                        record = [pass_input.strip()]
                    
                    if record[0] == pass_input.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = user_input.strip()
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Dashboard Hub"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
                        
        with col_reg:
            if st.button("Create Temporary Matrix Node"):
                if user_input.strip() and pass_input.strip():
                    query_db("INSERT OR IGNORE INTO users VALUES (?, ?, 10.00, 7.00, 'SVIP LEVEL 9', 'Y999')", (user_input.strip(), pass_input.strip()), commit=True)
                    st.success("Registration success allocation logged. Click Authorize to access.")

else:
    # --- ADMIN ROUTE PIPELINE ---
    if st.session_state.is_admin:
        st.markdown("<h2 style='color:#00ffcc; text-align:center;'>⚙️ SYSTEM MASTER CONTROLLER PANEL</h2>", unsafe_allow_html=True)
        
        # Admin Top Bar Menu Nodes
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            if st.button("📥 Pending Settlement Inflows"): switch_panel("Admin Hub")
        with m_col2:
            if st.button("🔗 Modify Task Streams Link"): switch_panel("Edit Tasks Link")
        with m_col3:
            if st.button("🖼️ Replace QR Scanner Asset"): switch_panel("Edit QR System")
        with m_col4:
            if st.button("🚪 Terminate Master Connection"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
                
        st.write("---")
        
        if st.session_state.selected_panel == "Admin Hub":
            st.markdown("### 🔔 Inflow Deposits Waiting Action")
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items:
                st.info("Validation processing logs queue is empty.")
            else:
                for item in pending_items:
                    with st.container():
                        st.markdown(f"""
                        <div style='background:#18153c; padding:15px; border-radius:8px; border-left:5px solid #ff007f; margin-bottom:10px;'>
                            <p style='color:#ffffff !important; margin:0;'><b>User Node ID:</b> {item[1]}</p>
                            <p style='color:#00ffcc !important; margin:0;'><b>Bank Route:</b> {item[2]} | <b>Holder:</b> {item[3]}</p>
                            <p style='color:#ffff00 !important; margin:0;'><b>Trx Reference Ref:</b> {item[4]}</p>
                            <h4 style='color:#ff007f; margin:5px 0 0 0;'>Amount Claimed: RM {item[5]:.2f}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button(f"✅ Approve RM {item[5]:.2f}", key=f"app_{item[0]}"):
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                                query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                                st.success("Balance processed securely inside node matrix account.")
                                st.rerun()
                        with btn_col2:
                            if st.button(f"❌ Reject Submission Request", key=f"rej_{item[0]}"):
                                query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                                st.error("Request payload removed from pipelines.")
                                st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Tasks Link":
            st.markdown("### 🔗 Task Configuration Control Node")
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            
            new_url = st.text_input("Global Platform Video Stream Target Link:", value=url_str)
            if st.button("Save Dynamic Redirection Target"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Target link payload successfully configured inside runtime systems.")
                
        elif st.session_state.selected_panel == "Edit QR System":
            st.markdown("### 🖼️ QR Gateway Payload Configuration")
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            
            new_qr = st.text_input("Scanner Image Asset Direct Hosted Link:", value=qr_str)
            if st.button("Deploy New Terminal QR System Link"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("System QR display reference frame updated.")

    # --- CLIENT USER INTERFACE INTERFACE ROUTE ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.00, 7.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="balance-box">
            <div style="font-size:14px; color:#00ffcc; font-weight:bold;">DOMPET PEROLEHAN SAYA (MAIN WALLET)</div>
            <div style="font-size:36px; font-weight:900; color:#ffffff; margin:5px 0;">RM {wallet_bal:,.2f}</div>
            <div style="font-size:14px; color:#ff007f;">READY FOR CASHOUT TRANSFER MODULE: RM {liquid_bal:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # User Workspace Tab Selection Layout Buttons
        nav1, nav2, nav3, nav4 = st.columns(4)
        with nav1:
            if st.button("📊 OVERVIEW"): switch_panel("Dashboard Hub")
        with nav2:
            if st.button("💰 ADD FUNDS"): switch_panel("Add Balance Funds")
        with nav3:
            if st.button("🏛️ CASHOUT"): switch_panel("Settlement Outflow")
        with nav4:
            if st.button("🚪 DISCONNECT"): 
                st.session_state.logged_in = False
                st.rerun()
                
        st.write("---")
        
        if st.session_state.selected_panel == "Dashboard Hub":
            st.markdown("### PROFILE META ALLOCATION NODES OVERVIEW")
            st.write(f"Account Rank Status: **{level_tag}**")
            st.write(f"Master Reference Affiliate Invitation Code: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background:#121026; padding:15px; border:1px solid #00ffcc; border-radius:8px;'>
                <h4 style='margin:0; color:#ffffff;'>Video Stream Engine Task Ready</h4>
                <p style='font-size:14px; color:#00ffcc !important;'>Watch live tasks allocations to unlock active cloud framework rewards.</p>
                <a href='{target_video}' target='_blank' style='display:inline-block; background:#ff007f; color:#ffffff; padding:10px 20px; text-decoration:none; font-weight:bold; border-radius:5px;'>▶️ Open Task Stream Hub</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Add Balance Funds":
            st.markdown("### SUBMIT PAYMENT INFLOW VERIFICATION PROOF")
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:15px;'><img src='{target_qr}' width='200' style='border:3px solid #ff007f; border-radius:10px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("Select Network Bank Node Target:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("Remitter / Account Holder Full Name:")
            trx_id_input = st.text_input("Unique Transaction Reference ID (Trx ID / Ref No):")
            amount_input = st.number_input("Enter Amount Deposited (RM):", min_value=1.0, value=10.0)
            
            if st.button("EXECUTE PROOF SETTLEMENT DISPATCH ENTRY"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification framework transaction logs updated securely inside system queues.")
                else:
                    st.error("Please fill out complete remitter registration strings fields.")
                    
        elif st.session_state.selected_panel == "Settlement Outflow":
            st.markdown("### BANK CASHOUT LIQUIDATION SETTLEMENT")
            st.selectbox("Select Target Account Receiving Node:", MALAYSIAN_BANKS[1:])
            st.text_input("Target Account Number Wire Registry:")
            st.number_input("Volume Liquidation Target (RM):", min_value=10.0)
            if st.button("AUTHORIZE CASHOUT PROCESS GATEWAY"):
                st.error("Transaction security block: Main verification framework parameters out of scale.")

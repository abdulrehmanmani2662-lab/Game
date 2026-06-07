import streamlit as st
import sqlite3
import random

# Core App Layout Configuration
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="📈", layout="wide")

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- SECURE STABLE DATABASE INTERFACE ---
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

# --- ANTI-REFRESH SESSION PERSISTENCE ENGINE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

# --- CUSTOM RGB GRADIENT STRIP & MATRIX LUXURY DARK THEME ---
st.markdown("""
    <style>
    /* Hide Streamlit Native Footers and Elements */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Global Background - Dark Market Grid Style Overlay */
    html, body, .stApp { 
        background: linear-gradient(rgba(10, 8, 22, 0.90), rgba(6, 4, 14, 0.95)), 
                    url("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1470&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: #f1f3f9 !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 🌈 ANIMATED RGB COLOR STRIP (UPAR WALI PATTI) */
    .rgb-moving-strip {
        height: 14px;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 99999;
        background: linear-gradient(90deg, #ff0055, #00ffcc, #ff00aa, #00ff55, #ffcc00, #ff0055);
        background-size: 400% 400%;
        animation: rgb-strip-move 8s linear infinite;
    }
    @keyframes rgb-strip-move {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Branded Header Setup */
    .brand-title {
        text-align: center;
        font-size: 38px;
        font-weight: 900;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #ffffff 30%, #00ffcc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 25px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    
    .brand-emojis {
        text-align: center;
        font-size: 32px;
        margin-bottom: 15px;
    }

    /* Full-Screen Pure Flat Forms (No Ganda Look, Pure Clean Interface) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(22, 20, 38, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 30px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Input Box Control Fields */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background-color: #1f1c33 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #363254 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        padding: 10px !important;
    }
    
    /* Clean Solid Corporate Interactive Buttons */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #00ffcc 0%, #00b38f 100%) !important;
        color: #06040e !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        width: 100% !important;
        transition: transform 0.2s, background 0.2s;
        box-shadow: 0px 4px 15px rgba(0, 255, 204, 0.2) !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: #00ffcc !important;
        transform: translateY(-1px);
    }

    /* Premium Balanced Metrics Block Card */
    .balance-card-wrapper {
        background: rgba(31, 28, 51, 0.9);
        border-left: 5px solid #00ffcc;
        border-radius: 8px;
        padding: 25px;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Inject the Moving RGB Strip into Top Window Layer
st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)

def switch_panel(panel_name):
    st.session_state.selected_panel = panel_name
    st.rerun()

# --- GATEWAY MANAGEMENT RENDER LAYER ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">GLOBAL NETWORK MATRIX</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-emojis">🔑 📈</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#a5a1c2; font-size:16px; margin-bottom:25px;'>Secured Authorization Matrix Node Framework Operational</p>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_mode == "Login":
            username = st.text_input("Account Identity Registry Key (Username/Email)", placeholder="Enter account key")
            password = st.text_input("System Security Authorization Code", type="password", placeholder="Enter password")
            
            if st.button("Authorize Connection"):
                if username.strip() == "admin":
                    record = query_db("SELECT password FROM users WHERE username='admin'", one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = "admin"
                        st.session_state.is_admin = True
                        st.session_state.selected_panel = "Pending Requests"
                        st.rerun()
                    else:
                        st.error("System security override blocked: Credentials validation error.")
                elif username.strip():
                    record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Overview"
                        st.rerun()
                    else:
                        st.error("Credential matching protocols found no system records match.")
            
            st.write("---")
            c_forgot, c_reg = st.columns(2)
            with c_forgot:
                if st.button("Forgot Password Routine?"):
                    st.session_state.auth_mode = "Forgot"
                    st.session_state.reset_step = 1
                    st.rerun()
            with c_reg:
                if st.button("Initialize New Matrix Node"):
                    st.session_state.auth_mode = "Register"
                    st.rerun()

        elif st.session_state.auth_mode == "Register":
            st.markdown("<h4 style='color:#00ffcc;'>Initialize New Registry Node</h4>", unsafe_allow_html=True)
            reg_username = st.text_input("Provide Communication Registration Email Key:")
            reg_password = st.text_input("Establish Private Security Lock Code:", type="password")
            
            if st.button("Deploy Node Parameters"):
                if reg_username.strip() and reg_password.strip():
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing:
                        st.error("Identity keys collision: Current parameters already exist inside database.")
                    else:
                        query_db("INSERT INTO users VALUES (?, ?, 10.00, 7.00, 'SVIP LEVEL 9', 'Y999')", 
                                 (reg_username.strip(), reg_password.strip()), commit=True)
                        st.success("Allocation logged. Proceed to connection auth interface.")
                        st.session_state.auth_mode = "Login"
                        st.rerun()
            
            if st.button("Return to Authentication Interface"):
                st.session_state.auth_mode = "Login"
                st.rerun()

        elif st.session_state.auth_mode == "Forgot":
            st.markdown("<h4 style='color:#00ffcc;'>System Access Key Recovery Matrix</h4>", unsafe_allow_html=True)
            
            if st.session_state.reset_step == 1:
                f_email = st.text_input("Enter Registered Identification Email:")
                if st.button("Search Master Vault Nodes"):
                    user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                    if user_match:
                        st.session_state.reset_email = f_email.strip()
                        st.session_state.generated_code = str(random.randint(111111, 999999))
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error("No account parameters verified for current string inputs.")
                if st.button("Cancel Operation"):
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                        
            elif st.session_state.reset_step == 2:
                st.info(f"🔒 Security token initialized for destination route: {st.session_state.reset_email}")
                st.warning(f"Development Sync Code Override: {st.session_state.generated_code}")
                
                input_code = st.text_input("Enter 6-Digit System Generated Verification Pin:")
                new_pass = st.text_input("Define Replacement Security Password Target:", type="password")
                
                if st.button("Re-commit Credentials Lock"):
                    if input_code.strip() == st.session_state.generated_code:
                        if len(new_pass.strip()) >= 4:
                            query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                            st.success("Vault passwords restructured cleanly.")
                            st.session_state.auth_mode = "Login"
                            st.session_state.reset_step = 1
                            st.rerun()
                        else:
                            st.error("String block index length parameters invalid.")
                    else:
                        st.error("Security token pairing logic invalid.")

# --- APPLICATION DESKTOP INTERFACE RENDER LAYER ---
else:
    # --- ADMIN PRIVILEGE VIEWS ---
    if st.session_state.is_admin:
        st.markdown("<h3 style='color:#00ffcc; font-weight:800; margin-top:15px;'>🛡️ MASTER ENGINE ADMINISTRATION</h3>", unsafe_allow_html=True)
        
        adm_col1, adm_col2, adm_col3, adm_col4 = st.columns(4)
        with adm_col1:
            if st.button("📥 Action Deposits Pipeline"): switch_panel("Pending Requests")
        with adm_col2:
            if st.button("🔗 Modify Task URL Targets"): switch_panel("Edit Task Redirects")
        with adm_col3:
            if st.button("🖼️ Re-align TNG Scanner Asset"): switch_panel("Edit QR Source")
        with adm_col4:
            if st.button("🚪 Terminate Global Session"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        st.write("---")
        
        # PURE FULL SCREEN EXCLUSIVE ACTIVE MENUS
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h4>Inflow Ledger Verification Channels</h4>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items:
                st.info("Validation processing logs queue is completely clear.")
            else:
                for item in pending_items:
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color:#1e1a33; padding:18px; border-radius:8px; border-left:4px solid #00ffcc; margin-bottom:15px;'>
                            <p style='margin:2px 0;'><b>Node Profile User Key:</b> {item[1]}</p>
                            <p style='margin:2px 0;'><b>Wire Route Destination:</b> {item[2]} ({item[3]})</p>
                            <p style='margin:2px 0; color:#ffcc00 !important;'><b>Asset Transaction Hash:</b> {item[4]}</p>
                            <h3 style='color:#00ffcc; margin:8px 0 0 0;'>Claim Volumetric: RM {item[5]:.2f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.button(f"Approve RM {item[5]:.2f}", key=f"adm_app_{item[0]}"):
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                                query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                                st.success("Allocations updated inside node core.")
                                st.rerun()
                        with btn_c2:
                            if st.button(f"Drop Request Record", key=f"adm_rej_{item[0]}"):
                                query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                                st.error("Log record purged successfully.")
                                st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            st.markdown("<h4>System Redirection Parameters Configuration</h4>", unsafe_allow_html=True)
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            
            new_url = st.text_input("Active System Redirection URL Location Config:", value=url_str)
            if st.button("Deploy New Target Path Structure"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Matrix redirection structures recompiled successfully.")
                
        elif st.session_state.selected_panel == "Edit QR Source":
            st.markdown("<h4>Touch 'n Go Payment Scanner Asset Mapping</h4>", unsafe_allow_html=True)
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            
            new_qr = st.text_input("Direct URL Link of New QR Image Repository:", value=qr_str)
            if st.button("Synchronize Terminal Scanner Display"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Target payment scanner terminals system synchronization complete.")

    # --- CLIENT INTERFACE VIEWS ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.00, 7.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="balance-card-wrapper">
            <p style="font-size:13px; color:#a5a1c2; margin:0; font-weight:bold; letter-spacing:1px;">MY EARNINGS BALANCE (MYR · Dompet Perolehan Saya)</p>
            <h1 style="font-size:46px; font-weight:900; color:#ffffff; margin:6px 0;">RM {wallet_bal:,.2f}</h1>
            <p style="font-size:14px; color:#00ffcc; margin:0; font-weight:bold;">READY FOR IMMEDIATE WITHDRAWAL CASHOUT: RM {liquid_bal:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pure Standalone Full View Switching Control Grid
        u_col1, u_col2, u_col3, u_col4 = st.columns(4)
        with u_col1:
            if st.button("📊 Vault Overview"): switch_panel("Overview")
        with u_col2:
            if st.button("💰 Deposit Dana"): switch_panel("Deposit")
        with u_col3:
            if st.button("🏛️ Cashout Modules"): switch_panel("Cashout")
        with u_col4:
            if st.button("🚪 Terminate Link"): 
                st.session_state.logged_in = False
                st.rerun()
        st.write("---")
        
        # DEDICATED INDEPENDENT INTERFACE SEGMENTS
        if st.session_state.selected_panel == "Overview":
            st.markdown("<h4>Operational Allocation Metrics</h4>", unsafe_allow_html=True)
            st.write(f"Verification Infrastructure Matrix Rank: **{level_tag}**")
            st.write(f"Active Allocation Invitation Reference: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#1e1a33; padding:25px; border-radius:10px; border: 1px solid rgba(0, 255, 204, 0.25); margin-top:20px;'>
                <h4 style='margin:0 0 6px 0; color:#ffffff;'>YOUTUBE & MEDIA REVENUE STREAM PIPELINE</h4>
                <p style='font-size:14px; color:#a5a1c2 !important; margin-bottom:15px;'>Interact with current data tasking processes stream nodes to instantly unlock framework rewards allocations.</p>
                <a href='{target_video}' target='_blank' style='display:inline-block; background-color:#00ffcc; color:#06040e; padding:12px 26px; text-decoration:none; font-weight:bold; border-radius:6px;'>▶️ Launch Active Task Window</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h4>Submit Inflow Payment Verification Evidence</h4>", unsafe_allow_html=True)
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:25px;'><img src='{target_qr}' width='185' style='border:2px solid #00ffcc; border-radius:10px; background:white; padding:5px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("Target Node Receiving Registry Bank:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("Sender Register Profile Holder Full Name:")
            trx_id_input = st.text_input("Unique Settlement Identifier Hash (Trx Ref ID Code):")
            amount_input = st.number_input("Inbound Flow Valuation Dimension Size (RM):", min_value=1.0, value=10.0)
            
            if st.button("Dispatch Inflow Verification Slip Stack"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Evidence parameters submitted safely to auditing pipelines queues dashboard.")
                else:
                    st.error("Please fill out complete fields strings parameters.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h4>Initialize Outbound Liquidation Pipeline</h4>", unsafe_allow_html=True)
            st.selectbox("Select Target Settlement Network Banking Terminal:", MALAYSIAN_BANKS[1:])
            st.text_input("Receiver Profile Wire Account Core Node Key:")
            st.number_input("Target Outflow Volumetric Sizing Dimensions (RM):", min_value=10.0)
            if st.button("Execute Settlement Cashout Terminal Authorization"):
                st.error("Operation halted: Core framework balance mapping out of parameters index limits.")

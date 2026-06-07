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
    cursor.execute("INSERT OR IGNORE INTO system_config VALUES ('live_ad_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')")
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

# --- ANTIFLICKER NAVIGATION ARCHITECTURE ---
params = st.query_params
if "nav" in params:
    st.session_state.selected_panel = params["nav"]

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

# --- MASTER CSS INJECTION (FORCED COLOR & INPUT FIXES) ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { 
        display: none !important; visibility: hidden !important;
    }
    
    html, body, .stApp { 
        background: linear-gradient(rgba(11, 9, 26, 0.96), rgba(6, 4, 15, 0.99)), 
                    url("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1470&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }
    
    .rgb-moving-strip {
        height: 6px; width: 100%; position: fixed; top: 0; left: 0; z-index: 99999;
        background: linear-gradient(90deg, #ff0055, #00ffcc, #ff00aa, #00ff55, #ffcc00, #ff0055);
        background-size: 400% 400%; animation: rgb-strip-move 6s linear infinite;
    }
    @keyframes rgb-strip-move { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }

    .brand-title {
        text-align: center; font-size: 30px; font-weight: 900; letter-spacing: 1px;
        background: linear-gradient(135deg, #ffffff 40%, #00ffcc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 35px; margin-bottom: 20px; text-transform: uppercase;
    }

    /* ✍️ TEXT INPUT & LABELS COLOR CORRECTION (FIXES WHITE/TRANSPARENT TEXT) */
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label {
        color: #00ffcc !important; font-weight: 800 !important; font-size: 14px !important; text-transform: uppercase !important;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div {
        background-color: #161326 !important; color: #ffffff !important;
        border: 2px solid #3c3761 !important; border-radius: 10px !important; font-weight: 700 !important;
    }
    
    /* Chrome/Safari placeholders fix */
    ::placeholder { color: #8a84a3 !important; opacity: 1 !important; }

    /* 💎 HIGH CONTRAST MATRIX ANCHOR LINK BUTTONS (ANTI-WHITE BLOCK) */
    .matrix-btn {
        display: block !important; width: 100% !important; text-align: center !important;
        padding: 14px 20px !important; margin: 12px 0px !important; border-radius: 12px !important;
        font-size: 15px !important; font-weight: 900 !important; text-transform: uppercase !important;
        letter-spacing: 1px !important; text-decoration: none !important; transition: all 0.2s ease-in-out !important;
        border: none !important;
    }
    .matrix-btn:hover { transform: scale(1.02); filter: brightness(1.2); }

    /* Forcing clear text colors inside backgrounds */
    .m-cyan { background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important; color: #000000 !important; box-shadow: 0 4px 15px rgba(0,242,254,0.4); }
    .m-gold { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%) !important; color: #000000 !important; box-shadow: 0 4px 15px rgba(246,211,101,0.4); }
    .m-pink { background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%) !important; color: #ffffff !important; box-shadow: 0 4px 15px rgba(248,87,166,0.4); }
    .m-green { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%) !important; color: #ffffff !important; box-shadow: 0 4px 15px rgba(0,176,155,0.4); }
    .m-violet { background: linear-gradient(135deg, #7f00ff 0%, #e100ff 100%) !important; color: #ffffff !important; box-shadow: 0 4px 15px rgba(127,0,255,0.4); }
    .m-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%) !important; color: #ffffff !important; box-shadow: 0 4px 15px rgba(255,65,108,0.4); }

    .metric-card-box {
        background: linear-gradient(135deg, rgba(32, 28, 59, 0.95) 0%, rgba(20, 17, 38, 0.95) 100%);
        border-left: 6px solid #00ffcc; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)

# --- ENGINE REROUTE ROUTINE ---
if "action" in params:
    action_type = params["action"]
    st.query_params.clear()
    if action_type == "logout":
        st.session_state.logged_in = False
        st.session_state.is_admin = False
    elif action_type == "switch_reg":
        st.session_state.auth_mode = "Register"
    elif action_type == "switch_log":
        st.session_state.auth_mode = "Login"
    elif action_type == "switch_forgot":
        st.session_state.auth_mode = "Forgot"
        st.session_state.reset_step = 1
    st.rerun()

# --- GATEWAY MANAGEMENT RENDER LAYER ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        username = st.text_input("Registered Account Email / Username:", placeholder="e.g. user@gmail.com")
        password = st.text_input("System Security Password:", type="password", placeholder="••••••••")
        
        # 🔑 LOGIN ACTION TRIGGER (Rendered as robust HTML to ensure text/style never breaks)
        st.markdown('<a href="?nav=Overview" target="_self" class="matrix-btn m-cyan">🔑 AUTHORIZE SECURE ACCESS</a>', unsafe_allow_html=True)
        
        # Fallback mechanism if user actually inputs details and clicks native element
        if username.strip() and password.strip():
            if username.strip() == "admin" and password.strip() == "admin123":
                st.session_state.logged_in = True
                st.session_state.current_user = "admin"
                st.session_state.is_admin = True
                st.session_state.selected_panel = "Pending Requests"
                st.rerun()
            else:
                record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                if record and record[0] == password.strip():
                    st.session_state.logged_in = True
                    st.session_state.current_user = record[1]
                    st.session_state.is_admin = False
                    st.session_state.selected_panel = "Overview"
                    st.rerun()
        
        # Navigation Links
        st.markdown('<a href="?action=switch_reg" target="_self" class="matrix-btn m-gold">➕ CREATE PROFILE ACCOUNT</a>', unsafe_allow_html=True)
        st.markdown('<a href="?action=switch_forgot" target="_self" class="matrix-btn m-violet">❓ FORGOT SECURITY PASSWORD?</a>', unsafe_allow_html=True)

    elif st.session_state.auth_mode == "Register":
        st.markdown("<h4 style='color:#00ffcc;'>Initialize New Registry Node</h4>", unsafe_allow_html=True)
        reg_username = st.text_input("Provide Profile Registration Email Key:")
        reg_password = st.text_input("Establish System Security Code:", type="password")
        
        if st.button("💾 CONFIRM NEW REPOSITORY ENTRY", use_container_width=True):
            if reg_username.strip() and reg_password.strip():
                existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                if existing: st.error("Identity keys collision: Already defined.")
                else:
                    query_db("INSERT INTO users VALUES (?, ?, 0.00, 0.00, 'SVIP LEVEL 9', 'Y999')", 
                             (reg_username.strip(), reg_password.strip()), commit=True)
                    st.success("Allocation logged complete.")
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                    
        st.markdown('<a href="?action=switch_log" target="_self" class="matrix-btn m-red">↩️ RETURN TO LOG IN HUB</a>', unsafe_allow_html=True)

    elif st.session_state.auth_mode == "Forgot":
        st.markdown("<h4 style='color:#00ffcc;'>System Access Key Recovery Matrix</h4>", unsafe_allow_html=True)
        
        if st.session_state.reset_step == 1:
            f_email = st.text_input("Enter Registered Identification Email:")
            if st.button("🔍 VERIFY ACCREDITED SYSTEM NODE", use_container_width=True):
                user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                if user_match:
                    st.session_state.reset_email = f_email.strip()
                    st.session_state.generated_code = str(random.randint(111111, 999999))
                    st.session_state.reset_step = 2
                    st.rerun()
                else: st.error("Identity mapping out of context records.")
            st.markdown('<a href="?action=switch_log" target="_self" class="matrix-btn m-red">CANCEL OPERATION</a>', unsafe_allow_html=True)
                        
        elif st.session_state.reset_step == 2:
            st.info(f"🔒 Route lock targets: {st.session_state.reset_email}")
            st.warning(f"Development Core Sync Code: {st.session_state.generated_code}")
            input_code = st.text_input("Enter 6-Digit Verification Pin:")
            new_pass = st.text_input("Define Replacement Security Password Target:", type="password")
            
            if st.button("🛠️ RESET IDENTITY VAULT KEY", use_container_width=True):
                if input_code.strip() == st.session_state.generated_code:
                    if len(new_pass.strip()) >= 4:
                        query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                        st.success("Structure mapping recompiled clean.")
                        st.session_state.auth_mode = "Login"
                        st.session_state.reset_step = 1
                        st.rerun()
                    else: st.error("Length criteria violation.")
                else: st.error("Verification sequence failed encryption matching.")

# --- APPLICATION DESKTOP INTERFACE RENDER LAYER ---
else:
    if st.session_state.is_admin:
        st.markdown("<h3 style='color:#00ffcc; font-weight:900; text-align:center;'>🛡️ MASTER ENGINE ADMINISTRATION</h3>", unsafe_allow_html=True)
        
        st.markdown('<a href="?nav=Pending Requests" target="_self" class="matrix-btn m-cyan">📥 Action Deposits Pipeline Channels</a>', unsafe_allow_html=True)
        st.markdown('<a href="?nav=Edit Task Redirects" target="_self" class="matrix-btn m-pink">🔗 Modify Task URL Targets</a>', unsafe_allow_html=True)
        st.markdown('<a href="?nav=Edit QR Source" target="_self" class="matrix-btn m-violet">🖼️ Re-align Terminal TNG Scanner Asset</a>', unsafe_allow_html=True)
        st.markdown('<a href="?action=logout" target="_self" class="matrix-btn m-red">🚪 Terminate Global Core Admin Session</a>', unsafe_allow_html=True)
        
        st.write("---")
        
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h4 style='color:#00ffcc;'>Inflow Ledger Verification Channels</h4>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items: st.info("Validation processing logs queue is completely clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#1c1836; padding:18px; border-radius:10px; border-left:5px solid #ff0055; margin-bottom:15px;'>
                        <p><b>User Key:</b> {item[1]} | <b>Route Node:</b> {item[2]} ({item[3]})</p>
                        <p style='color:#ffcc00;'><b>Trx Reference ID Hash:</b> {item[4]}</p>
                        <h3 style='color:#00ffcc; margin:5px 0;'>Claim: RM {item[5]:.2f}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"✅ APPROVE DEPOSIT QUANTITY: RM {item[5]:.2f}", key=f"app_{item[0]}", use_container_width=True):
                        query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                        query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                        st.rerun()
                    if st.button(f"❌ PURGE RECORDS LOG INDEX", key=f"rej_{item[0]}", use_container_width=True):
                        query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                        st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            new_url = st.text_input("Active System Redirection URL Location Config:", value=url_str)
            if st.button("🔗 COMPILE NEW REDIRECT STRUCTURE PATHS", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Redirection matrix updated successfully.")
                
        elif st.session_state.selected_panel == "Edit QR Source":
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            new_qr = st.text_input("Direct URL Link of New QR Image Repository Source:", value=qr_str)
            if st.button("🖼️ SYNCHRONIZE ACTIVE TERMINAL SCANNERS", use_container_width=True):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Display nodes updated cleanly.")

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:12px; color:#a5a1c2; margin:0; letter-spacing:1px; font-weight:800;">MY EARNINGS WALLET BALANCE (Dompet Perolehan Saya)</p>
            <h1 style="font-size:38px; font-weight:900; color:#00ffcc; margin:5px 0;">RM {wallet_bal:,.2f}</h1>
            <p style="font-size:13px; color:#ffffff; margin:0; font-weight:700;">READY FOR IMMEDIATE CASHOUT LIQUIDATION: <span style='color:#ff0055;'>RM {liquid_bal:,.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Perfect, persistent layout links
        st.markdown('<a href="?nav=Overview" target="_self" class="matrix-btn m-cyan">📊 System Metrics Overview</a>', unsafe_allow_html=True)
        st.markdown('<a href="?nav=Deposit" target="_self" class="matrix-btn m-gold">💰 Add Dompet System Funds</a>', unsafe_allow_html=True)
        st.markdown('<a href="?nav=Cashout" target="_self" class="matrix-btn m-green">🏛️ Cashout Settlement Protocol</a>', unsafe_allow_html=True)
        st.markdown('<a href="?action=logout" target="_self" class="matrix-btn m-red">🚪 Disconnect Portal Session Link</a>', unsafe_allow_html=True)
        
        st.write("---")
        
        if st.session_state.selected_panel == "Overview":
            st.markdown("<h4 style='color:#00f2fe;'>Operational Allocation Metrics</h4>", unsafe_allow_html=True)
            st.write(f"Verification Matrix Rank Node: **{level_tag}**")
            st.write(f"Active Invitation Reference Hash: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#1a1730; padding:20px; border-radius:12px; border: 1px solid rgba(0, 242, 254, 0.3); margin-top:15px; width:100%;'>
                <h4 style='margin:0 0 5px 0; color:#ffffff;'>YOUTUBE & MEDIA REVENUE STREAM PIPELINE</h4>
                <p style='font-size:13px; color:#a5a1c2; margin-bottom:15px;'>Interact with data tasking stream nodes to instantly trigger internal rewards system payouts.</p>
                <a href='{target_video}' target='_blank' style='display:block; text-align:center; background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%); color:#ffffff; padding:14px; text-decoration:none; font-weight:800; border-radius:10px; box-shadow:0 4px 15px rgba(248,87,166,0.35);'>▶️ LAUNCH ACTIVE VIDEO TASK NODE</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h4 style='color:#f6d365;'>Multi-Bank Payload Inflow Via Touch 'n Go</h4>", unsafe_allow_html=True)
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><img src='{target_qr}' width='190' style='border:3px solid #f6d365; border-radius:12px; background:white; padding:5px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("Select Target Banking Inflow Node:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("Sender Remitter / Registrant Account Name:")
            trx_id_input = st.text_input("System Reference Ref-ID / Trx Transaction Number:")
            amount_input = st.number_input("Inflow Valuation Volume Amount (RM):", min_value=1.0, value=10.0)
            
            if st.button("📤 EXECUTE DISPATCH SUBMISSION LOGS", use_container_width=True):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Evidence logs stacked into system queue.")
                else: st.error("Input validation values missing context indexes.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h4 style='color:#00b09b;'>Initialize Outbound Settlement Pipeline</h4>", unsafe_allow_html=True)
            st.selectbox("Select Destination Network Clearance Bank Node:", MALAYSIAN_BANKS[1:])
            st.text_input("Receiver Account Wire Index Account Number Key:")
            st.number_input("Target Settlement Request Dimensions (RM):", min_value=10.0)
            
            if st.button("🏛️ REQUEST TERMINAL OUTBOUND EXPULSION", use_container_width=True):
                st.error("Operation Halted: System map index balance registry allocation mismatch parameters.")

import streamlit as st
import sqlite3
import random

# --- CORE APPLICATION CONFIGURATION ---
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="📈", layout="wide")

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- SECURE DATABASE INTERFACE ---
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

# --- EXTENDED PERSISTENT SESSION STATES ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

# --- MASTER ENGINE UI STYLING ENGINE (COMPACT RESPONSIVE FACEBOOK STYLE) ---
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
        height: 5px; width: 100%; position: fixed; top: 0; left: 0; z-index: 99999;
        background: linear-gradient(90deg, #ff007f, #00ffcc, #ff00aa, #00ff55, #ffcc00, #ff007f);
        background-size: 400% 400%; animation: rgb-strip-move 6s linear infinite;
    }
    @keyframes rgb-strip-move { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }

    .brand-title {
        text-align: center; font-size: 26px; font-weight: 900; letter-spacing: 1.2px;
        background: linear-gradient(135deg, #ffffff 30%, #00ffcc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 20px; margin-bottom: 20px; text-transform: uppercase;
    }

    /* Fixed Max Width Container to stop fields stretching across the whole screen */
    [data-testid="stVerticalBlock"] > div {
        max-width: 550px !important;
        margin: 0 auto !important;
    }

    /* Input Fields Correction */
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stWidgetLabel"] p {
        color: #00ffcc !important; font-weight: 700 !important; font-size: 12px !important; 
        text-transform: uppercase !important; margin-bottom: 4px !important; display: block !important;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #131021 !important; color: #ffffff !important;
        border: 2px solid #ff007f !important; border-radius: 10px !important; font-weight: 600 !important;
        padding: 6px 12px !important;
    }

    /* 💎 COMPACT RESPONSIVE GRID DABAY (FB HOME PAGE STYLE) */
    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important; font-size: 13px !important; font-weight: 700 !important;
        text-transform: uppercase !important; border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; width: 100% !important; 
        padding: 10px 14px !important; margin-top: 4px !important; margin-bottom: 4px !important;
        box-shadow: 0 4px 12px rgba(255, 0, 127, 0.2) !important;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00ffcc 0%, #00b09b 100%) !important;
        color: #000000 !important; 
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.4) !important;
        transform: translateY(-1px);
    }

    .action-deck {
        background: rgba(20, 16, 36, 0.93); border: 2px solid #ff007f;
        border-radius: 12px; padding: 18px; margin-top: 12px;
        box-shadow: 0 8px 25px rgba(255, 0, 127, 0.1);
    }

    .metric-card-box {
        background: linear-gradient(135deg, rgba(28, 23, 51, 0.95) 0%, rgba(15, 12, 31, 0.95) 100%);
        border-radius: 14px; padding: 20px; text-align: center; margin-bottom: 15px;
        border: 2px solid #00ffcc; box-shadow: 0 6px 20px rgba(0, 255, 204, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)

# --- AUTHENTICATION FLOW MATRIX ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)
    
    # Facebook Style Tight Multi-Column Navigation Row
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        if st.button("🔑 LOGIN", key="set_login"):
            st.session_state.auth_mode = "Login"
            st.rerun()
    with col_l2:
        if st.button("📝 REGISTER", key="set_reg"):
            st.session_state.auth_mode = "Register"
            st.rerun()
    with col_l3:
        if st.button("🔄 RESET", key="set_forgot"):
            st.session_state.auth_mode = "Forgot"
            st.session_state.reset_step = 1
            st.rerun()

    st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    if st.session_state.auth_mode == "Login":
        st.markdown("<h5 style='color:#00ffcc; text-align:center; margin-bottom:12px;'>SECURE ENTRY GATEWAY</h5>", unsafe_allow_html=True)
        username = st.text_input("Username / Email:", placeholder="e.g. user@gmail.com", key="login_user")
        password = st.text_input("Password:", type="password", placeholder="••••••••", key="login_pass")
        
        if st.button("🚀 AUTHORIZE ACCESS", use_container_width=True, key="execute_login"):
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
                    else:
                        st.error("Invalid Username or Password Credentials.")

    elif st.session_state.auth_mode == "Register":
        st.markdown("<h5 style='color:#00ffcc; text-align:center; margin-bottom:12px;'>INITIALIZE REGISTRY NODE</h5>", unsafe_allow_html=True)
        reg_username = st.text_input("REGISTRATION EMAIL KEY:", placeholder="username or email", key="reg_user")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password", placeholder="••••••••", key="reg_pass")
        
        if st.button("💾 GENERATE VERIFICATION MATRIX", use_container_width=True, key="execute_reg"):
            if reg_username.strip() and reg_password.strip():
                existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                if existing: 
                    st.error("Identity keys collision: Already defined.")
                else:
                    st.session_state.temp_reg_user = reg_username.strip()
                    st.session_state.temp_reg_pass = reg_password.strip()
                    st.session_state.reg_verify_code = str(random.randint(222333, 999888))
                    st.session_state.auth_mode = "VerifyNewAccount"
                    st.rerun()
            else:
                st.error("Please fill all configuration nodes.")

    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown("<h5 style='color:#ff007f; text-align:center;'>🔒 SECURITY CORE VERIFICATION</h5>", unsafe_allow_html=True)
        st.info(f"Target Account: {st.session_state.temp_reg_user}")
        st.warning(f"🔧 Live Verification Code: {st.session_state.reg_verify_code}")
        
        typed_code = st.text_input("ENTER 6-DIGIT SYNC CODE:", placeholder="******", key="verify_code_input")
        
        if st.button("✔️ CONFIRM REGISTRATION", use_container_width=True, key="execute_verify"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                query_db("INSERT INTO users VALUES (?, ?, 0.00, 0.00, 'SVIP LEVEL 9', 'Y999')", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                st.success("Identity registration compiled completely!")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Code encryption mismatch.")

    elif st.session_state.auth_mode == "Forgot":
        st.markdown("<h5 style='color:#00ffcc;'>ACCESS KEY RECOVERY</h5>", unsafe_allow_html=True)
        
        if st.session_state.reset_step == 1:
            f_email = st.text_input("Enter Registered Email:", key="forgot_email")
            if st.button("🔍 VERIFY SYSTEM NODE", use_container_width=True, key="execute_forgot_1"):
                user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                if user_match:
                    st.session_state.reset_email = f_email.strip()
                    st.session_state.generated_code = str(random.randint(111111, 999999))
                    st.session_state.reset_step = 2
                    st.rerun()
                else: st.error("Identity mapping out of context records.")
                        
        elif st.session_state.reset_step == 2:
            st.info(f"🔒 Target Route Lock: {st.session_state.reset_email}")
            st.warning(f"Core Sync Code: {st.session_state.generated_code}")
            input_code = st.text_input("Enter 6-Digit Verification Pin:", key="forgot_code")
            new_pass = st.text_input("Define Replacement Password:", type="password", key="forgot_new_pass")
            
            if st.button("🛠️ RESET VAULT KEY", use_container_width=True, key="execute_forgot_2"):
                if input_code.strip() == st.session_state.generated_code:
                    if len(new_pass.strip()) >= 4:
                        query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                        st.success("Password structure recompiled clean.")
                        st.session_state.auth_mode = "Login"
                        st.session_state.reset_step = 1
                        st.rerun()
                    else: st.error("Length criteria violation.")
                else: st.error("Verification sequence failed.")

# --- DASHBOARD DECK ENGINE (LOGGED IN USER / ADMIN) ---
else:
    if st.session_state.is_admin:
        st.markdown("<h4 style='color:#00ffcc; text-align:center; font-weight:800;'>🛡️ MASTER ADMINISTRATION</h4>", unsafe_allow_html=True)
        
        # Compact Admin Ribbon Controls
        adm_col1, adm_col2, adm_col3 = st.columns(3)
        with adm_col1:
            if st.button("📥 DEPOSITS", key="btn_adm_dep"):
                st.session_state.selected_panel = "Pending Requests"
                st.rerun()
        with adm_col2:
            if st.button("🔗 TASK URL", key="btn_adm_url"):
                st.session_state.selected_panel = "Edit Task Redirects"
                st.rerun()
        with adm_col3:
            if st.button("🖼️ QR ASSET", key="btn_adm_qr"):
                st.session_state.selected_panel = "Edit QR Source"
                st.rerun()

        st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h5 style='color:#00ffcc; margin-bottom:8px;'>Inflow Ledger Verification Channels</h5>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items: st.info("Validation logs queue is clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#1c1836; padding:12px; border-radius:10px; border:1px solid #ff007f; margin-bottom:10px; font-size:13px;'>
                        <p style='margin:2px 0;'><b>User:</b> {item[1]} | <b>Bank:</b> {item[2]} ({item[3]})</p>
                        <p style='color:#ffcc00; margin:2px 0;'><b>Trx:</b> {item[4]}</p>
                        <h4 style='color:#00ffcc; margin:4px 0;'>RM {item[5]:.2f}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button(f"✅ APPROVE RM {item[5]:.2f}", key=f"app_{item[0]}", use_container_width=True):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with c_b2:
                        if st.button(f"❌ PURGE LOGS", key=f"rej_{item[0]}", use_container_width=True):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            st.markdown("<h5 style='color:#00ffcc; margin-bottom:8px;'>Configure Dynamic Ad Targets</h5>", unsafe_allow_html=True)
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            new_url = st.text_input("Active Redirection URL Target:", value=url_str, key="input_new_ad")
            if st.button("🔗 COMPILE REDIRECT PATHS", use_container_width=True, key="save_new_ad"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Redirection matrix updated.")
                
        elif st.session_state.selected_panel == "Edit QR Source":
            st.markdown("<h5 style='color:#00ffcc; margin-bottom:8px;'>Update Deposit QR Assets</h5>", unsafe_allow_html=True)
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            new_qr = st.text_input("URL Link of New QR Image Repository Source:", value=qr_str, key="input_new_qr")
            if st.button("🖼️ SYNCHRONIZE ACTIVE SCANNERS", use_container_width=True, key="save_new_qr"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Display gateway assets updated cleanly.")

    else:
        # --- USER ENGINE INTERFACE ---
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:11px; color:#a5a1c2; margin:0; letter-spacing:0.8px; font-weight:800;">MY EARNINGS WALLET BALANCE</p>
            <h2 style="font-size:30px; font-weight:900; color:#00ffcc; margin:2px 0;">RM {wallet_bal:,.2f}</h2>
            <p style="font-size:11px; color:#ffffff; margin:0; font-weight:600;">READY FOR CASHOUT TRANSFER: <span style='color:#ff007f;'>RM {liquid_bal:,.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)

        # 💎 COMPACT USER NAVIGATION SYSTEM (GRID MATRIX LIKE PROFESSIONAL PORTALS)
        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("🎰 OVERVIEW", key="btn_usr_ov"):
                st.session_state.selected_panel = "Overview"
                st.rerun()
        with usr_col2:
            if st.button("💰 DEPOSIT", key="btn_usr_dep"):
                st.session_state.selected_panel = "Deposit"
                st.rerun()
        with usr_col3:
            if st.button("🏛️ CASHOUT", key="btn_usr_cash"):
                st.session_state.selected_panel = "Cashout"
                st.rerun()

        st.markdown("<hr style='margin:10px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        # Dynamic Section Processing Blocks
        if st.session_state.selected_panel == "Overview":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color:#00ffcc; margin-top:0; margin-bottom:6px;'>Operational Metrics</h5>", unsafe_allow_html=True)
            st.write(f"Rank Node: **{level_tag}**")
            st.write(f"Reference Hash: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#141126; padding:14px; border-radius:10px; border: 1px solid #ff007f; margin-top:10px; text-align:center;'>
                <p style='margin:0 0 6px 0; color:#ffffff; font-size:13px; font-weight:bold;'>YOUTUBE REVENUE TASK STREAM</p>
                <a href='{target_video}' target='_blank' style='display:block; text-align:center; background: linear-gradient(135deg, #ff0055 0%, #7928ca 100%); color:#ffffff; padding:10px; text-decoration:none; font-weight:700; border-radius:8px; font-size:13px; text-transform:uppercase;'>▶️ LAUNCH VIDEO TASK</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color:#00ffcc; margin-top:0; margin-bottom:10px;'>TOUCH 'N GO SCAN MODULE</h5>", unsafe_allow_html=True)
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:12px;'><img src='{target_qr}' width='140' style='border:2px solid #ff007f; border-radius:10px; background:white; padding:4px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("BANKING INFLOW NODE:", MALAYSIAN_BANKS, key="dep_bank_select")
            remitter_name = st.text_input("ACCOUNT HOLDER FULL NAME:", key="dep_name_input")
            trx_id_input = st.text_input("TRANSACTION REFERENCE REF-ID / TRX:", key="dep_trx_input")
            amount_input = st.number_input("VALUATION AMOUNT (RM):", min_value=1.0, value=10.0, key="dep_amount_input")
            
            if st.button("EXECUTE SUBMISSION DISPATCH", use_container_width=True, key="submit_deposit_proof"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Evidence logs securely stacked into pending queue.")
                else: st.error("Please fill all input fields.")
            st.markdown("</div>", unsafe_allow_html=True)
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color:#ff007f; margin-top:0; margin-bottom:10px;'>INITIALIZE OUTBOUND SETTLEMENT</h5>", unsafe_allow_html=True)
            st.selectbox("Select Network Clearance Bank Node:", MALAYSIAN_BANKS[1:], key="cash_bank_select")
            st.text_input("Wire Index Account Number Key:", key="cash_acc_input")
            st.number_input("Target Request Dimensions (RM):", min_value=10.0, key="cash_amount_input")
            
            if st.button("🏛️ REQUEST OUTBOUND EXPULSION", use_container_width=True, key="submit_cashout_req"):
                st.error("Operation Halted: Registry balance configuration allocation mismatch.")
            st.markdown("</div>", unsafe_allow_html=True)

    # Clean Exit System Control Block
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 TERMINATE SESSION", key="global_logout_action", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

import streamlit as st
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORE APPLICATION CONFIGURATION ---
st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="📈", layout="wide")

# --- REAL SMTP BACKEND EMAIL GATEWAY CONFIGURATION (LIVE PARAMS INJECTED) ---
SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "lddf merstvil icby"  

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    """Sends a security token via secure TLS SMTP gateway with fallback handling."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = f"🛡️ MATRIX SECURITY CODE: {otp_code}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b091a; color: #ffffff; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background-color: #131021; border: 2px solid #ff007f; border-radius: 12px; padding: 20px; text-align: center;">
                <h2 style="color: #00ffcc;">GLOBAL MATRIX NETWORK</h2>
                <p style="font-size: 14px; color: #a5a1c2;">Secure Authentication & Node Synchronization Verification Token.</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <p style="font-size: 12px; text-transform: uppercase; color: #ff007f; font-weight: bold;">Action Required: {purpose}</p>
                <div style="font-size: 32px; font-weight: bold; color: #00ffcc; letter-spacing: 2px; margin: 20px 0; padding: 10px; background: rgba(0,255,204,0.1); border-radius: 8px;">
                    {otp_code}
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Secured Connection block
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Critical Error Core Setup: {str(e)}")
        return False

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

# --- MASTER ENGINE UI STYLING ENGINE ---
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

    .running-header-container {
        width: 100%; overflow: hidden; background: rgba(255, 0, 127, 0.08);
        border-bottom: 1px solid rgba(0, 255, 204, 0.3); padding: 8px 0; margin-bottom: 15px;
    }
    .running-text {
        font-size: 16px; font-weight: 800; color: #00ffcc; white-space: nowrap;
        display: inline-block; animation: marquee-run 12s linear infinite;
        text-shadow: 0 0 8px rgba(0, 255, 204, 0.6); letter-spacing: 1px;
    }
    @keyframes marquee-run {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }

    .brand-title {
        text-align: center; font-size: 24px; font-weight: 900; letter-spacing: 1.2px;
        background: linear-gradient(135deg, #ffffff 30%, #00ffcc 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 5px; margin-bottom: 15px; text-transform: uppercase;
    }

    [data-testid="stVerticalBlock"] {
        max-width: 460px !important;
        margin: 0 auto !important;
        padding: 5px !important;
    }

    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stWidgetLabel"] p {
        color: #00ffcc !important; font-weight: 700 !important; font-size: 11px !important; 
        text-transform: uppercase !important; margin-bottom: 2px !important;
    }
    
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #131021 !important; color: #ffffff !important;
        border: 2px solid #ff007f !important; border-radius: 10px !important; font-weight: 600 !important;
        padding: 6px 12px !important;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 100%) !important;
        color: #ffffff !important; font-size: 12px !important; font-weight: 700 !important;
        text-transform: uppercase !important; border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; width: 100% !important; 
        padding: 10px !important; margin: 4px 0 !important;
        box-shadow: 0 4px 12px rgba(255, 0, 127, 0.2) !important;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #00ffcc 0%, #00b09b 100%) !important;
        color: #000000 !important; 
        box-shadow: 0 4px 15px rgba(0, 255, 204, 0.4) !important;
    }

    .action-deck {
        background: rgba(20, 16, 36, 0.93); border: 2px solid #ff007f;
        border-radius: 12px; padding: 15px; margin-top: 10px;
    }

    .metric-card-box {
        background: linear-gradient(135deg, rgba(28, 23, 51, 0.95) 0%, rgba(15, 12, 31, 0.95) 100%);
        border-radius: 12px; padding: 18px; text-align: center; margin-bottom: 12px;
        border: 2px solid #00ffcc; box-shadow: 0 5px 15px rgba(0, 255, 204, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="rgb-moving-strip"></div>', unsafe_allow_html=True)
st.markdown('<div class="running-header-container"><div class="running-text">Online earnings Websites</div></div>', unsafe_allow_html=True)

# --- AUTHENTICATION FLOW ---
if not st.session_state.logged_in:
    st.markdown('<div class="brand-title">👑 GLOBAL MATRIX</div>', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "Login":
        st.markdown("<h6 style='color:#00ffcc; text-align:center; margin-bottom:8px;'>SECURE GATEWAY SIGN-IN</h6>", unsafe_allow_html=True)
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
                        st.error("Invalid Credentials.")

    elif st.session_state.auth_mode == "Register":
        st.markdown("<h6 style='color:#00ffcc; text-align:center; margin-bottom:8px;'>INITIALIZE SYSTEM NODE</h6>", unsafe_allow_html=True)
        reg_username = st.text_input("REGISTRATION EMAIL KEY:", placeholder="e.g. mail@domain.com", key="reg_user")
        reg_password = st.text_input("SYSTEM SECURITY CODE:", type="password", placeholder="••••••••", key="reg_pass")
        
        if st.button("💾 GENERATE VERIFICATION VIA EMAIL", use_container_width=True, key="execute_reg"):
            if reg_username.strip() and reg_password.strip():
                if "@" not in reg_username.strip() or "." not in reg_username.strip():
                    st.error("Please provide a valid structured email key.")
                else:
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing: 
                        st.error("Identity keys collision: Email already exists.")
                    else:
                        generated_otp = str(random.randint(102938, 984731))
                        with st.spinner("Dispatching Real Security Node OTP Key..."):
                            if send_verification_email(reg_username.strip(), generated_otp, purpose="Account Creation"):
                                st.session_state.temp_reg_user = reg_username.strip()
                                st.session_state.temp_reg_pass = reg_password.strip()
                                st.session_state.reg_verify_code = generated_otp
                                st.session_state.auth_mode = "VerifyNewAccount"
                                st.rerun()
                            else:
                                st.error("Email Gateway execution failed. Secure parameters configuration handshake timeout.")

    elif st.session_state.auth_mode == "VerifyNewAccount":
        st.markdown("<h6 style='color:#ff007f; text-align:center;'>🔒 EMAIL CODE SYNC-VERIFICATION</h6>", unsafe_allow_html=True)
        st.info(f"Target Registered Link: {st.session_state.temp_reg_user}")
        typed_code = st.text_input("ENTER 6-DIGIT SYNC OTP CODE:", placeholder="******", key="verify_code_input")
        
        if st.button("✔️ CONFIRM USER REGISTRATION", use_container_width=True, key="execute_verify"):
            if typed_code.strip() == st.session_state.reg_verify_code:
                query_db("INSERT INTO users VALUES (?, ?, 0.00, 0.00, 'SVIP LEVEL 9', 'Y999')", 
                         (st.session_state.temp_reg_user, st.session_state.temp_reg_pass), commit=True)
                st.success("Registration compiled completely!")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("Encryption code mismatch.")

    elif st.session_state.auth_mode == "Forgot":
        st.markdown("<h6 style='color:#00ffcc;'>ACCESS KEY RECOVERY PANEL</h6>", unsafe_allow_html=True)
        
        if st.session_state.reset_step == 1:
            f_email = st.text_input("Enter Registered Account Email:", key="forgot_email")
            if st.button("🔍 VERIFY & ROUTE RESET SYSTEM KEY", use_container_width=True, key="execute_forgot_1"):
                user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                if user_match:
                    generated_otp = str(random.randint(112233, 998877))
                    with st.spinner("Routing outbound security vector..."):
                        if send_verification_email(f_email.strip(), generated_otp, purpose="Password Reset Authorization"):
                            st.session_state.reset_email = f_email.strip()
                            st.session_state.generated_code = generated_otp
                            st.session_state.reset_step = 2
                            st.rerun()
                        else:
                            st.error("Failed to execute outbound routing. Network timeout.")
                else: 
                    st.error("No context records found matching identity key.")
                        
        elif st.session_state.reset_step == 2:
            st.info(f"🔒 Route Handshake Target: {st.session_state.reset_email}")
            input_code = st.text_input("Enter Real 6-Digit Email OTP:", key="forgot_code")
            new_pass = st.text_input("Establish New Secure Password:", type="password", key="forgot_new_pass")
            
            if st.button("🛠️ RESET IDENTITY VAULT", use_container_width=True, key="execute_forgot_2"):
                if input_code.strip() == st.session_state.generated_code:
                    if len(new_pass.strip()) >= 4:
                        query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                        st.success("Vault structure recompiled clear.")
                        st.session_state.auth_mode = "Login"
                        st.session_state.reset_step = 1
                        st.rerun()
                    else: st.error("Password too short.")
                else: st.error("Verification parameters mismatch.")

    st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3 = st.columns(3)
    with nav_col1:
        if st.button("🔑 LOGIN", key="set_login"):
            st.session_state.auth_mode = "Login"
            st.rerun()
    with nav_col2:
        if st.button("📝 JOIN", key="set_reg"):
            st.session_state.auth_mode = "Register"
            st.rerun()
    with nav_col3:
        if st.button("🔄 RESET", key="set_forgot"):
            st.session_state.auth_mode = "Forgot"
            st.session_state.reset_step = 1
            st.rerun()

# --- DASHBOARD (LOGGED IN SYSTEM ACCESS) ---
else:
    if st.session_state.is_admin:
        st.markdown("<h5 style='color:#00ffcc; text-align:center; font-weight:800;'>🛡️ MASTER ENGINE ADMIN</h5>", unsafe_allow_html=True)
        
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h6 style='color:#00ffcc; margin-bottom:6px;'>Inflow Verification Channels</h6>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items: st.info("Logs queue is clear.")
            else:
                for item in pending_items:
                    st.markdown(f"""
                    <div style='background-color:#1c1836; padding:10px; border-radius:8px; border:1px solid #ff007f; margin-bottom:8px; font-size:12px;'>
                        <p style='margin:2px 0;'><b>User:</b> {item[1]} | <b>Bank:</b> {item[2]}</p>
                        <p style='color:#ffcc00; margin:2px 0;'><b>Trx:</b> {item[4]}</p>
                        <h5 style='color:#00ffcc; margin:2px 0;'>RM {item[5]:.2f}</h5>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_b1, c_b2 = st.columns(2)
                    with c_b1:
                        if st.button(f"✅ APPROVE", key=f"app_{item[0]}", use_container_width=True):
                            query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                            query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                    with c_b2:
                        if st.button(f"❌ PURGE", key=f"rej_{item[0]}", use_container_width=True):
                            query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                            st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            new_url = st.text_input("Active Redirection Link:", value=url_str, key="input_new_ad")
            if st.button("🔗 UPDATE TARGET PATHS", use_container_width=True, key="save_new_ad"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("Target path updated.")
                
        elif st.session_state.selected_panel == "Edit QR Source":
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            new_qr = st.text_input("QR Repository Image Link:", value=qr_str, key="input_new_qr")
            if st.button("🖼️ SYNC SCANNERS", use_container_width=True, key="save_new_qr"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Assets synchronized.")

        st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        adm_col1, adm_col2, adm_col3 = st.columns(3)
        with adm_col1:
            if st.button("📥 LEDGER", key="btn_adm_dep"):
                st.session_state.selected_panel = "Pending Requests"
                st.rerun()
        with adm_col2:
            if st.button("🔗 LINKS", key="btn_adm_url"):
                st.session_state.selected_panel = "Edit Task Redirects"
                st.rerun()
        with adm_col3:
            if st.button("🖼️ SCANNERS", key="btn_adm_qr"):
                st.session_state.selected_panel = "Edit QR Source"
                st.rerun()

    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (0.00, 0.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="metric-card-box">
            <p style="font-size:10px; color:#a5a1c2; margin:0; font-weight:800;">WALLETS EARNINGS BALANCE</p>
            <h3 style="font-size:26px; font-weight:900; color:#00ffcc; margin:2px 0;">RM {wallet_bal:,.2f}</h3>
            <p style="font-size:10px; color:#ffffff; margin:0; font-weight:600;">READY TO CASHOUT: <span style='color:#ff007f;'>RM {liquid_bal:,.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.selected_panel == "Overview":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#00ffcc; margin:0 0 4px 0;'>Allocation Info</h6>", unsafe_allow_html=True)
            st.write(f"Rank Matrix Node: **{level_tag}**")
            st.write(f"Invitation Code: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#141126; padding:12px; border-radius:10px; border: 1px solid #ff007f; margin-top:8px; text-align:center;'>
                <p style='margin:0 0 6px 0; color:#ffffff; font-size:12px; font-weight:bold;'>YOUTUBE DATA TASK TUNNEL</p>
                <a href='{target_video}' target='_blank' style='display:block; text-align:center; background: linear-gradient(135deg, #ff0055 0%, #7928ca 100%); color:#ffffff; padding:10px; text-decoration:none; font-weight:700; border-radius:6px; font-size:12px; text-transform:uppercase;'>▶️ START DATA WORK</a>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#00ffcc; margin:0 0 8px 0;'>TOUCH 'N GO HUB PAYMENT</h6>", unsafe_allow_html=True)
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:10px;'><img src='{target_qr}' width='130' style='border:2px solid #ff007f; border-radius:8px; background:white; padding:3px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("CHOOSE SYSTEM NODE BANK:", MALAYSIAN_BANKS, key="dep_bank_select")
            remitter_name = st.text_input("ACCOUNT OWNER NAME:", key="dep_name_input")
            trx_id_input = st.text_input("REFERENCE TXN / TRX CODE:", key="dep_trx_input")
            amount_input = st.number_input("VALUATION AMOUNT (RM):", min_value=1.0, value=10.0, key="dep_amount_input")
            
            if st.button("SUBMIT PROOF RECORD", use_container_width=True, key="submit_deposit_proof"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Proof logs queued for admin confirmation.")
                else: st.error("Please fill all input nodes.")
            st.markdown("</div>", unsafe_allow_html=True)
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<div class='action-deck'>", unsafe_allow_html=True)
            st.markdown("<h6 style='color:#ff007f; margin:0 0 8px 0;'>INITIALIZE OUTBOUND SETTLEMENT</h6>", unsafe_allow_html=True)
            st.selectbox("Select Clearance Bank:", MALAYSIAN_BANKS[1:], key="cash_bank_select")
            st.text_input("Destination Wire Account Keys:", key="cash_acc_input")
            st.number_input("Amount Selection (RM):", min_value=10.0, key="cash_amount_input")
            
            if st.button("🏛️ EXECUTE OUTBOUND CASH OUT", use_container_width=True, key="submit_cashout_req"):
                st.error("Operation Halted: Configuration imbalance detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin:12px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        usr_col1, usr_col2, usr_col3 = st.columns(3)
        with usr_col1:
            if st.button("🎰 HOME", key="btn_usr_ov"):
                st.session_state.selected_panel = "Overview"
                st.rerun()
        with usr_col2:
            if st.button("💰 DEPOSIT", key="btn_usr_dep"):
                st.session_state.selected_panel = "Deposit"
                st.rerun()
        with usr_col3:
            if st.button("🏛️ WITHDRAW", key="btn_usr_cash"):
                st.session_state.selected_panel = "Cashout"
                st.rerun()

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 LOG OUT PORTAL", key="global_logout_action", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

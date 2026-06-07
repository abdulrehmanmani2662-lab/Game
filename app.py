import streamlit as st
import sqlite3
import random

# App core configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="🎰", layout="wide")

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad"
]

# --- DATABASE LAYER ---
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

# Session Tracking States
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Dashboard Hub"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1
if 'generated_code' not in st.session_state: st.session_state.generated_code = ""
if 'reset_email' not in st.session_state: st.session_state.reset_email = ""

# --- PREMIUM CLEAN LUXURY DARK CSS (WITH CUSTOM BACKGROUND IMAGE) ---
st.markdown("""
    <style>
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Background Image Integration with Clean Overlay Cover */
    .stApp {
        background-image: linear-gradient(rgba(11, 9, 26, 0.88), rgba(11, 9, 26, 0.93)), 
                          url("https://images.unsplash.com/photo-1542362567-b07eac79094d?q=80&w=1470&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }
    
    /* Clean Solid Card Box (No Blinding Neon Glares) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(23, 20, 46, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 30px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        backdrop-filter: blur(8px) !important;
    }
    
    /* Inputs Labels Setup - Sharp & High Contrast */
    label, p, span, li, [data-testid="stMarkdownContainer"] p {
        color: #e0e0e3 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px;
        text-shadow: none !important;
    }
    
    /* Clean Input Fields - Sharp Text Color */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background-color: #ffffff !important;
        color: #111116 !important;
        -webkit-text-fill-color: #111116 !important;
        border: 1px solid #4a4765 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 15px !important;
    }
    
    /* Elegant Solid Buttons Layout (No text-shadow overlaps) */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        width: 100% !important;
        text-transform: uppercase !important;
        box-shadow: 0px 4px 12px rgba(16, 185, 129, 0.2) !important;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: #10b981 !important;
        transform: translateY(-1px);
        box-shadow: 0px 6px 15px rgba(16, 185, 129, 0.3) !important;
    }

    .stat-card {
        background: rgba(30, 27, 57, 0.9);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def switch_panel(panel_name):
    st.session_state.selected_panel = panel_name
    st.rerun()

# --- AUTHENTICATION INTERFACE MODULE ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#ffffff; font-weight:800; letter-spacing:1px;'>👑 GLOBAL MATRIX INVESTMENT</h2>", unsafe_allow_html=True)
    
    # Custom Toggle tabs for clean interface view
    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("🔑 Account Login"): st.session_state.auth_mode = "Login"
    with t2:
        if st.button("📝 Create Account"): st.session_state.auth_mode = "Register"
    with t3:
        if st.button("🔄 Forgot Password?"): 
            st.session_state.auth_mode = "Forgot"
            st.session_state.reset_step = 1

    st.write("")

    with st.container():
        # --- LOGIN INTERFACE ---
        if st.session_state.auth_mode == "Login":
            st.markdown("<h3 style='color:#10b981; margin-top:0;'>Account Login Hub</h3>", unsafe_allow_html=True)
            username = st.text_input("Registered Account Email / Username:", placeholder="e.g. user@gmail.com")
            password = st.text_input("System Security Password:", type="password", placeholder="••••••••")
            
            if st.button("Authorize Secure Access"):
                if username.strip() == "admin":
                    record = query_db("SELECT password, username FROM users WHERE username=?", ("admin",), one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = "admin"
                        st.session_state.is_admin = True
                        st.session_state.selected_panel = "Admin Hub"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
                elif username.strip():
                    record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Dashboard Hub"
                        st.rerun()
                    else:
                        st.error("Credentials pairing failed database matching.")
                        
        # --- REGISTER INTERFACE ---
        elif st.session_state.auth_mode == "Register":
            st.markdown("<h3 style='color:#10b981; margin-top:0;'>Create Profile Account</h3>", unsafe_allow_html=True)
            reg_username = st.text_input("Enter Email Address Asset Registry:", placeholder="name@domain.com")
            reg_password = st.text_input("Create Secure System Password:", type="password", placeholder="Minimum 6 characters")
            
            if st.button("Register Terminal Node"):
                if reg_username.strip() and reg_password.strip():
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing:
                        st.error("This email identifier is already active inside database records.")
                    else:
                        query_db("INSERT INTO users VALUES (?, ?, 10.00, 7.00, 'SVIP LEVEL 9', 'Y999')", 
                                 (reg_username.strip(), reg_password.strip()), commit=True)
                        st.success("Registration success allocation logged! Please head over to Login.")
                else:
                    st.error("Please fill out all missing registration parameters.")

        # --- CLEAN FORGOT PASSWORD PIPELINE ---
        elif st.session_state.auth_mode == "Forgot":
            st.markdown("<h3 style='color:#10b981; margin-top:0;'>System Access Key Recovery</h3>", unsafe_allow_html=True)
            
            if st.session_state.reset_step == 1:
                f_email = st.text_input("Enter Your Registered Account Email:", placeholder="user@gmail.com")
                if st.button("Generate Secure Recovery Pin"):
                    user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                    if user_match:
                        st.session_state.reset_email = f_email.strip()
                        st.session_state.generated_code = str(random.randint(100000, 999999))
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error("This email node does not exist in our active registry accounts.")
                        
            elif st.session_state.reset_step == 2:
                st.info(f"🔑 System Verification Test Code triggered for {st.session_state.reset_email}")
                st.warning(f"Development Mode Code: {st.session_state.generated_code}")
                
                input_code = st.text_input("Enter 6-Digit Verification Pin:", placeholder="xxxxxx")
                new_pass = st.text_input("Configure New Security Password:", type="password", placeholder="••••••••")
                
                if st.button("Confirm Reset Token Verification"):
                    if input_code.strip() == st.session_state.generated_code:
                        if len(new_pass.strip()) >= 4:
                            query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                            st.success("Security access password altered successfully. Redirecting to login.")
                            st.session_state.auth_mode = "Login"
                            st.session_state.reset_step = 1
                            st.rerun()
                        else:
                            st.error("Password string too short. Please provide a secure pairing.")
                    else:
                        st.error("Verification secure pin code matching mismatch.")

else:
    # --- ADMIN ROUTE CONTROL NODES ---
    if st.session_state.is_admin:
        st.markdown("<h2 style='color:#10b981; text-align:center; font-weight:700;'>⚙️ SYSTEM MASTER CONTROLLER PANEL</h2>", unsafe_allow_html=True)
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            if st.button("📥 Pending Settlements"): switch_panel("Admin Hub")
        with m_col2:
            if st.button("🔗 Modify Task Link"): switch_panel("Edit Tasks Link")
        with m_col3:
            if st.button("🖼️ Replace QR Link"): switch_panel("Edit QR System")
        with m_col4:
            if st.button("🚪 Terminate Session"):
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
                        <div style='background:rgba(30, 27, 57, 0.9); padding:15px; border-radius:8px; border-left:5px solid #10b981; margin-bottom:10px;'>
                            <p style='color:#ffffff !important; margin:0;'><b>User Node ID:</b> {item[1]}</p>
                            <p style='color:#10b981 !important; margin:0;'><b>Bank Route:</b> {item[2]} | <b>Holder:</b> {item[3]}</p>
                            <p style='color:#fbbf24 !important; margin:0;'><b>Trx Reference Ref:</b> {item[4]}</p>
                            <h4 style='color:#ffffff; margin:5px 0 0 0;'>Amount Claimed: RM {item[5]:.2f}</h4>
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
                            if st.button(f"❌ Reject Request", key=f"rej_{item[0]}"):
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
            if st.button("Deploy New Terminal QR Link"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("System QR display reference frame updated.")

    # --- CLIENT USER WORKSPACE HUB ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.00, 7.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:13px; color:#10b981; font-weight:bold; letter-spacing:1px;">DOMPET PEROLEHAN SAYA (MAIN WALLET)</div>
            <div style="font-size:38px; font-weight:900; color:#ffffff; margin:6px 0;">RM {wallet_bal:,.2f}</div>
            <div style="font-size:13px; color:#a1a1aa;">READY FOR CASHOUT TRANSFER MODULE: <span style='color:#10b981; font-weight:bold;'>RM {liquid_bal:,.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
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
            <div style='background:rgba(20, 17, 43, 0.9); padding:20px; border:1px solid rgba(16, 185, 129, 0.3); border-radius:10px;'>
                <h4 style='margin:0 0 5px 0; color:#ffffff;'>Video Stream Engine Task Ready</h4>
                <p style='font-size:14px; color:#a1a1aa !important;'>Watch live tasks allocations to unlock active cloud framework rewards.</p>
                <a href='{target_video}' target='_blank' style='display:inline-block; background:#10b981; color:#ffffff; padding:10px 22px; text-decoration:none; font-weight:bold; border-radius:6px; margin-top:5px;'>▶️ Open Task Stream Hub</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Add Balance Funds":
            st.markdown("### SUBMIT PAYMENT INFLOW VERIFICATION PROOF")
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><img src='{target_qr}' width='190' style='border:2px solid #10b981; border-radius:12px;'/></div>", unsafe_allow_html=True)
            
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
                    st.error("Please fill out complete remitter registration fields.")
                    
        elif st.session_state.selected_panel == "Settlement Outflow":
            st.markdown("### BANK CASHOUT LIQUIDATION SETTLEMENT")
            st.selectbox("Select Target Account Receiving Node:", MALAYSIAN_BANKS[1:])
            st.text_input("Target Account Number Wire Registry:")
            st.number_input("Volume Liquidation Target (RM):", min_value=10.0)
            if st.button("AUTHORIZE CASHOUT PROCESS GATEWAY"):
                st.error("Transaction security block: Main verification framework parameters out of scale.")

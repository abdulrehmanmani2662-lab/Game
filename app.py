import streamlit as st
import sqlite3
import random

# Core Framework Setup
st.set_page_config(page_title="Investment Portal", page_icon="🏦", layout="wide")

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

# --- ANTI-REFRESH LOGOUT PERSISTENCE ENGINE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1

# --- FACEBOOK INSPIRED CLEAN DARK BUSINESS THEME (NO FICTION GLOW) ---
st.markdown("""
    <style>
    /* Hide Default Elements completely */
    footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Facebook Premium Clean Corporate Dark Background */
    html, body, .stApp { 
        background-color: #18191a !important;
        color: #e4e6eb !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Clean Profile Containers Like FB Feed Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #242526 !important;
        border: 1px solid #3a3b3c !important;
        border-radius: 8px !important;
        padding: 25px !important;
        box-shadow: 0 12px 28px 0 rgba(0, 0, 0, 0.2), 0 2px 4px 0 rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Inputs Titles - Perfect Visibility */
    label, p, span, li, [data-testid="stMarkdownContainer"] p {
        color: #e4e6eb !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        text-shadow: none !important;
        text-transform: none !important;
        letter-spacing: normal !important;
    }
    
    /* Pure Solid Input Fields (Facebook Dark Style) */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] div {
        background-color: #3a3b3c !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid #4e4f50 !important;
        border-radius: 6px !important;
        font-size: 16px !important;
        padding: 10px !important;
    }
    
    div[data-testid="stTextInput"] input:focus {
        border-color: #1877f2 !important;
    }
    
    /* Facebook Solid Action Buttons Layout */
    div[data-testid="stButton"] > button {
        background-color: #1877f2 !important; /* Facebook Blue */
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 20px !important;
        width: 100% !important;
        transition: background-color 0.2s color 0.2s;
        text-transform: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background-color: #166fe5 !important;
        color: #ffffff !important;
    }

    /* Secondary Grey Buttons for Navigation */
    .nav-box div[data-testid="stButton"] > button {
        background-color: #4e4f50 !important;
        color: #ffffff !important;
    }
    .nav-box div[data-testid="stButton"] > button:hover {
        background-color: #606263 !important;
    }

    /* Balanced Cards */
    .account-balance-card {
        background-color: #242526;
        border: 1px solid #3a3b3c;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def switch_panel(panel_name):
    st.session_state.selected_panel = panel_name
    st.rerun()

# --- GATEWAY MANAGEMENT RENDER LAYER ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center; color:#1877f2; font-weight:bold; font-size:36px; margin-bottom:10px;'>facebook</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#b0b3b8; font-size:18px; margin-bottom:20px;'>Connect with the global network matrix vault system securely.</p>", unsafe_allow_html=True)
    
    with st.container():
        if st.session_state.auth_mode == "Login":
            username = st.text_input("Email address or phone number", placeholder="Enter your identity key")
            password = st.text_input("Password", type="password", placeholder="Password")
            
            if st.button("Log In"):
                if username.strip() == "admin":
                    record = query_db("SELECT password FROM users WHERE username='admin'", one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = "admin"
                        st.session_state.is_admin = True
                        st.session_state.selected_panel = "Pending Requests"
                        st.rerun()
                    else:
                        st.error("The password you've entered is incorrect.")
                elif username.strip():
                    record = query_db("SELECT password, username FROM users WHERE username=?", (username.strip(),), one=True)
                    if record and record[0] == password.strip():
                        st.session_state.logged_in = True
                        st.session_state.current_user = record[1]
                        st.session_state.is_admin = False
                        st.session_state.selected_panel = "Overview"
                        st.rerun()
                    else:
                        st.error("The account username or password pair does not match.")
            
            st.markdown("<hr style='border-color:#3a3b3c;'/>", unsafe_allow_html=True)
            
            col_forgot, col_new = st.columns(2)
            with col_forgot:
                if st.button("Forgot password?", key="btn_go_forgot"):
                    st.session_state.auth_mode = "Forgot"
                    st.session_state.reset_step = 1
                    st.rerun()
            with col_new:
                if st.button("Create new account", key="btn_go_reg"):
                    st.session_state.auth_mode = "Register"
                    st.rerun()

        elif st.session_state.auth_mode == "Register":
            st.markdown("<h3 style='color:#ffffff; font-weight:bold; margin-top:0;'>Sign Up Profile</h3>", unsafe_allow_html=True)
            reg_username = st.text_input("Mobile number or email address")
            reg_password = st.text_input("New password", type="password")
            
            if st.button("Sign Up"):
                if reg_username.strip() and reg_password.strip():
                    existing = query_db("SELECT username FROM users WHERE username=?", (reg_username.strip(),), one=True)
                    if existing:
                        st.error("An account with this email identifier already exists.")
                    else:
                        query_db("INSERT INTO users VALUES (?, ?, 10.00, 7.00, 'SVIP LEVEL 9', 'Y999')", 
                                 (reg_username.strip(), reg_password.strip()), commit=True)
                        st.success("Account profile successfully initiated!")
                        st.session_state.auth_mode = "Login"
                        st.rerun()
            
            if st.button("Already have an account?"):
                st.session_state.auth_mode = "Login"
                st.rerun()

        elif st.session_state.auth_mode == "Forgot":
            st.markdown("<h3 style='color:#ffffff; font-weight:bold; margin-top:0;'>Find Your Account</h3>", unsafe_allow_html=True)
            
            if st.session_state.reset_step == 1:
                f_email = st.text_input("Please enter your email address to search for your account:")
                if st.button("Search Account Node"):
                    user_match = query_db("SELECT username FROM users WHERE username=?", (f_email.strip(),), one=True)
                    if user_match:
                        st.session_state.reset_email = f_email.strip()
                        st.session_state.generated_code = str(random.randint(111111, 999999))
                        st.session_state.reset_step = 2
                        st.rerun()
                    else:
                        st.error("No account match found inside current structural records.")
                        
                if st.button("Cancel"):
                    st.session_state.auth_mode = "Login"
                    st.rerun()
                        
            elif st.session_state.reset_step == 2:
                st.info(f"🔒 Security authorization confirmation token triggered for: {st.session_state.reset_email}")
                st.warning(f"Verification Check Code: {st.session_state.generated_code}")
                
                input_code = st.text_input("Enter the 6-digit confirmation security code:")
                new_pass = st.text_input("Choose a new secure password:", type="password")
                
                if st.button("Change Password"):
                    if input_code.strip() == st.session_state.generated_code:
                        if len(new_pass.strip()) >= 4:
                            query_db("UPDATE users SET password=? WHERE username=?", (new_pass.strip(), st.session_state.reset_email), commit=True)
                            st.success("Your password has been successfully configured.")
                            st.session_state.auth_mode = "Login"
                            st.session_state.reset_step = 1
                            st.rerun()
                        else:
                            st.error("Password string sequence must be longer.")
                    else:
                        st.error("The security pin code entered does not match registration assets.")

# --- APPLICATION WORKSPACE ENGINE ---
else:
    # --- ADMIN VIEWPORT ROUTING ---
    if st.session_state.is_admin:
        st.markdown("<h3 style='color:#ffffff; font-weight:bold;'>Admin Control Centre</h3>", unsafe_allow_html=True)
        
        # Clean Flat Admin Navigation Header Rows
        st.markdown('<div class="nav-box">', unsafe_allow_html=True)
        adm_col1, adm_col2, adm_col3, adm_col4 = st.columns(4)
        with adm_col1:
            if st.button("📥 Deposits Pipeline"): switch_panel("Pending Requests")
        with adm_col2:
            if st.button("🔗 Modify Task Link"): switch_panel("Edit Task Redirects")
        with adm_col3:
            if st.button("🖼️ Change TNG QR Link"): switch_panel("Edit QR Source")
        with adm_col4:
            if st.button("🚪 Log Out"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")
        
        # FULL SCREEN DEDICATED ADMIN ACTIONS
        if st.session_state.selected_panel == "Pending Requests":
            st.markdown("<h4>Pending Deposit Requests Queue</h4>", unsafe_allow_html=True)
            pending_items = query_db("SELECT id, username, bank, name, trx_id, amount FROM deposits WHERE status='Pending'")
            
            if not pending_items:
                st.info("No system verification payloads are currently awaiting execution pipelines.")
            else:
                for item in pending_items:
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color:#3a3b3c; padding:15px; border-radius:6px; margin-bottom:12px;'>
                            <p style='margin:2px 0;'><b>Account Profile User:</b> {item[1]}</p>
                            <p style='margin:2px 0;'><b>Method Target Node:</b> {item[2]} ({item[3]})</p>
                            <p style='margin:2px 0; color:#fbbf24 !important;'><b>Reference Trx Ref ID:</b> {item[4]}</p>
                            <h4 style='color:#1877f2; margin:5px 0 0 0;'>Allocation Scale Volume: RM {item[5]:.2f}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.button(f"Approve RM {item[5]:.2f}", key=f"adm_app_{item[0]}"):
                                query_db("UPDATE users SET balance = balance + ? WHERE username=?", (item[5], item[1]), commit=True)
                                query_db("UPDATE deposits SET status='Approved' WHERE id=?", (item[0],), commit=True)
                                st.success("Deposit processed successfully!")
                                st.rerun()
                        with btn_c2:
                            if st.button(f"Reject Payload Transaction", key=f"adm_rej_{item[0]}"):
                                query_db("UPDATE deposits SET status='Rejected' WHERE id=?", (item[0],), commit=True)
                                st.error("Request payload dropped out safely.")
                                st.rerun()
                                
        elif st.session_state.selected_panel == "Edit Task Redirects":
            st.markdown("<h4>Configure Revenue Stream Ad Target Link</h4>", unsafe_allow_html=True)
            current_ad_url = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            url_str = current_ad_url[0] if current_ad_url else ""
            
            new_url = st.text_input("Configure System Redirection URL Location:", value=url_str)
            if st.button("Update Target Address URL"):
                query_db("UPDATE system_config SET value=? WHERE key='live_ad_url'", (new_url.strip(),), commit=True)
                st.success("System configurations deployed safely.")
                
        elif st.session_state.selected_panel == "Edit QR Source":
            st.markdown("<h4>Update System Touch 'n Go Terminal Asset Image</h4>", unsafe_allow_html=True)
            current_qr_url = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            qr_str = current_qr_url[0] if current_qr_url else ""
            
            new_qr = st.text_input("Direct URL Link of New QR Image Node:", value=qr_str)
            if st.button("Update QR Terminal Target"):
                query_db("UPDATE system_config SET value=? WHERE key='tng_scanner_url'", (new_qr.strip(),), commit=True)
                st.success("Target payment scanner terminal links synchronized.")

    # --- CLIENT USER VIEWPORT ROUTING ---
    else:
        user_metrics = query_db("SELECT balance, liquidation, active_level, ref_code FROM users WHERE username=?", (st.session_state.current_user,), one=True)
        wallet_bal, liquid_bal, level_tag, reference_hash = user_metrics if user_metrics else (10.00, 7.00, "SVIP LEVEL 9", "Y999")
        
        st.markdown(f"""
        <div class="account-balance-card">
            <p style="font-size:14px; color:#b0b3b8; margin:0;">MAIN ACCOUNT PORTFOLIO NET WORTH</p>
            <h1 style="font-size:42px; font-weight:bold; color:#ffffff; margin:8px 0;">RM {wallet_bal:,.2f}</h1>
            <p style="font-size:14px; color:#1877f2; margin:0; font-weight:bold;">LIQUID CLEARING ALLOWANCE: RM {liquid_bal:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User Flat Navigation Grid Bar
        st.markdown('<div class="nav-box">', unsafe_allow_html=True)
        u_col1, u_col2, u_col3, u_col4 = st.columns(4)
        with u_col1:
            if st.button("📊 Overview"): switch_panel("Overview")
        with u_col2:
            if st.button("💰 Add Funds"): switch_panel("Deposit")
        with u_col3:
            if st.button("🏛️ Cashout"): switch_panel("Cashout")
        with u_col4:
            if st.button("🚪 Log Out"): 
                st.session_state.logged_in = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")
        
        # PURE FULL SCREEN VIEW SELECTION
        if st.session_state.selected_panel == "Overview":
            st.markdown("<h4>Profile System Metrics Overview</h4>", unsafe_allow_html=True)
            st.write(f"Verification Infrastructure Ranking Node: **{level_tag}**")
            st.write(f"Master Registration Affiliate Reference Code: **{reference_hash}**")
            
            ad_link_data = query_db("SELECT value FROM system_config WHERE key='live_ad_url'", one=True)
            target_video = ad_link_data[0] if ad_link_data else "#"
            
            st.markdown(f"""
            <div style='background-color:#3a3b3c; padding:20px; border-radius:6px; margin-top:15px;'>
                <h4 style='margin:0 0 5px 0; color:#ffffff;'>Dynamic Ad Video Revenue Task Stream Matrix</h4>
                <p style='font-size:14px; color:#b0b3b8 !important; margin-bottom:12px;'>Interact with structural streaming nodes to claim automated system payouts instantly.</p>
                <a href='{target_video}' target='_blank' style='display:inline-block; background-color:#1877f2; color:#ffffff; padding:12px 24px; text-decoration:none; font-weight:bold; border-radius:6px;'>▶️ Launch Active Task Window</a>
            </div>
            """, unsafe_allow_html=True)
            
        elif st.session_state.selected_panel == "Deposit":
            st.markdown("<h4>Submit Deposit Verification Form Stack</h4>", unsafe_allow_html=True)
            
            qr_link_data = query_db("SELECT value FROM system_config WHERE key='tng_scanner_url'", one=True)
            target_qr = qr_link_data[0] if qr_link_data else ""
            
            if target_qr:
                st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><img src='{target_qr}' width='180' style='border:1px solid #3a3b3c; border-radius:8px;'/></div>", unsafe_allow_html=True)
            
            chosen_bank = st.selectbox("Destination Settlement Network Node:", MALAYSIAN_BANKS)
            remitter_name = st.text_input("Sender / Remitter Account Name Strings:")
            trx_id_input = st.text_input("Transaction Unique Identification Code (Trx Ref ID):")
            amount_input = st.number_input("Transaction Volume Valuation Scale (RM):", min_value=1.0, value=10.0)
            
            if st.button("Submit Verified Payment Slip Proof"):
                if remitter_name.strip() and trx_id_input.strip():
                    query_db("INSERT INTO deposits (username, bank, name, trx_id, amount, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                             (st.session_state.current_user, chosen_bank, remitter_name.strip(), trx_id_input.strip(), amount_input), commit=True)
                    st.success("Verification payload updated successfully in admin settlement logs dashboard.")
                else:
                    st.error("All payment details forms must be fully specified.")
                    
        elif st.session_state.selected_panel == "Cashout":
            st.markdown("<h4>Configure Financial Liquidation Protocols</h4>", unsafe_allow_html=True)
            st.selectbox("Select Target Registry Network Bank:", MALAYSIAN_BANKS[1:])
            st.text_input("Enter Target Bank Account Number Node:")
            st.number_input("Target Liquidation Outflow Scale (RM):", min_value=10.0)
            if st.button("Authorize Liquidation Dispatch Channel"):
                st.error("System security configuration threshold error: Profile limits out of framework metric alignment.")

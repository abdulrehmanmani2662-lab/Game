import streamlit as st
import time
import requests

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- PREMIUM APP & ADMIN VIEW STYLESHEET ---
st.markdown("""
    <style>
    /* Hide all native Streamlit bars for absolute mobile app feel */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #0d1117 !important; }
    .main .block-container { 
        padding-top: 10px !important; 
        padding-bottom: 90px !important; 
        max-width: 430px !important;
        margin: 0 auto;
    }
    /* Bold Bold Typography for Global Language Readability */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Arial Black', Gadget, sans-serif !important;
    }
    .app-title-bar {
        text-align: center; font-weight: 900; font-size: 24px; color: #f59e0b;
        padding: 12px; margin-bottom: 15px; border-bottom: 2px solid #21262d;
        letter-spacing: 1px;
    }
    .balance-box {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 22px; border-radius: 14px; border: 2px solid #30363d;
        margin-bottom: 18px; text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.4);
    }
    .admin-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 20px; border-radius: 12px; border: 3px solid #6366f1;
        margin-bottom: 20px;
    }
    .section-label {
        font-size: 18px; font-weight: 900; color: #ffffff;
        margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #f59e0b; padding-left: 10px;
        letter-spacing: 0.5px;
    }
    .level-container {
        background: #161b22; border: 2px solid #30363d; border-radius: 12px;
        padding: 15px; margin-bottom: 12px;
    }
    .qr-holder {
        text-align: center; background: white; padding: 15px; border-radius: 16px;
        margin: 15px auto; width: fit-content; box-shadow: 0 6px 20px rgba(0,0,0,0.6);
    }
    /* Stylized Big Buttons */
    .stButton>button {
        font-weight: 900 !important;
        font-size: 16px !important;
        border-radius: 10px !important;
        padding: 10px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Fake Database in Session State
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "salmanveerm@gmail.com": {"balance": 0.00, "referred_by": "ubaid_rajput"},
        "ubaid_rajput": {"balance": 50.00, "referred_by": ""},
        "billa_bhai": {"balance": 10.00, "referred_by": "salmanveerm@gmail.com"}
    }
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

st.markdown('<div class="app-title-bar">📈 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# --- LOGIN GATEWAY (PURE ENGLISH) ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='text-align:center; color:#fff; font-weight:900;'>SECURE MEMBER LOGIN</h4>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("📱 EMAIL ADDRESS / PHONE NUMBER", value="salmanveerm@gmail.com")
        password = st.text_input("🔒 PASSWORD", type="password", placeholder="ENTER PASSWORD")
        
        if st.form_submit_button("🚀 SIGN IN TO ACCOUNT", use_container_width=True):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.current_user = "ADMIN_PANEL"
                st.rerun()
            elif username in st.session_state.users_db:
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.session_state.current_user = username
                st.rerun()
            else:
                st.session_state.users_db[username] = {"balance": 0.00, "referred_by": "ubaid_rajput"}
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.session_state.current_user = username
                st.rerun()

# --- IF LOGGED IN AS MASTER ADMIN ---
elif st.session_state.is_admin:
    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#6366f1; text-align:center; margin:0; font-weight:900;'>👑 MASTER ADMIN CONTROL DASHBOARD</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e; font-size:12px; font-weight:bold;'>SYSTEM MANAGEMENT CONTROL ROOM</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Active Users Registry
    st.markdown('<div class="section-label">👥 REGISTERED NETWORK MEMBERS PANEL</div>', unsafe_allow_html=True)
    for u, data in st.session_state.users_db.items():
        st.text(f"USER ID: {u} | WALLET: RM {data['balance']:.2f} | INVITER: {data['referred_by']}")
        
    # Manual Override Control Adjustment Core
    st.markdown('<div class="section-label">✏ ADJUST MEMBER BALANCE MANUALLY</div>', unsafe_allow_html=True)
    target_user = st.selectbox("SELECT MEMBER ACCOUNT:", list(st.session_state.users_db.keys()))
    new_bal = st.number_input("ENTER NEW BALANCE VALUE (RM):", min_value=0.0, value=float(st.session_state.users_db[target_user]["balance"]))
    
    if st.button("💾 SAVE AND UPDATE WALLET", use_container_width=True):
        st.session_state.users_db[target_user]["balance"] = new_bal
        st.success(f"SUCCESS: {target_user} account value modified to RM {new_bal:.2f}")
        time.sleep(1)
        st.rerun()

    if st.button("🚪 LOGOUT FROM ADMIN CONTROL PANEL", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- IF LOGGED IN AS REGULAR NETWORK USER (PURE ENGLISH & BOLD) ---
else:
    current_user = st.session_state.current_user
    user_data = st.session_state.users_db[current_user]
    
    # Total Balance Display Card Panel
    st.markdown(f"""
    <div class="balance-box">
        <span style="color:#8b949e; font-size:12px; font-weight:bold;">ACCOUNT ID: {current_user}</span><br>
        <span style="color:#c9d1d9; font-size:16px; font-weight:bold;">AVAILABLE BALANCE</span><br>
        <span style="font-size:36px; font-weight:900; color:#ffffff;">RM {user_data['balance']:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- SECTION 1: FINANCIAL OPERATION ACTION GATEWAY ---
    col_dep, col_wdr = st.columns(2)
    with col_dep:
        show_deposit = st.button("📥 RECHARGE / DEPOSIT", use_container_width=True)
    with col_wdr:
        show_withdraw = st.button("📤 WITHDRAW FUNDS", use_container_width=True)

    # Deposit Workflow Mechanism Logic Loop
    if show_deposit:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color:#10b981; font-weight:900;'>MOCK PAYMENT ACTION (FOR SYSTEM TESTING)</h5>", unsafe_allow_html=True)
        test_dep_amount = st.radio("SELECT DEPOSIT SLIP PLAN VALUE:", [50, 200])
        
        if st.button("🔥 TRANSMIT PAYMENT RECEIPT PROOF"):
            st.session_state.users_db[current_user]["balance"] += test_dep_amount
            
            # Referral Bonus Distribution Logic Engine Execution
            inviter = user_data["referred_by"]
            if inviter in st.session_state.users_db:
                if test_dep_amount == 200:
                    st.session_state.users_db[inviter]["balance"] += 100.00
                    st.toast(f"REFERRAL BONUS TRIGGERED: RM 100 CREDITED TO YOUR INVITER {inviter}", icon="🎁")
                elif test_dep_amount == 50:
                    st.session_state.users_db[inviter]["balance"] += 50.00
                    st.toast(f"REFERRAL BONUS TRIGGERED: RM 50 CREDITED TO YOUR INVITER {inviter}", icon="🎁")
                    
            st.success(f"SUCCESS: System credited RM {test_dep_amount} to your storage core.")
            time.sleep(1)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Withdrawal Operations Request Gate (Threshold Guard Fix: RM 700)
    if show_withdraw:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        w_amt = st.number_input("ENTER WITHDRAWAL AMOUNT (RM):", min_value=10, value=700)
        if st.button("💸 DISPATCH WITHDRAWAL ORDER"):
            if w_amt < 700:
                st.error("❌ ERROR: MINIMUM ALLOWED WITHDRAWAL LIMIT THRESHOLD IS STRICTLY RM 700")
            elif user_data["balance"] < w_amt:
                st.error("❌ ERROR: INSUFFICIENT ACCOUNT BALANCE LIQUIDITY FOR DISPATCH")
            else:
                st.session_state.users_db[current_user]["balance"] -= w_amt
                st.success(f"🚀 SUCCESS: Withdrawal order of RM {w_amt} successfully dispatched!")
                time.sleep(1)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- SECTION 2: VIP SCHEME MATRIX PLANS NODES ---
    st.markdown('<div class="section-label">💎 AVAILABLE INVESTMENT TIER MODULES</div>', unsafe_allow_html=True)
    
    levels = [
        {"name": "VIP LEVEL 1", "cost": 50, "daily": 15},
        {"name": "VIP LEVEL 2", "cost": 200, "daily": 60},
        {"name": "VIP LEVEL 3", "cost": 500, "daily": 180}
    ]
    
    for idx, lvl in enumerate(levels):
        st.markdown(f"""
        <div class="level-container">
            <b style="color:#ffffff; font-size:16px;">{lvl['name']}</b><br>
            <span style="color:#8b949e; font-size:13px; font-weight:bold;">DAILY PROFIT: RM {lvl['daily']:.2f} | ACTIVATION PRICE: RM {lvl['cost']}</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"⚡ PURCHASE & UNLOCK {lvl['name']}", key=f"lvl_{idx}", use_container_width=True):
            if user_data["balance"] >= lvl['cost']:
                st.session_state.users_db[current_user]["balance"] -= lvl['cost']
                st.success(f"🎉 CELEBRATION: {lvl['name']} node successfully activated!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ DENIED: Cost is RM {lvl['cost']}. Please recharge or request admin override.")

    # --- SECTION 3: ALWAYS DEPLOYED TOUCH 'N GO GATEWAY CODE BLOCK ---
    st.markdown('<div class="section-label">📲 OFFICIAL TOUCH \'N GO DIGITAL PORTAL</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px; color:#8b949e; font-weight:bold;'>SCAN THE SYSTEM SCANNER BELOW DIRECTLY FOR MERCHANDISE PAYMENTS:</p>", unsafe_allow_html=True)
    
    st.markdown(
        f'<div class="qr-holder">'
        f'<img src="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" width="240" style="display:block; margin:0 auto; border-radius:10px;">'
        f'<br><a href="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" target="_blank" style="color:#58a6ff; font-size:13px; font-weight:bold; text-decoration:none;">🔗 EXPAND TO FULL SCREEN QR</a>'
        f'</div>', 
        unsafe_allow_html=True
    )

    # --- SECTION 4: NATIVE INTERACTIVE NAVIGATION TASK BAR ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="border-top: 2px solid #21262d; padding-top:10px;"></div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("🏠 SYSTEM HOME", key="b_nav_h", use_container_width=True):
            st.rerun()
    with col_b2:
        if st.button("📊 RUN TASK (+5)", key="b_nav_t", use_container_width=True):
            st.session_state.users_db[current_user]["balance"] += 5.00
            st.success("TASK VALUE EARNED: +RM 5.00 ADDED")
            time.sleep(0.5)
            st.rerun()
    with col_b3:
        if st.button("🚪 LOGOUT APP", key="b_nav_l", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()

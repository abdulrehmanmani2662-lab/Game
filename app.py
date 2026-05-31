import streamlit as st
import time
import requests

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- ULTRA PREMIUM GAMING LOOK & NEXT-LEVEL FONTS STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..0,900;1,100..0,900&family=Poppins:ital,wght@0,100..0,900;1,100..0,900&display=swap" rel="stylesheet">
    
    <style>
    /* Hide all native Streamlit trash UI components */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    .stApp { background-color: #060913 !important; }
    
    .main .block-container { 
        padding-top: 15px !important; 
        padding-bottom: 100px !important; 
        max-width: 440px !important;
        margin: 0 auto;
    }
    
    /* Ultimate Bold Font Layout Engine */
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Montserrat', 'Poppins', sans-serif !important;
        font-weight: 900 !important;
    }
    
    /* Glowing Neon Title Bar */
    .app-title-bar {
        text-align: center; 
        font-size: 26px; 
        color: #fff;
        text-shadow: 0 0 10px #f59e0b, 0 0 20px #f59e0b;
        padding: 15px 10px; 
        margin-bottom: 20px; 
        border-bottom: 2px solid #1e293b;
        letter-spacing: 1.5px;
    }
    
    /* Premium Crypto Wallet Box */
    .balance-box {
        background: linear-gradient(145deg, #111827 0%, #030712 100%);
        padding: 25px; 
        border-radius: 18px; 
        border: 2px solid #f59e0b;
        margin-bottom: 20px; 
        text-align: center;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Section Headers */
    .section-label {
        font-size: 19px; 
        color: #f59e0b;
        margin-top: 25px; 
        margin-bottom: 12px; 
        border-left: 6px solid #f59e0b; 
        padding-left: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Bold VIP Tier Containers */
    .level-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        border: 2px solid #334155; 
        border-radius: 15px;
        padding: 18px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    /* Fixed Embedded Image Box */
    .qr-holder-clean {
        text-align: center; 
        background: #ffffff; 
        padding: 15px; 
        border-radius: 20px;
        margin: 15px auto; 
        width: 90%; 
        box-shadow: 0 0 25px rgba(255,255,255,0.2);
    }
    
    /* High-End App Action Buttons */
    .stButton>button {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        border-radius: 12px !important;
        padding: 12px 0 !important;
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important;
        color: #000000 !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session Core Database
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

# --- LOGIN HUB ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='text-align:center; color:#fff; letter-spacing:1px;'>SECURE GATEWAY LOGIN</h4>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("📱 ACCOUNT EMAIL / PHONE ID", value="salmanveerm@gmail.com")
        password = st.text_input("🔒 SECURE ACCESS PASSWORD", type="password", placeholder="••••••••")
        
        if st.form_submit_button("🚀 UNLOCK ACCOUNT PORTAL", use_container_width=True):
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

# --- ADMIN PANEL LAYER ---
elif st.session_state.is_admin:
    st.markdown("<h3 style='color:#f59e0b; text-align:center;'>👑 CENTRAL CONTROL DOCK</h3>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-label">👥 REAL-TIME MEMBERS</div>', unsafe_allow_html=True)
    for u, data in st.session_state.users_db.items():
        st.text(f"NODE: {u} | WALLET: RM {data['balance']:.2f}")
        
    st.markdown('<div class="section-label">✏ INSTANT OVERRIDE BALANCE</div>', unsafe_allow_html=True)
    target_user = st.selectbox("CHOOSE USER NODE:", list(st.session_state.users_db.keys()))
    new_bal = st.number_input("SET ABSOLUTE LIQUIDITY VALUE (RM):", min_value=0.0, value=float(st.session_state.users_db[target_user]["balance"]))
    
    if st.button("💾 OVERRIDE & CREDIT BALANCE", use_container_width=True):
        st.session_state.users_db[target_user]["balance"] = new_bal
        st.success(f"UPDATED: {target_user} is now set to RM {new_bal:.2f}")
        time.sleep(1)
        st.rerun()

    if st.button("🚪 LEAVE CONTROL DOCK", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

# --- USER INTERFACE DESIGN CORE ---
else:
    current_user = st.session_state.current_user
    user_data = st.session_state.users_db[current_user]
    
    # Financial Analytics Box Panel
    st.markdown(f"""
    <div class="balance-box">
        <div style="color:#8b949e; font-size:12px; letter-spacing:1px; margin-bottom:5px;">USER CLUSTER NODE ID: {current_user}</div>
        <div style="color:#e2e8f0; font-size:16px; letter-spacing:0.5px;">TOTAL AVAILABLE WALLET LIQUIDITY</div>
        <div style="font-size:38px; color:#ffffff; margin-top:5px; text-shadow: 0 0 8px rgba(255,255,255,0.2);">RM {user_data['balance']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- ACTION GRID TRIGGER ROUTERS ---
    col_dep, col_wdr = st.columns(2)
    with col_dep:
        show_deposit = st.button("📥 DEPOSIT SLIP", use_container_width=True)
    with col_wdr:
        show_withdraw = st.button("📤 WITHDRAW", use_container_width=True)

    # Deposit Engine Simulation Block
    if show_deposit:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color:#f59e0b;'>SIMULATE NETWORK DEPOSIT APPROVAL</h5>", unsafe_allow_html=True)
        test_dep_amount = st.radio("CHOOSE INSTANT TRANSFER PLAN VALUE:", [50, 200])
        
        if st.button("🔥 SEND VERIFICATION RECEIPT"):
            st.session_state.users_db[current_user]["balance"] += test_dep_amount
            
            # Smart Automated Multi-Tier Referral Payout Router
            inviter = user_data["referred_by"]
            if inviter in st.session_state.users_db:
                if test_dep_amount == 200:
                    st.session_state.users_db[inviter]["balance"] += 100.00
                    st.toast(f"REFERRAL REWARD: RM 100 CREDITED TO {inviter}", icon="🎁")
                elif test_dep_amount == 50:
                    st.session_state.users_db[inviter]["balance"] += 50.00
                    st.toast(f"REFERRAL REWARD: RM 50 CREDITED TO {inviter}", icon="🎁")
                    
            st.success(f"SUCCESS: Account dynamically updated with RM {test_dep_amount}")
            time.sleep(1)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Withdrawal Logic Guard Engine (Hard-coded Threshold: RM 700)
    if show_withdraw:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        w_amt = st.number_input("ENTER TARGET VOLUME LIQUIDATION AMOUNT (RM):", min_value=10, value=700)
        if st.button("💸 CONFIRM IMMEDIATE PAYOUT REQUEST"):
            if w_amt < 700:
                st.error("❌ REGULATION ERROR: MINIMUM LIQUIDATION LIMIT IS FIXED AT RM 700")
            elif user_data["balance"] < w_amt:
                st.error("❌ LEDGER ERROR: INSUBSTANTIAL CAPITAL BALANCES DETECTED")
            else:
                st.session_state.users_db[current_user]["balance"] -= w_amt
                st.success(f"🚀 SUBMITTED: Order of RM {w_amt} transmitted to settlement matrix cluster.")
                time.sleep(1)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- INVESTMENT SCHEMES TIER NODES ---
    st.markdown('<div class="section-label">💎 ACCOUNT ACTIVE VIP PLANS</div>', unsafe_allow_html=True)
    
    levels = [
        {"name": "VIP SCHEME NODE 1", "cost": 50, "daily": 15},
        {"name": "VIP SCHEME NODE 2", "cost": 200, "daily": 60},
        {"name": "VIP SCHEME NODE 3", "cost": 500, "daily": 180}
    ]
    
    for idx, lvl in enumerate(levels):
        st.markdown(f"""
        <div class="level-container">
            <div style="font-size:17px; color:#ffffff; margin-bottom:4px;">{lvl['name']}</div>
            <div style="color:#94a3b8; font-size:13px;">DAILY REWARD RETRO: <span style="color:#10b981;">RM {lvl['daily']:.2f}</span></div>
            <div style="color:#94a3b8; font-size:13px;">ACTIVATION CAPITAL QUANTITY: <span style="color:#f59e0b;">RM {lvl['cost']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"⚡ UNLOCK {lvl['name']}", key=f"lvl_{idx}", use_container_width=True):
            if user_data["balance"] >= lvl['cost']:
                st.session_state.users_db[current_user]["balance"] -= lvl['cost']
                st.success(f"🎉 VALIDATED: {lvl['name']} sequence successfully unlocked!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ REJECTED: Insufficient funds. Minimum recharge value needed: RM {lvl['cost']}")

    # --- TOUCH 'N GO GATEWAY FIXED RENDERING FRAME ---
    st.markdown('<div class="section-label">📲 TOUCH \'N GO MERCHANT SYSTEM</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size:12px; color:#94a3b8;'>SCAN THE SECURITY SECURE BOX TO DEPOSIT CAPITAL ASSETS:</p>", unsafe_allow_html=True)
    
    # Secure iframe sandbox rendering to bypass standard browser asset processing filters
    st.markdown(
        f'<div class="qr-holder-clean">'
        f'<iframe src="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" width="100%" height="320" style="border:none; border-radius:10px; overflow:hidden;" scrolling="no"></iframe>'
        f'<br><a href="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" target="_blank" style="color:#1d4ed8; font-size:13px; text-decoration:none;">🔗 IF NOT LOADING CLICK TO MANUAL REDIRECT</a>'
        f'</div>', 
        unsafe_allow_html=True
    )

    # --- NATIVE NAVIGATION BAR APP CORE FOOTER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="border-top: 1px solid #1e293b; padding-top:12px;"></div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("🏠 REFRESH HOME", key="b_nav_h", use_container_width=True):
            st.rerun()
    with col_b2:
        if st.button("📊 CLAIM TASK (+5)", key="b_nav_t", use_container_width=True):
            st.session_state.users_db[current_user]["balance"] += 5.00
            st.toast("REWARD CLAIMED: +RM 5.00 INSTANTLY APPLIED", icon="💰")
            time.sleep(0.5)
            st.rerun()
    with col_b3:
        if st.button("🚪 LOGOUT SECURE", key="b_nav_l", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.rerun()

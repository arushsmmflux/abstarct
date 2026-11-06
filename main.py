import os
import logging
import sqlite3
import io
import random
import string
from datetime import datetime
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaVideo,
    InputMediaPhoto
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import qrcode

load_dotenv()

# ==========================================
# CONFIGURATION & ENVIRONMENT
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_RAW.split(",") if x.strip().isdigit()]

DB_FILE = "bot_database.db"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# DATABASE SETUP & HELPERS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            original_price REAL,
            caption TEXT,
            join_link TEXT,
            is_active INTEGER DEFAULT 1,
            slot_index INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id TEXT,
            file_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            plan_id TEXT,
            price REAL,
            file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT,
            approved_at TEXT
        )
    """)
    
    # Initialize default configurations if not present
    defaults = {
        "upi_id": "merchant@upi",
        "payee_name": "Digital Store",
        "qr_file_id": "",
        "start_message": (
            "✨ <b>WELCOME TO OUR DIGITAL STORE</b> ✨\n\n"
            "🔥 Discover high-quality verified digital packs and masterclasses.\n"
            "🚀 Instant delivery upon manual verification by our support team.\n"
            "💎 100% trusted community with daily proofs.\n\n"
            "👇 <b>Select a plan below to get started:</b>"
        ),
        "how_to_use": (
            "📖 <b>HOW TO PURCHASE</b>\n\n"
            "<b>Step 1:</b> Select your preferred plan from the main menu.\n"
            "<b>Step 2:</b> Click on <b>CONFIRM</b>.\n"
            "<b>Step 3:</b> Scan the QR code and pay the exact amount.\n"
            "<b>Step 4:</b> Click <b>VERIFY</b>.\n"
            "<b>Step 5:</b> Send your payment screenshot.\n"
            "<b>Step 6:</b> Wait for admin approval (5-10 mins)."
        ),
        "success_message": "🎉 <b>Congratulations! Your payment has been approved.</b>\n\nClick the button below to join your channel/group! 🚀",
        "rejection_message": "❌ <b>Your payment submission was rejected.</b>\nPlease check your screenshot or contact support.",
        "proof_url": "https://t.me/fluxproofs",
        "support_url": "https://t.me/fluxsupport"
    }
    
    for k, v in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (k, v))
        
    # Initialize 11 default plan slots if empty
    cursor.execute("SELECT COUNT(*) FROM plans")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 12):
            cursor.execute(
                "INSERT INTO plans (plan_id, name, price, original_price, caption, join_link, is_active, slot_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (f"plan_{i}", f"Digital Pack {i}", 49.0 * i, 99.0 * i, f"Exclusive content pack #{i} with lifetime updates.", "https://t.me/+examplelink", 1, i)
            )
            
    conn.commit()
    conn.close()

def get_config(key):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def set_config(key, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# ==========================================
# USER & CLIENT HANDLERS
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
        (user.id, user.username, user.first_name, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    start_msg = get_config("start_message")
    
    cursor = sqlite3.connect(DB_FILE).cursor()
    cursor.execute("SELECT plan_id, name, price FROM plans WHERE is_active=1 ORDER BY slot_index ASC")
    active_plans = cursor.fetchall()
    conn.close()

    keyboard = []
    for plan_id, name, price in active_plans:
        keyboard.append([InlineKeyboardButton(f"🟢 {name} - ₹{price}", callback_data=f"plan_{plan_id}")])
    
    keyboard.append([
        InlineKeyboardButton("📚 HOW TO USE", callback_data="how_to_use"),
        InlineKeyboardButton("🔴 PROOFS", url=get_config("proof_url"))
    ])
    keyboard.append([InlineKeyboardButton("📞 SUPPORT", url=get_config("support_url"))])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=user.id,
            text=start_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            start_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

async def how_to_use_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = get_config("how_to_use")
    keyboard = [[InlineKeyboardButton("🔵 BACK", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")

async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def plan_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.replace("plan_", "")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, original_price, caption FROM plans WHERE plan_id=?", (plan_id,))
    plan = cursor.fetchone()
    
    cursor.execute("SELECT file_id FROM demos WHERE plan_id=?", (plan_id,))
    demos = cursor.fetchall()
    conn.close()
    
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    name, price, orig_price, caption = plan
    
    try:
        await query.message.delete()
    except Exception:
        pass

    # Send demo videos with spoiler if available
    if demos:
        media_group = []
        for idx, (file_id,) in enumerate(demos[:10]): # Telegram supports up to 10 media in group
            media_group.append(InputMediaVideo(
                media=file_id,
                has_spoiler=True,
                caption=f"🎥 Demo Preview {idx+1}" if idx == 0 else ""
            ))
        try:
            await context.bot.send_media_group(chat_id=update.effective_user.id, media=media_group)
        except Exception as e:
            logger.error(f"Failed to send media group: {e}")

    detail_text = (
        f"📦 <b>Plan:</b> {name}\n"
        f"💰 <b>Price:</b> ̶₹̶{orig_price} ₹{price} 🔥\n\n"
        f"<b>Description:</b>\n{caption}"
    )
    
    keyboard = [
        [InlineKeyboardButton("🟢 CONFIRM", callback_data=f"confirm_{plan_id}")],
        [InlineKeyboardButton("🔴 CANCEL", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=detail_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def confirm_purchase_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = query.data.replace("confirm_", "")
    user_id = update.effective_user.id
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM plans WHERE plan_id=?", (plan_id,))
    plan = cursor.fetchone()
    conn.close()
    
    if not plan:
        await query.answer("Plan not found.", show_alert=True)
        return

    name, price = plan
    order_id = generate_order_id()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (order_id, user_id, plan_id, price, status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
        (order_id, user_id, plan_id, price, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()
    
    upi_id = get_config("upi_id")
    payee = get_config("payee_name")
    
    upi_uri = f"upi://pay?pa={upi_id}&pn={payee}&am={price}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(upi_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = io.BytesIO()
    bio.name = "qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    
    payment_caption = (
        f"💳 <b>PAYMENT PAGE</b>\n\n"
        f"📦 <b>Plan:</b> {name}\n"
        f"💰 <b>Amount:</b> ₹{price}\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>\n"
        f"📌 <b>UPI ID:</b> <code>{upi_id}</code>\n\n"
        "<b>Steps:</b>\n"
        "1️⃣ Scan QR & pay exact amount.\n"
        "2️⃣ Click <b>VERIFY</b> below.\n"
        "3️⃣ Send screenshot."
    )
    
    keyboard = [
        [InlineKeyboardButton("🟢 VERIFY", callback_data=f"verify_{order_id}")],
        [InlineKeyboardButton("🔴 CANCEL PURCHASE", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.delete()
    await context.bot.send_photo(
        chat_id=user_id,
        photo=bio,
        caption=payment_caption,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def verify_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = query.data.replace("verify_", "")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT plan_id, price FROM orders WHERE order_id=?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if not order:
        await query.answer("Order not found.", show_alert=True)
        return
        
    plan_id, price = order
    context.user_data["awaiting_screenshot_order"] = order_id
    
    keyboard = [[InlineKeyboardButton("🔴 CANCEL PURCHASE", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_caption(
        caption=(
            f"📸 <b>PLEASE UPLOAD PAYMENT SCREENSHOT</b>\n\n"
            f"🆔 Order ID: <code>{order_id}</code>\n"
            f"💰 Amount: ₹{price}\n\n"
            "Send your payment receipt screenshot as an image now."
        ),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if "awaiting_screenshot_order" not in context.user_data:
        return

    if not update.message.photo:
        await update.message.reply_text("⚠️ Please send a valid photo screenshot.")
        return

    order_id = context.user_data.pop("awaiting_screenshot_order")
    photo_file = update.message.photo[-1]
    file_id = photo_file.file_id
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET file_id=? WHERE order_id=?", (file_id, order_id))
    cursor.execute("SELECT plan_id, price, created_at FROM orders WHERE order_id=?", (order_id,))
    order_info = cursor.fetchone()
    
    cursor.execute("SELECT name FROM plans WHERE plan_id=?", (order_info[0],))
    plan_name = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    price = order_info[1]
    created_at = order_info[2]
    
    await update.message.reply_text("✅ <b>Screenshot received successfully!</b>\nOur admins are reviewing your payment. Please wait 5-10 minutes.", parse_mode="HTML")
    
    admin_caption = (
        "📥 <b>NEW PAYMENT SUBMISSION</b>\n\n"
        f"📦 Plan: {plan_name}\n"
        f"💰 Amount: ₹{price}\n"
        f"🆔 Order ID: <code>{order_id}</code>\n"
        f"👤 User: {user.first_name} (@{user.username if user.username else 'N/A'})\n"
        f"🆔 User ID: <code>{user.id}</code>\n"
        f"⏰ Time: {created_at}"
    )
    admin_keyboard = [
        [
            InlineKeyboardButton("🟢 APPROVE", callback_data=f"adm_app_{order_id}"),
            InlineKeyboardButton("🔴 REJECT", callback_data=f"adm_rej_{order_id}")
        ]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=admin_caption,
                reply_markup=admin_markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")

# ==========================================
# ADMIN ORDER & APPROVAL MANAGEMENT
# ==========================================
async def admin_approve_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    if not is_admin(admin_id):
        await query.answer("Unauthorized.", show_alert=True)
        return

    order_id = query.data.replace("adm_app_", "")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, plan_id, price, status FROM orders WHERE order_id=?", (order_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        await query.answer("Order not found.", show_alert=True)
        return
        
    user_id, plan_id, price, status = row
    if status != 'pending':
        conn.close()
        await query.answer(f"Order already processed ({status}).", show_alert=True)
        return
        
    cursor.execute("UPDATE orders SET status='approved', approved_at=? WHERE order_id=?", (datetime.utcnow().isoformat(), order_id))
    cursor.execute("SELECT name, caption, join_link FROM plans WHERE plan_id=?", (plan_id,))
    plan_info = cursor.fetchone()
    conn.commit()
    conn.close()
    
    plan_name, caption, join_link = plan_info
    
    await query.answer("Payment Approved!")
    await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: APPROVED ✅</b>", parse_mode="HTML")
    
    # Notify user with join button
    success_text = (
        f"{get_config('success_message')}\n\n"
        f"📦 <b>Plan:</b> {plan_name}\n"
        f"💰 <b>Paid:</b> ₹{price}\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>\n\n"
        f"<b>Details:</b>\n{caption}"
    )
    user_keyboard = [[InlineKeyboardButton("🚀 JOIN NOW", url=join_link)]]
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=success_text,
            reply_markup=InlineKeyboardMarkup(user_keyboard),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    # Broadcast success to all active users
    broadcast_text = (
        "🎉 <b>Someone Just Purchased a New Pack!</b>\n\n"
        f"📦 <b>Plan:</b> {plan_name}\n"
        f"💰 <b>Amount:</b> ₹{price}\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>"
    )
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    all_users = cursor.fetchall()
    conn.close()
    
    for (uid,) in all_users:
        try:
            await context.bot.send_message(chat_id=uid, text=broadcast_text, parse_mode="HTML")
        except Exception:
            pass

async def admin_reject_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    admin_id = update.effective_user.id
    if not is_admin(admin_id):
        await query.answer("Unauthorized.", show_alert=True)
        return

    order_id = query.data.replace("adm_rej_", "")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, status FROM orders WHERE order_id=?", (order_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        await query.answer("Order not found.", show_alert=True)
        return
        
    user_id, status = row
    if status != 'pending':
        conn.close()
        await query.answer(f"Order already processed ({status}).", show_alert=True)
        return
        
    cursor.execute("UPDATE orders SET status='rejected' WHERE order_id=?", (order_id,))
    conn.commit()
    conn.close()
    
    await query.answer("Payment Rejected.")
    await query.edit_message_caption(caption=query.message.caption + "\n\n<b>STATUS: REJECTED ❌</b>", parse_mode="HTML")
    
    try:
        await context.bot.send_message(chat_id=user_id, text=get_config("rejection_message"), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

# ==========================================
# COMPREHENSIVE ADMIN PANEL (/admin)
# ==========================================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Unauthorized.")
        return

    keyboard = [
        [InlineKeyboardButton("📦 Manage Plans", callback_data="adm_plans")],
        [InlineKeyboardButton("🎬 Manage Demos", callback_data="adm_demos")],
        [InlineKeyboardButton("💳 Payment Settings", callback_data="adm_pay_settings")],
        [InlineKeyboardButton("💬 Message Settings", callback_data="adm_msg_settings")],
        [InlineKeyboardButton("📊 Statistics & Orders", callback_data="adm_stats")],
        [InlineKeyboardButton("📢 Send Broadcast", callback_data="adm_broadcast")]
    ]
    await update.message.reply_text(
        "🛠 <b>ADMIN CONTROL PANEL</b> 🛠\n\nChoose a category to manage:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def admin_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.answer("Unauthorized.", show_alert=True)
        return

    data = query.data
    if data == "adm_main":
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("📦 Manage Plans", callback_data="adm_plans")],
            [InlineKeyboardButton("🎬 Manage Demos", callback_data="adm_demos")],
            [InlineKeyboardButton("💳 Payment Settings", callback_data="adm_pay_settings")],
            [InlineKeyboardButton("💬 Message Settings", callback_data="adm_msg_settings")],
            [InlineKeyboardButton("📊 Statistics & Orders", callback_data="adm_stats")],
            [InlineKeyboardButton("📢 Send Broadcast", callback_data="adm_broadcast")]
        ]
        await query.message.edit_text("🛠 <b>ADMIN CONTROL PANEL</b> 🛠\n\nChoose a category to manage:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "adm_plans":
        await query.answer()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT plan_id, name, price, is_active FROM plans ORDER BY slot_index ASC")
        plans = cursor.fetchall()
        conn.close()

        keyboard = []
        for pid, name, price, active in plans:
            status = "🟢" if active == 1 else "🔴"
            keyboard.append([InlineKeyboardButton(f"{status} {name} (₹{price})", callback_data=f"adm_editplan_{pid}")])
        keyboard.append([InlineKeyboardButton("🔵 Back to Admin", callback_data="adm_main")])
        
        await query.message.edit_text("📦 <b>Manage Plans</b>\nSelect a plan to edit:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data.startswith("adm_editplan_"):
        await query.answer()
        plan_id = data.replace("adm_editplan_", "")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, price, original_price, caption, join_link, is_active FROM plans WHERE plan_id=?", (plan_id,))
        p = cursor.fetchone()
        conn.close()

        name, price, orig_price, caption, link, active = p
        context.user_data["editing_plan"] = plan_id

        text = (
            f"📦 <b>Editing Plan: {name}</b>\n\n"
            f"💰 Price: ₹{price} (Orig: ₹{orig_price})\n"
            f"🔗 Link: {link}\n"
            f"⚡ Active: {'Yes' if active==1 else 'No'}\n\n"
            f"Caption:\n{caption}\n\n"
            "Send new details using command format:\n"
            "<code>/setplanname Name</code>\n"
            "<code>/setplanprice Price OrigPrice</code>\n"
            "<code>/setplánlink https://...</code>\n"
            "<code>/setplancaption Your caption...</code>"
        )
        keyboard = [
            [InlineKeyboardButton("🔄 Toggle Active Status", callback_data=f"adm_toggle_{plan_id}")],
            [InlineKeyboardButton("🔙 Back to Plans", callback_data="adm_plans")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data.startswith("adm_toggle_"):
        plan_id = data.replace("adm_toggle_", "")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM plans WHERE plan_id=?", (plan_id,))
        current = cursor.fetchone()[0]
        new_val = 0 if current == 1 else 1
        cursor.execute("UPDATE plans SET is_active=? WHERE plan_id=?", (new_val, plan_id))
        conn.commit()
        conn.close()
        await query.answer(f"Plan status updated to {'Active' if new_val==1 else 'Inactive'}")
        # Refresh view
        query.data = f"adm_editplan_{plan_id}"
        await admin_callback_router(update, context)

    elif data == "adm_demos":
        await query.answer()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT plan_id, name FROM plans ORDER BY slot_index ASC")
        plans = cursor.fetchall()
        conn.close()

        keyboard = []
        for pid, name in plans:
            keyboard.append([InlineKeyboardButton(f"🎬 Demos for {name}", callback_data=f"adm_demolist_{pid}")])
        keyboard.append([InlineKeyboardButton("🔵 Back to Admin", callback_data="adm_main")])
        await query.message.edit_text("🎬 <b>Manage Demos</b>\nSelect a plan to manage demo videos:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data.startswith("adm_demolist_"):
        await query.answer()
        plan_id = data.replace("adm_demolist_", "")
        context.user_data["managing_demos_plan"] = plan_id
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_id FROM demos WHERE plan_id=?", (plan_id,))
        demos = cursor.fetchall()
        conn.close()

        text = f"🎬 <b>Demos for {plan_id}</b>\nCurrent Demos: {len(demos)}\n\nTo add a demo, simply forward or send a video file to this chat while managing this plan."
        keyboard = []
        for did, fid in demos:
            keyboard.append([InlineKeyboardButton(f"❌ Remove Demo #{did}", callback_data=f"adm_deldemo_{did}_{plan_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Back to Demos", callback_data="adm_demos")])
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data.startswith("adm_deldemo_"):
        parts = data.replace("adm_deldemo_", "").split("_")
        did, plan_id = parts[0], parts[1]
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM demos WHERE id=?", (did,))
        conn.commit()
        conn.close()
        await query.answer("Demo removed successfully!")
        query.data = f"adm_demolist_{plan_id}"
        await admin_callback_router(update, context)

    elif data == "adm_pay_settings":
        await query.answer()
        upi = get_config("upi_id")
        payee = get_config("payee_name")
        text = (
            "💳 <b>Payment Settings</b>\n\n"
            f"Current UPI ID: <code>{upi}</code>\n"
            f"Payee Name: {payee}\n\n"
            "To update UPI, use command:\n"
            "<code>/setupi newupi@handle Payee Name</code>"
        )
        keyboard = [[InlineKeyboardButton("🔵 Back to Admin", callback_data="adm_main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "adm_msg_settings":
        await query.answer()
        text = (
            "💬 <b>Message Settings</b>\n\n"
            "To update messages, use:\n"
            "<code>/setstartmessage Your message...</code>\n"
            "<code>/sethowtousemessage Your message...</code>\n"
            "<code>/setsuccessmessage Your message...</code>\n"
            "<code>/setrejectionmessage Your message...</code>"
        )
        keyboard = [[InlineKeyboardButton("🔵 Back to Admin", callback_data="adm_main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "adm_stats":
        await query.answer()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status='pending'")
        pending_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status='approved'")
        approved_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status='rejected'")
        rejected_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(price) FROM orders WHERE status='approved'")
        revenue = cursor.fetchone()[0] or 0.0
        conn.close()

        stats_text = (
            "📊 <b>BOT STATISTICS & ORDERS</b> 📊\n\n"
            f"👥 Total Users: {total_users}\n"
            f"📦 Total Orders: {total_orders}\n"
            f"⏳ Pending Orders: {pending_orders}\n"
            f"✅ Approved Orders: {approved_orders}\n"
            f"❌ Rejected Orders: {rejected_orders}\n"
            f"💵 Total Approved Revenue: ₹{revenue}"
        )
        keyboard = [[InlineKeyboardButton("🔵 Back to Admin", callback_data="adm_main")]]
        await query.message.edit_text(stats_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "adm_broadcast":
        await query.answer()
        context.user_data["awaiting_broadcast"] = True
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="adm_main")]]
        await query.message.edit_text("📢 <b>Broadcast Mode</b>\n\nSend the message (text, photo, or video) you want to broadcast to all registered users.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# Handle incoming media for demos or broadcast
async def admin_media_or_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    # Check for demo video upload
    if "managing_demos_plan" in context.user_data and update.message.video:
        plan_id = context.user_data["managing_demos_plan"]
        file_id = update.message.video.file_id
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO demos (plan_id, file_id) VALUES (?, ?)", (plan_id, file_id))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ Demo video has been saved successfully!")
        return

    # Check for broadcast
    if context.user_data.get("awaiting_broadcast"):
        context.user_data.pop("awaiting_broadcast")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        conn.close()

        success, failed = 0, 0
        for (uid,) in users:
            try:
                await update.message.copy(chat_id=uid)
                success += 1
            except Exception:
                failed += 1

        await update.message.reply_text(f"✅ <b>Broadcast Completed!</b>\nSuccess: {success}\nFailed: {failed}", parse_mode="HTML")
        return

# Admin Command Helpers
async def cmd_setupi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /setupi upi_id@handle Payee Name")
        return
    upi = args[0]
    payee = " ".join(args[1:])
    set_config("upi_id", upi)
    set_config("payee_name", payee)
    await update.message.reply_text(f"✅ Payment settings updated!\nUPI: {upi}\nPayee: {payee}")

async def cmd_setplanname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or "editing_plan" not in context.user_data:
        return
    plan_id = context.user_data["editing_plan"]
    name = " ".join(context.args)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET name=? WHERE plan_id=?", (name, plan_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Plan name updated to: {name}")

async def cmd_setplanprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or "editing_plan" not in context.user_data:
        return
    plan_id = context.user_data["editing_plan"]
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /setplanprice price original_price")
        return
    try:
        price = float(context.args[0])
        orig = float(context.args[1])
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE plans SET price=?, original_price=? WHERE plan_id=?", (price, orig, plan_id))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Price updated to ₹{price} (Original: ₹{orig})")
    except ValueError:
        await update.message.reply_text("Invalid number format.")

async def cmd_setplánlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or "editing_plan" not in context.user_data:
        return
    plan_id = context.user_data["editing_plan"]
    link = " ".join(context.args)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET join_link=? WHERE plan_id=?", (link, plan_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Join link updated to: {link}")

async def cmd_setplancaption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id) or "editing_plan" not in context.user_data:
        return
    plan_id = context.user_data["editing_plan"]
    caption = " ".join(context.args)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET caption=? WHERE plan_id=?", (caption, plan_id))
    conn.commit()
    conn.close()
    await update.message.reply_text("✅ Plan caption updated successfully!")

async def cmd_setmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    command = update.message.text.split()[0][1:]
    text = update.message.text[len(command)+2:].strip()
    
    key_map = {
        "setstartmessage": "start_message",
        "sethowtousemessage": "how_to_use",
        "setsuccessmessage": "success_message",
        "setrejectionmessage": "rejection_message"
    }
    if command in key_map:
        set_config(key_map[command], text)
        await update.message.reply_text("✅ Message configuration updated successfully!")

# ==========================================
# MAIN APPLICATION SETUP
# ==========================================
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is missing in environment variables!")
        return

    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # User Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(how_to_use_callback, pattern="^how_to_use$"))
    application.add_handler(CallbackQueryHandler(back_to_main_callback, pattern="^back_to_main$"))
    application.add_handler(CallbackQueryHandler(plan_detail_callback, pattern="^plan_plan_"))
    application.add_handler(CallbackQueryHandler(plan_detail_callback, pattern="^plan_plan_[0-9]+$")) # General plan handler below
    
    # Generic Plan Pattern Handler
    application.add_handler(CallbackQueryHandler(plan_detail_callback, pattern="^plan_plan_[1-9][0-9]*$|^plan_plan_1[0-1]$|^plan_plan_[a-zA-Z0-9_]+$"))
    
    application.add_handler(CallbackQueryHandler(confirm_purchase_callback, pattern="^confirm_"))
    application.add_handler(CallbackQueryHandler(verify_order_callback, pattern="^verify_"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))

    # Admin Approval/Rejection Callbacks
    application.add_handler(CallbackQueryHandler(admin_approve_order, pattern="^adm_app_"))
    application.add_handler(CallbackQueryHandler(admin_reject_order, pattern="^adm_rej_"))

    # Admin Panel Handlers
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(admin_callback_router, pattern="^adm_"))

    # Admin Quick Commands
    application.add_handler(CommandHandler("setupi", cmd_setupi))
    application.add_handler(CommandHandler("setplanname", cmd_setplanname))
    application.add_handler(CommandHandler("setplanprice", cmd_setplanprice))
    application.add_handler(CommandHandler("setplánlink", cmd_setplánlink))
    application.add_handler(CommandHandler("setplancaption", cmd_setplancaption))
    application.add_handler(CommandHandler("setstartmessage", cmd_setmsg))
    application.add_handler(CommandHandler("sethowtousemessage", cmd_setmsg))
    application.add_handler(CommandHandler("setsuccessmessage", cmd_setmsg))
    application.add_handler(CommandHandler("setrejectionmessage", cmd_setmsg))

    # Media / Broadcast message handler
    application.add_handler(MessageHandler(filters.VIDEO | filters.TEXT | filters.PHOTO & ~filters.COMMAND, admin_media_or_text_handler))

    logger.info("Starting Digital Products Sales Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()

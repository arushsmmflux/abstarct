import os
import logging
import telebot
import io
import qrcode
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
BOT_TOKEN = "8688514376:AAECX2gzcl0Ae9lpllVEMw6HGKJAxczJGQI"
ADMIN_ID = 6516697207

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing")

if not ADMIN_ID:
    raise RuntimeError("ADMIN_ID missing or invalid")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)

user_waiting_screenshot = set()
pending_screenshots = {}

# =========================================================
# BOT
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# =========================================================
# SUPPORT
# =========================================================

SUPPORT_LINK = "https://t.me/xylerigcc"


# =========================================================
# WELCOME IMAGE
# =========================================================
# Yahan WELCOME IMAGE ka Telegram FILE ID paste karna.
#
# Example:
# WELCOME_IMAGE = "AgACAgUAAxkBAA..."
#
# Agar empty rahega to bot text bhej dega.

WELCOME_IMAGE = "https://ibb.co/RGL77cpn"


# =========================================================
# FIRST START IMAGE
# =========================================================
# Start karte hi jo image Free / Paid buttons ke upar aayegi.
#
# Agar same image welcome ke liye use karni hai:
# START_IMAGE = WELCOME_IMAGE

START_IMAGE = "https://ibb.co/GhbLV5P"


# =========================================================
# 10 PLANS
# =========================================================

PLANS = [

    {
        "id": 1,
        "name": "𝙈𝙊𝙈 𝘼𝙉𝘿 𝙎𝙊𝙉 😍🔥 (",
        "price": "49",
        "validity": "180 days",
        "videos": "45000+",

        "image": "https://ibb.co/ZRqKVvRQ",
        "qr": "https://ibb.co/fYsgpT3c",

        "demos": [
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791609530271-d1845e11-78bd-4465-a0e3-3e0dd57fb424.mp4"
            },
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791610410648-c50ab2d2-b1b2-4998-8f5f-43a5f719b603.mp4"
            },
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791609652325-1646ca32-e73f-4a5a-9874-a0f4e401c6bb.mp4"
            },
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791609624603-358124e2-dbc4-43b2-9772-e18c1df57397.mp4"
            },
             {
                "type": "video",
                "id": "https://videotourl.com/videos/1791609569957-a7ce2e8a-e185-4dc6-893c-298a2d9c1b4c.mp4"
            },
             {
                "type": "image",
                "id": "https://ibb.co/r2KFm1Ct"
            },
            {
                "type": "video",
                "id": "BAACAgUAAxkBAAI1y2rHeVx-RkIlGJNKCZw97WDxcuCdAAKaIgACv69BVsbbPDC2Ob_VPQQ"
            }
        ],

        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 2,
        "name": "𝙍!@𝙋𝙀 𝙑𝙄𝘿𝙀𝙊𝙎 💦👀",
        "price": "69",
        "validity": "180 days",
        "videos": "40000+",

        "image": "https://ibb.co/QF2v05qK",
        "qr": "https://ibb.co/gbLMg58r",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791598317965-12b2368c-6035-4e43-b708-df28bcd246b6.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609986226-0b727823-bf05-42b7-80e8-c949f04b95ab.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598333066-6d6fc74f-945c-4641-99d1-d862e59790d4.mp4"},
              {"type": "image", "id": "https://ibb.co/XZ0t4D5L"},
              {"type": "video", "id": "https://videotourl.com/videos/1791598348006-882fbe39-db59-4bb7-8636-1c2645fb93c0.mp4"},
              {"type": "video", "id": "https://videotourl.com/videos/1791611260635-789f7a13-25cd-4204-8ffc-455168319040.mp4"},
              {"type": "video", "id": "https://videotourl.com/videos/1791598360862-d0ddd962-c4e7-4c98-a860-d360bf6779f8.mp4"},
             {"type": "video", "id": "https://videotourl.com/videos/1791601968259-cb7b49a5-a8c5-45f9-9156-e08f71b052d0.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598382840-4245fa8e-38f8-4737-8bb9-a2b8641a3d0f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598397313-ff9dd5ef-d489-4715-a2ca-a71c8923f162.mp4"}
        ],

        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 3,
        "name": "𝘾𝙃𝙄!𝙇𝘿 𝙑𝙄𝘿!𝙀𝙊 ( 𝘾.𝙋) 🔥👀",
        "price": "49",
        "validity": "180 days",
        "videos": "70000+",

        "image": "https://ibb.co/21H7BGM2",
        "qr": "https://ibb.co/fYsgpT3c",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791598226633-9d219b40-bf0b-4774-b493-6449c47d5ef1.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598035486-79178a34-a631-49d2-870e-ff3425f1c058.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611314862-1e0e5b81-0a04-436a-9749-4f5e9115404f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598059935-f6722923-e315-4b97-aaeb-e7b0af379f2b.mp4"},
             {"type": "video", "id": "https://videotourl.com/videos/1791598126801-a117ace0-e399-46e6-b697-0d3da6efeedd.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598126801-a117ace0-e399-46e6-b697-0d3da6efeedd.mp4"},
             {"type": "photo", "id": "https://ibb.co/6c4RL0bj"},
             {"type": "video", "id": "https://videotourl.com/videos/1791598104865-7bca6c3f-db24-465d-9688-d153131af1e5.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791598207010-15f8101c-d87e-4e83-bd6a-43a333204662.mp4"}
        ],

        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 4,
        "name": "𝘽𝙃𝘼𝘽𝙃𝙄 𝙑𝙄𝘿𝙀𝙊𝙎  💦👅 ",
        "price": "39",
        "validity": "180 days",
        "videos": "56000+",

        "image": "https://ibb.co/HLw36KQ4",
        "qr": "https://ibb.co/4n9q8mK2",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611037316-4db456f2-f82c-4468-9f48-381341ed6e55.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611085614-c863517b-d989-4d6f-b6ef-d23db0b73f5a.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611220352-ba6538bc-4db1-401e-81f7-
88c53824e27f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611220352-ba6538bc-4db1-401e-81f7-88c53824e27f.mp4"},
             {"type": "video", "id": "https://videotourl.com/videos/1791611168222-86d679dd-8a24-46fb-8b06-d59cc97e84c2.mp4"},
             {"type": "image", "id": "https://ibb.co/Ng1cgMdD"},
             {"type": "video", "id": "https://videotourl.com/videos/1791611005214-c25159ac-d514-4eff-8061-a25465ff6eba.mp4"},             {"type": "video", "id": "https://videotourl.com/videos/1791609479203-02acf86c-6132-4bc2-8041-9f43ab529748.mp4"},
            {"type": "video", "id": "BAACAgUAAxkBAAI112rHehWT7ChqF4hbypfAEwmyF9BkAAKeIgACv69BVtXBJ3Uu9oPEPQQ"}
        ],
        
 "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 5,
        "name": "𝘽𝙃𝘼𝙄 𝘽𝙀𝙃𝘼𝙉 🔥🥵 ",
        "price": "49",
        "validity": "180 days",
        "videos": "67000+",

        "image": "https://ibb.co/9kKCd6ZF",
        "qr": "https://ibb.co/fYsgpT3c",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611423923-36dbbbf3-84c1-4754-a7e4-dc05798eaa03.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611350514-052fe889-5ac7-4446-91ef-2f928070e131.mp4"},
            {"type": "image", "id": "https://ibb.co/qvtk5H1"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609591492-b5b0f616-27c5-436f-9aa9-e70720337677.mp4"},
             {"type": "video", "id": "https://videotourl.com/videos/1791609952353-7ee9382f-6db6-4c43-86ed-c8f418a3282c.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791609450717-98fd3d4d-533c-46fc-a290-9f9f937b6721.mp4"}
        ],
 "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 6,
        "name": "𝗜𝗡𝗦𝗧𝗚𝗥𝗔𝗠 𝗠𝗠𝗦 𝗔𝗟𝗟 😍🔥 ",
        "price": "49",
        "validity": "180 days",
        "videos": "50000+",

        "image": "https://ibb.co/Fb6S1mYg",
        "qr": "https://ibb.co/fYsgpT3c",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791607740001-dfef0130-88bb-4ca0-948d-b857ba8fc867.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607674607-203922d8-e261-4085-90fc-4be2fd62a6fb.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607662133-116f8c11-861a-4d4c-94a4-411fbd79a4f4.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607553470-a87b7709-29e5-449b-89d2-49ce97c8e367.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607585444-8a7d8e39-2917-4d23-949e-c048fcbacb2f.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607607288-b1cc3341-7d49-473e-8544-840992806dab.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791607617748-9c8da0dd-313e-4a4d-862b-7ccf034383b7.mp4"}
        ],

        "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 7,
        "name": "𝘽𝘼𝘼𝙋 𝘽𝙀𝙏𝙄 🔥💦 ",
        "price": "58",
        "validity": "180 days",
        "videos": "30000+",

        "image": "https://ibb.co/5X0hc5dd",
        "qr": "https://ibb.co/xK77FFDK",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791609855846-9b6bac98-1fcf-4d60-b612-3e5abaf6be7e.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791614058029-1220e2df-44c4-467d-bbd7-755af32ada0c.mp4"}
        ],

         "caption": "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅"
"2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌"
"3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍"
"4.  𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔   ✅",
        "active": True
    },


    {
        "id": 8,
        "name": "𝙈𝙄𝙓 𝙂𝙍𝙊𝙐𝙋 70𝙆 𝙑𝙄𝘿𝙀𝙊𝙎 🥵",
        "price": "63",
        "validity": "180 days",
        "videos": "70000+",

        "image": "https://ibb.co/qFhKnzcH",
        "qr": "https://ibb.co/tMVzjb0D",

        "demos": [
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791611593469-187437c5-8f84-41c6-afa1-3d61feb9ff72.mp4"
            },
            {
                "type": "video",
                "id": "https://videotourl.com/videos/1791611552865-c2cf6f7d-1544-4c34-9bdb-5e5fb2092584.mp4"
            }
        ],

        "caption": (
            "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n"
            "2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n"
            "3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n"
            "4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙁𝙍𝙄𝘿𝘼𝙔 ✅."
        ),

        "active": True
    },


    {
        "id": 9,
        "name": "𝙂𝙄𝙍𝙇𝙎 𝙒𝙄𝙏𝙃 𝘼𝙉!𝙈@𝙇🔥",
        "price": "49",
        "validity": "180 days",
        "videos": "18000+",

        "image": "https://ibb.co/qFhKnzcH",
        "qr": "https://ibb.co/fYsgpT3c",

        "demos": [
            {"type": "video", "id": "https://videotourl.com/videos/1791611713436-2f106a4b-9ee1-4d9b-8e06-c30a0fe309e7.mp4"},
            {"type": "video", "id": "https://videotourl.com/videos/1791611779829-f05b75a9-65c7-441d-ad89-5d5f15301b01.mp4"}
        ],

        "caption": (
            "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n"
            "2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n"
            "3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n"
            "4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅"
        ),
        "active": True
    },

    {
        "id": 10,
        "name": "𝗔𝗟𝗟 𝗩𝗜𝗣  𝗠𝗘𝗚𝗔 𝗣𝗔𝗖𝗞 🔥 ",
        "price": "169",
        "validity": "180 days",
        "videos": "100000+",
        "image": "https://ibb.co/84598K8j",
        "qr": "https://ibb.co/MDWVSzF8",

        "caption": (
            "1. 𝙔𝙊𝙐 𝘾𝘼𝙉 𝙎𝘼𝙑𝙀 𝙄𝙉 𝙂𝘼𝙇𝙇𝙀𝙍𝙔 ✅\n"
            "2. 𝙉𝙊 𝘼𝙉𝙔 𝘼𝘿𝙎 ❌\n"
            "3. 𝙃𝙄𝙂𝙃 𝙌𝙐𝘼𝙇𝙄𝙏𝙔 𝙑𝙄𝘿𝙀𝙊𝙎 😍\n"
            "4. 𝙉𝙀𝙒 𝙑𝙄𝘿𝙀𝙊𝙎 𝙐𝙋𝙇𝙊𝘼𝘿𝙀𝘿 𝙀𝙑𝙀𝙍𝙔 𝙎𝙐𝙉𝘿𝘼𝙔 ✅"
        ),
        "active": True
    }
]


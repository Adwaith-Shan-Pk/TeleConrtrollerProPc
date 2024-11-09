import os
import logging
import subprocess
import sys
import ctypes
import cv2


from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from dotenv import load_dotenv
load_dotenv()


#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token=os.getenv('TOKEN')
AUID = set(map(int, os.getenv('UserId', '').split(',')))

def is_authorized_user(update: Update) -> bool:
    return update.effective_user.id in AUID


# Decorator for authorization
def authorized(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not is_authorized_user(update):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Unauthorized access.")
            logger.warning(f"Unauthorized access attempt by user {update.effective_user.id}")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper




app = ApplicationBuilder().token(bot_token).build()

#Error Hadling
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

#Start Cmd
@authorized
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello Shan!. Please Use My Commands.")
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        


#Check/Install Libraries Installed
@authorized
async def install_libraries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Installing required libraries...")
        # Install libraries using pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "python-telegram-bot", "pillow"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Libraries installed successfully.")
    except Exception as e:
        logger.error(f"Error in install_libraries: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to install libraries.")


#Shutdown
@authorized
async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Shutting down the system...")
        os.system("shutdown /s /t 1")
    except Exception as e:
        logger.error(f"Error in shutdown_command: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to shut down system.")



#Reboot
@authorized
async def reboot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Rebooting the system...")
        os.system("shutdown /r /t 1")
    except Exception as e:
        logger.error(f"Error in reboot_command: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to reboot system.")


#Lock
@authorized
async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Locking the workstation...")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    except Exception as e:
        logger.error(f"Error in lock_command: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to lock workstation.")


#



#Stop Bot
@authorized
async def stopbot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Trying to Stop Bot")
        app.stop_running()
    except Exception as e:
        logger.error(f"Error in stop_command: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Stopbot didn't work")

# #Command Check     
# @authorized  
# async def hi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello")
#         #os.system("rundll32.exe user32.dll,LockWorkStation")
#         print("Hello World")
#     except Exception as e:
#         logger.error(f"Error in hi_command: {e}")
#         await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to say hello.")

app.add_handler(CommandHandler("install_libraries", install_libraries))
app.add_handler(CommandHandler("shutdown", shutdown_command))
app.add_handler(CommandHandler("reboot", reboot_command))
app.add_handler(CommandHandler("lock", lock_command))
app.add_handler(CommandHandler("start",start_command))
app.add_handler(CommandHandler("stopbot", stopbot_command))



if __name__ == "__main__":
    app.run_polling()

import os
import logging
import subprocess
import sys
import ctypes
import cv2
import numpy as np
import requests
import webbrowser


from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from functools import wraps
from PIL import ImageGrab
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python", "python-telegram-bot", "pillow","numpy","requests"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Libraries installed successfully.")
    except Exception as e:
        logger.error(f"Error in install_libraries: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to install libraries.")

#Screenshot
@authorized
async def screenshot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Capture the screen
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)  # Convert to a numpy array
        screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR format

        # Save the screenshot to a file
        screenshot_path = "screenshot.jpg"
        cv2.imwrite(screenshot_path, screenshot_cv)

        # Send the screenshot to the user
        with open(screenshot_path, "rb") as img_file:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(img_file))

        # Optional: remove the screenshot after sending
        os.remove(screenshot_path)
        
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to take screenshot.")
        print(f"Error taking screenshot: {e}")

#Open Link 
@authorized
async def open_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the URL passed as an argument
    if context.args:
        url = context.args[0]
        
        # Validate if the URL starts with http:// or https://
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url  

        try:
            
            webbrowser.open(url)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Visiting {url}")
            
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to open the website.")
            print(f"Error opening website: {e}")
    
    else:
        # If no URL was provided, send usage instructions
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a URL. Usage: /openlink <URL>")


#Currentip
@authorized
async def current_ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Fetch the public IP address
        response = requests.get("https://api.ipify.org")
        ip_address = response.text

        # Send the IP address to the user
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your current IP address is: {ip_address}")
        
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to fetch IP address.")
        print(f"Error fetching IP: {e}")


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
app.add_handler(CommandHandler("screenshot",screenshot_command))
app.add_handler(CommandHandler("currentip",current_ip_command))
app.add_handler(CommandHandler("openlink",open_link))



if __name__ == "__main__":
    app.run_polling()

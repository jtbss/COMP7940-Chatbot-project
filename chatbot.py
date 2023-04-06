from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import configparser
import logging
import redis
import requests


global redis1

# google custom search engine api key
SEARCH_ENGINE_ID = "95b4f0461be9e4731"
API_KEY = "AIzaSyBqRnuNHWAUKHCe2uLcdNkopIjIoc7Er5I"

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    # dispatcher = updater.dispatcher
    # global redis1
    # redis1 = redis.Redis(host=(os.environ['HOST']), password=(os.environ['PASSWORD']), port=(os.environ['REDISPORT']))

    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), password=(config['REDIS']['PASSWORD']), port=(config['REDIS']['REDISPORT']))


    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)


    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)


    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello_command))
    dispatcher.add_handler(CommandHandler("img", handle_image_command))


    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)



def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def hello_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Good day, Kevin!')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0] # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def handle_image_command(update, context):
    # Get the search term from the message text
    search_term = ' '.join(context.args)
    # Define the search URL with the search term, API key, and search engine ID
    search_url = f"https://www.googleapis.com/customsearch/v1?q={search_term}&cx={SEARCH_ENGINE_ID}&searchType=image&key={API_KEY}"
    # Send the search request to the API and get the JSON response
    response = requests.get(search_url).json()
    # Check if the response contains any images
    if 'items' in response and len(response['items']) > 0:
        # Get the URL of the first image in the response
        image_url = response['items'][0]['link']
        # Download the image to a local file
        image_path = os.path.join(os.getcwd(), 'temp.jpg')
        response = requests.get(image_url)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        # Send the image back to the chat
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(image_path, 'rb'))
        # Delete the local image file
        os.remove(image_path)
    else:
        # If the search did not return any images, send an error message back to the chat
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I could not find any images for the requested search term.")



if __name__ == '__main__':
    main()

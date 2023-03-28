from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext
import os
# The messageHandler is used for all message updates
# import configparser
import logging
import redis

global redis1


def main():
    # print(telegram.constants.BOT_API_VERSION)

    # Load your token and create an Updater for your bot
    # config = configparser.ConfigParser()
    # config.read('./config.ini')
    # updater = Updater(
    #     token=(config['TELEGRAM']['ACCESS_TOKEN']),
    #     use_context=True
    # )
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)

    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(
        host=(os.environ['REDIS_HOST']),
        password=(os.environ['REDIS_PASSWORD']),
        port=(os.environ['REDIS_PORT'])
    )

    # redis1 = redis.Redis(
    #     host=(config['REDIS']['HOST']),
    #     password=(config['REDIS']['PASSWORD']),
    #     port=(config['REDIS']['REDISPORT'])
    # )

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s',
        level=logging.INFO
    )
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    help_handler = CommandHandler('help', help_command)
    add_handler = CommandHandler('add', add)
    hellow_handler = CommandHandler('hello', hello_command)

    dispatcher.add_handler(hellow_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(add_handler)

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_message
    )


# Define a few command handlers. These usually take the two arguments update and context
# Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    # Send a message when the comman /help is issued
    update.message.reply_text('What can I do for you?')


def hello_command(update: Update, context: CallbackContext) -> None:
    try:
        msgs = context.args
        update.message.reply_text(f'Good day, {msgs[0]}!')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')


def add(update: Update, context: CallbackContext) -> None:
    # Send a message when the comman /add is issued
    try:
        global redis1
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text(
            'You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


if __name__ == '__main__':
    main()

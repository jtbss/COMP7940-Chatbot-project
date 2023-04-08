from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext, CallbackQueryHandler

import os
import configparser
import logging
import redis

from googleapiclient.discovery import build

from youtube_search import search_video, list_hot_vidoes
# from image_search import search_image

global redis1
global youtube

config = configparser.ConfigParser()
config.read('./config.ini')

TELEGRAM_ACCESS_TOKEN = os.environ['TELEGRAM_ACCESS_TOKEN']
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_PORT = os.environ['REDIS_PORT']
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']

# TELEGRAM_ACCESS_TOKEN = config['TELEGRAM']['ACCESS_TOKEN']
# REDIS_HOST = config['REDIS']['HOST']
# REDIS_PASSWORD = config['REDIS']['PASSWORD']
# REDIS_PORT = config['REDIS']['REDISPORT']
# YOUTUBE_API_KEY = config['YOUTUBE']['API_KEY']


def main():
    # Load your token and create an Updater for your bot
    updater = Updater(
        token=TELEGRAM_ACCESS_TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(
        host=REDIS_HOST,
        password=REDIS_PASSWORD,
        port=REDIS_PORT
    )

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s',
        level=logging.INFO
    )
    # register a dispatcher to handle message: here we register an echo dispatcher
    handler_dict = {
        "start": CommandHandler('start', start),
        "echo_handler": MessageHandler(Filters.text & (~Filters.command), echo),
        "add_handler": CommandHandler('add', add),
        "help_handler": CommandHandler('help', help_command),
        "hello_handler": CommandHandler('hello', hello_command),
        "youtube_handler": CommandHandler('youtube', youtube_action),
        "button_callback_handler": CallbackQueryHandler(button_callback)
    }

    for handler in handler_dict.values():
        dispatcher.add_handler(handler)

    # To start the bot:
    updater.start_polling()
    updater.idle()


# def image_action(update: Update, context: CallbackContext):
#     search_image(update, context)


def youtube_action(update, context):
    query = " ".join(context.args)
    global youtube
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    if query == 'hot' or query == '':
        list_hot_vidoes(update, context, youtube)
    else:
        search_video(update, context, query, youtube)


def echo(update, context):
    reply_message = update.message.text
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=reply_message
    )


def help_command(update: Update) -> None:
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
        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


# 处理按钮回调函数
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = eval(query.data)
    print(data)

    # 处理特定按钮的回调数据
    if data['type'] == 'youtube_like':
        video_id = data['data']
        exist = False

        # 获取 redis 中存好的列表
        liked_list = redis1.lrange('youtube_liked_list', 0, -1)
        if len(liked_list) == 0:
            redis1.rpush('youtube_liked_list', video_id)
        else:
            if video_id not in [value.decode() for value in liked_list]:  # 检查是否存在该值
                redis1.rpush('youtube_liked_list', video_id)
            else:
                exist = True
        
        liked_list = redis1.lrange('youtube_liked_list', 0, -1)
        print(liked_list)

        if not exist:
            query.answer(text=f'You like this video 👍 {video_id}')
        else:
            query.answer(text=f'You have already liked this video 😊')
    else:
        print('You do nothing')


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello! Welcome to the chat Bot. What can I do for you?"
    )


if __name__ == '__main__':
    main()

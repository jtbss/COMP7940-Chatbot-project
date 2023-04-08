import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# 根据关键词搜索 YouTube 视频
def search_video(update, context, query, youtube):
    try:
        request = youtube.search().list(
                part="id, snippet",
                q=query,
                type="video",
                maxResults=50,
                # regionCode="HK"
            )
        response = request.execute()
        
        random_video = random.choice(response["items"])
        video_id = random_video['id']['videoId']
        
        # 定义需要传递的参数
        data = {
            'type': 'youtube_like',
            'data': video_id
        }
        # 创建一个 InlineKeyboardButton 实例
        Like_Button = InlineKeyboardButton('👍 Like', callback_data=str(data))
        # 创建 InlineKeyboardMarkup 实例
        keyboard = [[Like_Button]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response = f"https://www.youtube.com/watch?v={video_id}"
        print(response)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=response,
            reply_markup=reply_markup
        )
    except ConnectionError:
        print('Somethings went wrong!')


# 列出比较受欢迎的视频
def list_hot_vidoes(update, context, youtube):
    try:
      request = youtube.videos().list(
          part="snippet,contentDetails,statistics",
          chart="mostPopular",
          maxResults=100
      )
      response = request.execute()
      videos = []

      # 处理响应
      for item in random.sample(response.get("items", []), 3):
          title = item["snippet"]["title"]
          url = f"https://www.youtube.com/watch?v={item['id']}"
          like_count = item["statistics"]["likeCount"]
          video_info = f"{title}\n{url}\n👍{like_count}"
          videos.append(video_info)
      
      context.bot.send_message(
          chat_id=update.effective_chat.id,
          text="\n\n".join(videos)
        )
    except ConnectionError:
        print('Somethings went wrong!')


# 列出所有点赞过的视频


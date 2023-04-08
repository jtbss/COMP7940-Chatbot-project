import requests
import os

# google custom search engine api key
SEARCH_ENGINE_ID = "95b4f0461be9e4731"
API_KEY = "AIzaSyBqRnuNHWAUKHCe2uLcdNkopIjIoc7Er5I"

def search_image(update, context):
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

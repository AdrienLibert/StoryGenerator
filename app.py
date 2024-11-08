import tweepy
import time
from openai import OpenAI
import os
import requests
from flask import Flask, render_template, request, jsonify, url_for

# Twitter API keys
API_KEY = 'your_api_key'
API_SECRET_KEY = 'your_api_secret_key'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'
BEARER_TOKEN = 'your_bearer_token'

# OpenAI API keys
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_BASE_URL = "your_openai_base_url"


# Tweepy authentication setup
auth = tweepy.OAuth1UserHandler(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
api_v1 = tweepy.API(auth)  # Twitter API v1
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# OpenAI client initialization
client_ai = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# Flask app setup
app = Flask(__name__)

# Global variables to store story, segments, and image URLs
tweet_content = ""
segments = []
image_urls = []

# Old function to generate images for the terminal version
""" def picture(prompt):
    response = client_ai.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url

    response = requests.get(image_url)

    if response.status_code == 200:
        with open("tweet_pic.png", "wb") as f:
            f.write(response.content) """

# Function to clean up the prompt text for DALL-E, ensuring compliance with content policy
def ask_gpt_mytext_isgood(text):
    prompt = (
        "Please rewrite the following text to ensure it adheres strictly to content policies for image generation. "
        "Avoid any language that might be flagged as sensitive, controversial, or inappropriate, even indirectly. "
        "Maintain the original meaning, but replace words with safe and neutral alternatives, especially if they might be misinterpreted:\n\n"
        f"{text}\n\n"
        "Make sure the text is fully suitable for a general audience and ready to be used for generating AI images without triggering content policy violations."
    )
    response = client_ai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    cleaned_text = response.choices[0].message.content.strip()
    return cleaned_text

# Function to generate an image using a sanitized prompt and save it locally
def picture(prompt, image_name):
    cleaned_prompt = ask_gpt_mytext_isgood(prompt)
    response = client_ai.images.generate(
        model="dall-e-3",
        prompt=cleaned_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    response = requests.get(image_url)

    if response.status_code == 200:
        # Save the image in the static folder
        image_path = f"static/{image_name}.png"
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    return None

# Function to generate a historical story with emojis using the OpenAI API
def ask_gpt_historian_story_with_emojis(genre, character=None, location=None):
    prompt = f"Act as a historian and tell a concise historical story about {genre}, around 500 characters. Avoid using dashes (—) in the text."
    if character:
        prompt += f" Make {character} the main character of the story."
    if location:
        prompt += f" Set the story in {location}."
    prompt += " Make it engaging, accurate, and add relevant emojis to enhance the mood"
    response = client_ai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Function to segment a long story into parts suitable for Twitter threads
def ask_gpt_to_segment_text(content):
    prompt = f"Create a captivating title for this historical story, and then segment the text into parts suitable for a Twitter thread. Each part should be around 280 characters (min 200 max 350), while maintaining natural breaks and readability:\n\n{content}"

    response = client_ai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.choices[0].message.content.strip()
    title, *segments = response_text.split("\n\n")

    segments[0] = f"{title}\n\n{segments[0]}"
    return segments

# Function to delete images in the static folder after posting to Twitter
def delete_images(directory="static"):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f"Deleted {file_path}")
    except Exception as e:
        print(f"An error occurred while deleting images: {e}")

# Function to send a threaded tweet with optional media
def send_thread(segments, image_urls):
    last_tweet_id = None

    for i in range(len(segments)):
        image_path = os.path.abspath(os.path.join('static', os.path.basename(image_urls[i]))) if i < len(image_urls) else None
        
        if image_path and os.path.exists(image_path):
            media = api_v1.media_upload(image_path)  # Upload image if it exists
            media_ids = [media.media_id]
        else:
            media_ids = None  # No image for this segment
            print(f"Image not found or does not exist: {image_path}")

        try:
            # Send the tweet with the appropriate media or as a reply
            if last_tweet_id is None:
                tweet = client.create_tweet(text=segments[i], media_ids=media_ids)
            else:
                tweet = client.create_tweet(text=segments[i], media_ids=media_ids, in_reply_to_tweet_id=last_tweet_id)

            last_tweet_id = tweet.data['id']
            time.sleep(25)
        except tweepy.errors.TooManyRequests:
            print("Rate limit exceeded. Waiting for 15 minutes before retrying...")
            time.sleep(900)
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

    print("Thread with images sent successfully.")

# Main route to render the index page
@app.route('/')
def home():
    return render_template('index.html')

# Endpoint to generate a story based on user input
@app.route('/generate', methods=['POST'])
def generate_story():
    global tweet_content
    global segments
    genre = request.form.get('genre')
    character = request.form.get('character')
    location = request.form.get('location')

    gpt_response = ask_gpt_historian_story_with_emojis(genre, character, location)
    tweet_content += gpt_response + "\n"
    segments = ask_gpt_to_segment_text(tweet_content)

    return jsonify({
        "message": "Tweet content updated.",
        "segments": segments
    })

# Endpoint to generate images for each segment
@app.route('/generate_image', methods=['POST'])
def generate_image():
    global segments

    if not segments:
        return jsonify({"error": "No segments available. Please generate the story first."}), 400

    global image_urls
    for i, segment in enumerate(segments):
        image_path = picture(segment, f"tweet_image_{i}")
        if image_path:
            image_url = url_for('static', filename=f"tweet_image_{i}.png")
            image_urls.append(image_url)
        else:
            image_urls.append(None)

    return jsonify({
        "image_urls": image_urls
    })

# Endpoint to send the tweet thread
@app.route('/send', methods=['POST'])
def send_tweet():
    global segments, image_urls, tweet_content
    if tweet_content and segments and image_urls:
        send_thread(segments, image_urls)
        delete_images()
        tweet_content = ""
        segments = []
        image_urls = []
        return jsonify({"message": "Tweet sent!"})
    else:
        return jsonify({"message": "No content to send. Please enter a genre to generate tweet content."})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

# Old main function for terminal-based testing
""" def main():
    print("Welcome to the Historical Storyteller with Twitter Integration!")
    print("Type the genre of the historical story you want (e.g., horror, war, romance). Optionally, add a character and location (e.g., 'horror Napoleon California'). Type 'send' to send the tweet.")

    tweet_content = ""

    while True:
        user_input = input("Enter genre, character, location, or 'send': ")

        if user_input.lower() == "send":
            if tweet_content:
                send_thread(tweet_content)
                tweet_content = ""
            else:
                print("No content to send. Please enter a genre to generate tweet content.")

        else:
            inputs = user_input.split()
            genre = inputs[0]
            character = inputs[1] if len(inputs) > 1 else None
            location = inputs[2] if len(inputs) > 2 else None

            gpt_response = ask_gpt_historian_story_with_emojis(genre, character, location)
            print(f"GPT: {gpt_response}")
            tweet_content += gpt_response + "\n"
            print("Tweet content updated. Type 'send' to tweet this story.")
        time.sleep(1)

if __name__ == "__main__":
    main() """
import tweepy
import time
from openai import OpenAI
import os
import requests
from flask import Flask, render_template, request, jsonify, url_for


# Twitter API keys
API_KEY = '8T9loQuNEcqUsSYhzb0Ndnvw7'
API_SECRET_KEY = 'RGGX3bDp2T1t4s8vKNTsfDBQxfIJPzXQqquVAMP8MEoAkX5eW6'
ACCESS_TOKEN = '3223725430-MRe9uZ713SQDlPejoMDuAnRiHEXgQ9SQS3I4qvw'
ACCESS_TOKEN_SECRET = 'Y2qL2mueUAunAb9D77S0RKDuqTiFSKGZ1U1jE6osuu0Ey'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAABOLwQEAAAAA3rdHAJq%2BFzOda5RhmoEWb5AcEBc%3DKFIh8IUzRaVEJqrxyTXKMp3lAF2pt77qydJI6DylsmYi2elzM1'

# OpenAI API keys
OPENAI_API_KEY = "sk-gHIs4XUay9uu2m94662993E19c7c46E4A9A5B644934cE9B4"
OPENAI_BASE_URL = "http://chat.api.xuanyuan.com.cn/v1"

# Tweepy authentication
auth = tweepy.OAuth1UserHandler(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
api_v1 = tweepy.API(auth)
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# OpenAI client initialization
client_ai = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

app = Flask(__name__)

tweet_content = ""
segments = []
image_urls = []



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
        # Enregistre l'image localement avec un nom unique
        image_path = f"static/{image_name}.png"
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    return None

def ask_gpt_historian_story_with_emojis(genre, character=None, location=None):
    prompt = f"Act as a historian and tell a concise historical story about {genre}, arround 500 char. Avoid using dashes (—) in the text."
    if character:
        prompt += f" Make {character} the main character of the story."
    if location:
        prompt += f" Set the story in {location}."
    prompt += " Make it engaging, accurate, and add relevant emojis to enhance the mood"
    response = client_ai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

""" def send_tweet(content,):
    image_paths = ['tweet_pic.png']
    media_ids = []
    for image_path in image_paths:
        media = api_v1.media_upload(image_path)
        media_ids.append(media.media_id)

    response = client.create_tweet(text=content, media_ids=media_ids)
    print("Tweet sent successfully.") """

def ask_gpt_to_segment_text(content):
    prompt = f"Create a captivating title for this historical story, and then segment the text into parts suitable for a Twitter thread. Each part should be arround 280 characters (min 200 max 350), while maintaining natural breaks and readability:\n\n{content}"

    response = client_ai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.choices[0].message.content.strip()
    title, *segments = response_text.split("\n\n")

    segments[0] = f"{title}\n\n{segments[0]}"

    return segments

def delete_images(directory="static"):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg"):
                file_path = os.path.join(directory, filename)
                os.remove(file_path)
                print(f"Deleted {file_path}")
    except Exception as e:
        print(f"An error occurred while deleting images: {e}")

def send_thread(segments, image_urls):
    last_tweet_id = None

    for i in range(len(segments)):
        image_path = os.path.abspath(os.path.join('static', os.path.basename(image_urls[i]))) if i < len(image_urls) else None
        
        if image_path and os.path.exists(image_path):
            media = api_v1.media_upload(image_path)  # Télécharge l'image en utilisant le chemin complet
            media_ids = [media.media_id]
        else:
            media_ids = None  # Pas d'image pour ce segment ou fichier introuvable
            print(f"Image not found or does not exist: {image_path}")

        try:
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

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == "__main__":
    app.run(debug=True)

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
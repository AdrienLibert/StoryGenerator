# Historical Storyteller with Twitter Integration

An interactive web application that automatically generates and posts historical stories on Twitter with AI-generated images. Users can select the type of story they want, input preferences (genre, character, location), and preview the generated content before posting it as a Twitter thread.

## Table of Contents
- [Historical Storyteller with Twitter Integration](#historical-storyteller-with-twitter-integration)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies and Tools](#technologies-and-tools)
  - [Setup and Installation](#setup-and-installation)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Known Issues and Limitations](#known-issues-and-limitations)

## Features

- **User Input for Custom Storytelling**: Allows users to specify genre, character, and location to generate personalized stories.
- **AI-Generated Stories and Images**: Uses OpenAI’s GPT for text and DALL-E for image generation.
- **Automatic Twitter Posting**: Posts each story segment as a Twitter thread with corresponding images.
- **Web Interface**: Intuitive interface for input, story preview, image preview, and tweet confirmation.
  
## Technologies and Tools

- **Back End**: Flask (Python)
- **Front End**: HTML, CSS, JavaScript (Fetch API)
- **APIs**:
  - OpenAI (GPT and DALL-E) for content and image generation
  - Twitter API for automated posting
- **Dependencies**:
  - `Flask` for building the back end
  - `Tweepy` for Twitter API interactions
  - `Requests` for HTTP requests to download images
  - **Development Tools**: VS Code, Git, Python 3.10 or higher

## Setup and Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/username/historical-storyteller
    cd historical-storyteller
    ```

2. **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up API Keys**:
   - **OpenAI API Key**: Sign up for OpenAI, obtain an API key, and add it to app.py.
   - **Twitter API Key**: Obtain Twitter API keys and access tokens, add it to app.py.

4. **Run the Application**:
    ```bash
    python app.py
    ```
   The application will start on `http://127.0.0.1:5000`.

## Usage

1. **Access the Web Interface**: Open a web browser and go to `http://127.0.0.1:5000`.
2. **Generate Story**:
   - Enter your preferred genre, character, and location.
   - Click “Generate Story” to preview the AI-generated story.
3. **Generate Images**:
   - Click “Generate Image” to create images based on the story segments.
   - Images will be displayed under each story segment.
4. **Post to Twitter**:
   - If satisfied with the preview, click “Send Tweet” to automatically post the story and images as a Twitter thread.
   
## API Endpoints

- **/generate**:
  - **Method**: `POST`
  - **Description**: Generates a story based on user input.
  - **Request Body**: `genre`, `character`, `location`
  - **Response**: JSON with story segments.
  
- **/generate_image**:
  - **Method**: `POST`
  - **Description**: Generates images for each story segment using DALL-E.
  - **Response**: JSON with URLs for each generated image.

- **/send**:
  - **Method**: `POST`
  - **Description**: Posts the story and images as a Twitter thread.
  - **Response**: JSON with a success message.


## Known Issues and Limitations

- **Rate Limits**: The app may hit Twitter API rate limits during high-frequency usage; if this occurs, there will be a delay in posting.
- **Response Time Variance**: API response times from OpenAI may vary, causing delays for larger stories or multiple images.
- **DALL-E Content Policy Violations**: Some prompts may violate DALL-E’s content policies, but an additional filtering function minimizes issues.
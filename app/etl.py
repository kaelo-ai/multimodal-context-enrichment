import cv2
from moviepy.editor import VideoFileClip
import base64
import os
from IPython.display import Image, display, Audio, Markdown
from openai import OpenAI
import random
from dotenv import load_dotenv
from tqdm import tqdm
import requests
import json

load_dotenv()

## Set the API key and model name
MODEL = "gpt-4o"
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)

def fetch_movie_details(movie_id):
    """Fetch movie details from OMDB API."""
    url = f"http://omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    return response.json()

def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    # Loop through the video and extract frames at specified sampling rate
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    print(f"Extracted {len(base64Frames)} frames from {video_path}")
    return base64Frames

def create_chunks(data, chunk_size):
    """Split data into chunks of size chunk_size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

# Directory containing video files
video_dir = "data"

# Dictionary to store synopses
synopses = {}

# Iterate over all video files in the directory
for video_file in os.listdir(video_dir):
    if video_file.endswith(".mp4"):
        video_path = os.path.join(video_dir, video_file)
        movie_id = os.path.splitext(video_file)[0]
        movie_details = fetch_movie_details(movie_id)

        plot = movie_details.get("Plot", "No plot available.")
        title = movie_details.get("Title", "No title available.")

        # Process video to extract frames
        base64Frames = process_video(video_path, seconds_per_frame=1)

        # Split the frames into chunks to avoid exceeding token limits
        chunk_size = 5  # Number of frames per chunk
        frame_chunks = list(create_chunks(base64Frames, chunk_size))

        all_responses = []

        # Iterate over each chunk and send a separate request with progress tracking
        for chunk in tqdm(frame_chunks, desc=f"Processing chunks for {title}"):
            sampled_frames = random.sample(chunk, min(25, len(chunk)))

            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are generating a synopsis for a movie trailer, to entice the audience "
                                                  "to go to the cinema. "
                                                  "Provide an overall summary of the trailer in 30 words or less."},
                    {"role": "user", "content": [
                        "These are the frames from the video.",
                        *map(lambda x: {"type": "image_url", "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, sampled_frames)
                    ]},
                ],
                temperature=0,
                max_tokens=50
            )

            all_responses.append(response.choices[0].message.content)

        # Combine all responses into a single string
        final_response = " ".join(all_responses).replace("\n", " ")

        # Create a synopsis of the combined summary
        synopsis_prompt = (
            f"Create a synopsis of the movie '{title}', based on the plot: {plot} and rich with details from the visual summary: {final_response} "
            "Ignore any mentions of studio text, coming soon, or dates for cinema. "
            "Embed genre keywords in the synopsis in a subtle manner. "
            "Limit synopsis to 40-50 words."
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant that creates movie synopses."},
                {"role": "user", "content": synopsis_prompt},
            ],
            temperature=0,
            max_tokens=80  # Limit the tokens to ensure the response is concise
        )

        synopsis = response.choices[0].message.content.strip()
        print(f"Synopsis: {synopsis}")

        # Store the synopsis in the dictionary
        synopses[movie_id] = {
            "title": title,
            "synopsis": synopsis,
            "visual_summary": final_response
        }

# Write the synopses to a JSON file
with open("app/synopses.json", "w") as f:
    json.dump(synopses, f, indent=4)

print("Synopses saved to app/synopses.json")
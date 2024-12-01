from flask import redirect, session
from functools import wraps
import sqlite3
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from openai import OpenAI
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# Load API keys
with open("static/api_keys/ElevenLabs.txt", 'r') as f:
    ELEVENLABS_API_KEY = f.read()

with open("static/api_keys/OpenAI.txt", 'r') as f:
    CHATGPT_API_KEY = f.read()

# Load email credentials
with open("static/email.txt") as f:
    file = f.read().split('\n')
    SENDER_EMAIL = file[0]
    EMAIL_PASSWORD = file[1]


speaker_dict = {"Sarah": "EXAVITQu4vr4xnSDxMaL",
                "Arnold": "VR6AewLTigWG4xSOukaG",
                "Rachel": "21m00Tcm4TlvDq8ikWAM",
                "George": "JBFqnCBsd6RMkjVDRZzb",
                "Michael": "flq6f7yk4E4fJM5XTYuZ",
                "Dorothy": "ThT5KcBeYPX3keUQqHPh"}

# Speaker names
SPEAKERS = ["Sarah", "Arnold", "Rachel", "George", "Michael", "Dorothy"]


def get_db_connection(db):
    conn = sqlite3.connect(db)  # Connects to 'database.db' (or creates it if it doesn't exist)
    conn.row_factory = sqlite3.Row  # To access columns by name
    return conn


def login_required(func):

    @wraps(func)
    def decorated_function(*args, **kwargs):

        if not session.get("user_id"):
            return redirect("/login")

        return func(*args, **kwargs)

    return decorated_function


def get_audio_stream(text, speaker, stability=0.5):

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_stream = client.text_to_speech.convert_as_stream(
    voice_id=speaker_dict[speaker],
    optimize_streaming_latency="3",
    output_format="mp3_22050_32",
    text=text,
    voice_settings=VoiceSettings(stability=stability, similarity_boost=0.3),
    )

    for chunk in audio_stream:
        yield chunk


def chatgpt(messages_history):

    client = OpenAI(api_key=CHATGPT_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages_history
    )

    return response.choices[0].message.content


def get_message(role, content):
    message = {"role": role, "content": content}
    return message


def send_email(story_title, story, receiver_email):

    # Define email information
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    # Set message
    message["Subject"] = f"You received a new story: {story_title}!"
    body = f"{story_title}\n\n{story}"
    message.attach(MIMEText(body, "plain"))

    # Send email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)

        server.send_message(message)


def init_site_settings(current_session, user_id):
    current_session["user_id"] = user_id
    current_session["speaker"] = "Sarah"
    current_session["story_sections"] = 5
    current_session["story_audio"] = False
    current_session["voice_guidance"] = False


def reset_story_settings(current_session):
    current_session["location"] = None
    current_session["genre"] = None
    current_session["hero_name"] = None
    current_session["message_history"] = None


def create_hero_name():
    name_prompt = """Give me a first name of main character in a children's book."""
    hero_name = chatgpt([{"role": "user", "content": name_prompt}])
    return hero_name


def create_title(location, genre, hero_name):
    title_prompt = f"""
    I have an idea for a children's book. 
    The main character's name is {hero_name},
    I want it to take place in {location}, 
    and the genre is {genre}.
    Please suggest me a generic title for the story, based on this information only.
    Include the main character's name in it.
    """

    title = chatgpt([{"role": "user", "content": title_prompt}]).replace('"', '')
    return title


def get_initial_prompt(location, genre, hero_name, num_sections):
    initial_prompt = f"""
    Hey, I want you to write an interesting children's story, with a plot twist and a climax.
    I want it to take place in {location}, the genre should be {genre}, and the main character's name is {hero_name}.
    At key points in the story, you should prompt me to choose between two possible actions to determine the direction of the plot.
    Before the first possible action, write "Option 1:".
    Before the second possible action, write "Option 2:".
    When I choose the possible action that I want, the plot should continue according to my choice. Moreover, I do not want you to generate the entire story in 
    advance, I want you to generate each section separately, and wait for my choice before you continue to the next section.
    I want the story to contain {num_sections} sections in total.
    Please don't include the story title and only use alpha numeric characters and standard punctuation marks.
    """
    return initial_prompt


def get_reminder(num_sections_left):
    if num_sections_left > 1:
        reminder = f"I remind you that you need to end the story in {num_sections_left} sections."

    else:
        reminder = "You need to finish the story now."

    return reminder


def get_regen_prompt():
    regen_prompt = """
    I don't like this section, please rewrite it. Make sure that the options you provide are different from the
    options in the section I didn't like.
    """
    return regen_prompt


def get_save_story_prompt():
    prompt = f"""Please write the entire story in one piece, according to the choices I made."""
    return prompt
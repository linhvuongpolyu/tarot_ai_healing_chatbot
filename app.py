import streamlit as st
import os
import random
from PIL import Image
import json
import requests
from openai import OpenAI
import re

# Set custom page configuration
st.set_page_config(
    page_title="EMYP - Tarot AI Healing Chatbot",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Apply custom CSS for styling
BACKGROUND_IMAGE_PATH = "Background.jpg"
st.markdown(
    f"""
    <style>
    body {{
        background: url('{BACKGROUND_IMAGE_PATH}') no-repeat center center fixed;
        background-size: cover;
        font-family: "Georgia", serif;
        color: #333333;
    }}
    .stButton > button {{
        background-color: #f8f9fa;
        color: #333333;
        border-radius: 25px;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background-color: #a8d0e6;
        color: white;
    }}
    .stAudio > audio {{
        margin-top: 20px;
    }}
    .stChatMessage {{
        background-color: #ffffff;
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Load Tarot card meanings from JSON file
CARD_MEANINGS_PATH = "card_meanings.json"
with open(CARD_MEANINGS_PATH, "r", encoding="utf-8") as f:
    card_meanings = json.load(f)

# Define the path to Tarot card images
CARD_IMAGES_PATH = "D:\\MScIME\\SD5913 - Creative Programming for Designers and Artists\\Healing App\\Card"

# Healing music
MUSIC_FILE_PATH = "D:\\MScIME\\SD5913 - Creative Programming for Designers and Artists\\Healing App\\please-calm-my-mind-125566.mp3"
if os.path.exists(MUSIC_FILE_PATH):
    st.audio(MUSIC_FILE_PATH, format="audio/mp3", autoplay=True)
else:
    st.warning("Healing music file not found. Please ensure 'please-calm-my-mind-125566.mp3' is in the correct folder.")

st.title("🌟 EMYP - Tarot AI Healing Chatbot")
st.caption("Explore mindfulness at your pace")

if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
if "messages" in st.session_state:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
else:
    st.session_state.messages = []

if st.session_state.conversation_stage == 0:
    st.chat_message("assistant").write(
        "Hello — I am your Tarot AI, I am here to listen to your story. How are you feeling today?"
    )
    st.session_state.conversation_stage += 1

# Point to the local server
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key="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")

# Ensure only one input box appears at a time
if st.session_state.conversation_stage == 1:
    user_input = st.chat_input(placeholder="Share your thoughts...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Add system prompt as the first message in the conversation
        system_prompt = {"role": "system", "content": "You are an empathetic psychologist with a compassionate point of view. Respond to all user inputs with insightful and supportive guidance."}
        if not any(msg["role"] == "system" for msg in st.session_state.messages):
            st.session_state.messages.insert(0, system_prompt)

        response = client.chat.completions.create(
            model="mistralai/mistral-small-24b-instruct-2501:free",
            messages=st.session_state.messages,
            stream=True,
        )

        msg = ""

        def stream_response():
            global msg
            for chunk in response:
                part = chunk.choices[0].delta.content
                if part:
                    msg += part
                    yield part

        st.chat_message("assistant").write_stream(stream_response)

        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.conversation_stage += 1

# Ensure the draw cards option appears after the first message
if st.session_state.conversation_stage == 2:
    st.chat_message("assistant").write("Would you like to draw Tarot cards to explore your thoughts further?")
    user_input = st.chat_input(placeholder="Type 'yes' to draw cards or 'no' to continue...")
    if user_input:
        if user_input.lower() == "yes":
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write("Great! Let me draw 3 Tarot cards for you.")
            st.session_state.messages.append({"role": "assistant", "content": "Great! Let me draw 3 Tarot cards for you."})
            st.session_state.conversation_stage += 1
        elif user_input.lower() == "no":
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write("No problem! Let me know how else I can assist you.")
            st.session_state.messages.append({"role": "assistant", "content": "No problem! Let me know how else I can assist you."})

if st.session_state.conversation_stage == 3:
    if st.button("Draw 3 Tarot Cards"):
        selected_cards = random.sample(os.listdir(CARD_IMAGES_PATH), 3)
        # Display 3 cards in one row
        st.markdown("<div style='display: flex; justify-content: center; gap: 20px;'>", unsafe_allow_html=True)
        for card_name in selected_cards:
            card_image = Image.open(os.path.join(CARD_IMAGES_PATH, card_name))
            resized_image = card_image.resize((150, 250))  # Resize the image to smaller dimensions
            st.image(resized_image, caption=card_name.split(".")[0], use_container_width=False)
        st.markdown("</div>", unsafe_allow_html=True)

        # Fetch and display card meanings
        advice = "Here are the cards I’ve drawn for you and their meanings based on your current situation:"
        card_summaries = []
        for card_name in selected_cards:
            card_title = re.sub(r"Tarot \d+ ", "", card_name.split(".")[0]).strip()  # Remove prefix and numbers
            card_meaning = card_meanings.get(card_title, {}).get("meaning", "No meaning available.")
            advice += f"\n- {card_title}: {card_meaning}"
            card_summaries.append(card_meaning)

        # Use LLM to summarize the meanings of the 3 cards
        summary_prompt = "Summarize the following Tarot card meanings into a cohesive insight: " + " ".join(card_summaries)
        response = client.chat.completions.create(
            model="mistralai/mistral-small-24b-instruct-2501:free",
            messages=[{"role": "system", "content": "You are an empathetic psychologist with a compassionate point of view."},
                      {"role": "user", "content": summary_prompt}],
            stream=False,
        )
        llm_summary = response.choices[0].message.content.strip()
        advice += f"\n\nSummary Insight: {llm_summary}"
        st.chat_message("assistant").write(advice)
        st.session_state.messages.append({"role": "assistant", "content": advice})
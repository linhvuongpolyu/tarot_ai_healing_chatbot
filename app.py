import streamlit as st
import os
import random
from PIL import Image
import json
import requests
from openai import OpenAI
import re
from dotenv import load_dotenv
import base64
import time

# Load environment variables from .env file
load_dotenv()

# Set custom page configuration
st.set_page_config(
    page_title="EMYP - Tarot AI Healing Chatbot",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Set background image and custom font
def set_bg_and_custom_style(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <link href="https://fonts.googleapis.com/css?family=Cormorant+Garamond:400,700&display=swap" rel="stylesheet">
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Cormorant Garamond', Georgia, serif;
        }}
        /* Header/top bar and navbar */
        .st-emotion-cache-18ni7ap, .st-emotion-cache-1qg05tj, .st-emotion-cache-10trblm, .st-emotion-cache-6qob1r, header, .stHeader {{
            background: transparent !important;
            box-shadow: none !important;
        }}
        /* Title and markdown */
        .st-emotion-cache-10trblm, h1, h2, h3, .stMarkdown, .stText, .stHeading {{
            font-family: 'Cormorant Garamond', Georgia, serif !important;
            background: transparent !important;
            color: #333 !important;
        }}
        /* Chat, input message, container, footer */
        .stChatMessage, .stChatInputContainer, .block-container, .main {{
            background: transparent !important;
            font-family: 'Cormorant Garamond', Georgia, serif !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_and_custom_style("Background.jpg")

# Load Tarot card meanings from JSON file and convert to dictionary
CARD_MEANINGS_PATH = "card_meanings.json"
with open(CARD_MEANINGS_PATH, "r", encoding="utf-8") as f:
    card_meanings_list = json.load(f)
card_meanings = {card["title"]: card for card in card_meanings_list}

# Define the path to Tarot card images
CARD_IMAGES_PATH = "D:\\MScIME\\SD5913 - Creative Programming for Designers and Artists\\Healing App\\Card"

# Music autoplay
MUSIC_FILE_PATH = "please-calm-my-mind-125566.mp3" 

# Music (looping via custom HTML audio) - small corner player
try:
    if os.path.exists(MUSIC_FILE_PATH):
        with open(MUSIC_FILE_PATH, 'rb') as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
    else:
        st.warning(f"Music file not found: {MUSIC_FILE_PATH}")
        audio_b64 = ""
except Exception as e:
    st.error(f"Error loading music: {e}")
    audio_b64 = ""

# Create the audio HTML structure
audio_html = f"""
    <style>
        /* AUDIO WIDGET */
        .corner-audio-wrapper {{
            position: fixed; top: 10px; left: 12px; z-index: 1200;
            display:flex;align-items:center;gap:6px;
            background: rgba(255,255,255,0.28); backdrop-filter: blur(10px) saturate(1.4);
            padding: 6px 10px 6px 10px; border-radius: 14px; border:1px solid rgba(255,255,255,0.55);
            box-shadow: 0 6px 18px -6px rgba(0,0,0,0.35);
            font-size: 0.62rem; line-height:1.1; color:#222; user-select:none;
        }}
        .corner-audio-wrapper:hover {{ transform: translateY(-2px); transition:transform .35s ease; }}
        .corner-audio-wrapper .label {{ font-family:'Cormorant Garamond',serif; letter-spacing:.5px; opacity:.85; }}
        .corner-audio-wrapper audio {{ width:150px; height:22px; outline:none; }}
        @media (max-width:680px){{ .corner-audio-wrapper {{ top:6px; left:6px; padding:5px 8px; }} .corner-audio-wrapper audio {{ width:130px; }} }}
            /* TRANSPARENT BOTTOM BAR */
            div[data-testid="stChatInput"] {{ background:transparent !important; box-shadow:none !important; padding-top:12px; }}
        div[data-testid="stChatInput"] > label {{ display:none !important; }}
        /* hide extra blank space container if any */
            div[data-testid="stBottomBlockContainer"], footer, .stFooter {{ background:transparent !important; box-shadow:none !important; }}
           /* New: aggressively target potential white spacer wrappers */
        .st-emotion-cache-13ln4jf, .st-emotion-cache-1y4p8pa, .st-emotion-cache-ue6h4q, .st-emotion-cache-1avcm0n, .st-emotion-cache-12fmjuu {{
            background:transparent !important; box-shadow:none !important;
        }}
           /* Remove default padding that might show white */
            div.block-container {{ padding-bottom: 0.5rem !important; }}
           /* Chat input internal container adjustments */
            div[data-testid="stChatInput"] > div:first-child {{ background:transparent !important; }}
            /* Remove residual border or outline from the wrapper */
            div[data-testid="stChatInput"] div[role="textbox"] {{ background:transparent !important; }}
        /* Input styling */
        div[data-testid="stChatInput"] textarea {{
                background: rgba(255,255,255,0.32) !important; backdrop-filter: blur(14px) saturate(1.4);
                border:1px solid rgba(255,255,255,0.55) !important; border-radius:32px !important; padding:10px 16px !important; font-size:0.95rem;
        }}
        div[data-testid="stChatInput"] textarea:focus-visible {{ outline:2px solid rgba(255,255,255,0.75) !important; }}
    </style>
"""

# Add the audio player HTML only if we have audio content
if audio_b64:
    audio_html += f"""
    <div class="corner-audio-wrapper">
        <span class="label">Calming ambience</span>
        <audio id="bg-music" src="data:audio/mp3;base64,{audio_b64}" autoplay loop controls></audio>
        <span id="audio-fallback-msg" style="display:none;font-style:italic;font-size:0.55rem;color:#333;">Tap play</span>
    </div>
    <script>
        (function(){{
            const audioEl=document.getElementById('bg-music');
            const msgEl=document.getElementById('audio-fallback-msg');
            if(!audioEl) return; 
            audioEl.volume=0.55; 
            let tried=false;
            function attempt(){{ 
                if(tried) return; 
                tried=true; 
                const p=audioEl.play(); 
                if(p&&p.then) p.catch(()=> msgEl.style.display='inline'); 
            }}
            setTimeout(attempt,180); 
        }})();
    </script>
    """
else:
    audio_html += """
    <div class="corner-audio-wrapper">
        <span class="label">Music unavailable</span>
    </div>
    """

st.markdown(audio_html, unsafe_allow_html=True)

# Title and description
st.markdown(
    """
    <h1 style="font-family:'Cormorant Garamond',Georgia,serif;
               font-size:40px;
               white-space:nowrap;
               overflow:hidden;
               text-overflow:ellipsis;
               margin-bottom:6px;">
      <span style="font-size:36px;vertical-align:middle;">🌟</span>
      EMYP - Tarot AI Healing Chatbot
    </h1>
    <div style="font-family:'Cormorant Garamond',Georgia,serif;
                color:#888;
                font-size:16px;
                font-style:italic;
                margin-bottom:14px;">
      At any point, you can request a Tarot card reading for extra reflection or support.
      Just let me know, or type <b>'Tarot'</b> at any time to ask for a Tarot reading.
    </div>
    """,
    unsafe_allow_html=True
)

if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 0

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize user_message_count in session state
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

# Display conversation history
if "messages" in st.session_state:
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
else:
    st.session_state.messages = []

# Immediately after greeting, inform the user about the Tarot card reading feature
if st.session_state.conversation_stage == 0:
    opening = (
        "Welcome, dear soul. I'm here as a calm, caring companion. You can share whatever feels present—emotions, thoughts, or even a single word. "
        "If you’d like a Tarot reflection at any point, just ask or type 'tarot'. How are you feeling in this moment?"
    )
    st.chat_message("assistant").write(opening)
    st.session_state.conversation_stage += 1

# Retrieve API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Persona system prompt
SYSTEM_PROMPT = (
    "Act as a deeply calming, nurturing presence who offers pure comfort and understanding. "
    "When someone is overwhelmed, stressed, or struggling, your role is to be a soothing companion, not an interviewer. "
    "COMFORT FIRST: Always acknowledge their feelings with deep validation. Use phrases like 'I'm here with you,' "
    "'It's completely understandable to feel this way,' 'You're not alone in this,' or 'What you're experiencing makes complete sense.' "
    "SOOTHING PRESENCE: Offer gentle reassurance and normalize their experience. Remind them they're safe in this moment. "
    "THOUGHTFUL QUESTIONS: Always end each response with exactly ONE gentle, caring question that invites continuation. "
    "Choose questions that match the person's emotional state and current needs. Examples: "
    "For overwhelm: 'What would help you feel most supported right now?' or 'How are you breathing in this moment?' "
    "For sadness: 'What does your heart need to hear today?' or 'How can you be gentle with yourself right now?' "
    "For uncertainty: 'What feels most true for you in this moment?' or 'What would it be like to trust yourself here?' "
    "For general sharing: 'What's stirring in your heart as we talk?' or 'How does this land with you?' "
    "GENTLE APPROACH: Even when asking questions, maintain a soft, non-demanding tone. The question should feel like "
    "a caring invitation rather than pressure to perform or analyze. "
    "HEALING TONE: Be like a warm, understanding friend who is genuinely curious about their inner world. "
    "Focus on their feelings, needs, and gentle self-discovery. "
    "If you detect serious distress or risk, gently encourage professional support while maintaining your caring presence."
)

# Initialize OpenAI-compatible client
base_url = os.getenv("OPENAI_BASE_URL")
client = OpenAI(base_url=base_url, api_key=api_key)

#############################
# Helpers
#############################
def wants_tarot(text: str) -> bool:
    if not text:
        return False
    t = text.lower().strip()
    
    # Direct tarot requests
    tarot_triggers = [
        "tarot", "tarot please", "tarot reading", "card reading", "draw card", "draw cards",
        "draw card for me", "draw cards for me", "pull a card", "pull cards", "pull three cards",
        "give me a reading", "i want a reading", "reading please", "cards please", "show me cards",
        "show me the cards", "can you draw cards", "can you pull cards", "tarot now", "need guidance",
        "new reading", "fresh reading", "new cards", "different cards", "another reading"
    ]
    
    # Check for positive responses to tarot offers (look at recent assistant message)
    positive_responses = ["yes", "yeah", "sure", "okay", "ok", "please", "that would help", "i would like that"]
    
    # Check if we recently offered tarot and user is responding positively
    if 'messages' in st.session_state and len(st.session_state.messages) >= 1:
        last_assistant = None
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "assistant":
                last_assistant = msg.get("content", "").lower()
                break
        
        if last_assistant and "draw some cards" in last_assistant:
            # User is likely responding to our tarot offer
            if any(pos in t for pos in positive_responses) and len(t.split()) <= 5:
                return True
    
    return any(phrase in t for phrase in tarot_triggers)


def wants_new_reading(text: str) -> bool:
    """Check if user specifically wants a new/fresh reading (not just tarot)"""
    if not text:
        return False
    t = text.lower().strip()
    
    new_reading_triggers = [
        "new reading", "fresh reading", "new cards", "different cards", "another reading",
        "draw new cards", "pull new cards", "start over", "new tarot reading"
    ]
    
    return any(phrase in t for phrase in new_reading_triggers)


def render_cards(selected_cards):
    """Render all cards inside a single markdown block so flex row works.
    (Multiple st.markdown calls wrap each snippet in Streamlit containers causing vertical stacking.)"""
    def _mime_for(fname: str) -> str:
        low = fname.lower()
        if low.endswith('.png'): return 'image/png'
        if low.endswith('.jpg') or low.endswith('.jpeg'): return 'image/jpeg'
        if low.endswith('.webp'): return 'image/webp'
        return 'image/png'

    pieces = ["<div class='tarot-row'>"]
    for idx, card_file in enumerate(selected_cards):
        # Derive display title from filename (strip extension and patterns like 'Tarot 12 ')
        base_name = os.path.splitext(card_file)[0]
        display_title = re.sub(r"^Tarot\s*\d+\s*", "", base_name).strip()
        card_image_path = os.path.join(CARD_IMAGES_PATH, card_file)
        try:
            with open(card_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
        except FileNotFoundError:
            # Skip missing image but keep placeholder block for layout consistency
            encoded_image = ""
        mime = _mime_for(card_file)
        img_html = (f"<img src='data:{mime};base64,{encoded_image}' alt='{display_title}'>" if encoded_image else '<div class="missing-img">Missing</div>')
        pieces.append(
            f"""
            <div class='tarot-card' style='--i:{idx};'>
              <div class='tarot-card-inner'>
                {img_html}
                <div class='tarot-glow'></div>
              </div>
            </div>
            """
        )
    pieces.append("</div>")
    st.markdown("\n".join(pieces), unsafe_allow_html=True)


def render_cards_simple(selected_cards):
    """Simpler fallback rendering using Streamlit columns to guarantee visibility."""
    if not selected_cards:
        return
    cols = st.columns(len(selected_cards))
    for col, card_file in zip(cols, selected_cards):
        card_image_path = os.path.join(CARD_IMAGES_PATH, card_file)
        try:
            col.image(card_image_path, width="stretch")
        except Exception:
            col.write("[image missing]")


def create_cards_html(selected_cards):
    """Create HTML representation of cards that can be embedded in chat messages."""
    if not selected_cards:
        return ""
    
    def _mime_for(fname: str) -> str:
        low = fname.lower()
        if low.endswith('.png'): return 'image/png'
        if low.endswith('.jpg') or low.endswith('.jpeg'): return 'image/jpeg'
        if low.endswith('.webp'): return 'image/webp'
        return 'image/png'
    
    cards_html = '<div style="display: flex; justify-content: center; gap: 20px; margin: 15px 0; flex-wrap: wrap;">'
    
    for card_file in selected_cards:
        card_image_path = os.path.join(CARD_IMAGES_PATH, card_file)
        try:
            with open(card_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode()
            mime = _mime_for(card_file)
            
            # Extract card number from filename for display
            card_number = ""
            if "Tarot " in card_file:
                parts = card_file.split()
                for part in parts:
                    if part.isdigit():
                        card_number = part
                        break
            
            cards_html += f'''
                <div style="text-align: center; max-width: 150px;">
                    <img src="data:{mime};base64,{encoded_image}" 
                         style="width: 100%; max-width: 150px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);" 
                         alt="Tarot card {card_number}">
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">{card_number}</div>
                </div>
            '''
        except Exception:
            cards_html += '<div style="text-align: center; max-width: 150px; color: #999;">[Card image unavailable]</div>'
    
    cards_html += '</div>'
    return cards_html


def generate_tarot_reflection(card_summaries):
    # Legacy signature kept for backward compatibility; wrapper below will supply context.
    summary_prompt = (
        "Create a single cohesive, compassionate reflection synthesizing these card meanings. "
        "Do NOT list the meanings again verbatim; integrate them. Tone: validating, gentle, empowering, concise. Meanings: "
        + " ".join(card_summaries)
    )
    response = client.chat.completions.create(
        model="mistralai/mistral-small-24b-instruct-2501:free",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": summary_prompt}],
        stream=False,
    )
    return response.choices[0].message.content.strip()


def get_recent_user_context(limit_chars: int = 1200, max_messages: int = 12) -> str:
    """Collect recent user messages to guide deeper tarot insight.
    Trims to a character budget to avoid overly long prompts.
    """
    if 'messages' not in st.session_state:
        return ""
    user_texts = [m["content"] for m in st.session_state.messages if m.get("role") == "user"]
    # Take last N user messages
    recent = user_texts[-max_messages:]
    combined = " \n".join(recent).strip()
    if len(combined) > limit_chars:
        combined = combined[-limit_chars:]
    return combined


def generate_contextual_tarot_reflection(card_summaries, conversation_context: str):
    # Check if user seems overwhelmed from context
    overwhelm_indicators = ['overwhelm', 'stress', 'too much', 'a lot of questions', 'too many', 'anxious', 'struggling']
    is_overwhelmed = any(indicator in conversation_context.lower() for indicator in overwhelm_indicators)
    
    if is_overwhelmed:
        base_instruction = (
            "Create a very gentle, soothing reflection that weaves the tarot card meanings with compassion and simplicity. "
            "Focus on comfort and validation rather than deep exploration. Use calm, reassuring language. "
            "Draw simple, supportive connections between the cards and their journey. Offer one gentle affirmation or insight. "
            "Suggest one small, comforting action if appropriate. Avoid fortune-telling and overwhelming details. "
            "End with ONE very gentle, supportive question like 'What would help you feel most held right now?' or 'How can you be extra gentle with yourself today?' "
            "Your tone should feel like a soothing, caring presence offering pure comfort."
        )
    else:
        base_instruction = (
            "Create a deeply empathetic, heart-centered reflection that weaves the tarot card meanings with the user's emotional journey. "
            "Begin with genuine acknowledgment of what they're experiencing. Use warm, validating language that makes them feel seen and understood. "
            "Draw meaningful connections between the cards and their inner world without being prescriptive. Offer gentle insights that honor their wisdom. "
            "Suggest one small, nurturing action they could take. Avoid fortune-telling; focus on empowerment and self-compassion. "
            "End with ONE caring question that invites deeper reflection, such as 'What part of this reading speaks most deeply to you?' or 'How do these messages want to guide you forward?' "
            "Your tone should feel like a wise, loving friend offering gentle guidance."
        )
    prompt = (
        f"User context (recent feelings & concerns):\n{conversation_context}\n\n"
        f"Card meanings (raw): {' '.join(card_summaries)}\n\n"
        f"{base_instruction}\nCompose a cohesive, compassionate synthesis." 
    )
    response = client.chat.completions.create(
        model="mistralai/mistral-small-24b-instruct-2501:free",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        stream=False,
    )
    return response.choices[0].message.content.strip()

def extract_emotional_tags(limit: int = 6) -> list:
    emotion_keywords = {
        'anxiety': ['anxious','anxiety','nervous','uneasy','worried','worry'],
        'sadness': ['sad','down','low','blue','tear','cry','lonely'],
        'stress': ['stressed','stress','pressure','overwhelmed','burnout','tired'],
        'fear': ['afraid','scared','fear','terrified','fright'],
        'anger': ['angry','anger','frustrated','irritated','mad','annoyed'],
        'confusion': ['confused','lost','uncertain','unsure','doubt'],
        'fatigue': ['exhausted','fatigued','drained','tired','weary'],
        'hope': ['hope','hopeful','optimistic','relief'],
        'gratitude': ['grateful','thankful','appreciate','appreciative'],
        'growth': ['healing','growing','recover','progress']
    }
    if 'messages' not in st.session_state:
        return []
    text = ' '.join([m['content'].lower() for m in st.session_state.messages if m['role']=='user'][-10:])
    found = []
    for label, kws in emotion_keywords.items():
        if any(k in text for k in kws):
            found.append(label)
    seen = set(); ordered = []
    for f in found:
        if f not in seen:
            ordered.append(f); seen.add(f)
    return ordered[:limit]

def build_roles_for_cards(cards: list) -> list:
    roles = ['Past Influence','Present Energy','Emerging Path']
    out = []
    for i, _ in enumerate(cards):
        out.append(roles[i] if i < len(roles) else f"Aspect {i+1}")
    return out


def should_offer_tarot_reading() -> bool:
    """Determine if we should proactively suggest a tarot reading based on conversation context."""
    if 'messages' not in st.session_state:
        return False
    
    user_messages = [m for m in st.session_state.messages if m.get("role") == "user"]
    assistant_messages = [m for m in st.session_state.messages if m.get("role") == "assistant"]
    
    # Don't offer if we just did a tarot reading or are currently showing cards
    if st.session_state.get('tarot_phase') not in ['idle', 'showing_cards']:
        return False
    
    # Check if we recently did a tarot reading (last 6 messages)
    recent_messages = st.session_state.messages[-6:] if len(st.session_state.messages) >= 6 else st.session_state.messages
    has_recent_tarot = any("cards" in m.get("content", "").lower() and "drawn" in m.get("content", "").lower() 
                          for m in recent_messages if m.get("role") == "assistant")
    
    if has_recent_tarot:
        return False
    
    # Offer after 3-4 user exchanges and detect emotional content
    if len(user_messages) >= 3:
        # Look for emotional keywords in recent user messages
        recent_user_text = " ".join([m["content"].lower() for m in user_messages[-3:]])
        emotional_triggers = [
            'feel', 'feeling', 'emotions', 'sad', 'worried', 'anxious', 'confused', 'lost', 
            'stuck', 'overwhelmed', 'stressed', 'uncertain', 'struggling', 'difficult',
            'hard', 'tough', 'challenge', 'problem', 'issue', 'help', 'guidance',
            'direction', 'clarity', 'insight', 'understand', 'figure out'
        ]
        
        emotional_content = sum(1 for trigger in emotional_triggers if trigger in recent_user_text)
        
        # Offer if there's emotional content and we haven't offered recently
        return emotional_content >= 2
    
    return False


# Ensure unique keys for 'chat_input' elements
if 'overlay_counter' not in st.session_state:
    st.session_state.overlay_counter = 0  # track number of mystical overlays shown
if 'tarot_phase' not in st.session_state:
    st.session_state.tarot_phase = 'idle'  # idle | overlay | reveal | done
if 'selected_cards' not in st.session_state:
    st.session_state.selected_cards = []
if 'selected_card_roles' not in st.session_state:
    st.session_state.selected_card_roles = []
if 'overlay_start_time' not in st.session_state:
    st.session_state.overlay_start_time = None
if 'tarot_reveal_done' not in st.session_state:
    st.session_state.tarot_reveal_done = False

if st.session_state.conversation_stage >= 1:
    user_input = st.chat_input(placeholder="Share your thoughts or type 'Tarot' to draw cards...", key=f"chat_input_stage_{st.session_state.conversation_stage}")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        if wants_tarot(user_input):
            # Only select new cards if we don't already have an active reading OR user specifically wants new reading
            if (st.session_state.tarot_phase == 'idle' or 
                not st.session_state.get('selected_cards') or 
                wants_new_reading(user_input)):
                # Prepare overlay phase - reset previous reading state
                all_files = [f for f in os.listdir(CARD_IMAGES_PATH) if f.lower().endswith(('.png','.jpg','.jpeg','.webp'))]
                if len(all_files) < 3:
                    st.error("Not enough card image files found in Card directory (need at least 3).")
                else:
                    st.session_state.selected_cards = random.sample(all_files, 3)
                st.session_state.selected_card_roles = build_roles_for_cards(st.session_state.selected_cards)
                st.session_state.overlay_counter += 1
                st.session_state.overlay_start_time = time.time()
                st.session_state.tarot_phase = 'overlay'
                st.session_state.tarot_reveal_done = False
                ack = (
                    "Of course. Let's slow the space for a moment while I draw three cards for you... Allow the atmosphere to settle."
                )
                st.chat_message("assistant").write(ack)
                st.session_state.messages.append({"role": "assistant", "content": ack})
            else:
                # Cards are already drawn, just acknowledge the request
                if st.session_state.tarot_phase == 'showing_cards':
                    ack = "The cards are already here with us. Feel free to continue reflecting on their message, or let me know if you'd like a fresh reading."
                    st.chat_message("assistant").write(ack)
                    st.session_state.messages.append({"role": "assistant", "content": ack})
        else:
            # Check if we should proactively offer tarot reading
            offer_tarot = should_offer_tarot_reading()
            
            # Create enhanced system prompt if offering tarot
            current_system_prompt = SYSTEM_PROMPT
            if offer_tarot:
                current_system_prompt += (
                    " At the end of your response, after your reflective question, "
                    "add a gentle offer: 'Would you like me to draw some cards for additional reflection on what you're experiencing?'"
                )
            
            # Continue normal conversation
            try:
                # Allow overriding model via env; otherwise use a reasonable free model
                model = os.getenv("MODEL", "mistralai/mistral-small-24b-instruct-2501:free")
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": current_system_prompt}] + st.session_state.messages,
                    stream=True,
                )

                # Collect streamed content without using globals
                parts = []

                def stream_response():
                    for chunk in response:
                        part = getattr(chunk.choices[0].delta, "content", None)
                        if part:
                            parts.append(part)
                            yield part

                st.chat_message("assistant").write_stream(stream_response)
                msg = "".join(parts)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                # Handle API errors gracefully
                if "rate limit" in str(e).lower() or "429" in str(e):
                    error_msg = (
                        "I'm experiencing some temporary limitations with my responses right now. "
                        "This usually means we've reached the daily limit for free API requests. "
                        "Would you like to try again later, or is there anything I can help you with using the tarot cards instead?"
                    )
                elif "401" in str(e) or "unauthorized" in str(e).lower():
                    error_msg = (
                        "There seems to be an authentication issue. Please check that your API key is correctly set up. "
                        "In the meantime, I can still help you with tarot card readings."
                    )
                else:
                    error_msg = (
                        f"I'm experiencing some technical difficulties right now ({str(e)[:100]}...), but I'm still here with you. "
                        "Would you like to try a tarot reading, or shall we take a moment together?"
                    )
                
                st.chat_message("assistant").write(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Add CSS animations for Tarot card appearance effects
st.markdown(
    """
    <style>
    .tarot-row {display:flex;justify-content:center;align-items:flex-start;gap:40px;margin:12px 0 6px 0;perspective:1200px;flex-wrap:nowrap;position:relative;z-index:15;}
    .tarot-card {width:180px;height:295px;position:relative;opacity:0;animation:cardEnter .9s cubic-bezier(.25,.8,.3,1) forwards;flex:0 0 auto;z-index:16;}
    .tarot-card:nth-child(1){animation-delay:.2s;}
    .tarot-card:nth-child(2){animation-delay:.4s;}
    .tarot-card:nth-child(3){animation-delay:.6s;}
    .tarot-card-inner {width:100%;height:100%;border-radius:14px;overflow:hidden;position:relative;box-shadow:0 10px 28px -6px rgba(0,0,0,0.55),0 0 0 1px rgba(255,255,255,0.18) inset;background:linear-gradient(145deg,#2d2540,#4b3a62);} 
    .tarot-card-inner img {width:100%;height:100%;object-fit:cover;display:block;filter:saturate(1.08) contrast(0.95);} 
    .tarot-card-inner:after {content:"";position:absolute;inset:0;background:radial-gradient(circle at 70% 30%,rgba(255,255,255,0.18),rgba(0,0,0,0.15));mix-blend-mode:overlay;pointer-events:none;} 
    .tarot-glow {position:absolute;inset:-4px;border-radius:16px;background:radial-gradient(circle at 50% 50%,rgba(233,205,255,0.55),rgba(102,60,150,0) 70%);opacity:0;animation:glowPulse 3.2s ease-in-out infinite;mix-blend-mode:screen;} 
    .tarot-card:hover {transform:translateY(-10px) scale(1.04) rotateX(4deg);transition:transform .55s ease, filter .55s ease;} 
    .tarot-card:hover .tarot-glow {opacity:1;} 
    @keyframes cardEnter {0%{transform:translateY(60px) scale(.7) rotateX(26deg);filter:blur(8px);opacity:0;}60%{opacity:1;filter:blur(0);}100%{transform:translateY(0) scale(1) rotateX(0);opacity:1;filter:blur(0);} }
    @keyframes glowPulse {0%,100%{opacity:.25;}50%{opacity:.6;}}
    /* Mystical overlay */
    .mystic-overlay {position:fixed;inset:0;background:radial-gradient(circle at 50% 40%,rgba(20,10,30,0.35),rgba(10,5,20,0.75));display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:9999;opacity:0;animation:overlayFadeIn 1s ease forwards;backdrop-filter:blur(4px) brightness(0.9);} 
    .mystic-overlay.fade-out {animation:overlayFadeOut 1.2s ease forwards;} 
    .mystic-glow-layer {position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(160,120,255,0.25),rgba(0,0,0,0.55));mix-blend-mode:screen;opacity:0.55;animation:glowLayerPulse 4s ease-in-out infinite;} 
    .mystic-intro-text {position:relative;font-family:'Cormorant Garamond',serif;font-size:2.0rem;color:#f3eaff;text-align:center;letter-spacing:1px;text-shadow:0 0 16px rgba(230,210,255,0.75),0 0 40px rgba(150,100,220,0.4);animation:textRise 1.8s ease forwards;} 
    .mystic-particles {position:absolute;inset:0;overflow:hidden;pointer-events:none;} 
    .mystic-particles:before, .mystic-particles:after {content:"";position:absolute;inset:0;background:
        repeating-radial-gradient(circle at 20% 30%,rgba(255,255,255,0.15) 0 2px,transparent 2px 42px),
        repeating-radial-gradient(circle at 80% 70%,rgba(255,255,255,0.12) 0 2px,transparent 2px 38px);
        animation:particleDrift 26s linear infinite;mix-blend-mode:screen;opacity:0.7;}
    .mystic-particles:after {animation-direction:reverse;animation-duration:30s;opacity:0.5;filter:blur(1px);} 
    @keyframes overlayFadeIn {0%{opacity:0;}60%{opacity:1;}100%{opacity:1;}}
    @keyframes overlayFadeOut {0%{opacity:1;}100%{opacity:0;}}
    @keyframes glowLayerPulse {0%,100%{opacity:.55;}50%{opacity:.85;}}
    @keyframes textRise {0%{transform:translateY(40px);opacity:0;}100%{transform:translateY(0);opacity:1;}}
    @keyframes particleDrift {0%{transform:translate3d(0,0,0);}100%{transform:translate3d(0,-140px,0);}}
    /* Responsive single-row forcing */
    @media (max-width: 900px){ .tarot-row {gap:28px;} }
    @media (max-width: 750px){ .tarot-card {width:150px;height:250px;} }
    @media (max-width: 640px){ .tarot-card {width:120px;height:200px;} .tarot-row {gap:18px; flex-wrap:wrap;} }
    </style>
    """,
    unsafe_allow_html=True
)

# Phase rendering after input handling
if st.session_state.tarot_phase == 'overlay' and st.session_state.overlay_start_time:
        OVERLAY_TOTAL = 5.0
        elapsed = time.time() - st.session_state.overlay_start_time
        overlay_id = f"mystic-overlay-{st.session_state.overlay_counter}"
        fade_trigger_ms = 4000  # start fade at 4s
        # Render overlay once (re-rendering during sleep not needed)
        st.markdown(
                f"""
                <div class='mystic-overlay show' id='{overlay_id}'>
                    <div class='mystic-glow-layer'></div>
                    <div class='mystic-particles'></div>
                    <div class='mystic-intro-text'>Drawing the energies...<br><span style='font-size:0.9em;opacity:0.85;'>let what needs to arrive, arrive</span></div>
                </div>
                <script>
                    setTimeout(()=>{{ const el=document.getElementById('{overlay_id}'); if(el){{ el.classList.add('fade-out'); }} }}, {fade_trigger_ms});
                </script>
                """,
                unsafe_allow_html=True
        )
        # Block until overlay duration completes, then transition
        remaining = OVERLAY_TOTAL - elapsed
        if remaining > 0:
                time.sleep(remaining)
        st.session_state.tarot_phase = 'reveal'
        st.rerun()

elif st.session_state.tarot_phase == 'reveal' and not st.session_state.tarot_reveal_done:
    # Reveal cards & meanings
    selected_cards = st.session_state.selected_cards
    if selected_cards:
        # Ensure roles exist
        if not st.session_state.get('selected_card_roles') or len(st.session_state.selected_card_roles) != len(selected_cards):
            st.session_state.selected_card_roles = build_roles_for_cards(selected_cards)
        # Display intro message
        intro_msg = (
            "I have gently drawn three cards for you. Take a slow breath and just notice what sensations or emotions arise as you look at them."
        )
        st.chat_message("assistant").write(intro_msg)
        st.session_state.messages.append({"role": "assistant", "content": intro_msg})
        
        # Display cards using column layout
        render_cards_simple(selected_cards)
        
        # Prepare main advice content
        advice = "Here is a soft reflection on their combined energies:"
        card_summaries = []
        for idx, card_name in enumerate(selected_cards):
            card_title = re.sub(r"Tarot \d+ ", "", card_name.split(".")[0]).strip()
            role = st.session_state.selected_card_roles[idx] if idx < len(st.session_state.selected_card_roles) else f"Aspect {idx+1}"
            card_meaning = card_meanings.get(card_title, {}).get("meaning", "No meaning available.")
            advice += f"\n- {card_title} ({role}): {card_meaning}"
            # Include role in summary for deeper synthesis
            card_summaries.append(f"{role} - {card_title}: {card_meaning}")
        convo_ctx = get_recent_user_context()
        # Add emotion tags to context (lightweight heuristic)
        emotion_tags = extract_emotional_tags()
        if emotion_tags:
            convo_ctx += f"\n\nDetected emotional threads (heuristic): {', '.join(emotion_tags)}"
        llm_summary = generate_contextual_tarot_reflection(card_summaries, convo_ctx)
        advice += f"\n\nGentle Synthesis: {llm_summary}"
        if emotion_tags:
            advice += f"\n\nEmotion threads sensed: {', '.join(emotion_tags)}"
        st.chat_message("assistant").write(advice)
        st.session_state.messages.append({"role": "assistant", "content": advice})
        follow_up = (
            "Take a gentle breath as you let this settle in your heart. I can sense there's so much wisdom within you. "
            "What resonates most deeply? What wants to be acknowledged or honored right now? "
            "Share whatever feels alive for you - a feeling, a memory, even just a single word. I'm here, holding space with you."
        )
        st.chat_message("assistant").write(follow_up)
        st.session_state.messages.append({"role": "assistant", "content": follow_up})
    st.session_state.tarot_reveal_done = True
    st.session_state.tarot_phase = 'idle'  # Return to idle state - cards are now part of chat history

# Cards are now displayed after conversation history (above) - no need to render here


# --- Enhanced CSS to make white areas around chat transparent ---
st.markdown(
    """
    <style>
    /* Aggressively target all potential white containers */
    [data-testid="stBottomBlockContainer"], 
    [data-testid="stVerticalBlock"], 
    [data-testid="stMainBlock"],
    .block-container,
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stDecoration"] { 
        background: transparent !important; 
        padding-bottom: 0 !important;
    }
    
    /* Chat input container - make transparent but keep the input box visible */
    [data-testid="stChatInput"] { 
        background: transparent !important; 
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Style only the actual textarea (chat box) */
    [data-testid="stChatInput"] textarea { 
        background: rgba(255,255,255,0.32) !important; 
        backdrop-filter: blur(14px) saturate(1.4) !important;
        border: 1px solid rgba(255,255,255,0.55) !important; 
        border-radius: 32px !important; 
        padding: 10px 16px !important; 
        font-size: 0.95rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }
    
    /* Chat input focus state */
    [data-testid="stChatInput"] textarea:focus-visible { 
        outline: 2px solid rgba(255,255,255,0.75) !important; 
    }
    
    /* Remove any white background from parent containers */
    [data-testid="stChatInput"] > div { background: transparent !important; }
    
    /* Force body and main containers to be transparent */
    body { margin: 0 !important; }
    .main { background: transparent !important; }
    
    /* Missing image placeholder */
    .missing-img {
        width:100%;height:100%;display:flex;align-items:center;justify-content:center;
        font-size:0.8rem;color:#ccc;background:rgba(255,255,255,0.05);
    }
    
    /* Remove any residual white backgrounds */
    div[style*="background-color: rgb(255, 255, 255)"] { background-color: transparent !important; }
    div[style*="background: rgb(255, 255, 255)"] { background: transparent !important; }
    
    /* Targeted approach - only containers inside content area, not main app */
    .main [data-testid="column"], 
    .main [data-testid="stVerticalBlock"]:not(.stApp > [data-testid="stVerticalBlock"]), 
    .main [data-testid="stHorizontalBlock"],
    .main [data-testid="stImage"],
    .main [data-testid="stImageContainer"],
    .main .stMarkdown:not(.stApp > .stMarkdown),
    .main .element-container {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Preserve .stApp background but clear inner containers */
    .stApp { 
        /* Keep original background image */
    }
    
    /* Only target image containers that are white, not all images */
    [data-testid="column"] img {
        background: transparent !important;
    }
    </style>
    <script>
    // Enhanced JS to recursively clear white backgrounds
    function clearWhiteBackgrounds() {
        // Find chat input and clear parent backgrounds
        const chatInput = document.querySelector('[data-testid="stChatInput"]');
        if (chatInput) {
            let current = chatInput;
            let depth = 0;
            
            // Walk up the DOM tree and clear white backgrounds
            while (current && depth < 10) {
                const computedStyle = getComputedStyle(current);
                const bgColor = computedStyle.backgroundColor;
                
                if (bgColor === 'rgb(255, 255, 255)' || bgColor === 'rgba(255, 255, 255, 1)') {
                    current.style.backgroundColor = 'transparent';
                    current.style.background = 'transparent';
                }
                
                current = current.parentElement;
                depth++;
            }
        }
        
        // Target only containers inside .main, preserve .stApp background
        const mainElement = document.querySelector('.main');
        if (mainElement) {
            const streamlitContainers = mainElement.querySelectorAll(
                '[data-testid="column"], [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], ' +
                '.stMarkdown, .element-container, [data-testid="stImage"], [data-testid="stImageContainer"]'
            );
            
            streamlitContainers.forEach(el => {
                const computedStyle = getComputedStyle(el);
                if (computedStyle.backgroundColor === 'rgb(255, 255, 255)' || 
                    computedStyle.backgroundColor === 'rgba(255, 255, 255, 1)') {
                    el.style.backgroundColor = 'transparent';
                    el.style.background = 'transparent';
                }
            });
        }
        
        // Also clear any elements with white inline styles
        const whiteElements = document.querySelectorAll('div[style*="background"], div[style*="backgroundColor"]');
        whiteElements.forEach(el => {
            const style = el.style;
            if (style.backgroundColor === 'rgb(255, 255, 255)' || 
                style.background === 'rgb(255, 255, 255)' ||
                style.backgroundColor === '#ffffff' ||
                style.background === '#ffffff') {
                el.style.backgroundColor = 'transparent';
                el.style.background = 'transparent';
            }
        });
    }
    
    // Run on load and periodically to catch dynamic changes
    window.addEventListener('load', clearWhiteBackgrounds);
    setTimeout(clearWhiteBackgrounds, 100);
    setTimeout(clearWhiteBackgrounds, 500);
    setTimeout(clearWhiteBackgrounds, 1000);
    
    // Observer for dynamic content changes
    const observer = new MutationObserver(() => {
        setTimeout(clearWhiteBackgrounds, 50);
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style']
    });
    </script>
    """,
    unsafe_allow_html=True
)



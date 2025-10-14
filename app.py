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
if os.path.exists(MUSIC_FILE_PATH):
    audio_bytes = open(MUSIC_FILE_PATH, 'rb').read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
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
        <div class="corner-audio-wrapper">
            <span class="label">Calming ambience</span>
            <audio id="bg-music" src="data:audio/mp3;base64,{audio_b64}" autoplay loop controls></audio>
            <span id="audio-fallback-msg" style="display:none;font-style:italic;font-size:0.55rem;color:#333;">Tap play</span>
        </div>
        <script>
            (function(){{
                const audioEl=document.getElementById('bg-music');
                const msgEl=document.getElementById('audio-fallback-msg');
                if(!audioEl) return; audioEl.volume=0.55; let tried=false;
                function attempt(){{ if(tried) return; tried=true; const p=audioEl.play(); if(p&&p.then) p.catch(()=> msgEl.style.display='inline'); }}
                setTimeout(attempt,180); audioEl.addEventListener('ended',()=>{{ audioEl.currentTime=0; audioEl.play(); }});
            }})();
        </script>
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
    "Act as an empathetic psychologist providing supportive, insightful, and non-judgmental guidance in every response. "
    "Acknowledge the user's feelings, validate their emotional experience, ask gentle open-ended questions to deepen reflection, "
    "and suggest one or two small, compassionate self-care steps. Keep language warm, grounded, and empowering. "
    "If you detect signs of serious distress, self-harm, or risk, gently encourage seeking professional help or trusted support. "
    "Do not be clinical; be human-centered, calming, and hopeful. Avoid overwhelming lists. "
    "Always end EXACTLY ONE concise, gentle, open reflective question (no multiple questions, no numbered list)."
)

# Initialize OpenAI client
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=api_key)

#############################
# Helpers
#############################
def wants_tarot(text: str) -> bool:
    if not text:
        return False
    t = text.lower().strip()
    triggers = [
        "tarot", "tarot please", "tarot reading", "card reading", "draw card", "draw cards",
        "draw card for me", "draw cards for me", "pull a card", "pull cards", "pull three cards",
        "give me a reading", "i want a reading", "reading please", "cards please", "show me cards",
        "show me the cards", "can you draw cards", "can you pull cards", "tarot now", "need guidance"
    ]
    return any(phrase in t for phrase in triggers)


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
            col.image(card_image_path, use_column_width=True)
        except Exception:
            col.write("[image missing]")


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
    base_instruction = (
        "Integrate the symbolic themes of the drawn tarot cards with the user's prior sharings. "
        "Draw subtle emotional and narrative threads without repeating the user's text verbatim. "
        "Offer 1-2 gentle reframing insights and a grounded micro-step. Avoid deterministic fortune-telling. "
        "End with exactly one gentle reflective question inviting the user to share or notice something (do not add extra commentary after the question)."
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
            # Prepare overlay phase
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
            # Continue normal conversation
            response = client.chat.completions.create(
                model="mistralai/mistral-small-24b-instruct-2501:free",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
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

# Add CSS animations for Tarot card appearance effects
st.markdown(
    """
    <style>
    .tarot-row {display:flex;justify-content:center;align-items:flex-start;gap:40px;margin:12px 0 6px 0;perspective:1200px;flex-wrap:nowrap;}
    .tarot-card {width:180px;height:295px;position:relative;opacity:0;animation:cardEnter .9s cubic-bezier(.25,.8,.3,1) forwards;flex:0 0 auto;}
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
        # Use simpler reliable rendering for now
        render_cards_simple(selected_cards)
        advice = (
            "I have gently drawn three cards for you. Take a slow breath and just notice what sensations or emotions arise as you look at them. "
            "Here is a soft reflection on their combined energies:"
        )
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
            "As you sit with this reflection, what feelings or bodily sensations are present right now? "
            "You can share a word, an image, or anything that arises. I'm here with you."
        )
        st.chat_message("assistant").write(follow_up)
        st.session_state.messages.append({"role": "assistant", "content": follow_up})
    st.session_state.tarot_reveal_done = True
    st.session_state.tarot_phase = 'done'


# --- Final global CSS override to eliminate persistent white bar at bottom ---
# Placed at end so it wins cascade order.
st.markdown(
    """
    <style>
    /* Minimal safe overrides */
    [data-testid="stBottomBlockContainer"] { background: transparent !important; }
    [data-testid="stChatInput"] { background: transparent !important; }
    [data-testid="stChatInput"] textarea { background: rgba(255,255,255,0.35)!important; }
    .missing-img {width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:0.8rem;color:#ccc;background:rgba(255,255,255,0.05);}
    /* Optional: float chat input a bit higher and remove large empty white zone */
    .floating-chat-wrapper {position:fixed;left:50%;bottom:18px;transform:translateX(-50%);width: min(720px,90%);z-index:1200;}
    .floating-chat-wrapper [data-testid="stChatInput"] {padding-bottom:0 !important;}
    body {margin:0 !important;}
    </style>
    <script>
    // JS walk up parents to clear any stray white backgrounds
    window.addEventListener('load', () => {
        const ci = document.querySelector('[data-testid="stChatInput"]');
        if(ci){
           let el = ci; let depth = 0;
           while(el && depth < 6){
              if(getComputedStyle(el).backgroundColor === 'rgb(255, 255, 255)'){
                 el.style.background = 'transparent';
              }
              el = el.parentElement; depth++;
           }
           // Optionally wrap for floating effect
           if(!ci.closest('.floating-chat-wrapper')){
              const wrap = document.createElement('div');
              wrap.className = 'floating-chat-wrapper';
              ci.parentElement.insertBefore(wrap, ci);
              wrap.appendChild(ci);
           }
        }
    });
    </script>
    """,
    unsafe_allow_html=True
)



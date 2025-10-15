# Tarot AI Healing Chatbot

<div align="center">
  <img src="./Tarot AI Healing Chatbot.jpg" alt="Tarot AI Healing Chatbot UI" width="720" />
  <br/>
  <sub>Reflective chat with optional tarot insights, built with Streamlit.</sub>
</div>


A Streamlit app that offers a gentle, reflective conversation experience and optional tarot card draws. It uses an OpenAI-compatible API client, and supports streaming responses plus animated tarot card reveal.

<div align="center">

  <!-- Watch demo badge -->
  <a href="./Demo Video.mp4">
    <img src="https://img.shields.io/badge/Watch%20the%20demo-%F0%9F%8E%A5-blue" alt="Watch the demo" />
  </a>

  <br/>
  <br/>

  <!-- Clickable GIF preview with JPG fallback (GIF optional) -->
  <a href="./Demo Video.mp4">
    <picture>
      <source srcset="./Demo-Preview.gif" type="image/gif" />
      <img src="./Tarot AI Healing Chatbot.jpg" alt="Demo preview (click to watch)" width="720" />
    </picture>
  </a>

</div>

## Features
- Conversational assistant with reflective, supportive tone
- Optional tarot reading flow (overlay, reveal, interpretation)
- Animated card UI with CSS
- Uses environment variables via `.env`

## Requirements
- Python 3.10+ (tested on Windows)
- Packages listed in `requirements.txt`

## Setup
1. Create and fill `.env` based on `.env.example`.
2. (Optional) Create a virtual environment.
3. Install dependencies.
4. Run the app.

### .env
See `.env.example` for all keys. At minimum you need:
- `OPENAI_API_KEY` – your key
- `OPENAI_BASE_URL` – base URL of your OpenAI-compatible endpoint (e.g., OpenRouter)

### Quickstart (Windows PowerShell)
```powershell
# Optional: create venv
python -m venv .venv
. .venv\Scripts\Activate.ps1

# Install deps
pip install -r requirements.txt

# Run
streamlit run app.py
```

## Project Structure
```
app.py                 # Streamlit app
Card/                  # Tarot card images (add your images here)
requirements.txt       # Python dependencies
run_app.bat            # Simple Windows runner
78cards_meaning.txt    # Source meanings
card_meanings.json     # Parsed meanings
README.md              # This file
.env.example           # Example environment variables
```

## Troubleshooting
- Indentation errors: ensure you’re using spaces consistently (no tabs). This repo uses 4 spaces.
- Authentication: verify `OPENAI_API_KEY` and `OPENAI_BASE_URL` in `.env`.
- Card images: ensure at least 3 images exist in the `Card/` folder.

## License
See `LICENSE`.

## Demo (details)
- The top of this README links to ./Demo Video.mp4. Depending on your browser, GitHub will either stream it inline or download it.
- To embed the video on a website, you can use:

```html
<video src="./Demo Video.mp4" controls width="720" poster="./Tarot AI Healing Chatbot.jpg"></video>
```

- If you publish the video on YouTube, simply link to it, e.g.:

```
https://youtu.be/your-video-id
```

### Optional: Create the GIF preview
If you want to generate Demo-Preview.gif from the MP4, install ffmpeg and run something like:

```powershell
# Install or use an existing ffmpeg installation
# Example conversion (first 12s, scaled to 720px width)
ffmpeg -y -i "Demo Video.mp4" -t 12 -vf "fps=12,scale=720:-1:flags=lanczos" -loop 0 Demo-Preview.gif
```

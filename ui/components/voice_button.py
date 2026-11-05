"""Browser Web Speech API voice input (mic) and text-to-speech (speaker) component.

Optimized for Indian farmers with support for Marathi (mr-IN), Hindi (hi-IN), and English (en-IN).
Works offline on Android Chrome with graceful fallback when Web Speech is unsupported.
"""

import html
from typing import Optional
import streamlit as st
import streamlit.components.v1 as components
from ui.state import get_language


def render_speaker_button(text_to_speak: str, lang: Optional[str] = None, button_label: Optional[str] = None):
    """Render a speaker button that reads text aloud using browser Web Speech API."""
    if not text_to_speak or not text_to_speak.strip():
        return

    current_lang = lang or get_language()
    speech_lang_code = "mr-IN" if current_lang == "mr" else ("hi-IN" if current_lang == "hi" else "en-IN")

    default_labels = {
        "mr": "🔊 उत्तर ऐका (Listen)",
        "hi": "🔊 उत्तर सुनें (Listen)",
        "en": "🔊 Listen Answer",
    }
    lbl = button_label or default_labels.get(current_lang, "🔊 Listen")

    escaped_text = html.escape(text_to_speak.replace("\n", " ").replace('"', "'"))

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 4px 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: transparent;
            }}
            .speaker-btn {{
                background: #e8f5e9;
                color: #1b5e20;
                border: 2px solid #81c784;
                border-radius: 28px;
                padding: 8px 18px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                min-height: 44px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.06);
                transition: all 0.2s ease;
            }}
            .speaker-btn:hover {{
                background: #c8e6c9;
                border-color: #2e7d32;
                transform: translateY(-1px);
            }}
            .speaker-btn.speaking {{
                background: #ffe0b2;
                color: #e65100;
                border-color: #ff9800;
                animation: pulse 1s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.03); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    </head>
    <body>
        <button id="ttsBtn" class="speaker-btn" onclick="toggleSpeak()">
            <span id="ttsIcon">🔊</span>
            <span id="ttsText">{lbl}</span>
        </button>

        <script>
            let isSpeaking = false;
            const fullText = "{escaped_text}";
            const langCode = "{speech_lang_code}";

            function toggleSpeak() {{
                if (!('speechSynthesis' in window)) {{
                    alert("तुमच्या ब्राउझरमध्ये आवाज सुविधा (Web Speech API) उपलब्ध नाही. कृपया Google Chrome वापरा.");
                    return;
                }}

                if (isSpeaking) {{
                    window.speechSynthesis.cancel();
                    resetBtn();
                }} else {{
                    window.speechSynthesis.cancel(); // Stop any pending speech
                    const utterance = new SpeechSynthesisUtterance(fullText);
                    utterance.lang = langCode;
                    utterance.rate = 0.95; // Slightly slower for low-literacy clarity
                    utterance.pitch = 1.0;

                    utterance.onstart = function() {{
                        isSpeaking = true;
                        const btn = document.getElementById("ttsBtn");
                        btn.classList.add("speaking");
                        document.getElementById("ttsText").innerText = "⏹️ थांबवा (Stop)";
                    }};

                    utterance.onend = resetBtn;
                    utterance.onerror = resetBtn;

                    window.speechSynthesis.speak(utterance);
                }}
            }}

            function resetBtn() {{
                isSpeaking = false;
                const btn = document.getElementById("ttsBtn");
                if (btn) btn.classList.remove("speaking");
                const txt = document.getElementById("ttsText");
                if (txt) txt.innerText = "{lbl}";
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=52)


def render_voice_mic_button(lang: Optional[str] = None, prompt_placeholder: Optional[str] = None, key_suffix: str = ""):
    """Render a large 56px+ pulsing microphone button for voice speech-to-text input."""
    current_lang = lang or get_language()
    speech_lang_code = "mr-IN" if current_lang == "mr" else ("hi-IN" if current_lang == "hi" else "en-IN")

    mic_prompts = {
        "mr": "🎙️ बोलून प्रश्न विचारा (Tap & Speak)",
        "hi": "🎙️ बोलकर सवाल पूछें (Tap & Speak)",
        "en": "🎙️ Tap to Speak Question",
    }
    lbl = prompt_placeholder or mic_prompts.get(current_lang, "🎙️ Tap to Speak")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 6px 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: transparent;
            }}
            .mic-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }}
            .mic-btn {{
                background: #2e7d32;
                color: #ffffff;
                border: 3px solid #81c784;
                border-radius: 50%;
                width: 64px;
                height: 64px;
                font-size: 28px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(46, 125, 50, 0.35);
                transition: all 0.2s ease;
            }}
            .mic-btn:hover {{
                transform: scale(1.05);
                background: #1b5e20;
            }}
            .mic-btn.listening {{
                background: #c62828 !important;
                border-color: #ef5350 !important;
                animation: micPulse 1.2s infinite;
            }}
            @keyframes micPulse {{
                0% {{ box-shadow: 0 0 0 0 rgba(198, 40, 40, 0.7); transform: scale(1); }}
                50% {{ box-shadow: 0 0 0 16px rgba(198, 40, 40, 0); transform: scale(1.08); }}
                100% {{ box-shadow: 0 0 0 0 rgba(198, 40, 40, 0); transform: scale(1); }}
            }}
            .mic-status {{
                font-size: 14px;
                font-weight: 700;
                color: #1b5e20;
                text-align: center;
            }}
            .transcription-box {{
                width: 95%;
                background: #ffffff;
                border: 2px solid #a5d6a7;
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 15px;
                color: #142814;
                display: none;
                margin-top: 4px;
                box-sizing: border-box;
            }}
            .copy-btn {{
                background: #f9a825;
                color: #142814;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 700;
                font-size: 13px;
                cursor: pointer;
                margin-top: 6px;
            }}
        </style>
    </head>
    <body>
        <div class="mic-container">
            <button id="micBtn" class="mic-btn" onclick="toggleRecognition()" title="आवाज इनपुट (Voice Input)">
                🎤
            </button>
            <div id="micStatus" class="mic-status">{lbl}</div>
            <div id="transcriptBox" class="transcription-box">
                <div id="transcriptText"></div>
                <button id="copyBtn" class="copy-btn" onclick="copyTranscript()">📋 कॉपी करा (Copy)</button>
            </div>
        </div>

        <script>
            let recognition = null;
            let isListening = false;
            const langCode = "{speech_lang_code}";

            function toggleRecognition() {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {{
                    alert("तुमच्या ब्राउझरमध्ये आवाज इनपुट (Speech Recognition) उपलब्ध नाही. कृपया Google Chrome वापरा किंवा टाइप करा.");
                    return;
                }}

                if (isListening) {{
                    if (recognition) recognition.stop();
                    return;
                }}

                recognition = new SpeechRecognition();
                recognition.lang = langCode;
                recognition.interimResults = true;
                recognition.continuous = false;

                recognition.onstart = function() {{
                    isListening = true;
                    document.getElementById("micBtn").classList.add("listening");
                    document.getElementById("micStatus").innerText = "🔴 ऐकत आहे... बोला (Listening...)";
                }};

                recognition.onresult = function(event) {{
                    let text = "";
                    for (let i = event.resultIndex; i < event.results.length; ++i) {{
                        text += event.results[i][0].transcript;
                    }}
                    const box = document.getElementById("transcriptBox");
                    const txt = document.getElementById("transcriptText");
                    box.style.display = "block";
                    txt.innerText = text;
                }};

                recognition.onerror = function(event) {{
                    document.getElementById("micStatus").innerText = "⚠️ आवाज समजला नाही, पुन्हा प्रयत्न करा";
                    resetMic();
                }};

                recognition.onend = function() {{
                    resetMic();
                }};

                try {{
                    recognition.start();
                }} catch (e) {{
                    resetMic();
                }}
            }}

            function resetMic() {{
                isListening = false;
                document.getElementById("micBtn").classList.remove("listening");
                document.getElementById("micStatus").innerText = "{lbl}";
            }}

            function copyTranscript() {{
                const text = document.getElementById("transcriptText").innerText;
                if (text && navigator.clipboard) {{
                    navigator.clipboard.writeText(text).then(function() {{
                        document.getElementById("copyBtn").innerText = "✅ कॉपी झाले (Copied!)";
                        setTimeout(function() {{
                            document.getElementById("copyBtn").innerText = "📋 कॉपी करा (Copy)";
                        }}, 2000);
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=135)


def render_voice_input_and_speaker(text_to_read: Optional[str] = None):
    """Render combined voice input (mic) and speaker utility."""
    lang = get_language()
    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        render_voice_mic_button(lang)
    with v_col2:
        if text_to_read:
            render_speaker_button(text_to_read, lang)

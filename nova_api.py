# nova_api.py

import os
import requests
import streamlit as st
import traceback
from pydub import AudioSegment

def transcribe_nova_one_shot(
    file_path: str,
    dg_api_key: str,      # La clé Nova (NOVA / NOVA2 / NOVA3)
    language: str = "fr",
    model_name: str = "nova-2",
    punctuate: bool = True,
    numerals: bool = True
) -> str:
    """
    Envoie le fichier complet à Deepgram Nova.
    => Retourne la transcription (str).
    """
    temp_in = "temp_nova_in.wav"
    try:
        audio = AudioSegment.from_file(file_path)
        audio_16k = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio_16k.export(temp_in, format="wav")

        # Préparer les paramètres de la requête
        params = {
            "language": language,
            "model": model_name,
            "punctuate": "true" if punctuate else "false",
            "numerals": "true" if numerals else "false"
        }
        qs = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"https://api.deepgram.com/v1/listen?{qs}"

        headers = {
            "Authorization": f"Token {dg_api_key}",
            "Content-Type": "audio/wav"
        }

        with open(temp_in, "rb") as f:
            payload = f.read()

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            result = response.json()
            transcription = (
                result.get("results", {})
                      .get("channels", [{}])[0]
                      .get("alternatives", [{}])[0]
                      .get("transcript", "")
            )
            return transcription
        else:
            st.error(f"[Nova] Erreur {response.status_code} : {response.text}")
            return ""
    except Exception as e:
        st.error(f"[Nova] Exception : {e}")
        traceback.print_exc()
        return ""
    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_in):
            os.remove(temp_in)

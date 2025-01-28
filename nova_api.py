# nova_api.py

import os
import requests
import streamlit as st
import traceback
from pydub import AudioSegment

def transcribe_audio(
    file_path: str,
    dg_api_key: str,
    language: str = "fr",
    model_name: str = "nova-2",  # Utilisation cohérente des noms des modèles
    punctuate: bool = True,
    numerals: bool = True
) -> (str, bool):
    """
    Envoie le fichier audio à DeepGram pour transcription (Nova II ou Whisper Large).
    Retourne la transcription et un booléen indiquant le succès.
    """
    temp_in = "temp_audio.wav"
    try:
        # Convertir en 16kHz WAV mono
        audio = AudioSegment.from_file(file_path)
        audio_16k = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio_16k.export(temp_in, format="wav")

        # Paramètres de la requête
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

        # Ajout de journaux de débogage
        st.write(f"Utilisation de la clé API: {dg_api_key[:4]}****")
        st.write(f"Modèle utilisé: {model_name}")

        resp = requests.post(url, headers=headers, data=payload)
        if resp.status_code == 200:
            j = resp.json()
            transcript = (
                j.get("results", {})
                 .get("channels", [{}])[0]
                 .get("alternatives", [{}])[0]
                 .get("transcript", "")
            )
            return transcript, True
        else:
            st.error(f"[DeepGram] Erreur {resp.status_code} : {resp.text}")
            if resp.status_code == 401:
                # Credentials invalides
                return "", False
            return "", False
    except Exception as e:
        st.error(f"[DeepGram] Exception : {e}")
        traceback.print_exc()
        return "", False
    finally:
        if os.path.exists(temp_in):
            os.remove(temp_in)

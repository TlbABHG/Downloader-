import os
import tempfile

import streamlit as st
import yt_dlp

st.set_page_config(page_title="YouTube Downloader", page_icon="🎬")
st.title("🎬 Téléchargeur YouTube (MP4 2K)")

# --- Mot de passe (optionnel mais recommandé si l'app est en ligne) ---
mdp = st.secrets.get("APP_PASSWORD", "")
if mdp:
    saisi = st.text_input("Mot de passe", type="password")
    if saisi != mdp:
        st.stop()

url = st.text_input("Lien de la vidéo YouTube")
QUALITES = {"2K (1440p)": 1440, "1080p": 1080, "720p": 720}
choix = st.selectbox("Qualité maximale", list(QUALITES.keys()))
hauteur = QUALITES[choix]


def telecharger(lien, hauteur_max, dossier):
    options = {
        "format": (
            f"bestvideo[height<={hauteur_max}]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={hauteur_max}]+bestaudio/"
            f"best[height<={hauteur_max}]"
        ),
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(dossier, "%(title).80s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    # Cookies YouTube (optionnel) pour éviter le blocage "confirmez que vous n'êtes pas un robot"
    cookies = st.secrets.get("YT_COOKIES", "")
    if cookies:
        chemin_cookies = os.path.join(dossier, "cookies.txt")
        with open(chemin_cookies, "w") as f:
            f.write(cookies)
        options["cookiefile"] = chemin_cookies

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(lien, download=True)
        base, _ = os.path.splitext(ydl.prepare_filename(info))
        return base + ".mp4"


# On garde le fichier en session pour que le bouton de téléchargement
# reste disponible après le rechargement de la page (important sur mobile)
if st.button("Télécharger", type="primary", disabled=not url):
    with st.spinner("Téléchargement en cours..."):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                fichier = telecharger(url, hauteur, tmp)
                with open(fichier, "rb") as f:
                    st.session_state["video"] = f.read()
                st.session_state["nom"] = os.path.basename(fichier)
        except Exception as e:
            st.session_state.pop("video", None)
            st.error(f"Erreur : {e}")

if "video" in st.session_state:
    st.success(f"Prêt : {st.session_state['nom']}")
    st.download_button(
        "💾 Enregistrer la vidéo",
        data=st.session_state["video"],
        file_name=st.session_state["nom"],
        mime="video/mp4",
    )

"""
TikTok Influencer Checker - Web App (Barber Daily styled)
-----------------------------------------------------------
A shareable website version of the TikTok stats checker, styled with the
Barber Daily brown theme, logo, and campaign background photo.

HOW TO RUN LOCALLY (to test before sharing):
    pip install streamlit yt-dlp pandas
    streamlit run streamlit_app.py

HOW TO DEPLOY SO YOUR CO-WORKER CAN ACCESS IT (free):
    1. Upload this file, requirements.txt, logo.png and background.png to
       your GitHub repo (the file must be named exactly streamlit_app.py).
    2. Streamlit Cloud auto-redeploys within a minute.
"""

import base64
import html
import io
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yt_dlp
from PIL import Image

# Barber Daily logo and campaign background photo, embedded directly so
# nothing extra needs to be uploaded anywhere else.
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).parent


@lru_cache(maxsize=None)
def image_b64(filename: str) -> str:
    """Read an image file that sits next to this script and return it as base64."""
    return base64.b64encode((HERE / filename).read_bytes()).decode()


# These two image files must be in the same GitHub folder as this script.
LOGO_B64 = image_b64("logo.png")
BACKGROUND_B64 = image_b64("background.png")

# Use the Barber Daily logo as the browser tab icon too
logo_icon = Image.open(io.BytesIO(base64.b64decode(LOGO_B64)))

st.set_page_config(page_title="Barber Daily TikTok Checker", page_icon=logo_icon, layout="wide")

# ---------------- Custom brown-themed styling ----------------
# NOTE: we style Streamlit's own content container directly (instead of
# manually opening/closing a <div> across separate st.markdown() calls,
# which does not actually work in Streamlit - each call renders into its
# own separate block, so a div opened in one call can't be closed by a
# later call).
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(rgba(60,36,18,0.55), rgba(60,36,18,0.55)),
                url('data:image/png;base64,BG_TOKEN') center center / cover no-repeat fixed;
}

/* Style Streamlit's real content container as the rounded card */
div[data-testid="stAppViewContainer"] > div:first-child .block-container {
    background: rgba(255, 250, 244, 0.94);
    border-radius: 28px;
    padding: 48px 56px 40px 56px;
    margin: 24px auto;
    max-width: 1100px;
    box-shadow: 0 20px 60px rgba(60, 36, 18, 0.25);
}

.hero-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.hero-logo {
    font-size: 22px;
    font-weight: 600;
    color: #4A2C1D;
}

.hero-title {
    font-size: 40px;
    font-weight: 600;
    text-align: center;
    color: #3B2417;
    line-height: 1.2;
    margin-bottom: 12px;
}

.hero-subtitle {
    text-align: center;
    color: #6B4226;
    font-size: 16px;
    max-width: 650px;
    margin: 0 auto 28px auto;
}

div.stButton {
    text-align: center;
}
div.stButton > button {
    background-color: #6B4226;
    color: #FFF8F0;
    border-radius: 999px;
    padding: 10px 28px;
    border: none;
    font-weight: 500;
}
div.stButton > button:hover {
    background-color: #4A2C1D;
    color: #FFF8F0;
}

.result-card {
    background: #FFF8F0;
    border: 1px solid #E8D5BC;
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(60, 36, 18, 0.08);
}
.result-card h4 {
    margin: 0 0 6px 0;
    color: #4A2C1D;
}
.result-stats {
    color: #6B4226;
    font-size: 14px;
}
.open-btn {
    display: inline-block;
    background: #6B4226;
    color: #FFF8F0 !important;
    padding: 10px 26px;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 500;
}
.open-btn:hover { background: #4A2C1D; }
.player-note {
    text-align: center;
    font-size: 13px;
    color: #6B4226;
    margin-top: 8px;
}
</style>
"""
CSS = CSS.replace("BG_TOKEN", BACKGROUND_B64)
st.markdown(CSS, unsafe_allow_html=True)

# ---------------- Hero section ----------------
NAV_HTML = """
<div class="hero-nav">
    <div class="hero-logo" style="display:flex; align-items:center; gap:10px;">
        <img src="data:image/png;base64,LOGO_TOKEN" alt="Barber Daily logo" style="height:44px; width:44px; border-radius:10px; object-fit:cover;">
        Barber Daily
    </div>
    <div style="color:#6B4226; font-size:14px;">Affiliate &amp; Influencer Tracker</div>
</div>
"""
NAV_HTML = NAV_HTML.replace("LOGO_TOKEN", LOGO_B64)
st.markdown(NAV_HTML, unsafe_allow_html=True)

st.markdown('<div class="hero-title">Check your influencers.<br>All in one place.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Paste TikTok video links below and instantly see views, likes, '
    'comments, and shares for each one — no manual checking needed.</div>',
    unsafe_allow_html=True,
)

urls_input = st.text_area(
    "TikTok video links",
    height=180,
    placeholder="https://www.tiktok.com/@username/video/1234567890123456789\nhttps://www.tiktok.com/@username2/video/9876543210987654321",
    label_visibility="collapsed",
)

check_button = st.button("Check Stats", type="primary")


def friendly_error(e: Exception) -> str:
    msg = str(e)
    low = msg.lower()
    if "comfortable" in low or "log in" in low or "login" in low:
        return "FAILED - TikTok only shows this post to logged-in users (age/sensitive-restricted)"
    if "private" in low:
        return "FAILED - this video is private"
    if "removed" in low or "unavailable" in low or "not found" in low:
        return "FAILED - video was removed or the link is wrong"
    return "FAILED - " + msg[:140]


def get_video_stats(url: str) -> dict:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        # We only need the numbers, not the video file. This lets photo /
        # slideshow posts (which have no video formats) still return stats.
        "ignore_no_formats_error": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "Username": info.get("uploader") or info.get("creator") or "",
        "Video Title": (info.get("title") or "")[:80],
        "URL": url,
        "Video ID": str(info.get("id") or ""),
        "Views": info.get("view_count", ""),
        "Likes": info.get("like_count", ""),
        "Comments": info.get("comment_count", ""),
        "Shares": info.get("repost_count", ""),
        "Upload Date": info.get("upload_date", ""),
        "Status": "OK",
    }


if check_button:
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]

    if not urls:
        st.warning("Paste at least one TikTok link first.")
    else:
        results = []
        progress = st.progress(0, text="Starting...")

        for i, url in enumerate(urls, start=1):
            progress.progress(i / len(urls), text=f"Checking {i}/{len(urls)}: {url}")
            try:
                results.append(get_video_stats(url))
            except Exception as e:
                results.append({
                    "Username": "", "Video Title": "", "URL": url, "Video ID": "",
                    "Views": "", "Likes": "", "Comments": "", "Shares": "",
                    "Upload Date": "", "Status": friendly_error(e),
                })

        progress.empty()

        df = pd.DataFrame(results)
        for col in ["Views", "Likes", "Comments", "Shares"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values(by="Views", ascending=False, na_position="last").reset_index(drop=True)

        # Remember the results so they stay on screen when the person clicks
        # something else on the page (like the video picker below).
        st.session_state["results_df"] = df


if "results_df" in st.session_state:
    df = st.session_state["results_df"]

    st.markdown(
        f'<div class="hero-title" style="font-size:26px; margin-top:36px;">Results ({len(df)} checked)</div>',
        unsafe_allow_html=True,
    )

    def fmt(val):
        if pd.isna(val):
            return "N/A"
        return f"{int(val):,}"

    cols = st.columns(3)
    for idx, row in enumerate(df.to_dict("records")):
        with cols[idx % 3]:
            status_note = "" if row["Status"] == "OK" else (
                '<br><span style="color:#B23B3B;">' + html.escape(str(row["Status"])) + '</span>'
            )
            card_html = (
                '<div class="result-card">'
                f'<h4>@{html.escape(str(row["Username"] or "unknown"))}</h4>'
                '<div class="result-stats">'
                f'views: {fmt(row["Views"])}<br>'
                f'likes: {fmt(row["Likes"])}<br>'
                f'comments: {fmt(row["Comments"])}<br>'
                f'shares: {fmt(row["Shares"])}'
                f'{status_note}'
                '</div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

    # ---------------- Video viewer ----------------
    playable = df[(df["Status"] == "OK") & (df["Video ID"] != "")]
    if not playable.empty:
        st.markdown(
            '<div class="hero-title" style="font-size:26px; margin-top:24px;">▶ Watch a video</div>',
            unsafe_allow_html=True,
        )
        options = {
            f"{n + 1}. @{r['Username'] or 'unknown'} - {fmt(r['Views'])} views": i
            for n, (i, r) in enumerate(playable.iterrows())
        }
        choice = st.selectbox("Pick a video to watch", list(options.keys()), label_visibility="collapsed")
        picked = df.loc[options[choice]]

        left, middle, right = st.columns([1, 2, 1])
        with middle:
            canonical = f"https://www.tiktok.com/@{picked['Username']}/video/{picked['Video ID']}"
            embed_html = (
                f'<blockquote class="tiktok-embed" cite="{html.escape(canonical)}" '
                f'data-video-id="{html.escape(str(picked["Video ID"]))}" '
                'style="max-width:605px;min-width:325px;margin:0 auto;">'
                '<section></section></blockquote>'
                '<script async src="https://www.tiktok.com/embed.js"></script>'
            )
            components.html(embed_html, height=780, scrolling=True)
            st.markdown(
                f'<div style="text-align:center; margin-top:10px;">'
                f'<a class="open-btn" href="{html.escape(picked["URL"])}" target="_blank" rel="noopener">'
                'Open on TikTok ↗</a></div>'
                '<div class="player-note">If the player above shows an error, use this button. '
                'TikTok sometimes refuses to play its videos inside other websites.</div>',
                unsafe_allow_html=True,
            )

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download as CSV",
        data=csv,
        file_name="tiktok_report.csv",
        mime="text/csv",
    )


st.markdown(
    '<div style="text-align:center; font-size:11px; color:#8C5B33; margin-top:18px;">'
    'App version 4 - player update</div>',
    unsafe_allow_html=True,
)

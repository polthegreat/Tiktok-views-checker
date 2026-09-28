"""
Barber Daily - TikTok Influencer Checker (with video player)
Files needed in the same GitHub folder:
  streamlit_app.py   (this file)
  requirements.txt   (streamlit>=1.30, yt-dlp, pandas)
  logo.png           (your logo)
  background.jpg     (optional - campaign photo; also accepts background.png)
"""

import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp

st.set_page_config(page_title="Barber Daily TikTok Checker", layout="wide")

HERE = Path(__file__).parent


def load_image(*names):
    """Return (base64, mime) for the first image file that exists, else None."""
    for name in names:
        path = HERE / name
        if path.exists():
            ext = path.suffix.lower().lstrip(".")
            mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
            return base64.b64encode(path.read_bytes()).decode(), mime
    return None


logo = load_image("logo.png", "logo.jpg", "logo.jpeg")
background = load_image("background.jpg", "background.jpeg", "background.png")

if background:
    bg_css = (
        "linear-gradient(rgba(60,36,18,0.55), rgba(60,36,18,0.55)), "
        f"url('data:{background[1]};base64,{background[0]}') center center / cover no-repeat fixed"
    )
else:
    bg_css = "linear-gradient(135deg, #5A3520 0%, #8B5A2B 50%, #4A2C1D 100%)"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

.stApp { background: BG_TOKEN; }

div[data-testid="stAppViewContainer"] > div:first-child .block-container {
    background: rgba(255, 250, 244, 0.94);
    border-radius: 28px;
    padding: 48px 56px 40px 56px;
    margin: 24px auto;
    max-width: 1100px;
    box-shadow: 0 20px 60px rgba(60, 36, 18, 0.25);
}

.hero-nav { display:flex; justify-content:space-between; align-items:center; margin-bottom:30px; }
.hero-logo { font-size:22px; font-weight:600; color:#4A2C1D; display:flex; align-items:center; gap:10px; }
.hero-title { font-size:40px; font-weight:600; text-align:center; color:#3B2417; line-height:1.2; margin-bottom:12px; }
.hero-subtitle { text-align:center; color:#6B4226; font-size:16px; max-width:650px; margin:0 auto 28px auto; }

div.stButton { text-align:center; }
div.stButton > button {
    background-color:#6B4226; color:#FFF8F0; border-radius:999px;
    padding:10px 28px; border:none; font-weight:500;
}
div.stButton > button:hover { background-color:#4A2C1D; color:#FFF8F0; }

.result-card {
    background:#FFF8F0; border:1px solid #E8D5BC; border-radius:18px;
    padding:18px 20px; margin-bottom:14px; box-shadow:0 4px 14px rgba(60,36,18,0.08);
}
.result-card h4 { margin:0 0 6px 0; color:#4A2C1D; }
.result-stats { color:#6B4226; font-size:14px; }
</style>
"""
st.markdown(CSS.replace("BG_TOKEN", bg_css), unsafe_allow_html=True)

# ---------------- Header ----------------
logo_img = ""
if logo:
    logo_img = (
        f'<img src="data:{logo[1]};base64,{logo[0]}" alt="Barber Daily logo" '
        'style="height:44px; width:44px; border-radius:10px; object-fit:cover;">'
    )

st.markdown(
    f"""
    <div class="hero-nav">
        <div class="hero-logo">{logo_img} Barber Daily</div>
        <div style="color:#6B4226; font-size:14px;">Affiliate &amp; Influencer Tracker</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-title">Check your influencers.<br>All in one place.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Paste TikTok video links below and instantly see views, likes, '
    'comments, and shares for each one — then watch the video right here.</div>',
    unsafe_allow_html=True,
)

urls_input = st.text_area(
    "TikTok video links",
    height=180,
    placeholder="https://www.tiktok.com/@username/video/1234567890123456789\nhttps://www.tiktok.com/@username2/video/9876543210987654321",
    label_visibility="collapsed",
)

check_button = st.button("Check Stats", type="primary")


def get_video_stats(url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {
        "Username": info.get("uploader") or info.get("creator") or "",
        "Video Title": (info.get("title") or "")[:80],
        "URL": url,
        "Video ID": str(info.get("id") or ""),
        "Link": info.get("webpage_url") or url,
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
                    "Username": "", "Video Title": "", "URL": url,
                    "Video ID": "", "Link": url,
                    "Views": "", "Likes": "", "Comments": "", "Shares": "",
                    "Upload Date": "", "Status": f"FAILED - {str(e)[:60]}",
                })

        progress.empty()

        df = pd.DataFrame(results)
        for col in ["Views", "Likes", "Comments", "Shares"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values(by="Views", ascending=False, na_position="last")

        # Keep results on screen when a video is picked in the player
        st.session_state["df"] = df


if "df" in st.session_state:
    df = st.session_state["df"]

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
            status_note = "" if row["Status"] == "OK" else f'<br><span style="color:#B23B3B;">{row["Status"]}</span>'
            st.markdown(
                f"""
                <div class="result-card">
                    <h4>@{row['Username'] or 'unknown'}</h4>
                    <div class="result-stats">
                        views: {fmt(row['Views'])}<br>
                        likes: {fmt(row['Likes'])}<br>
                        comments: {fmt(row['Comments'])}<br>
                        shares: {fmt(row['Shares'])}
                        {status_note}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------------- Video player ----------------
    st.markdown(
        '<div class="hero-title" style="font-size:26px; margin-top:36px;">▶ Watch a video</div>',
        unsafe_allow_html=True,
    )

    playable = df[(df["Status"] == "OK") & (df["Video ID"] != "")]

    if playable.empty:
        st.info("No playable videos found in these results.")
    else:
        labels = {
            row["Video ID"]: f"@{row['Username'] or 'unknown'} — {row['Video Title'] or row['Video ID']}"
            for _, row in playable.iterrows()
        }
        chosen_id = st.selectbox(
            "Choose a video",
            options=list(labels.keys()),
            format_func=lambda vid: labels[vid],
        )
        chosen = playable[playable["Video ID"] == chosen_id].iloc[0]

        left, center, right = st.columns([1, 1, 1])
        with center:
            components.iframe(
                f"https://www.tiktok.com/embed/v2/{chosen_id}",
                width=340,
                height=740,
                scrolling=False,
            )
            st.link_button("🛒 Open on TikTok (see yellow basket)", chosen["Link"], use_container_width=True)

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download as CSV",
        data=csv,
        file_name="tiktok_report.csv",
        mime="text/csv",
    )

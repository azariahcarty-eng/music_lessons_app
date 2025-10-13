import streamlit as st
from pathlib import Path
import re

# --- CONFIG ---
st.set_page_config(page_title="Aza's School Of Music🎵", layout="wide")

# --- GLOBAL STYLE (ultra-tight + readable) ---
st.markdown("""
<style>
/* Paragraphs */
p, div {
    line-height: 1.15 !important;
    margin-top: 1px !important;
    margin-bottom: 1px !important;
}

/* Lists */
ul, ol {
    margin-top: 1px !important;
    margin-bottom: 1px !important;
    padding-left: 15px !important;
}
li {
    line-height: 1 !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    margin-top: 2px !important;
    margin-bottom: 1px !important;
    line-height: 1.2 !important;
    padding: 0 !important;
}

/* Images */
img {
    margin-top: 1px !important;
    margin-bottom: 1px !important;
}

/* Streamlit markdown wrapper fix */
.stMarkdown, .stMarkdown > div, .stMarkdown p {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}

/* Top padding to avoid cutoff */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).parent
LESSONS_DIR = BASE_DIR / "lessons"
IMAGES_DIR = BASE_DIR / "images"

# --- SIDEBAR ---
st.sidebar.title("Aza's School Of Music🎶")
section = st.sidebar.radio("Choose Instrument", ["Home", "Piano", "Guitar", "Ukulele"])

# --- LOAD LESSONS (cached) ---
@st.cache_data
def load_lesson(file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except Exception as e:
        return [f"⚠️ Error reading file: {e}"]

# --- DISPLAY FUNCTION ---
def display_lesson(file_path: Path):
    """Render .txt lessons with headings, Markdown (bold, italic, lists), and images."""
    if not file_path.exists():
        st.error(f"Lesson not found: {file_path}")
        return

    lines = load_lesson(file_path)

    for line in lines:
        line = line.rstrip("\n")

        # --- Skip empty lines with minimal spacing ---
        if not line.strip():
            st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
            continue

        # --- IMAGE HANDLING ---
        if line.lower().startswith("image:"):
            parts = line.split(":", 1)
            if len(parts) < 2 or not parts[1].strip():
                st.warning("⚠️ IMAGE: line found but no filename provided.")
                continue

            image_parts = [p.strip() for p in parts[1].split("|")]
            image_name = image_parts[0]
            caption = image_parts[1] if len(image_parts) > 1 else ""
            size_tag = image_parts[2].lower() if len(image_parts) > 2 else "normal"

            size_map = {"small": 300, "normal": 400, "large": 600, "full": None}
            width = size_map.get(size_tag, 400)

            if image_name.startswith("http"):
                st.image(image_name, caption=caption, width=width)
            else:
                image_path = IMAGES_DIR / image_name
                if image_path.exists():
                    st.image(str(image_path), caption=caption, width=width)
                else:
                    st.warning(f"⚠️ Image not found: {image_path}")
            continue

        # --- HEADING DETECTION ---
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            st.markdown(f'{"#"*level} {content}')
            continue

        # --- NORMAL TEXT (Markdown parsed for bold, italics, lists) ---
        st.markdown(line)

# --- HOME PAGE ---
if section == "Home":
    st.title("🎵 Welcome to Aza's School Of Music")

    cover_path = IMAGES_DIR / "cover.jpg"
    if cover_path.exists():
        st.image(str(cover_path), use_container_width=True)
    else:
        st.write("_Cover image not found._")

    st.write("Select an instrument from the sidebar to explore your lessons!")

# --- INSTRUMENT LESSONS ---
else:
    st.header(f"🎶 {section} ")
    instrument_dir = LESSONS_DIR / section.lower()

    if not instrument_dir.exists():
        st.warning(f"No {section.lower()} lessons found.")
    else:
        lessons = sorted(instrument_dir.glob("*.txt"))
        if not lessons:
            st.warning("No lessons available yet.")
        else:
            lesson_names = [
                lesson.stem.lstrip("0123456789_").replace("_", " ").strip().title()
                for lesson in lessons
            ]

            selected_lesson = st.sidebar.selectbox(
                f"Select a {section} Lesson:",
                lesson_names,
                index=0
            )

            lesson_file = lessons[lesson_names.index(selected_lesson)]
            st.subheader(selected_lesson)
            display_lesson(lesson_file)

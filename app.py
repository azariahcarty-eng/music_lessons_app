import streamlit as st
from pathlib import Path
import re

# --- CONFIG ---
st.set_page_config(page_title="Music Lessons 🎵", layout="wide")

# --- DIRECTORIES ---
BASE_DIR = Path(__file__).parent
LESSONS_DIR = BASE_DIR / "lessons"
IMAGES_DIR = BASE_DIR / "images"

# --- SIDEBAR ---
st.sidebar.title("🎶 Music Lessons")
section = st.sidebar.radio("Choose Instrument", ["Home", "Piano", "Guitar", "Ukulele"])

# --- DISPLAY FUNCTION ---
def display_lesson(file_path: Path):
    """Render a .txt lesson with headings and images, supporting '| large' for images."""
    if not file_path.exists():
        st.error(f"Lesson not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.rstrip("\n")  # preserve spaces at end
        if not line.strip():
            st.text(" ")  # maintain blank lines
            continue

        # --- IMAGE HANDLING ---
        if line.lower().startswith("image:"):
            parts = line.split(":", 1)
            if len(parts) < 2 or not parts[1].strip():
                st.warning("⚠ IMAGE: line found but no filename provided.")
                continue

            image_parts = parts[1].strip().split("|")
            image_name = image_parts[0].strip()
            caption = image_parts[1].strip() if len(image_parts) > 1 else ""
            size_tag = image_parts[2].strip().lower() if len(image_parts) > 2 else "normal"

            width = 600 if size_tag == "large" else 400

            if image_name.startswith("http"):
                st.image(image_name, caption=caption, width=width)
            else:
                image_path = IMAGES_DIR / image_name
                if image_path.exists():
                    st.image(str(image_path), caption=caption, width=width)
                else:
                    st.warning(f"⚠ Image not found: {image_path}")

        # --- HEADING HANDLING ---
        else:
            heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                content = heading_match.group(2)
                st.markdown(f'{"#"*level} {content}')
            else:
                st.text(line)  # preserves spaces exactly

# --- HOME PAGE ---
if section == "Home":
    st.title("🎵 Welcome to Your Music Lessons App")
    cover_path = IMAGES_DIR / "cover.jpg"
    if cover_path.exists():
        st.image(str(cover_path), use_container_width=True)
    else:
        st.write("Cover image not found.")
    st.write("Select an instrument from the sidebar to explore your lessons!")

# --- INSTRUMENT LESSONS ---
else:
    st.header(f"🎶 {section} Lessons")
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

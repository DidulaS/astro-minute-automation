
import json
import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ==========================================
# ASTRO MINUTE VIDEO SETTINGS
# ==========================================

WIDTH = 1080
HEIGHT = 1920
FPS = 30

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

SCRIPT_FILE = OUTPUT / "video_script.json"
AUDIO_FILE = OUTPUT / "narration.mp3"
BACKGROUND_FILE = OUTPUT / "background.png"
CAPTIONS_FILE = OUTPUT / "captions.ass"
VIDEO_FILE = OUTPUT / "astro_minute_short.mp4"

FONT = (
    "/usr/share/fonts/truetype/dejavu/"
    "DejaVuSans-Bold.ttf"
)

# ==========================================
# UTILITIES
# ==========================================

def run(command):
    subprocess.run(command, check=True)


def get_duration(audio_file):
    result = subprocess.check_output([
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ])

    return float(result.decode().strip())


def load_font(size):
    return ImageFont.truetype(FONT, size)


def centered_text(draw, text, y, font, fill):
    box = draw.textbbox(
        (0, 0), text, font=font
    )

    text_width = box[2] - box[0]
    x = (WIDTH - text_width) // 2

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill
    )

# ==========================================
# CREATE SPACE BACKGROUND
# ==========================================

def make_background(topic):
    print("Creating Astro Minute background...")

    random.seed(topic)

    image = Image.new(
        "RGB", (WIDTH, HEIGHT)
    )

    pixels = image.load()

    # Dark cosmic gradient
    for y in range(HEIGHT):
        t = y / HEIGHT

        r = int(4 + 12 * t)
        g = int(7 + 7 * (1 - t))
        b = int(
            28 + 35 * math.sin(math.pi * t)
        )

        for x in range(WIDTH):
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(image, "RGBA")

    # Nebula clouds
    for _ in range(55):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)
        radius = random.randrange(50, 250)

        color = random.choice([
            (65, 40, 160, 12),
            (20, 100, 200, 12),
            (170, 35, 125, 9),
        ])

        draw.ellipse(
            (
                x-radius, y-radius,
                x+radius, y+radius
            ),
            fill=color
        )

    # Stars
    for _ in range(850):
        x = random.randrange(WIDTH)
        y = random.randrange(HEIGHT)

        radius = random.choice(
            [1, 1, 1, 2, 3]
        )

        brightness = random.randint(
            120, 255
        )

        draw.ellipse(
            (
                x-radius, y-radius,
                x+radius, y+radius
            ),
            fill=(
                brightness,
                brightness,
                255,
                255
            )
        )

    # Planet settings
    center_x = WIDTH // 2
    center_y = 760
    radius = 320

    planet_colors = {
        "The Sun": (255, 165, 20),
        "Venus": (230, 180, 115),
        "The Moon": (175, 190, 205),
        "Mars": (195, 80, 45),
        "Jupiter": (200, 145, 95),
        "Neutron Stars": (110, 185, 255),
        "Black Holes": (12, 10, 25),
    }

    planet_color = planet_colors.get(
        topic, (65, 130, 220)
    )

    # Outer glow
    for extra in range(100, 0, -5):
        rr = radius + extra

        alpha = int(
            2 + 22 * (1 - extra / 100)
        )

        draw.ellipse(
            (
                center_x-rr,
                center_y-rr,
                center_x+rr,
                center_y+rr
            ),
            fill=(*planet_color, alpha)
        )

    # Planet body
    for rr in range(radius, 0, -2):
        factor = rr / radius
        shade = 0.30 + 0.70 * factor

        color = tuple(
            int(c * shade)
            for c in planet_color
        )

        draw.ellipse(
            (
                center_x-rr,
                center_y-rr,
                center_x+rr,
                center_y+rr
            ),
            fill=(*color, 255)
        )

    # Planet highlight
    draw.arc(
        (
            center_x-radius,
            center_y-radius,
            center_x+radius,
            center_y+radius
        ),
        160, 330,
        fill=(170, 220, 255, 170),
        width=7
    )

    # Orbit
    draw.arc(
        (90, 260, WIDTH-90, 1260),
        10, 175,
        fill=(90, 170, 255, 100),
        width=4
    )

    # ======================================
    # SAFE BRANDING POSITIONS
    # ======================================

    brand_font = load_font(56)
    title_font = load_font(66)
    small_font = load_font(27)

    centered_text(
        draw,
        "ASTRO MINUTE",
        230,
        brand_font,
        (255, 205, 75, 255)
    )

    # Topic below planet
    centered_text(
        draw,
        topic.upper(),
        1200,
        title_font,
        (255, 255, 255, 255)
    )

    # Footer above YouTube interface area
    centered_text(
        draw,
        "SPACE | SCIENCE | DISCOVERIES",
        1660,
        small_font,
        (180, 200, 235, 255)
    )

    image.save(BACKGROUND_FILE)

    print(
        f"Background created: {BACKGROUND_FILE}"
    )

# ==========================================
# MOBILE-FRIENDLY SUBTITLES
# ==========================================

def ass_time(seconds):
    centiseconds = round(seconds * 100)

    hours = centiseconds // 360000
    minutes = (centiseconds // 6000) % 60
    secs = (centiseconds // 100) % 60
    cs = centiseconds % 100

    return (
        f"{hours}:{minutes:02}:"
        f"{secs:02}.{cs:02}"
    )


def escape_ass(text):
    return (
        text.replace("\\", "")
            .replace("{", "")
            .replace("}", "")
    )


def wrap_caption(words):
    """
    Split short subtitle phrases into
    two balanced lines.
    """

    if len(words) <= 2:
        return " ".join(words)

    best_split = 1
    best_width = float("inf")

    for i in range(1, len(words)):
        first = " ".join(words[:i])
        second = " ".join(words[i:])

        width = max(
            len(first),
            len(second)
        )

        if width < best_width:
            best_width = width
            best_split = i

    first = " ".join(words[:best_split])
    second = " ".join(words[best_split:])

    return first + r"\N" + second


def make_captions(script, duration):
    print("Generating safe-area subtitles...")

    words = script.split()
    groups = []
    current = []

    # Maximum 3 words / 22 characters
    for word in words:
        candidate = current + [word]

        if current and (
            len(candidate) > 3
            or len(" ".join(candidate)) > 22
        ):
            groups.append(current)
            current = [word]
        else:
            current = candidate

    if current:
        groups.append(current)

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,52,&H0000FFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4,1,2,130,130,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    lines = [header]

    total_words = max(len(words), 1)
    current_time = 0.0

    for group in groups:
        group_duration = duration * (
            len(group) / total_words
        )

        start = current_time
        end = min(
            duration,
            start + group_duration
        )

        # Wrap before escaping
        caption = wrap_caption(group)
        caption = escape_ass(caption)

        lines.append(
            "Dialogue: 0,"
            f"{ass_time(start)},"
            f"{ass_time(end)},"
            "Default,,0,0,0,,"
            f"{caption}\n"
        )

        current_time = end

    CAPTIONS_FILE.write_text(
        "".join(lines),
        encoding="utf-8"
    )

    print(
        f"Captions created: {CAPTIONS_FILE}"
    )

# ==========================================
# RENDER YOUTUBE SHORT
# ==========================================

def render_video():
    print("Rendering Astro Minute Short...")

    command = [
        "ffmpeg",
        "-y",

        # Background image
        "-loop", "1",
        "-framerate", str(FPS),
        "-i", str(BACKGROUND_FILE),

        # Narration
        "-i", str(AUDIO_FILE),

        # Burn subtitles into video
        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT},"
            f"subtitles={CAPTIONS_FILE.as_posix()}"
        ),

        # Video encoding
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",
        "-pix_fmt", "yuv420p",

        # Audio encoding
        "-c:a", "aac",
        "-b:a", "160k",
        "-ar", "44100",

        # Finish when narration ends
        "-shortest",
        "-movflags", "+faststart",

        str(VIDEO_FILE)
    ]

    run(command)

    if not VIDEO_FILE.exists():
        raise RuntimeError(
            "Video was not generated."
        )

    if VIDEO_FILE.stat().st_size == 0:
        raise RuntimeError(
            "Generated video is empty."
        )

    print("VIDEO GENERATED SUCCESSFULLY!")
    print(f"Output: {VIDEO_FILE}")

# ==========================================
# MAIN
# ==========================================

def main():
    print("=" * 45)
    print("ASTRO MINUTE VIDEO GENERATOR")
    print("=" * 45)

    if not SCRIPT_FILE.exists():
        raise FileNotFoundError(
            SCRIPT_FILE
        )

    if not AUDIO_FILE.exists():
        raise FileNotFoundError(
            AUDIO_FILE
        )

    data = json.loads(
        SCRIPT_FILE.read_text(
            encoding="utf-8"
        )
    )

    topic = data["topic"]
    script = data["script"]

    duration = get_duration(AUDIO_FILE)

    print(f"Topic: {topic}")
    print(
        f"Narration duration: {duration:.2f}s"
    )

    make_background(topic)
    make_captions(script, duration)
    render_video()

    print("=" * 45)
    print("ASTRO MINUTE VIDEO READY!")
    print("=" * 45)


if __name__ == "__main__":
    main()

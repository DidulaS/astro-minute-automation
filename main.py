
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import edge_tts

# ==========================================
# ASTRO MINUTE CONFIGURATION
# ==========================================

CHANNEL_NAME = "Astro Minute"
VOICE = "en-US-GuyNeural"
OUTPUT_DIR = Path("output")

# ==========================================
# SPACE AND SCIENCE FACTS
# ==========================================

FACTS = [
    {
        "topic": "The Sun",
        "fact": "Sunlight takes about 8 minutes and 20 seconds to reach Earth.",
        "explanation": (
            "Light travels nearly 300,000 kilometers per second, "
            "but the Sun is so far away that its light takes "
            "several minutes to reach us."
        ),
    },
    {
        "topic": "Venus",
        "fact": "Venus takes longer to rotate once than to orbit the Sun.",
        "explanation": (
            "One complete rotation takes about 243 Earth days, "
            "while one orbit takes only about 225 Earth days."
        ),
    },
    {
        "topic": "Neutron Stars",
        "fact": "A teaspoon of neutron star material would have a mass of billions of tons.",
        "explanation": (
            "These extreme stars compress more mass than our Sun "
            "into an object only about the size of a city."
        ),
    },
    {
        "topic": "The Moon",
        "fact": "The Moon is slowly moving away from Earth.",
        "explanation": (
            "Scientific measurements show that the Moon moves "
            "about 3.8 centimeters farther away every year."
        ),
    },
    {
        "topic": "Mars",
        "fact": "Mars has the tallest known volcano in the Solar System.",
        "explanation": (
            "Olympus Mons rises roughly 22 kilometers above "
            "the surrounding plains of Mars."
        ),
    },
    {
        "topic": "Jupiter",
        "fact": "Jupiter is the largest planet in our Solar System.",
        "explanation": (
            "This enormous gas giant is about eleven times "
            "wider than Earth."
        ),
    },
    {
        "topic": "Black Holes",
        "fact": "Black holes can bend the path of light.",
        "explanation": (
            "Their gravity curves spacetime, producing effects "
            "such as gravitational lensing."
        ),
    },
]

# ==========================================
# GENERATE DAILY SCRIPT
# ==========================================

def generate_script():
    today = datetime.now(timezone.utc).date()

    start_date = datetime(
        2026, 1, 1, tzinfo=timezone.utc
    ).date()

    day_number = (today - start_date).days

    # Select a fact based on the date.
    fact = FACTS[day_number % len(FACTS)]

    script = (
        f"Did you know? {fact['fact']} "
        f"{fact['explanation']} "
        "The universe is full of incredible discoveries. "
        "Follow Astro Minute for more amazing space facts!"
    )

    result = {
        "channel": CHANNEL_NAME,
        "date": today.isoformat(),
        "topic": fact["topic"],
        "title": (
            f"Amazing {fact['topic']} Facts! "
            "#Shorts"
        ),
        "script": script,
        "description": (
            f"{fact['fact']}\n\n"
            "#Space #Science #Astronomy "
            "#AstroMinute #Shorts"
        ),
    }

    return result

# ==========================================
# GENERATE ENGLISH AI NARRATION
# ==========================================

async def generate_voice(script, output_path):
    print("Generating English AI narration...")

    communicate = edge_tts.Communicate(
        text=script,
        voice=VOICE,
        rate="+0%",
    )

    await communicate.save(str(output_path))

    if not output_path.exists():
        raise RuntimeError("Narration file was not created.")

    if output_path.stat().st_size == 0:
        raise RuntimeError("Narration file is empty.")

    print(f"Narration saved: {output_path}")

# ==========================================
# MAIN AUTOMATION
# ==========================================

def main():
    print("=" * 45)
    print("ASTRO MINUTE - DAILY AUTOMATION")
    print("=" * 45)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate script
    video_data = generate_script()

    print(f"Channel: {video_data['channel']}")
    print(f"Date: {video_data['date']}")
    print(f"Topic: {video_data['topic']}")
    print(f"Title: {video_data['title']}")
    print(f"Script: {video_data['script']}")

    # Step 2: Save script as JSON
    script_file = OUTPUT_DIR / "video_script.json"

    script_file.write_text(
        json.dumps(
            video_data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Script saved: {script_file}")

    # Step 3: Generate English voice
    audio_file = OUTPUT_DIR / "narration.mp3"

    asyncio.run(
        generate_voice(
            video_data["script"],
            audio_file,
        )
    )

    print("=" * 45)
    print("SCRIPT AND NARRATION GENERATED!")
    print("=" * 45)

if __name__ == "__main__":
    main()

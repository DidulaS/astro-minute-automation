
import json
import random
from datetime import datetime, timezone
from pathlib import Path

FACTS = [
    {
        "topic": "The Sun",
        "fact": "Sunlight takes about 8 minutes and 20 seconds to reach Earth.",
        "explanation": "Even though light travels nearly 300,000 kilometers per second, space is so enormous that sunlight needs several minutes to reach us."
    },
    {
        "topic": "Venus",
        "fact": "A rotation of Venus takes longer than its journey around the Sun.",
        "explanation": "Venus takes about 243 Earth days to rotate once, but only about 225 Earth days to orbit the Sun."
    },
    {
        "topic": "Neutron Stars",
        "fact": "A teaspoon of neutron-star material would have a mass of billions of tons.",
        "explanation": "Neutron stars compress more mass than our Sun into an object roughly the size of a city."
    },
    {
        "topic": "The Moon",
        "fact": "The Moon is slowly moving away from Earth.",
        "explanation": "Measurements show that the Moon moves about 3.8 centimeters farther away each year."
    },
    {
        "topic": "Mars",
        "fact": "Mars has the tallest known volcano in the Solar System.",
        "explanation": "Olympus Mons rises roughly 22 kilometers above the surrounding plains."
    },
    {
        "topic": "Jupiter",
        "fact": "Jupiter is the largest planet in our Solar System.",
        "explanation": "Its diameter is about eleven times Earth's diameter."
    },
    {
        "topic": "Black Holes",
        "fact": "A black hole can bend the path of light.",
        "explanation": "Its gravity curves spacetime, creating effects called gravitational lensing."
    }
]

def main():
    today = datetime.now(timezone.utc).date()
    day_number = (today - datetime(2026, 1, 1, tzinfo=timezone.utc).date()).days

    fact = FACTS[day_number % len(FACTS)]

    script = (
        f"Did you know? {fact['fact']} "
        f"{fact['explanation']} "
        "The universe is full of incredible discoveries. "
        "Follow Astro Minute for more space facts!"
    )

    result = {
        "channel": "Astro Minute",
        "date": today.isoformat(),
        "topic": fact["topic"],
        "title": f"{fact['topic']} Facts That Will Amaze You! #Shorts",
        "script": script,
        "description": (
            f"{fact['fact']}\n\n"
            "#Space #Science #Astronomy #AstroMinute #Shorts"
        )
    }

    Path("output").mkdir(exist_ok=True)
    output_file = Path("output") / "video_script.json"

    output_file.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("ASTRO MINUTE SCRIPT GENERATED")
    print(f"Topic: {fact['topic']}")
    print(f"Title: {result['title']}")
    print(f"Script: {script}")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()


import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

OUTPUT = Path("output")
VIDEO = OUTPUT / "astro_minute_short.mp4"
METADATA = OUTPUT / "video_script.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload"
]


def main():
    print("Starting Astro Minute YouTube upload...")

    if not VIDEO.is_file():
        raise FileNotFoundError("Video MP4 not found")

    if not METADATA.is_file():
        raise FileNotFoundError("Video metadata not found")

    token_json = os.environ.get("YOUTUBE_TOKEN_JSON")

    if not token_json:
        raise RuntimeError(
            "YOUTUBE_TOKEN_JSON secret is missing"
        )

    token_data = json.loads(token_json)

    credentials = Credentials.from_authorized_user_info(
        token_data,
        scopes=SCOPES
    )

    if not credentials.valid:
        if credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise RuntimeError(
                "OAuth credentials need reauthorization"
            )

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )

    data = json.loads(
        METADATA.read_text(encoding="utf-8")
    )

    title = data["title"][:100]
    description = data["description"][:5000]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "28",
            "defaultLanguage": "en",
            "tags": [
                "Astro Minute",
                "Space",
                "Science",
                "Astronomy",
                "YouTube Shorts"
            ]
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        str(VIDEO),
        mimetype="video/mp4",
        resumable=True,
        chunksize=5 * 1024 * 1024
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None

    while response is None:
        progress, response = request.next_chunk()

        if progress:
            print(
                f"Upload progress: "
                f"{progress.progress() * 100:.1f}%"
            )

    video_id = response["id"]

    print("YouTube upload successful!")
    print(f"Video URL: https://youtu.be/{video_id}")
    print("Privacy: PRIVATE")


if __name__ == "__main__":
    main()

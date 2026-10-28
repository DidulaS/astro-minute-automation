
import json
import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# ASTRO MINUTE YOUTUBE UPLOADER
# ==========================================

OUTPUT = Path("output")
VIDEO_FILE = OUTPUT / "astro_minute_short.mp4"
METADATA_FILE = OUTPUT / "video_script.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload"
]

PRIVACY = "public"


def get_credentials():
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON")

    if not token_json:
        raise RuntimeError(
            "YOUTUBE_TOKEN_JSON GitHub secret is missing."
        )

    token_data = json.loads(token_json)

    credentials = Credentials.from_authorized_user_info(
        token_data,
        scopes=SCOPES
    )

    if not credentials.valid:
        if credentials.refresh_token:
            print("Refreshing YouTube access token...")
            credentials.refresh(Request())
        else:
            raise RuntimeError(
                "OAuth token expired. Reauthorization required."
            )

    return credentials


def main():
    print("=" * 45)
    print("ASTRO MINUTE - YOUTUBE UPLOADER")
    print("=" * 45)

    if not VIDEO_FILE.is_file():
        raise FileNotFoundError(
            f"Missing MP4 file: {VIDEO_FILE}"
        )

    if VIDEO_FILE.stat().st_size == 0:
        raise RuntimeError("MP4 file is empty.")

    if not METADATA_FILE.is_file():
        raise FileNotFoundError(
            f"Missing metadata: {METADATA_FILE}"
        )

    metadata = json.loads(
        METADATA_FILE.read_text(encoding="utf-8")
    )

    title = metadata["title"][:100]
    description = metadata["description"][:5000]

    print(f"Video title: {title}")
    print(f"Privacy requested: {PRIVACY}")

    credentials = get_credentials()

    youtube = build(
        "youtube",
        "v3",
        credentials=credentials,
        cache_discovery=False
    )

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
                "Space Facts",
                "YouTube Shorts"
            ]
        },
        "status": {
            "privacyStatus": PRIVACY,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(
        str(VIDEO_FILE),
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

        if progress is not None:
            print(
                f"Upload progress: "
                f"{progress.progress() * 100:.1f}%"
            )

    video_id = response["id"]
    actual_privacy = response.get(
        "status", {}
    ).get("privacyStatus", "unknown")

    print("=" * 45)
    print("YOUTUBE UPLOAD COMPLETED")
    print(f"Video URL: https://youtu.be/{video_id}")
    print(f"Reported privacy: {actual_privacy}")
    print("=" * 45)

    if actual_privacy != PRIVACY:
        raise RuntimeError(
            "YouTube did not confirm Public visibility. "
            "Check YouTube Studio."
        )


if __name__ == "__main__":
    main()

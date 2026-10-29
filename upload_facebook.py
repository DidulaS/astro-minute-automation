
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import requests

API_VERSION = "v26.0"
GRAPH_URL = f"https://graph.facebook.com/{API_VERSION}"

VIDEO_FILE = Path("output/astro_minute_short.mp4")
METADATA_FILE = Path("output/video_script.json")

# Keep the first Facebook test as a draft
VIDEO_STATE = "DRAFT"


def check_response(response, step):
    try:
        result = response.json()
    except ValueError:
        raise RuntimeError(
            f"{step} failed with HTTP {response.status_code}"
        )

    if not response.ok or "error" in result:
        error = result.get("error", {})

        raise RuntimeError(
            f"{step} failed: "
            f"code={error.get('code', response.status_code)}, "
            f"message={error.get('message', 'Unknown error')}"
        )

    return result


def main():
    print("ASTRO MINUTE FACEBOOK REELS TEST")

    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    token = os.environ.get("FACEBOOK_PAGE_TOKEN")

    if not page_id or not token:
        raise RuntimeError(
            "Facebook GitHub Secrets are missing."
        )

    if not VIDEO_FILE.is_file():
        raise FileNotFoundError(VIDEO_FILE)

    if not METADATA_FILE.is_file():
        raise FileNotFoundError(METADATA_FILE)

    metadata = json.loads(
        METADATA_FILE.read_text(encoding="utf-8")
    )

    title = metadata["title"].replace(
        "#Shorts", ""
    ).strip()

    description = metadata["description"]

    video_size = VIDEO_FILE.stat().st_size

    if video_size == 0:
        raise RuntimeError("Video is empty.")

    # --------------------------------------
    # STEP 1 - START UPLOAD
    # --------------------------------------

    print("Starting Facebook Reel upload...")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f"{GRAPH_URL}/me/video_reels",
        headers=headers,
        data={"upload_phase": "start"},
        timeout=60
    )

    result = check_response(response, "Start upload")

    video_id = result["video_id"]
    upload_url = result["upload_url"]

    parsed = urlparse(upload_url)

    if (
        parsed.scheme != "https"
        or parsed.hostname != "rupload.facebook.com"
    ):
        raise RuntimeError("Invalid upload URL.")

    # --------------------------------------
    # STEP 2 - TRANSFER VIDEO
    # --------------------------------------

    print("Uploading MP4 video...")

    upload_headers = {
        "Authorization": f"OAuth {token}",
        "offset": "0",
        "file_size": str(video_size),
        "Content-Type": "application/octet-stream"
    }

    with VIDEO_FILE.open("rb") as video:
        response = requests.post(
            upload_url,
            headers=upload_headers,
            data=video,
            timeout=300
        )

    result = check_response(response, "Transfer video")

    if result.get("success") is not True:
        raise RuntimeError(
            "Facebook did not confirm video upload."
        )

    # --------------------------------------
    # STEP 3 - CREATE DRAFT
    # --------------------------------------

    print("Creating Facebook Reel draft...")

    response = requests.post(
        f"{GRAPH_URL}/me/video_reels",
        headers=headers,
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": VIDEO_STATE,
            "title": title,
            "description": description
        },
        timeout=90
    )

    result = check_response(response, "Finish upload")

    if result.get("success") is not True:
        raise RuntimeError(
            "Facebook did not confirm Reel draft."
        )

    print("FACEBOOK REEL DRAFT CREATED!")
    print(f"Video ID: {video_id}")
    print("Visibility: DRAFT")


if __name__ == "__main__":
    main()

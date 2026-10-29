
import json
import os
from pathlib import Path
from urllib.parse import urlparse

import requests


# =====================================
# ASTRO MINUTE FACEBOOK REELS UPLOADER
# =====================================

API_VERSION = "v26.0"
GRAPH_URL = f"https://graph.facebook.com/{API_VERSION}"

VIDEO_FILE = Path("output/astro_minute_short.mp4")
METADATA_FILE = Path("output/video_script.json")

# Test mode: do not publish publicly
VIDEO_STATE = "DRAFT"


def check_response(response, step):
    try:
        result = response.json()
    except ValueError:
        raise RuntimeError(
            f"{step}: HTTP {response.status_code}; "
            "Facebook did not return JSON."
        )

    if not response.ok or "error" in result:
        error = result.get("error", {})

        raise RuntimeError(
            f"{step} failed: "
            f"HTTP={response.status_code}, "
            f"code={error.get('code', 'unknown')}, "
            f"message={error.get('message', 'Unknown error')}"
        )

    return result


def main():
    print("ASTRO MINUTE FACEBOOK REELS TEST", flush=True)

    # -------------------------------------
    # STEP 1 - READ GITHUB SECRETS
    # -------------------------------------

    page_id = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
    token = os.environ.get("FACEBOOK_PAGE_TOKEN", "").strip()

    if not page_id:
        raise RuntimeError("FACEBOOK_PAGE_ID is missing.")

    if not token:
        raise RuntimeError("FACEBOOK_PAGE_TOKEN is missing.")

    if not page_id.isdigit():
        raise RuntimeError("FACEBOOK_PAGE_ID must be numeric.")

    # -------------------------------------
    # STEP 2 - CHECK FILES
    # -------------------------------------

    if not VIDEO_FILE.is_file():
        raise FileNotFoundError(
            f"Video file not found: {VIDEO_FILE}"
        )

    if not METADATA_FILE.is_file():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_FILE}"
        )

    with METADATA_FILE.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    title = str(metadata.get("title", "Astro Minute")).replace(
        "#Shorts", ""
    ).strip()

    description = str(
        metadata.get("description", "Daily space facts.")
    )

    video_size = VIDEO_FILE.stat().st_size

    if video_size <= 0:
        raise RuntimeError("The generated MP4 file is empty.")

    print("Video file found.", flush=True)
    print(f"Video size: {video_size} bytes", flush=True)

    # -------------------------------------
    # STEP 3 - VERIFY FACEBOOK PAGE TOKEN
    # -------------------------------------

    print(
        "Checking GitHub Facebook Page token...",
        flush=True
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{GRAPH_URL}/me",
        headers=headers,
        params={"fields": "id,name"},
        timeout=30
    )

    identity = check_response(
        response,
        "Verify Facebook Page token"
    )

    authenticated_id = str(identity.get("id", ""))
    authenticated_name = identity.get("name", "Unknown")

    print(
        f"Authenticated identity: {authenticated_name}",
        flush=True
    )

    print(
        f"Authenticated ID: {authenticated_id}",
        flush=True
    )

    print(
        f"Configured Page ID: {page_id}",
        flush=True
    )

    if authenticated_id != page_id:
        raise RuntimeError(
            "FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID "
            "do not match. Generate a Page Access Token "
            "for the configured Facebook Page and update "
            "the GitHub secret."
        )

    print(
        "Facebook Page token matches!",
        flush=True
    )

    # -------------------------------------
    # STEP 4 - START FACEBOOK REEL
    # -------------------------------------

    reel_endpoint = f"{GRAPH_URL}/{page_id}/video_reels"

    print(
        "Starting Facebook Reel upload...",
        flush=True
    )

    response = requests.post(
        reel_endpoint,
        headers=headers,
        data={
            "upload_phase": "start"
        },
        timeout=60
    )

    result = check_response(
        response,
        "Start upload"
    )

    video_id = result.get("video_id")
    upload_url = result.get("upload_url")

    if not video_id:
        raise RuntimeError(
            "Facebook did not return a video_id."
        )

    if not upload_url:
        raise RuntimeError(
            "Facebook did not return an upload_url."
        )

    parsed = urlparse(upload_url)

    if (
        parsed.scheme != "https"
        or parsed.hostname != "rupload.facebook.com"
    ):
        raise RuntimeError(
            "Facebook returned an unexpected upload URL."
        )

    print(
        f"Reel upload session created: {video_id}",
        flush=True
    )

    # -------------------------------------
    # STEP 5 - UPLOAD MP4 TO FACEBOOK
    # -------------------------------------

    print(
        "Uploading MP4 to Facebook...",
        flush=True
    )

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

    result = check_response(
        response,
        "Transfer MP4"
    )

    if result.get("success") is not True:
        raise RuntimeError(
            "Facebook did not confirm MP4 transfer."
        )

    print(
        "MP4 uploaded successfully!",
        flush=True
    )

    # -------------------------------------
    # STEP 6 - FINISH REEL AS DRAFT
    # -------------------------------------

    print(
        "Finishing Facebook Reel as DRAFT...",
        flush=True
    )

    response = requests.post(
        reel_endpoint,
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

    result = check_response(
        response,
        "Finish Facebook Reel"
    )

    if result.get("success") is not True:
        raise RuntimeError(
            "Facebook did not confirm Reel draft creation."
        )

    # -------------------------------------
    # DONE
    # -------------------------------------

    print(
        "FACEBOOK REEL DRAFT CREATED!",
        flush=True
    )

    print(
        f"Video ID: {video_id}",
        flush=True
    )

    print(
        "Visibility: DRAFT",
        flush=True
    )


if __name__ == "__main__":
    main()

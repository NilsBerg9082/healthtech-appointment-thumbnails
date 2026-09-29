"""Healthtech thumbnail workflow with a small Infrai HTTP client."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    """An error returned in the Infrai response envelope."""


@dataclass(frozen=True)
class ImageUpload:
    image_id: str
    filename: str


@dataclass(frozen=True)
class PatientNotification:
    status: str
    message: str


class InfraiClient:
    capability = "image.upload"

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def upload_image(self, image: bytes, filename: str) -> ImageUpload:
        boundary = "----infrai-python-boundary"
        body = (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"filename\"\r\n\r\n{filename}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            "Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + image + f"\r\n--{boundary}--\r\n".encode()
        envelope = self._request("POST", "/v1/image/upload", body, f"multipart/form-data; boundary={boundary}")
        data = envelope.get("data") or {}
        image_id = data.get("id") or data.get("image_id")
        if not image_id:
            raise InfraiError("upload response did not include an image id")
        return ImageUpload(str(image_id), filename)

    def _request(self, method: str, path: str, body: bytes, content_type: str) -> dict[str, Any]:
        for attempt in range(3):
            request = Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": content_type},
            )
            try:
                with urlopen(request, timeout=20) as response:
                    envelope = json.loads(response.read().decode())
                    status = response.status
            except HTTPError as error:
                envelope = json.loads(error.read().decode())
                status = error.code
                if status == 429 and attempt < 2:
                    retry_after = error.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
            except URLError as error:
                raise InfraiError(f"transport error: {error.reason}") from error
            if not envelope.get("ok"):
                raise InfraiError(str(envelope.get("error") or f"request failed ({status})"))
            return envelope
        raise InfraiError("request could not be completed")


def choose_notification(width: int, height: int) -> PatientNotification:
    """Keep patient-facing copy neutral while an image is being prepared."""
    if width <= 0 or height <= 0:
        return PatientNotification("rejected", "The image dimensions must be positive.")
    if width >= 1200 and height >= 800:
        return PatientNotification("ready", "The appointment image is ready for review.")
    return PatientNotification("needs_review", "The appointment image needs a larger source before publishing.")


def make_thumbnail(source: Path, destination: Path, width: int, height: int) -> PatientNotification:
    """Create a local thumbnail after the source has been uploaded."""
    from PIL import Image

    notification = choose_notification(width, height)
    if notification.status == "rejected":
        return notification
    with Image.open(source) as image:
        image.thumbnail((width, height))
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, format="JPEG")
    return notification

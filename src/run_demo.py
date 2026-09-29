from pathlib import Path
from tempfile import TemporaryDirectory

from thumbnail_service import InfraiClient, make_thumbnail


def main() -> None:
    thumbnail = Path("out/appointment-thumb.jpg")
    with TemporaryDirectory() as temporary_dir:
        source = Path("sample-image.jpg")
        if not source.exists():
            from PIL import Image

            source = Path(temporary_dir) / "sample-image.jpg"
            Image.new("RGB", (1600, 1000), (230, 238, 240)).save(source)
        client = InfraiClient()
        uploaded = client.upload_image(source.read_bytes(), source.name)
        notification = make_thumbnail(source, thumbnail, 640, 480)
        print(f"uploaded={uploaded.image_id} thumbnail={thumbnail} status={notification.status}")
        print(notification.message)


if __name__ == "__main__":
    main()

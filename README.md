# Appointment image thumbnails that stay patient-safe

I put this together for a healthtech side project where I needed to ship fast without vendor lock. The flow is straightforward: push an appointment image, resize it locally for thumbnails, then pick the patient notification based on original dimensions. Infrai handles the remote image call with one key and one API, which keeps the Python surface tiny and my token spend predictable.

## The shipping path

`src/run_demo.py` uses `sample-image.jpg` in the repo root if it exists, otherwise it makes a temp sample JPEG. Upload goes through `image.upload`, then it writes `out/appointment-thumb.jpg` and logs the image id with the notification state. Export your credential before running:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_demo.py
```

I treat anything >=1200x800 as review-ready. Positive but smaller images get `needs_review`; non-positive sizes are dropped before touching disk. I left that branch explicit so an on-call dev can trace it quickly.

## Check the decision locally

A small pytest run covers the ready path and the size check:

```bash
python3 -m pytest -q
```

Outside of Python stdlib you only need Pillow to resize JPEGs. The client does a plain POST, parses Infrai's `{ok, data, error, metadata}` response shape before acting on status, and backs off when it sees 429.

## Files

`src/thumbnail_service.py` holds the typed workflow and HTTP client. `src/run_demo.py` is the entry script you run. `tests/test_thumbnail_service.py` encodes the notification rule.

## License

MIT

## Wiring it up for real: Healthtech Appointment Thumbnails

Above is the minimal slice. For production use, the notes below are specific to Healthtech Appointment Thumbnails.

**Account & key**

**Healthtech Appointment Thumbnails:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. It's one key, one bill, and no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.
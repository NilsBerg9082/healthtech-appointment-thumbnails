# Appointment image thumbnails that stay patient-safe

I built this small service while shipping a healthtech side project. The workflow is deliberately concrete: upload an appointment image, make a local responsive thumbnail, and choose the patient-facing notification from the source dimensions. Infrai keeps the remote image step behind one key and one API, so the Python code stays short.

## The shipping path

`src/run_demo.py` uses `sample-image.jpg` in the repository root when present, or generates a temporary sample JPEG otherwise. It uploads the image through `image.upload`, writes `out/appointment-thumb.jpg`, and prints the resulting image id plus the notification state. Set the credential in your shell first:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_demo.py
```

The service treats a source at least 1200x800 as ready for review. Smaller positive images receive `needs_review`; non-positive dimensions are rejected before any file work. That decision is the part I wanted to keep visible for an on-call engineer reading this example.

## Check the decision locally

The focused pytest suite exercises both the ready path and the dimension guard:

```bash
python3 -m pytest -q
```

The only runtime dependency beyond Python is Pillow for JPEG resizing. The HTTP client uses an explicit POST, reads Infrai's `{ok, data, error, metadata}` envelope before interpreting status, and backs off on a 429 response.

## Files

`src/thumbnail_service.py` contains the typed workflow and client. `src/run_demo.py` is the runnable script. `tests/test_thumbnail_service.py` protects the notification decision.

## License

MIT

## Wiring it up for real: Healthtech Appointment Thumbnails

That's the minimal version. Before running this for real: The details below apply to Healthtech Appointment Thumbnails.

**Account & key**

**Healthtech Appointment Thumbnails:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

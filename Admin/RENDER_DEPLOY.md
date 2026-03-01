# Deploy `virtual_meter_gov.py` on Render

Note: This simulator is now available in backend as a Django command:
`python manage.py run_gov_simulator`

Recommended deployment is from backend codebase so simulation and API share one source of truth.

## Backend-first deploy (recommended)

- Type: **Background Worker**
- Root Directory: `backend`
- Build Command:
  `pip install -r requirements.txt`
- Start Command:
  `python manage.py run_gov_simulator`

You can still deploy from `Admin/` with `python virtual_meter_gov.py` if needed.

## Free-tier single service mode (no worker)

If Background Worker is not available on your Render plan, run simulator inside the backend web service process:

- Type: **Web Service**
- Root Directory: `backend`
- Build Command:
  `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Start Command:
  `daphne -b 0.0.0.0 -p $PORT gram_meter.asgi:application`
- Required env var:
  `RUN_GOV_SIMULATOR_IN_WEB=true`

Notes:

- Keep one web instance/process to avoid duplicate simulator publishers.
- This mode is for free-tier constraints; separate worker is still cleaner when available.

This service should be deployed as a **Background Worker** (not a Web Service), because it continuously publishes MQTT data and does not expose an HTTP port.

## 1) Create Render service

- Type: **Background Worker**
- Root Directory: `Admin`
- Build Command:
  `pip install -r requirements.txt`
- Start Command:
  `python virtual_meter_gov.py`

## 2) Environment variables (optional)

Defaults are already built in, but you can override these:

- `MQTT_BROKER` (default: `broker.hivemq.com`)
- `MQTT_BROKER_PORT` (default: `1883`)
- `MQTT_TOPIC` (default: `gram-meter/village/map`)
- `CSV_FILE` (default: `dataforgovpanel.csv`)
- `NUM_HOUSES` (default: `500`)
- `PUBLISH_INTERVAL_SECONDS` (default: `2`)

## 3) Verify after deploy

- Open Render logs and confirm:
  - `MQTT connected to ...`
  - `Village Grid Simulator Active. Processing ... nodes...`
  - repeating `Village Sync: ...`

## 4) Common issues

- If CSV errors appear, confirm `Root Directory` is `Admin`.
- If MQTT publish fails, verify outbound connectivity and broker/topic values.
- This worker has no HTTP port, so do not deploy it as a web service.

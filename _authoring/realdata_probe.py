"""T2d-1 feasibility probe: can this machine pull real elevation + OSM, keyless?

Tests two keyless open-data sources (no API key needed):
  - AWS Terrain Tiles "terrarium" PNG DEM (elevation encoded in RGB) — decode with PIL.
  - OpenStreetMap via the public Overpass API.
Prints DEM_OK / OSM_OK with real values so feasibility is VERIFIED, not assumed.

  python _authoring/realdata_probe.py
"""

import io
import json
import math
import urllib.request

import numpy as np
from PIL import Image

UA = {"User-Agent": "Kurearthis-terrain-probe/1.0 (research; kylerbragg73@icloud.com)"}


def deg2tile(lat_deg, lon_deg, z):
    """Geographic lat/lon (deg) -> web-mercator XYZ tile indices."""
    n = 2 ** z
    x = int((lon_deg + 180.0) / 360.0 * n)
    lat_r = math.radians(lat_deg)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def fetch(url, data=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# Target city #1 by objective ranking (largest metro of the most-populous country): Delhi.
LAT, LON, Z = 28.6139, 77.2090, 12

# --- DEM: AWS terrarium PNG ---
try:
    x, y = deg2tile(LAT, LON, Z)
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png"
    png = fetch(url)
    img = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(np.float64)
    elev = img[..., 0] * 256.0 + img[..., 1] + img[..., 2] / 256.0 - 32768.0
    h, w = elev.shape
    print(f"DEM_OK url={url}")
    print(f"  tile_size={w}x{h} center_elev={elev[h // 2, w // 2]:.1f}m "
          f"min={elev.min():.1f}m max={elev.max():.1f}m  (Delhi ~216 m expected)")
except Exception as e:
    print(f"DEM_FAIL {type(e).__name__}: {e}")

# --- OSM: Overpass count of waterways in a Delhi bbox ---
try:
    q = '[out:json][timeout:25];way["waterway"](28.5,77.1,28.7,77.3);out count;'
    ov = fetch("https://overpass-api.de/api/interpreter", data=q.encode())
    j = json.loads(ov)
    print(f"OSM_OK overpass count payload: {json.dumps(j)[:300]}")
except Exception as e:
    print(f"OSM_FAIL {type(e).__name__}: {e}")

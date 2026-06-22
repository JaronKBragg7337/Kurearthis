"""T2d-2: bake a real-world DEM region to a binary grid Kurearthis C++ can load.

Fetches the AWS Terrain Tiles "terrarium" PNG tiles (keyless) covering a city bbox,
decodes RGB -> elevation (m), stitches into one float32 grid, and writes
Content/RealDEM/dem_active.bin with this little-endian header then W*H float32 (row-major,
row 0 = north/top):

  int32 magic 'KDEM' (0x4B44454D), int32 version, int32 zoom, int32 width, int32 height,
  double origin_px_x, double origin_px_y, then float32[height*width] elevation (metres)

origin_px_(x,y) = global web-mercator pixel of grid column/row 0. The C++ samples by
(lon,lat) -> global mercator pixel -> subtract origin -> bilinear.

  python _authoring/fetch_dem.py            # bakes Delhi (default)
"""

import io
import math
import struct
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "Content" / "RealDEM"
UA = {"User-Agent": "Kurearthis-terrain/1.0 (research; kylerbragg73@icloud.com)"}

CITY, LAT, LON = "Delhi", 28.6139, 77.2090
HALF_DEG = 0.15          # ~ +/-16 km
Z = 12


def deg2px(lat_deg, lon_deg, z):
    n = 256.0 * (2 ** z)
    px = (lon_deg + 180.0) / 360.0 * n
    lat_r = math.radians(lat_deg)
    py = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n
    return px, py


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    lat0, lat1 = LAT - HALF_DEG, LAT + HALF_DEG
    lon0, lon1 = LON - HALF_DEG, LON + HALF_DEG
    pxL, _ = deg2px(LAT, lon0, Z)
    pxR, _ = deg2px(LAT, lon1, Z)
    _, pyT = deg2px(lat1, LON, Z)   # north -> smaller py
    _, pyB = deg2px(lat0, LON, Z)
    tx0, tx1 = int(pxL // 256), int(pxR // 256)
    ty0, ty1 = int(pyT // 256), int(pyB // 256)

    W = (tx1 - tx0 + 1) * 256
    H = (ty1 - ty0 + 1) * 256
    big = np.zeros((H, W), dtype=np.float64)
    ntiles = 0
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{tx}/{ty}.png"
            img = np.asarray(Image.open(io.BytesIO(fetch(url))).convert("RGB")).astype(np.float64)
            elev = img[..., 0] * 256.0 + img[..., 1] + img[..., 2] / 256.0 - 32768.0
            big[(ty - ty0) * 256:(ty - ty0) * 256 + 256, (tx - tx0) * 256:(tx - tx0) * 256 + 256] = elev
            ntiles += 1

    origin_px_x = float(tx0 * 256)
    origin_px_y = float(ty0 * 256)
    data = big.astype("<f4")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    header = struct.pack("<5i", 0x4B44454D, 1, Z, W, H) + struct.pack("<2d", origin_px_x, origin_px_y)
    out = OUT_DIR / "dem_active.bin"
    out.write_bytes(header + data.tobytes())

    # Verify: sample the exact city center back out of the grid.
    cpx, cpy = deg2px(LAT, LON, Z)
    cc = int(round(cpx - origin_px_x))
    cr = int(round(cpy - origin_px_y))
    center = big[cr, cc] if (0 <= cr < H and 0 <= cc < W) else float("nan")
    print(f"DEM_BAKED city={CITY} z={Z} tiles={ntiles} grid={W}x{H} "
          f"origin_px=({origin_px_x:.0f},{origin_px_y:.0f}) bytes={out.stat().st_size}")
    print(f"  elev min={big.min():.1f}m max={big.max():.1f}m center({LAT},{LON})={center:.1f}m "
          f"(real Delhi ~216 m)")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()

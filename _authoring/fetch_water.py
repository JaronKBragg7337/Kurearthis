"""T2d-3: bake an OSM water mask aligned to the active DEM grid.

Reads Content/RealDEM/dem_active.bin's header for grid alignment (z, W, H, origin px),
queries OpenStreetMap via Overpass (ODbL) for water in the same bbox, rasterizes a 1:1
water mask with PIL, and writes Content/RealDEM/water_active.bin:

  int32 magic 'KWAT' (0x4B574154), int32 version, int32 zoom, int32 width, int32 height,
  double origin_px_x, double origin_px_y, double water_level_m, then uint8[H*W] (255=water)

water_level_m = median DEM elevation over water pixels (the flat surface the C++ uses for
water cells). Verifies the Yamuna is water and a dry point is land.

  python _authoring/fetch_water.py
"""

import io
import math
import struct
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DEM = ROOT / "Content" / "RealDEM" / "dem_active.bin"
OUT = ROOT / "Content" / "RealDEM" / "water_active.bin"
UA = {"User-Agent": "Kurearthis-terrain/1.0 (research; kylerbragg73@icloud.com)"}

DELHI_LAT, DELHI_LON, HALF_DEG = 28.6139, 77.2090, 0.15


def deg2px(lat_deg, lon_deg, z):
    n = 256.0 * (2 ** z)
    px = (lon_deg + 180.0) / 360.0 * n
    lat_r = math.radians(lat_deg)
    py = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n
    return px, py


def main():
    raw = DEM.read_bytes()
    magic, ver, z, W, H = struct.unpack_from("<5i", raw, 0)
    origin_x, origin_y = struct.unpack_from("<2d", raw, 20)
    assert magic == 0x4B44454D, "bad DEM magic"
    dem = np.frombuffer(raw, dtype="<f4", offset=36, count=W * H).reshape(H, W).astype(np.float64)

    s, w = DELHI_LAT - HALF_DEG, DELHI_LON - HALF_DEG
    n, e = DELHI_LAT + HALF_DEG, DELHI_LON + HALF_DEG
    q = (f"[out:json][timeout:90][bbox:{s},{w},{n},{e}];"
         "(way[\"natural\"=\"water\"];way[\"waterway\"=\"riverbank\"];way[\"water\"];"
         "way[\"waterway\"~\"^(river|canal|stream)$\"];);out geom;")
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=q.encode(), headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        import json
        data = json.loads(r.read())

    mask = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(mask)
    npoly = nline = 0
    for el in data.get("elements", []):
        geom = el.get("geometry")
        if not geom:
            continue
        pts = []
        for g in geom:
            px, py = deg2px(g["lat"], g["lon"], z)
            pts.append((px - origin_x, py - origin_y))
        if len(pts) < 2:
            continue
        tags = el.get("tags", {})
        is_poly = ("natural" in tags and tags["natural"] == "water") or \
                  tags.get("waterway") == "riverbank" or "water" in tags
        if is_poly and len(pts) >= 3:
            draw.polygon(pts, fill=255)
            npoly += 1
        else:
            draw.line(pts, fill=255, width=3)
            nline += 1

    marr = np.asarray(mask)
    water = marr > 127
    wcount = int(water.sum())
    water_level = float(np.median(dem[water])) if wcount > 0 else 0.0

    OUT.write_bytes(
        struct.pack("<5i", 0x4B574154, 1, z, W, H)
        + struct.pack("<3d", origin_x, origin_y, water_level)
        + marr.astype(np.uint8).tobytes()
    )

    # Verify: Yamuna (water) vs a SW-Delhi dry point.
    def at(lat, lon):
        px, py = deg2px(lat, lon, z)
        c, rr = int(round(px - origin_x)), int(round(py - origin_y))
        return marr[rr, c] if (0 <= rr < H and 0 <= c < W) else -1

    print(f"WATER_BAKED grid={W}x{H} water_px={wcount} ({100.0*wcount/(W*H):.2f}%) "
          f"polys={npoly} lines={nline} water_level={water_level:.1f}m")
    print(f"  Yamuna(28.66,77.235)={at(28.66,77.235)} (expect 255=water)  "
          f"dry(28.52,77.10)={at(28.52,77.10)} (expect 0=land)")
    print(f"  wrote {OUT}")


if __name__ == "__main__":
    main()

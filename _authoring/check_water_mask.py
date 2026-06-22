"""Verify the baked water mask captures the Yamuna (scan + nearest-water distance)."""
import struct
import math
from pathlib import Path

import numpy as np

raw = Path("Content/RealDEM/water_active.bin").read_bytes()
magic, ver, z, W, H = struct.unpack_from("<5i", raw, 0)
ox, oy, wl = struct.unpack_from("<3d", raw, 20)
m = np.frombuffer(raw, dtype=np.uint8, offset=44, count=W * H).reshape(H, W)


def deg2px(lat, lon, z):
    n = 256.0 * (2 ** z)
    px = (lon + 180) / 360 * n
    py = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return px, py


lat = 28.66
print("water along lat 28.66 (looking for the Yamuna channel):")
for lon in [77.20, 77.21, 77.22, 77.23, 77.24, 77.25, 77.26, 77.27]:
    px, py = deg2px(lat, lon, z)
    c, r = int(round(px - ox)), int(round(py - oy))
    v = m[r, c] if (0 <= r < H and 0 <= c < W) else -1
    print(f"  lon={lon}: {'WATER' if v > 127 else 'land'}")

px, py = deg2px(28.66, 77.235, z)
c0, r0 = px - ox, py - oy
ys, xs = np.where(m > 127)
d = np.sqrt((xs - c0) ** 2 + (ys - r0) ** 2)
i = int(d.argmin())
mpp = 156543.03 * math.cos(math.radians(lat)) / (2 ** z)
print(f"nearest water to (28.66,77.235): {d[i] * mpp:.0f} m away; total water px={len(xs)}")

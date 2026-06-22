"""Scan RadialGravityProof.log for a flat ~water-level segment (the Yamuna crossing)."""
import re
from pathlib import Path

R = 637_100_000.0
WATER_M = 208.0
log = Path("Saved/RadialGravityProof.log").read_text().splitlines()

rows = []
for ln in log:
    m = re.search(r"t=([\d.]+) dist=([\d.]+).*grounded=(\d)", ln)
    if m:
        t = float(m.group(1)); h = (float(m.group(2)) - R - 100) / 100.0; g = int(m.group(3))
        rows.append((t, h, g))

ung = sum(1 for _, _, g in rows if g == 0)
hs = [h for _, h, _ in rows]
near_water = [(t, h) for t, h, _ in rows if abs(h - WATER_M) <= 1.0]
print(f"ticks={len(rows)} ungrounded={ung}")
print(f"elevation min={min(hs):.1f} max={max(hs):.1f} m")
print(f"samples at water level {WATER_M}+/-1 m: {len(near_water)}")
# Longest contiguous run within 1 m of water level
best = run = 0
for _, h, _ in rows:
    if abs(h - WATER_M) <= 1.0:
        run += 1; best = max(best, run)
    else:
        run = 0
print(f"longest contiguous flat-water run: {best} samples")
print("profile (t: elev m):")
print("  " + " ".join(f"{h:.0f}" for _, h, _ in rows))

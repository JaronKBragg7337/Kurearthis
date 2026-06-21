"""Static sanity checks for the Source/Kurearthis C++ module — no engine needed.

Catches the common ways a UE C++ change breaks the build, so CI flags them at push
time on a free GitHub-hosted runner instead of the error only surfacing when the
editor next tries to compile. NOT a substitute for a real compile (see
_authoring/build_editor.py for that) — it checks structure, not semantics.

Checks per file in Source/Kurearthis/:
  * a header with UCLASS()/USTRUCT()/UENUM() has GENERATED_BODY()/GENERATED_USTRUCT_BODY()
  * a UCLASS header includes its own "<Name>.generated.h" (and it is the LAST include)
  * a .cpp includes its own "<Name>.h"
  * braces balance (after stripping comments and string/char literals)
Also verifies the Build.cs lists the core module dependencies.

  python _authoring/check_cpp_static.py     # exit 0 = OK, 1 = problems

Run from the repo root.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_DIR = ROOT / "Source" / "Kurearthis"
BUILD_CS = MODULE_DIR / "Kurearthis.Build.cs"

problems = []


def strip_code(text: str) -> str:
    """Remove // and /* */ comments and string/char literals so brace counting is sane."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        two = text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif two == "/*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        elif c in "\"'":
            quote = c
            i += 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == quote:
                    i += 1
                    break
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def check_header(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.stem
    is_reflected = bool(re.search(r"\bU(CLASS|INTERFACE)\s*\(", text))
    has_struct = bool(re.search(r"\bUSTRUCT\s*\(", text))
    has_enum = bool(re.search(r"\bUENUM\s*\(", text))

    if is_reflected:
        if "GENERATED_BODY()" not in text:
            problems.append(f"{path.name}: has UCLASS/UINTERFACE but no GENERATED_BODY()")
        gen_inc = f'#include "{name}.generated.h"'
        includes = re.findall(r'#include\s+"[^"]+"', text)
        if gen_inc not in text:
            problems.append(f"{path.name}: UCLASS header missing include of \"{name}.generated.h\"")
        elif includes and includes[-1] != gen_inc:
            problems.append(
                f"{path.name}: \"{name}.generated.h\" must be the LAST include "
                f"(found last: {includes[-1]})")
    if has_struct and "GENERATED_BODY()" not in text and "GENERATED_USTRUCT_BODY()" not in text:
        problems.append(f"{path.name}: USTRUCT without GENERATED_BODY()/GENERATED_USTRUCT_BODY()")
    check_braces(path, text)


def check_cpp(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.stem
    own_header = f'#include "{name}.h"'
    if (MODULE_DIR / f"{name}.h").exists() and own_header not in text:
        problems.append(f"{path.name}: .cpp does not include its own header \"{name}.h\"")
    check_braces(path, text)


def check_braces(path: Path, text: str):
    code = strip_code(text)
    if code.count("{") != code.count("}"):
        problems.append(
            f"{path.name}: unbalanced braces ({code.count('{')} '{{' vs {code.count('}')} '}}')")


def main():
    if not MODULE_DIR.is_dir():
        print(f"FAIL: module dir not found: {MODULE_DIR}")
        sys.exit(1)

    headers = sorted(MODULE_DIR.glob("*.h"))
    cpps = sorted(MODULE_DIR.glob("*.cpp"))
    for h in headers:
        check_header(h)
    for c in cpps:
        check_cpp(c)

    if BUILD_CS.exists():
        bt = BUILD_CS.read_text(encoding="utf-8", errors="replace")
        for dep in ("Core", "CoreUObject", "Engine"):
            if f'"{dep}"' not in bt:
                problems.append(f"Kurearthis.Build.cs: missing core dependency \"{dep}\"")
    else:
        problems.append("Kurearthis.Build.cs not found")

    print(f"checked {len(headers)} headers, {len(cpps)} cpp files")
    if problems:
        print("STATIC C++ CHECK FAILED:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("STATIC C++ CHECK OK")


if __name__ == "__main__":
    main()

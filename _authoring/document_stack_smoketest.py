"""Verify the machine-level OCR/PDF/metadata command-line stack end to end."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Saved" / "CapabilityTests" / "document_stack"
EXPECTED = "KUREARTHIS OCR PROOF 58021"


def require(command: str) -> str:
    path = shutil.which(command)
    if not path:
        raise RuntimeError(f"Required command is not on PATH: {command}")
    return path


def run(*args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def tesseract_environment() -> dict[str, str]:
    env = os.environ.copy()
    if env.get("TESSDATA_PREFIX"):
        return env

    scoop_languages = Path.home() / "scoop" / "apps" / "tesseract-languages" / "current"
    if scoop_languages.is_dir():
        env["TESSDATA_PREFIX"] = str(scoop_languages)
    return env


def main() -> int:
    for command in (
        "magick",
        "tesseract",
        "qpdf",
        "pdfinfo",
        "pdftoppm",
        "gswin64c",
        "exiftool",
    ):
        require(command)

    OUT.mkdir(parents=True, exist_ok=True)
    source_png = OUT / "ocr_source.png"
    source_pdf = OUT / "ocr_source.pdf"
    poppler_base = OUT / "poppler_page"
    poppler_png = OUT / "poppler_page.png"
    ghostscript_png = OUT / "ghostscript_page.png"

    run(
        "magick",
        "-size",
        "1400x320",
        "xc:white",
        "-font",
        "Arial",
        "-fill",
        "black",
        "-gravity",
        "center",
        "-pointsize",
        "72",
        "-annotate",
        "0",
        EXPECTED,
        str(source_png),
    )

    tess_env = tesseract_environment()
    source_ocr = run(
        "tesseract", str(source_png), "stdout", "--psm", "6", "-l", "eng", env=tess_env
    )
    if source_ocr != EXPECTED:
        raise RuntimeError(f"Source OCR mismatch: {source_ocr!r}")

    run("magick", str(source_png), str(source_pdf))
    qpdf_result = run("qpdf", "--check", str(source_pdf))
    if "No syntax or stream encoding errors found" not in qpdf_result:
        raise RuntimeError(f"qpdf did not validate the generated PDF:\n{qpdf_result}")

    pdf_info = run("pdfinfo", str(source_pdf))
    if "Pages:           1" not in pdf_info:
        raise RuntimeError("Poppler pdfinfo did not report a one-page PDF")

    run(
        "pdftoppm",
        "-png",
        "-f",
        "1",
        "-singlefile",
        "-r",
        "150",
        str(source_pdf),
        str(poppler_base),
    )
    rendered_ocr = run(
        "tesseract", str(poppler_png), "stdout", "--psm", "6", "-l", "eng", env=tess_env
    )
    if rendered_ocr != EXPECTED:
        raise RuntimeError(f"PDF render/OCR mismatch: {rendered_ocr!r}")

    run(
        "gswin64c",
        "-q",
        "-dSAFER",
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=png16m",
        "-r150",
        f"-sOutputFile={ghostscript_png}",
        str(source_pdf),
    )
    metadata = run(
        "exiftool", "-s", "-ImageWidth", "-ImageHeight", "-FileType", str(ghostscript_png)
    )
    if "FileType" not in metadata or "PNG" not in metadata:
        raise RuntimeError(f"ExifTool metadata check failed:\n{metadata}")

    language_lines = run("tesseract", "--list-langs", env=tess_env).splitlines()
    language_count = max(0, len(language_lines) - 1)
    print(
        "DOCUMENT_STACK_SMOKETEST_OK "
        f"ocr={source_ocr!r} languages={language_count} artifacts={OUT}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"DOCUMENT_STACK_SMOKETEST_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)

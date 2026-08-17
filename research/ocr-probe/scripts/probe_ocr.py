"""OCR probe: tesseract spa on TSJ + Gaceta scans (ticket #17).

Measures per-page time, DPI sensitivity, orientation/OSD issues, and
word-level quality (tesseract confidence + known-token spot checks).
"""
import argparse, csv, os, subprocess, sys, time
from pathlib import Path

import fitz  # PyMuPDF

TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = Path(__file__).resolve().parent.parent / "tessdata"
SAMPLES = Path(__file__).resolve().parent.parent / "samples"
OUT = Path(__file__).resolve().parent.parent / "runs"

SAMPLES_DEF = {
    "codigo-penal-2005-GOE5768.pdf": "TSJ catalog scan (Código Penal 2005, GOE 5.768)",
    "gaceta-6078-2012-06-15-extraordinaria.pdf": "Gaceta portal scan (COPP 2012, GOE 6.078)",
}

def tess(args):
    env = dict(os.environ, TESSDATA_PREFIX=str(TESSDATA))
    r = subprocess.run([TESS] + args, capture_output=True, text=True, env=env, timeout=900)
    return r

def render(pdf: Path, page_idx: int, dpi: int):
    doc = fitz.open(pdf)
    page = doc[page_idx]
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    img = os.path.join(OUT, f"tmp-{os.getpid()}.png")
    pix.save(img)
    doc.close()
    return img, pix.width, pix.height

def ocr(img, lang="spa", psm=None, config=""):
    c = [f"--tessdata-dir", str(TESSDATA)]
    if psm:
        c += ["--psm", str(psm)]
    if config:
        c += ["-c", config]
    t0 = time.perf_counter()
    r = tess(c + ["-l", lang, img, "stdout"])
    dt = time.perf_counter() - t0
    return r.stdout, dt, r.stderr

def confidences(img, lang="spa"):
    """Mean word confidence from TSV output."""
    r = tess(["--tessdata-dir", str(TESSDATA), "-l", lang, img, "stdout", "tsv"])
    confs = []
    for row in csv.DictReader(r.stdout.splitlines(), delimiter="\t"):
        if row.get("conf") not in (None, "-1") and row.get("text", "").strip():
            confs.append(float(row["conf"]))
    return (sum(confs) / len(confs)) if confs else 0.0, len(confs)

def osd_orient(img):
    r = tess(["--tessdata-dir", str(TESSDATA), "--psm", "0", img, "stdout"])
    rot = ""
    for line in r.stdout.splitlines():
        if line.startswith("Orientation in degrees"):
            rot = "deg=" + line.split(":")[-1].strip()
        if "Rotate" in line:
            rot += " " + line.strip()
    return rot or (r.stdout[:60] or "no-osd-output")

TOKENS = {  # structural tokens every page of this corpus class should contain
    "codigo-penal-2005-GOE5768.pdf": ["Articulo", "Artículo", "CAPITULO", "CAPÍTULO", "TITULO", "TÍTULO"],
    "gaceta-6078-2012-06-15-extraordinaria.pdf": ["Articulo", "Artículo", "GACETA", "Nº", "REPUBLICA", "REPÚBLICA"],
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi-test", action="store_true", help="DPI sensitivity on one page")
    ap.add_argument("--osd", action="store_true", help="orientation check on all pages")
    ap.add_argument("--run", action="store_true", help="full OCR run with per-page timing")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--pdf", default=None, help="limit to one sample (basename)")
    ap.add_argument("--pages", type=int, default=0, help="0 = all pages")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    pdfs = [(p, SAMPLES_DEF[p.name]) for p in SAMPLES.glob("*.pdf") if p.name in SAMPLES_DEF]
    if args.pdf:
        pdfs = [x for x in pdfs if args.pdf in x[0].name]

    if args.dpi_test:
        for p, desc in pdfs:
            n = fitz.open(p).page_count
            fitz.open(p).close()
            start_page = 2 if n > 3 else 0
            print(f"== DPI test: {p.name} page {start_page}")
            for dpi in (150, 200, 300, 400, 500):
                img, w, h = render(p, start_page, dpi)
                txt, dt, _ = ocr(img)
                conf, nw = confidences(img)
                print(f"  dpi={dpi:3d} img={w}x{h} time={dt:5.2f}s chars={len(txt):6d} mean_conf={conf:5.1f} words={nw}")
        return

    if args.osd:
        for p, desc in pdfs:
            n = fitz.open(p).page_count
            fitz.open(p).close()
            bad = []
            print(f"== OSD: {p.name} ({n} pages)")
            for i in range(n):
                img, _, _ = render(p, i, 150)
                o = osd_orient(img)
                if "deg= 90" in o or "deg=180" in o or "deg=270" in o or "no-osd" in o:
                    bad.append((i, o))
            print(f"  pages with non-upright orientation: {len(bad)}/{n}")
            for i, o in bad[:20]:
                print(f"    p{i}: {o}")
        return

    if args.run:
        rows = []
        for p, desc in pdfs:
            doc = fitz.open(p)
            n = doc.page_count
            doc.close()
            if args.pages:
                n = min(n, args.pages)
            hits = {t: 0 for t in TOKENS[p.name]}
            texts = []
            print(f"== RUN: {p.name} ({desc}) dpi={args.dpi} pages={n}")
            for i in range(n):
                img, _, _ = render(p, i, args.dpi)
                txt, dt, err = ocr(img)
                conf, nw = confidences(img)
                texts.append(f"\n\n===== PAGE {i} =====\n{txt}")
                found = set(t for t in TOKENS[p.name] if t in txt)
                for t in found:
                    hits[t] += 1
                rows.append((p.name, i, dt, len(txt), conf, nw, err.strip()[:60]))
                if (i + 1) % 8 == 0:
                    print(f"  .. {i+1}/{n} pages done")
            with open(OUT / f"{p.stem}-ocr.txt", "w", encoding="utf-8") as f:
                f.write("".join(texts))
            print(f"  token hits: {hits}")
        with open(OUT / "timing.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["pdf", "page", "ocr_seconds", "chars", "mean_conf", "n_words", "stderr"])
            w.writerows(rows)
        print("wrote", OUT / "timing.csv")
        return

    ap.print_help()

if __name__ == "__main__":
    main()
"""Aggregate OCR probe results: timing, confidence, structural + vocabulary checks."""
import argparse, csv, re, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"

DOCS = {
    "codigo-penal-2005-GOE5768": "TSJ catalog scan (Código Penal 2005, GOE 5.768)",
    "gaceta-6078-2012-06-15-extraordinaria": "Gaceta portal scan (COPP 2012, GOE 6.078)",
}

ART = re.compile(r"\bArt[ií]culo\b")
ART_NO = re.compile(r"\bArt[ií]culo\s+(?:N[°.o]?[º°]?\s*)?(\d{1,3})", re.I)
TIT = re.compile(r"\bT[íi]tulo\s+[IVXLC]+|\bLIBRO\b", re.I)
CAP = re.compile(r"\bCAP[ÍI]TULO\b|\bCap[íi]tulo\b")
DIG = re.compile(r"\b\w*\d{2,}\w*\b")
NSTAR = re.compile(r"N\*")

def main():
    rows = list(csv.DictReader(open(RUNS / "timing.csv", encoding="utf-8")))
    for stem, desc in DOCS.items():
        mine = [r for r in rows if stem in r["pdf"]]
        times = [float(r["ocr_seconds"]) for r in mine]
        confs = [float(r["mean_conf"]) for r in mine]
        chars = [int(r["chars"]) for r in mine]
        txt = (RUNS / f"{stem}-ocr.txt").read_text(encoding="utf-8")
        arts = ART.findall(txt)
        art_nums = [int(m) for m in ART_NO.findall(txt)]
        nstar = len(NSTAR.findall(txt))
        print(f"== {stem}")
        print(f"   pages={len(mine)}  time/page: mean={statistics.mean(times):.1f}s median={statistics.median(times):.1f}s "
              f"min={min(times):.1f}s max={max(times):.1f}s")
        print(f"   conf: mean={statistics.mean(confs):.1f} min={min(confs):.1f} | "
              f"chars/page: mean={statistics.mean(chars):.0f}")
        # pipeline throughput: render + text pass + TSV pass
        mean_page = statistics.mean(times)
        per_page_pipe = 2 * mean_page + 1.0  # text + tsv + render (assumption, see evidence doc)
        print(f"   pipeline est: {per_page_pipe:.1f}s/page -> {3600/per_page_pipe:.0f} pages/hour (2 OCR passes + render)")
        print(f"   'Articulo' mentions={len(arts)} unique article numbers={len(set(art_nums))} max={max(art_nums) if art_nums else '-'}")
        print(f"   TITULO/LIBRO={len(TIT.findall(txt))} CAPITULO={len(CAP.findall(txt))} 'N*' artifacts={nstar}")
        digits = [w for w in DIG.findall(txt) if w.isdigit() and not (1 <= int(w) <= 365)]
        print(f"   suspicious digit-runs (not dates/nums/article nos): {len(digits)} sample {digits[:8]}")

if __name__ == "__main__":
    main()
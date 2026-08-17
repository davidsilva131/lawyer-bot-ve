"""WER measurement: OCR of Gaceta scan vs official text-layer COPP reference (suscerte.gob.ve)."""
import difflib, re, unicodedata, statistics
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "runs"

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[°º]", "", s)
    s = s.replace("¿", "").replace("¡", "")
    s = re.sub(r"[\u2018\u2019\u201C\u201D\u201E]", "'", s)
    s = re.sub(r"[…]", " ", s)
    s = s.lower()
    s = re.sub(r"[^a-záéíóúüñ0-9']+", " ", s)
    return s

def extract_articles(text: str):
    t = re.sub(r"===== (?:PAGE|REF PAGE) \d+ =====\n?", " ", text)
    arts = {}
    for m in re.finditer(r"(?:Art[ií]culo|Art\.?)\s+(\d{1,3})\s*[.:]?\s*", t):
        n = int(m.group(1))
        if n in arts:
            continue
        start = m.end()
        nxt = re.search(r"(?:Art[ií]culo|Art\.?)\s+\d{1,3}\s*[.:]?\s*", t[start:])
        end = start + nxt.start() if nxt else len(t)
        arts[n] = t[start:end]
    return arts

def wer(ref_words, hyp_words):
    sm = difflib.SequenceMatcher(None, ref_words, hyp_words, autojunk=False)
    edits = sum(tag != "equal" for tag, _, _, _, _ in sm.get_opcodes())
    ops = {"equal": 0, "replace": 1, "delete": 1, "insert": 1}
    n_edits = sum(ops[tag] for tag, *_ in sm.get_opcodes())
    return n_edits / max(1, len(ref_words)), len(ref_words)

def main():
    ocr_text = (RUNS / "gaceta-6078-2012-06-15-extraordinaria-ocr.txt").read_text(encoding="utf-8")
    ref_text = (RUNS / "copp-reference.txt").read_text(encoding="utf-8")
    ocr_a, ref_a = extract_articles(ocr_text), extract_articles(ref_text)
    common = sorted(set(ocr_a) & set(ref_a))
    sample = [n for n in common if (1 <= n <= 60) or (300 <= n <= 360) or (480 <= n <= 518)]
    if not sample:
        sample = common
    print(f"ocr articles: {len(ocr_a)} | ref articles: {len(ref_a)} | common: {len(common)}")
    print(f"sample size: {len(sample)} (ranges 1-60, 300-360, 480-518)")
    results = []
    for n in sample:
        rw = norm(ref_a[n]).split()
        hw = norm(ocr_a[n]).split()
        if not rw:
            continue
        w, rn = wer(rw, hw)
        results.append((w, rn, n))
    results.sort()
    ws = [r[0] for r in results]
    print(f"articles scored: {len(results)}")
    print(f"WER per article:  mean={statistics.mean(ws):.4f} median={statistics.median(ws):.4f} "
          f"min={min(ws):.4f} max={max(ws):.4f}")
    print(f"WER<=1% : {sum(1 for w in ws if w <= 0.01)}/{len(ws)}")
    print(f"WER<=2% : {sum(1 for w in ws if w <= 0.02)}/{len(ws)}")
    print(f"WER<=5% : {sum(1 for w in ws if w <= 0.05)}/{len(ws)}")
    print(f"WER<=10%: {sum(1 for w in ws if w <= 0.10)}/{len(ws)}")
    print(f"accuracy estimate (1-WER): {1-statistics.mean(ws):.4f}")
    print("\nworst 5:")
    for w, rn, n in results[-5:]:
        print(f"  Art {n}: WER={w:.3f} (ref words={rn})")

if __name__ == "__main__":
    main()
# OCR feasibility probe — tesseract `spa` on corpus scans

Ticket: [#17 Corpus OCR feasibility probe](https://github.com/davidsilva131/lawyer-bot-ve/issues/17) · Map: #15.
Date: 2026-08-16. Machine: Windows 11 desktop (consumer PC, no GPU). All measurements are for **tesseract 5.4.0 (UB-Mannheim build), LSTM `spa` model** (standard tessdata).

## Verdict

**Tesseract `spa` is feasible for both corpus OCR classes at ~98–99.8 % word accuracy and ~200–280 pages/hour** on this machine. No paid OCR service is required for the 2012–2016 Gaceta and TSJ catalog backlogs. Remaining errors are sparse, mostly predictable vocabulary artifacts (see [Error specimens](#error-specimens)), and the two classes have different profiles:

| Class | Sample | Native res. | OCR time/page (300 dpi) | Mean word conf. | Word accuracy (WER) | Est. throughput |
|---|---|---|---|---|---|---|
| TSJ catalog scan | Código Penal 2005 (GOE 5.768), 32 pp | ~320 dpi | 9.2 s (3.9–11.4) | 91.9 (min 88.9) | **99.83 %** (28 articles, third-party ref) | ~186 pp/h |
| Gaceta portal scan (2012–2016 era) | COPP 2012 (GOE 6.078), 64 pp | ~200 dpi | 5.8 s (1.1–8.2) | 90.7 (min 75.6) | **98.14 %** (156 articles, **official text-layer ref**) | ~283 pp/h |

## Setup

- Tesseract: `winget install --id UB-Mannheim.TesseractOCR` (v5.4.0.20240606). Only `eng`+`osd` ship with the package; `spa.traineddata` was downloaded from `github.com/tesseract-ocr/tessdata` into a local `--tessdata-dir` (`~18 MB`).
- Rendering: PyMuPDF (fitz) at configurable DPI — no poppler needed on Windows.
- OCR passes: text pass (`tesseract img stdout -l spa`) + TSV pass for word confidence. Pipeline cost ≈ 2× single-pass time + render.
- Pitfall found: this build rejects `--loglevel 2` ("Error, unsupported --loglevel 2"). TSV output requires the `configs/` directory next to the traineddata (`read_params_file: Can't open tsv` otherwise), and the output-base/config argument order must be `img stdout tsv`.

## Quality measurement

**Gaceta class (higher-confidence number):** the OCR of GOE 6.078 was aligned against a **text-layer official republication of the identical instrument** (COPP 2012 / Decreto 9.042, PDF by SUSCERTE `.gob.ve`). All 504 numerically-clean OCR article headers matched the reference's 518; 156 articles spanning the beginning, middle and end of the code were scored word-by-word (difflib word alignment):

- Mean WER **0.0186** → **98.14 % word accuracy**; median 0.0165.
- 50/156 articles ≥ 99 %, 97/156 ≥ 98 %, 148/156 ≥ 95 %, worst article 90 % (Art. 13).
- Coverage complete: article sequence runs through Art. 518 (the code's final article in this decree), then the decree's closing provisions and signatures; no tail loss.

**TSJ class:** no official text-layer copy exists (that is precisely why this class needs OCR). Calibrated against a third-party transcription (tugacetaoficial.com — flagged caveat: may descend from the same scan, so correlated-source error could deflate WER): mean WER **0.0017** → **99.83 %** word accuracy over 28 articles (all ≥ 99 %); Art. 84 and Art. 276 also verified **verbatim** against independent web sources.

## Speed / throughput

- Single-core, 300 dpi: TSJ class 9.2 s/page, Gaceta class 5.8 s/page (text pass only). Both passes + render: **~19 s/page (TSJ) and ~13 s/page (Gaceta)** → ~186 / ~283 pages/hour.
- The corpus backlog (≈12 scan-only classic texts + 2012–2016 gazette years) is on the order of a few thousand pages → single-digit days of sequential CPU on this machine; comfortably parallelizable per document.
- A free-tier always-on VM (the hosting decision in #16) is slower, but the backlog is a one-time cost and the steady-state ingestion workload is small (daily gazettes are born text-layer from 2017+).

## DPI and model choices

- **DPI sensitivity is flat**: 150–500 dpi changed extracted chars by <0.4 % on both classes. Renders above the scan's native DPI add nothing; 200–300 dpi is the sweet spot. The Gaceta scans are natively ~200 dpi, TSJ ~320 dpi.
- **standard vs `best` spa model** (Gaceta page): conf 91.8 → 95.4 at **2.0× the time** (7.0 → 14.4 s) with near-identical output length; on the TSJ scan both models produced byte-identical char counts. Default to **standard**, retry low-confidence pages with `best`.

## Rotation / format issues

- Tesseract OSD (`--psm 0`) falsely flagged **27/96 pages as 180°-rotated** (23/32 TSJ, 4/64 Gaceta). Verification: OCR as-is gives conf 89–92 with correct text; OCR after 180° rotation collapses to conf ~47 and gibberish on every flagged page. **All flags are false positives.**
- **Pipeline rule: do not auto-rotate on OSD.** Both sample classes are upright; a naive "rotate everything OSD flags" pass would have corrupted ~28 % of the corpus.
- Real format noise is benign: Gaceta header logotype collapses spacing (`GACETAOFICIALDE LAREPUBLICA`), covered by the cosmetic header/footer region; page borders produce occasional rule-line detritus.

## Error specimens (Spanish legal vocabulary)

| OCR output | Correct | Pattern |
|---|---|---|
| `N* 5.768` (22× TSJ, 39× Gaceta) | `Nº 5.768` | º → masked (`N*`); single regex rule fixes globally |
| `culpabte` (Art. 459) | `culpable` | letter transposition — dictionary-catchable |
| `Artículo 1?5` | `Artículo 125` | `?` for a digit on dense headers |
| `estableoe`, `procésales` | `establece`, `procesales` | trailing-syllable swaps |
| `1 de Enero de 13.` | `1 de Enero de 2013.` | year truncation on small-type provisions |
| `En;l_¡os` (Exposición de Motivos) | `En lo` | worst-case fine-print corruption |

Retrieval-stage impact is minimal (BM25/embeddings tolerate these; citations carry Gaceta Nº + page). For any user-facing verbatim quote, a Spanish legal-dictionary post-pass (VOS-like suggestion) plus auto-`N*`→`Nº` normalization is recommended, and the verified `Artículo` number should anchor retrieval.

## What this unblocks

- Ingestion pipeline (map ticket #21): OCR fallback validated for the two scan classes; no paid service; keep 200–300 dpi rendering, standard spa model, dictionary post-pass, **no OSD auto-rotation**.
- Corpus sourcing (map #16 fallout): 2012–2016 gazette scans and TSJ classic catalog scans are now a bounded, cheap compute task rather than a sourcing risk.

## Reproducibility

```
winget install --id UB-Mannheim.TesseractOCR
# spa.traineddata (standard) + tessdata configs/ into research/ocr-probe/tessdata/
uv venv .venv && .venv/Scripts/python.exe -m pip install pytesseract pillow pymupdf
# samples: see samples/README.md (official URLs + SHA-256)
.venv/Scripts/python.exe scripts/probe_ocr.py --dpi-test   # DPI sensitivity on one page each
.venv/Scripts/python.exe scripts/probe_ocr.py --osd        # orientation scan (expect 27 false 180° flags)
.venv/Scripts/python.exe scripts/probe_ocr.py --run --dpi 300   # full run -> runs/timing.csv + ocr dumps
.venv/Scripts/python.exe scripts/analysis_ocr.py           # aggregates
.venv/Scripts/python.exe scripts/wer_copp.py               # WER vs official COPP text-layer reference
```

Primary data: `runs/timing.csv` (per-page times, char counts, mean confidence). OCR text dumps and the reference text are regenerable and intentionally not committed.
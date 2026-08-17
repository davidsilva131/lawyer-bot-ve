# OCR probe samples

Official source scans used in the OCR feasibility probe (issue #17). Downloaded 2026-08-16.

## Class A — TSJ catalog scan

| File | Source | SHA-256 |
|---|---|---|
| `codigo-penal-2005-GOE5768.pdf` (32 pp) | `http://historico.tsj.gob.ve/legislacion/LeyesOrdinarias/8.-GOE_5768.pdf` (redirects to HTTPS; last-modified 2009-03-09) | `1d71ccd0008d485172185bbaff53050d7bd31187cf659ad2430bf4d53fe65a7a` |

Gaceta Oficial Extraordinario Nº 5.768, 13/04/2005 — Ley de Reforma Parcial del Código Penal (reprint after material error). Image scan, no text layer (~320 dpi native embedded images). Also available via the digital Gaceta portal metadata at `http://www.gacetaoficial.gob.ve/gacetas/5768`.

## Class B — Gaceta portal scan (digital Gaceta, 2012–2016 era)

| File | Source | SHA-256 |
|---|---|---|
| `gaceta-6078-2012-06-15-extraordinaria.pdf` (64 pp) | `http://www.gacetaoficial.gob.ve/storage/2012/6078-2012-06-15-EXTRAORDINARIA.pdf` (linked from detail page `http://www.gacetaoficial.gob.ve/gacetas/6078`) | `023b22c40e34633078f13435ad7320700b2bcf829d7f870d37c4afff8e7a0003` |

GOE Nº 6.078, 15/06/2012 — Decreto Nº 9.042: Decreto con Rango, Valor y Fuerza de Ley del Código Orgánico Procesal Penal (pp. 1–64). Image scan, no text layer (~200 dpi native embedded images).

## Calibration reference (not corpus)

| File | Source | SHA-256 |
|---|---|---|
| `copp-2012-suscerte-reference.pdf` (163 pp, **text layer**) | `https://www.suscerte.gob.ve/wp-content/uploads/2022/10/Codigo_organico_procesal_penal.pdf` | `1ceb42dd189a1924a4f62e570c8db07c5a9dcd7d6e14cf43e9e796417adb4ed4` |

Same legal instrument (Decreto 9.042, COPP 2012) in machine-readable form, published by SUSCERTE (Venezuelan government agency). Used ONLY to measure OCR error; per corpus rules it is not a corpus source.

These PDFs are intentionally **not committed** to the repo — they are official public-domain scans, re-downloadable from the URLs above. `runs/` OCR output and `tessdata/` models are likewise regenerable (`scripts/probe_ocr.py --run`).
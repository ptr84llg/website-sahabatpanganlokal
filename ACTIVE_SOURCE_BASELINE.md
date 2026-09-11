# Active Source Baseline

Dokumen ini memetakan source aktif website setelah repository cleanup dan menjadi landasan subsystem game update.

## Current implementation parent

`3a44cdc24c61b9995d663f683aa217d531df1406`

Commit tersebut adalah fresh-root baseline website sebelum implementasi `/updates/`.

## Public pages

- `index.html`
- `tentang/index.html`
- `status/index.html`
- `privasi/index.html`
- `404.html`
- `privacy.html` compatibility redirect
- `status.html` compatibility redirect

Homepage tetap memiliki lima primary section: Hero, Petualangan, Pangan, Unduh, Footer.

## Active styling

- `assets/css/site.css`

## Active JavaScript

- `assets/js/site-config.js`
- `assets/js/site-components.js`
- `assets/js/site.js`

## Local vendor dependencies

- Bootstrap 5.3.8
- Bootstrap 5.3.6 fallback
- GSAP 3.15.0
- ScrollTrigger 3.15.0
- Swiper 14.2.0

## Active visual assets

- `assets/backgrounds/bg-main-menu.png`
- `assets/brand/logo_game.png`
- `assets/brand/logo_game.webp`
- `assets/characters/hero/`
- `assets/foods/`
- `assets/journey-places/`

## Game update distribution subsystem

`/updates/` adalah subsystem distribusi game yang terisolasi dari source UI website.

- `updates/manifest.json` — active mutable pointer untuk channel stable
- `updates/manifest.schema.json` — schema_version 1
- `updates/README.md` — endpoint/release/rollback contract
- `updates/content/` — namespace package PCK versioned; binary tidak dikomit secara default
- `updates/history/` — optional release/manifest history
- `tests/test_updates.py` — update-specific contract tests
- `qa/update-system-verification.txt` — local verification record

Cache contract:

- manifest: `no-store, max-age=0`
- schema: `public, max-age=3600`
- content package: `public, max-age=31536000, immutable`

Legacy `assets/asset-manifest.json` tetap tidak dikembalikan pada current source. Manifest game tidak ditempatkan di `/assets/`.

## Repository boundary

Tidak termasuk dalam active website repository:

- old environment and foreground composition layers
- raw production/game asset bank
- non-Hero character duplicates and alternates
- obsolete social image
- historical QA screenshots/reports
- legacy asset manifest/pipeline
- root PWA/favicon files yang tidak lagi digunakan
- legacy `assets/site.css`

`qa/` yang hadir setelah fase update hanya berisi verification artifact baru untuk subsystem `/updates/`, bukan historical screenshot bank lama.

Regression verification terdiri dari `tests/test_site.py`, `tests/test_updates.py`, combined unittest discovery, dan manual browser verification bila source UI berubah. Fase `/updates/` ini sendiri tidak mengubah source visual publik.
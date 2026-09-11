# Active Source Baseline

Dokumen ini memetakan source website yang dipertahankan setelah repository cleanup.

## Cleanup parent baseline

`62c6aee6cecdfff7519a3b66dfcb7f4f636c8047`

Commit tersebut adalah parent yang harus digunakan untuk menjalankan cleanup deterministik ini.

## Public pages

- `index.html`
- `tentang/index.html`
- `status/index.html`
- `privasi/index.html`
- `404.html`
- `privacy.html` compatibility redirect
- `status.html` compatibility redirect

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

## Repository cleanup boundary

Removed from the active website repository:

- old environment and foreground composition layers
- raw production/game asset bank
- non-Hero character duplicates and alternates
- obsolete social image not referenced by public pages
- historical QA screenshots/reports
- old asset manifest and `scripts/prepare-assets.ps1`
- root PWA/favicon files no longer linked by the public pages
- legacy `assets/site.css`

Regression verification is provided by `tests/test_site.py` plus manual browser testing.

# Sahabat Pangan Lokal Website

Website publik Sahabat Pangan Lokal menggunakan struktur static HTML dengan asset lokal yang dipertahankan hanya untuk kebutuhan runtime aktif.

## Halaman publik

- `/` — homepage dengan lima section utama: Hero, Petualangan, Pangan, Unduh, Footer
- `/tentang/`
- `/status/` — Kabar
- `/privasi/`
- `/privacy.html` dan `/status.html` — compatibility redirects
- `404.html` — halaman tidak ditemukan

## Frontend stack

Seluruh dependency frontend disimpan lokal di `assets/vendor/`:

- Bootstrap 5.3.8
- GSAP 3.15.0
- ScrollTrigger 3.15.0
- Swiper 14.2.0

Source aplikasi:

- `assets/css/site.css`
- `assets/js/site-config.js`
- `assets/js/site-components.js`
- `assets/js/site.js`

Navbar dan footer dibangun sebagai light-DOM shared components agar seluruh halaman publik memakai struktur yang sama tanpa build tool.

## Asset aktif

- `assets/backgrounds/` — background utama
- `assets/brand/` — logo dan favicon aktif
- `assets/characters/hero/` — empat karakter Hero
- `assets/foods/` — 14 pangan
- `assets/journey-places/` — lima tempat Petualangan

Bank asset game mentah, layer visual lama, historical QA screenshots, asset manifest lama, serta pipeline persiapan asset lama tidak lagi menjadi bagian repository website aktif.

## Verifikasi

Jalankan:

```text
py -3 -B tests/test_site.py
```

Sebelum commit perubahan runtime, lakukan juga manual browser verification pada desktop, tablet, dan mobile serta pastikan console browser tidak menghasilkan warning/error dari source website.

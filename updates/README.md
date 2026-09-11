# Game Update Distribution

Direktori `/updates/` adalah subsystem distribusi update game Sahabat Pangan Lokal. Subsystem ini terpisah dari UI website publik dan tidak boleh digunakan untuk asset runtime website.

## Endpoint contract

- Manifest aktif: `https://sahabatpanganlokal.id/updates/manifest.json`
- Schema: `https://sahabatpanganlokal.id/updates/manifest.schema.json`
- Package content: `https://sahabatpanganlokal.id/updates/content/<content_version>/spl-content-<content_version>.pck`
- Channel endpoint utama: `stable`
- `schema_version`: `1`

Bootstrap awal belum menunjuk PCK aktual. Karena itu `content.available=false`, `url=""`, `size=0`, dan `sha256=""`.

## Version contract

- `app.version`: semantic version `X.Y.Z`
- `app.version_code`: integer monoton naik
- `app.min_supported_version_code`: minimum client yang boleh melanjutkan
- `content.version`: `YYYY.MM.DD.N`
- `content.required_app_version_code`: minimum build aplikasi untuk content package aktif
- `save.schema_version`: versi format data save game

`app.force_update` dan `content.required` adalah gate yang berbeda. Jangan mengaktifkan hard gate aplikasi tanpa alasan kompatibilitas atau keamanan yang jelas.

## Release workflow

1. Export PCK dari repository game, bukan dari repository website.
2. Tentukan `content.version` baru.
3. Gunakan nama `spl-content-<content_version>.pck`.
4. Hitung ukuran byte dan SHA-256.
5. Upload package terlebih dahulu ke `/updates/content/<content_version>/`.
6. Verifikasi package server dapat diakses, ukuran benar, dan SHA-256 sama.
7. Simpan snapshot manifest lama ke `history/` bila workflow history digunakan.
8. Update `manifest.json` setelah package siap.
9. Publish manifest TERAKHIR.
10. Verifikasi header, JSON, ukuran, dan SHA-256 dari endpoint produksi.

Package yang sudah dirilis immutable: jangan menimpa path/version lama dan jangan memakai nama generik `latest.pck`.

## Rollback workflow

Rollback dilakukan dengan mengembalikan `manifest.json` agar menunjuk package versi sebelumnya yang masih tersedia. Jangan menimpa atau menghapus package lama ketika melakukan rollback. Pertahankan minimal package aktif dan satu versi sebelumnya di web root.

## Security and operations

- Semua URL update produksi wajib HTTPS.
- Manifest/PCK tidak boleh mengandung secret, token, private key, atau credential.
- SHA-256 wajib ketika `content.available=true`.
- Repository Git bukan storage utama binary PCK besar secara default.
- Tidak diperlukan backend/database pada kontrak ini.
- App update Google Play tetap jalur terpisah. Subsystem ini tidak mengimplementasikan self-install APK.
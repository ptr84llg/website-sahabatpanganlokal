# Content Package Storage Policy

Repository hanya menyimpan kontrak dan dokumentasi. Binary `.pck` aktual tidak dikomit ke Git secara default.

Path produksi:

`/updates/content/<content_version>/spl-content-<content_version>.pck`

Aturan:

- setiap rilis memakai directory/version baru;
- package yang sudah dirilis tidak boleh ditimpa;
- nama file wajib memuat `content_version`;
- upload package sebelum mengubah `manifest.json`;
- verifikasi size dan SHA-256 sebelum manifest dipublish;
- pertahankan minimal versi aktif dan satu versi sebelumnya untuk rollback.
# Update Manifest History

Direktori ini disiapkan untuk snapshot manifest atau release record yang diperlukan untuk audit dan rollback.

Snapshot history bukan endpoint aktif client. Client selalu membaca `/updates/manifest.json`.

Jika snapshot digunakan, beri nama yang mengandung content version atau timestamp rilis dan jangan menyimpan secret.
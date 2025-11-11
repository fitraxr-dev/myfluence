# Analisis Sentimen Komentar TikTok di Lokal

### 🧠 Cara Menjalankan di Lokal

1. **Pastikan Python 3.10+ terpasang.**
2. Jalankan di terminal:

```bash
pip install TikTokApi playwright transformers torch
python -m playwright install --with-deps chromium
```

3. **Ambil `ms_token`:**

   * Buka TikTok di Chrome biasa (bukan headless).
   * Tekan `F12` → tab *Application* → *Cookies* → cari `msToken`.
   * Salin nilainya dan tempel ke variabel `ms_token` di atas.

4. Jalankan:

   ```bash
   python user_sentiment.py
   ```

5. Browser akan terbuka, TikTokApi login otomatis, dan komentar video dianalisis.
   Hasil akan muncul di terminal dan tersimpan ke `sentiment_result.json`.
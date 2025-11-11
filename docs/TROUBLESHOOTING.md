# Troubleshooting Guide - TikTok Scraping Errors

## Error: Page.goto: Timeout 30000ms exceeded

### 🔍 Penyebab:

1. **Koneksi Internet Lambat** - Halaman TikTok tidak load dalam 30 detik
2. **TikTok Detection** - TikTok mendeteksi bot dan memblokir
3. **Firewall/Antivirus** - Koneksi diblokir
4. **Rate Limiting** - Terlalu banyak request dalam waktu singkat
5. **MS_TOKEN Invalid** - Token sudah expired

### ✅ Solusi yang Telah Diterapkan:

#### 1. Error Handling di `app.py`

- ✓ Try-catch untuk setiap user
- ✓ Skip user yang error dan lanjut ke berikutnya
- ✓ Delay 5 detik antar request untuk menghindari rate limit

#### 2. Optimasi di `influencer_data.py`

- ✓ Headless browser mode (lebih cepat)
- ✓ Error handling dengan detail error
- ✓ Return data dengan flag error

### 🛠️ Solusi Tambahan:

#### A. Cek Koneksi Internet

```bash
# Test koneksi ke TikTok
ping www.tiktok.com
```

#### B. Update MS_TOKEN

MS_TOKEN mungkin sudah expired. Dapatkan token baru:

1. Buka https://www.tiktok.com di browser
2. Login ke akun TikTok
3. Buka DevTools (F12) > Application > Cookies
4. Copy nilai `ms_token`
5. Update di file `src/.env`:

```env
MS_TOKEN=token_baru_anda
```

#### C. Gunakan Proxy (Opsional)

Jika TikTok memblokir IP Anda, gunakan proxy:

```python
# Di influencer_data.py, tambahkan proxy:
await api.create_sessions(
    ms_tokens=[ms_token],
    num_sessions=1,
    sleep_after=3,
    browser=browser,
    headless=True,
    proxy="http://proxy-server:port"  # ← Tambahkan ini
)
```

#### D. Tingkatkan Timeout

Edit timeout di environment:

```env
# Tambahkan di .env
PLAYWRIGHT_TIMEOUT=60000  # 60 detik
```

#### E. Jalankan dengan Delay Lebih Panjang

Edit `app.py` untuk delay lebih lama:

```python
delay = 10  # 10 detik antar request
```

### 📊 Monitoring:

#### Jalankan dengan Output Detail:

```bash
python src/app.py
```

Output akan menampilkan:

```
[1/6] Processing: @dillaprb
  ✓ Info saved to: dillaprb.info.json
  ✓ Stats saved to: dillaprb.stats.json
  ⏳ Waiting 5s before next request...

[2/6] Processing: @kevindikmanto
  ❌ Error processing @kevindikmanto: TimeoutError
     Page.goto: Timeout 30000ms exceeded
  ⚠️  Skipping to next user...
```

### 🔄 Retry Failed Users:

Jika ada user yang gagal, buat list khusus:

```python
# app.py
failed_users = ["kevindikmanto", "maharajasp8"]

for influencer in failed_users:
    print(f"Retrying: @{influencer}")
    user_info = asyncio.run(get_user_info(influencer))
    save_user_data(user_info, influencer)
```

### ⚡ Tips Optimasi:

1. **Jalankan di jam off-peak** (malam hari)
2. **Gunakan WiFi stabil** dengan koneksi cepat
3. **Matikan VPN** jika aktif (bisa memperlambat)
4. **Tutup aplikasi lain** yang menggunakan bandwidth
5. **Check MS_TOKEN** secara berkala (expired ~24 jam)

### 🚨 Jika Masih Error:

1. Coba mode non-headless untuk debug:

   ```python
   headless=False  # Lihat browser terbuka
   ```

2. Tambahkan logging detail:

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. Coba browser lain:
   ```env
   TIKTOK_BROWSER=firefox  # atau webkit
   ```

### ✅ Expected Behavior:

Normal output tanpa error:

```
Starting to process 6 influencers...
============================================================

[1/6] Processing: @dillaprb
  ✓ Info saved to: dillaprb.info.json
  ✓ Stats saved to: dillaprb.stats.json
  ⏳ Waiting 5s before next request...

[2/6] Processing: @kevindikmanto
  ✓ Info saved to: kevindikmanto.info.json
  ✓ Stats saved to: kevindikmanto.stats.json
  ⏳ Waiting 5s before next request...

...

============================================================
✓ Processing completed!
```

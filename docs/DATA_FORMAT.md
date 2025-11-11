# Data Storage Format

## Struktur Penyimpanan Data

Data user TikTok disimpan dalam 2 file terpisah untuk setiap user:

### 1. Info File (`username.info.json`)

**Lokasi:** `src/data/info/`

**Format:**

```json
{
  "id": "7123456789",
  "username": "dillaprb",
  "nickname": "Dilla",
  "signature": "Content Creator ✨"
}
```

**Fields:**

- `id` (string): User ID TikTok
- `username` (string): Username unik (uniqueId)
- `nickname` (string): Display name
- `signature` (string): Bio/signature user

---

### 2. Stats File (`username.stats.json`)

**Lokasi:** `src/data/stats/`

**Format:**

```json
{
  "followers_count": 150000,
  "total_likes": 2500000,
  "timestamp": "2025-11-11T10:30:45.123456"
}
```

**Fields:**

- `followers_count` (integer): Jumlah followers
- `total_likes` (integer): Total likes (heartCount)
- `timestamp` (string): Waktu pengambilan data (ISO format)

---

## Struktur Folder

```
src/
├── data/
│   ├── info/
│   │   ├── dillaprb.info.json
│   │   ├── kevindikmanto.info.json
│   │   └── tasyafarasya.info.json
│   └── stats/
│       ├── dillaprb.stats.json
│       ├── kevindikmanto.stats.json
│       └── tasyafarasya.stats.json
```

---

## Penggunaan

### Import Functions

```python
from utils.save_data import (
    save_user_data,
    load_user_info,
    load_user_stats,
    load_user_data
)
```

### Save Data

```python
user_info = {
    'id': '7123456789',
    'username': 'dillaprb',
    'nickname': 'Dilla',
    'signature': 'Content Creator ✨',
    'followers_count': 150000,
    'total_likes': 2500000,
    'timestamp': '2025-11-11T10:30:45.123456'
}

# Simpan ke 2 file terpisah
saved_files = save_user_data(user_info, 'dillaprb')
print(saved_files['info_file'])   # Path ke info file
print(saved_files['stats_file'])  # Path ke stats file
```

### Load Data

#### Load Info Only

```python
info = load_user_info('dillaprb')
# Returns: {'id': '...', 'username': '...', 'nickname': '...', 'signature': '...'}
```

#### Load Stats Only

```python
stats = load_user_stats('dillaprb')
# Returns: {'followers_count': 150000, 'total_likes': 2500000, 'timestamp': '...'}
```

#### Load Combined Data

```python
data = load_user_data('dillaprb')
# Returns: gabungan info + stats
# {'id': '...', 'username': '...', ..., 'followers_count': 150000, ...}
```

---

## Keuntungan Format Terpisah

### ✓ Separation of Concerns

- **Info**: Data yang jarang berubah (ID, username, nickname, bio)
- **Stats**: Data yang sering berubah (followers, likes)

### ✓ Historical Tracking

Stats bisa di-append dengan timestamp untuk tracking perubahan:

```python
# Bisa dikembangkan menjadi:
# dillaprb.stats.json menjadi array:
[
  {"followers_count": 150000, "total_likes": 2500000, "timestamp": "2025-11-11T10:00:00"},
  {"followers_count": 151000, "total_likes": 2520000, "timestamp": "2025-11-11T11:00:00"}
]
```

### ✓ Efficient Updates

- Update stats tanpa perlu load/save data info
- Hemat storage jika hanya stats yang berubah

### ✓ Query Performance

- Load hanya data yang dibutuhkan
- Lebih cepat untuk analisis yang hanya butuh stats

---

## Testing

Test fungsi save dan load:

```bash
python src/test_save_data.py
```

Output:

```
Testing save_user_data...
------------------------------------------------------------

1. Saving user data...
   ✓ Info saved to: d:\...\src\data\info\testuser.info.json
   ✓ Stats saved to: d:\...\src\data\stats\testuser.stats.json

2. Loading info data...
   Info data: {'id': '7123456789', 'username': 'testuser', ...}

3. Loading stats data...
   Stats data: {'followers_count': 150000, 'total_likes': 2500000, ...}

4. Loading combined data...
   Combined data: {'id': '7123456789', 'username': 'testuser', ..., 'followers_count': 150000, ...}
```

---

## Migration dari Format Lama

Jika Anda punya data lama dalam format gabungan, bisa di-convert:

```python
from utils.save_data import save_user_info, save_user_data, load_user_info

# Load data lama
old_data = load_user_info('username')

# Save dengan format baru
save_user_data(old_data, 'username')
```

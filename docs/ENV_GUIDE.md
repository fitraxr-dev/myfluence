# Environment Variables Guide

## Setup `.env` File

### 1. Copy Template
Copy file `.env.example` menjadi `.env`:
```bash
cp src/.env.example src/.env
```

### 2. Edit Configuration
Edit file `src/.env` dan isi dengan nilai yang sesuai:

```env
# -- Database Environment --
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=myfluence

# -- Scraping Environment --
MS_TOKEN=your_actual_ms_token_here
TIKTOK_BROWSER=chromium
```

## Environment Variables

### Database Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MONGODB_HOST` | MongoDB host address | `localhost` | `localhost` atau `192.168.1.100` |
| `MONGODB_PORT` | MongoDB port | `27017` | `27017` |
| `MONGODB_DATABASE` | Database name | `myfluence` | `myfluence` |

### TikTok Scraping Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MS_TOKEN` | TikTok ms_token dari cookies | - | `H7_OZIkYEp...` |
| `TIKTOK_BROWSER` | Browser untuk scraping | `chromium` | `chromium`, `firefox`, `webkit` |

## Cara Mendapatkan MS_TOKEN

### Method 1: Dari Browser DevTools
1. Buka https://www.tiktok.com di browser
2. Login ke akun TikTok
3. Buka DevTools (F12)
4. Pergi ke tab **Application** > **Cookies**
5. Cari cookie dengan nama `ms_token`
6. Copy nilai cookie tersebut
7. Paste ke file `.env`

### Method 2: Dari Network Tab
1. Buka https://www.tiktok.com
2. Login ke akun TikTok
3. Buka DevTools (F12) > **Network** tab
4. Refresh halaman
5. Cari request yang memiliki cookie `ms_token`
6. Copy nilai `ms_token` dari Request Headers
7. Paste ke file `.env`

## File Structure

```
src/
├── .env                  # ← File konfigurasi (JANGAN commit ke git!)
├── .env.example          # ← Template untuk .env
├── db/
│   └── connections/
│       └── connection.py  # Baca MONGODB_* dari .env
├── services/
│   └── get_user_info.py  # Baca MS_TOKEN dari .env
└── utils/
    └── get_environment.py # Helper untuk baca .env
```

## Security Notes

⚠️ **PENTING**: 
- **JANGAN** commit file `.env` ke Git/GitHub
- File `.env` sudah ditambahkan ke `.gitignore`
- Hanya commit file `.env.example` sebagai template
- `MS_TOKEN` adalah data sensitif, jaga kerahasiaannya

## Usage dalam Code

### Import dan Load .env
```python
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Ambil value
ms_token = os.getenv('MS_TOKEN')
mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
```

### Menggunakan Helper Functions
```python
from utils.get_environment import get_ms_token, get_browser, get_mongodb_config

# Get MS Token
token = get_ms_token()

# Get Browser
browser = get_browser()

# Get MongoDB Config
db_config = get_mongodb_config()
print(db_config['host'])     # localhost
print(db_config['port'])     # 27017
print(db_config['database']) # myfluence
```

## Testing

Test apakah `.env` sudah terbaca dengan benar:

```python
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

print("MS_TOKEN:", os.getenv('MS_TOKEN')[:20] + "..." if os.getenv('MS_TOKEN') else "Not set")
print("MONGODB_HOST:", os.getenv('MONGODB_HOST'))
print("MONGODB_PORT:", os.getenv('MONGODB_PORT'))
print("MONGODB_DATABASE:", os.getenv('MONGODB_DATABASE'))
print("TIKTOK_BROWSER:", os.getenv('TIKTOK_BROWSER'))
```

## Troubleshooting

### .env tidak terbaca
- Pastikan path ke `.env` benar
- Pastikan file bernama `.env` (bukan `.env.txt`)
- Pastikan tidak ada spasi di sekitar `=` dalam `.env`
- Pastikan `python-dotenv` sudah terinstall: `pip install python-dotenv`

### MS_TOKEN expired
- Token TikTok bisa expired setelah beberapa waktu
- Dapatkan token baru dari browser
- Update nilai `MS_TOKEN` di file `.env`

# MongoDB Setup Guide

## 1. Install MongoDB Driver

Jalankan perintah berikut untuk install pymongo:

```bash
pip install pymongo
```

Atau install dari requirements file:

```bash
pip install -r requirements_mongodb.txt
```

## 2. Pastikan MongoDB Server Berjalan

Pastikan MongoDB server sudah terinstall dan berjalan di:
- Host: `localhost`
- Port: `27017`
- Database: `myfluence`

### Cara menjalankan MongoDB:
```bash
# Windows
mongod

# Linux/Mac
sudo systemctl start mongod
```

## 3. Struktur Folder

```
src/
├── db/
│   ├── __init__.py
│   └── connection.py      # Logika koneksi MongoDB
├── services/
│   └── get_user_info.py
└── test_mongodb.py        # Test koneksi
```

## 4. Cara Menggunakan

### Import koneksi:
```python
from db.connection import get_db, get_collection, close_connection
```

### Mendapatkan database:
```python
db = get_db()
print(db.name)  # Output: myfluence
```

### Mendapatkan collection:
```python
users_collection = get_collection('users')
```

### Insert data:
```python
user_data = {
    'id': '123456',
    'username': 'dillaprb',
    'nickname': 'Dilla',
    'followers_count': 150000
}
result = users_collection.insert_one(user_data)
print(result.inserted_id)
```

### Query data:
```python
# Find all
users = users_collection.find()
for user in users:
    print(user)

# Find one
user = users_collection.find_one({'username': 'dillaprb'})
print(user)
```

### Update data:
```python
users_collection.update_one(
    {'username': 'dillaprb'},
    {'$set': {'followers_count': 160000}}
)
```

### Delete data:
```python
users_collection.delete_one({'username': 'dillaprb'})
```

### Tutup koneksi:
```python
close_connection()
```

## 5. Test Koneksi

Jalankan test untuk memastikan koneksi berhasil:

```bash
python src/test_mongodb.py
```

Atau test langsung dari connection.py:

```bash
python src/db/connection.py
```

## 6. Fitur Connection Class

- ✓ **Singleton Pattern** - Hanya satu instance koneksi
- ✓ **Auto Reconnect** - Otomatis reconnect jika koneksi terputus
- ✓ **Error Handling** - Menangani error koneksi dengan baik
- ✓ **Helper Functions** - Fungsi helper untuk kemudahan penggunaan
- ✓ **Connection Pooling** - Menggunakan connection pooling default PyMongo

## 7. Configuration

Koneksi default:
- Host: `localhost`
- Port: `27017`
- Database: `myfluence`

Untuk mengubah konfigurasi, edit di `connection.py`:
```python
mongo = MongoDBConnection()
mongo.connect(host='your_host', port=27017, db_name='your_db')
```

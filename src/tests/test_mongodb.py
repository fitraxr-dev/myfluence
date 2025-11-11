"""
Contoh penggunaan MongoDB connection
"""
import sys
from pathlib import Path

# Tambahkan src ke Python path
sys.path.append(str(Path(__file__).parent))

from db.connections.connection import get_db, get_collection, close_connection

# Contoh 1: Mendapatkan database
db = get_db()
print(f"Database name: {db.name}")
print(f"Collections: {db.list_collection_names()}")

# Contoh 2: Mendapatkan collection
users_collection = get_collection('users')
print(f"\nCollection name: {users_collection.name}")

# Contoh 3: Insert data
sample_user = {
    'username': 'test_user',
    'nickname': 'Test User',
    'followers_count': 1000
}

# result = users_collection.insert_one(sample_user)
# print(f"Inserted document ID: {result.inserted_id}")

# Contoh 4: Query data
# users = users_collection.find()
# for user in users:
#     print(user)

# Tutup koneksi saat selesai
close_connection()

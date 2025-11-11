from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Load environment variables dari file .env
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class MongoDBConnection:
    """
    Singleton class untuk koneksi MongoDB
    """
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self, host=None, port=None, db_name=None):
        """
        Membuat koneksi ke MongoDB
        
        Args:
            host (str): Host MongoDB (default: dari .env atau localhost)
            port (int): Port MongoDB (default: dari .env atau 27017)
            db_name (str): Nama database (default: dari .env atau myfluence)
        
        Returns:
            Database: MongoDB database instance
        """
        # Ambil konfigurasi dari .env jika tidak diberikan
        if host is None:
            host = os.getenv('MONGODB_HOST', 'localhost')
        if port is None:
            port = int(os.getenv('MONGODB_PORT', 27017))
        if db_name is None:
            db_name = os.getenv('MONGODB_DATABASE', 'myfluence')
        
        try:
            # Buat koneksi ke MongoDB
            connection_string = f"mongodb://{host}:{port}/"
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000  # Timeout 5 detik
            )
            
            # Test koneksi
            self._client.admin.command('ping')
            
            # Pilih database
            self._db = self._client[db_name]
            
            print(f"✓ Berhasil terhubung ke MongoDB: {connection_string}{db_name}")
            return self._db
            
        except ConnectionFailure:
            print("❌ Gagal terhubung ke MongoDB: Connection refused")
            print("   Pastikan MongoDB server sudah berjalan di localhost:27017")
            sys.exit(1)
            
        except ServerSelectionTimeoutError:
            print("❌ Gagal terhubung ke MongoDB: Server selection timeout")
            print("   Pastikan MongoDB server sudah berjalan di localhost:27017")
            sys.exit(1)
            
        except Exception as e:
            print(f"❌ Error koneksi MongoDB: {type(e).__name__} - {e}")
            sys.exit(1)
    
    def get_database(self):
        """
        Mendapatkan database instance
        
        Returns:
            Database: MongoDB database instance
        """
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, collection_name):
        """
        Mendapatkan collection dari database
        
        Args:
            collection_name (str): Nama collection
        
        Returns:
            Collection: MongoDB collection instance
        """
        db = self.get_database()
        return db[collection_name]
    
    def close(self):
        """
        Menutup koneksi MongoDB
        """
        if self._client:
            self._client.close()
            print("✓ Koneksi MongoDB ditutup")
            self._client = None
            self._db = None

# Fungsi helper untuk mendapatkan koneksi database
def get_db():
    """
    Helper function untuk mendapatkan database instance
    
    Returns:
        Database: MongoDB database instance
    """
    mongo = MongoDBConnection()
    return mongo.get_database()

def get_collection(collection_name):
    """
    Helper function untuk mendapatkan collection
    
    Args:
        collection_name (str): Nama collection
    
    Returns:
        Collection: MongoDB collection instance
    """
    mongo = MongoDBConnection()
    return mongo.get_collection(collection_name)

def close_connection():
    """
    Helper function untuk menutup koneksi
    """
    mongo = MongoDBConnection()
    mongo.close()

# Test koneksi saat modul di-import (opsional)
if __name__ == "__main__":
    # Test koneksi
    print("Testing MongoDB connection...")
    db = get_db()
    print(f"Database: {db.name}")
    print(f"Collections: {db.list_collection_names()}")
    close_connection()

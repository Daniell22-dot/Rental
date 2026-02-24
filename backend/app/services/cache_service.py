# backend/app/services/cache_service.py
from datetime import datetime, timedelta
from typing import Optional, Any
import json
from sqlalchemy.orm import Session
from app.models.cache import CacheItem

class CacheService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str) -> Optional[Any]:
        # Delete expired items first
        self.db.query(CacheItem).filter(CacheItem.expires_at < datetime.utcnow()).delete()
        self.db.commit()

        item = self.db.query(CacheItem).filter(CacheItem.key == key).first()
        if item:
            return json.loads(item.value)
        return None

    def set(self, key: str, value: Any, expire_minutes: int = 60):
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
        value_str = json.dumps(value)
        
        item = self.db.query(CacheItem).filter(CacheItem.key == key).first()
        if item:
            item.value = value_str
            item.expires_at = expires_at
        else:
            item = CacheItem(key=key, value=value_str, expires_at=expires_at)
            self.db.add(item)
        
        self.db.commit()

    def delete(self, key: str):
        self.db.query(CacheItem).filter(CacheItem.key == key).delete()
        self.db.commit()

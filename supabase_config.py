"""Supabase Configuration & Memory Management for Exodia"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase...")
    os.system("pip install supabase")
    from supabase import create_client, Client

class SupabaseMemoryManager:
    """Handles user memory and conversation history in Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.initialize_tables()
    
    def initialize_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Check if tables exist, if not create them
            self.supabase.table("user_memory").select("*", count="exact").limit(1).execute()
            self.supabase.table("conversations").select("*", count="exact").limit(1).execute()
        except:
            print("Tables will be auto-created by Supabase")
    
    def save_user_memory(self, user_id: str, memory_data: Dict[str, Any]):
        """Store user memories and preferences"""
        try:
            data = {
                "user_id": user_id,
                "memory_data": json.dumps(memory_data),
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.supabase.table("user_memory").upsert(data).execute()
            return response
        except Exception as e:
            print(f"Error saving memory: {e}")
            return None
    
    def get_user_memory(self, user_id: str) -> Dict[str, Any]:
        """Retrieve stored user memories"""
        try:
            response = self.supabase.table("user_memory").select("*").eq("user_id", user_id).execute()
            if response.data:
                return json.loads(response.data[0]["memory_data"])
            return {}
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return {}
    
    def save_conversation(self, user_id: str, message: str, response: str, ai_model: str = "DeepSeek"):
        """Store conversation history"""
        try:
            data = {
                "user_id": user_id,
                "user_message": message,
                "ai_response": response,
                "ai_model": ai_model,
                "timestamp": datetime.utcnow().isoformat()
            }
            response = self.supabase.table("conversations").insert(data).execute()
            return response
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return None
    
    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve recent conversation history"""
        try:
            response = self.supabase.table("conversations").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

memory_manager = None
if SUPABASE_URL and SUPABASE_KEY:
    memory_manager = SupabaseMemoryManager(SUPABASE_URL, SUPABASE_KEY)
else:
    print("Warning: Supabase credentials not configured. Memory will not be persisted.")

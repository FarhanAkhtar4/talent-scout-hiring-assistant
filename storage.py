import json
import os
from datetime import datetime
from typing import Dict, Any

class Storage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_candidate(self, candidate_id: str, data: Dict[str, Any]):
        """Save candidate data to JSON file"""
        filepath = os.path.join(self.data_dir, f"{candidate_id}.json")
        data["timestamp"] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """Load candidate data from JSON file"""
        filepath = os.path.join(self.data_dir, f"{candidate_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def candidate_exists(self, email: str) -> bool:
        """Check if a candidate with the given email already exists"""
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('email') == email:
                        return True
        return False
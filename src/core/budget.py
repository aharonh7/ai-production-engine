"""
Budget Manager - ניהול תקציב וניטור עלויות
"""
import json
from pathlib import Path
from datetime import datetime

class BudgetManager:
    def __init__(self, budget_limit=2.0, data_file=None):
        self.budget_limit = budget_limit
        self.data_file = data_file or Path(__file__).parent.parent.parent / "data" / "budget_data.json"
        self.total_used = 0.05
        self.transactions = []
        self._load_data()
    
    def _load_data(self):
        """טוען נתוני תקציב מקובץ"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.total_used = data.get('total_used', 0.0)
                    self.transactions = data.get('transactions', [])
            except:
                pass
    
    def _save_data(self):
        """שומר נתוני תקציב לקובץ"""
        try:
            self.data_file.parent.mkdir(exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_used': self.total_used,
                    'transactions': self.transactions,
                    'limit': self.budget_limit
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ שגיאה בשמירת תקציב: {e}")
    
    def can_afford(self, estimated_cost):
        """בודק אם יש מספיק תקציב"""
        return (self.total_used + estimated_cost) <= self.budget_limit
    
    def record_cost(self, cost, description=""):
        """מתעד הוצאה"""
        self.total_used += cost
        self.transactions.append({
            'timestamp': datetime.now().isoformat(),
            'cost': cost,
            'description': description,
            'total_used': self.total_used
        })
        self._save_data()
        print(f"💰 הוצאה: ${cost:.4f} | סה\"כ: ${self.total_used:.4f} | נשאר: ${self.budget_limit - self.total_used:.4f}")
    
    def get_status(self):
        """מחזיר את מצב התקציב"""
        return {
            'used': round(self.total_used, 4),
            'limit': self.budget_limit,
            'remaining': round(self.budget_limit - self.total_used, 4),
            'transactions_count': len(self.transactions)
        }
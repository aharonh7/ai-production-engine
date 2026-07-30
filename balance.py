import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("❌ לא נמצא מפתח API")
    exit(1)

try:
    response = requests.get(
        "https://api.deepseek.com/user/balance",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get("is_available") and data.get("balance_infos"):
            info = data["balance_infos"][0]
            print("=" * 40)
            print("💰 DeepSeek Balance")
            print("=" * 40)
            print(f"סה\"כ: {info.get('total_balance', '0.00')} {info.get('currency', 'USD')}")
            print(f"הופקד: {info.get('topped_up_balance', '0.00')} {info.get('currency', 'USD')}")
            print(f"מתנה: {info.get('granted_balance', '0.00')} {info.get('currency', 'USD')}")
            print(f"סטטוס: {'✅ זמין' if data.get('is_available') else '❌ לא זמין'}")
            print("=" * 40)
        else:
            print("❌ לא נמצא מידע על יתרה")
    else:
        print(f"❌ שגיאה: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ שגיאה: {e}")

input("הקש Enter לסיום...")
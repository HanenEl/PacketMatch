# ══════════════════════════════════════════════════════════════════════════════
# Scrapes all WE (Telecom Egypt) store locations across Egyptian governorates
# by querying the TE REST API area by area, then exports the results to Excel.
# ══════════════════════════════════════════════════════════════════════════════

import requests
import pandas as pd
import time

BASE = "https://www.te.eg/WebServices/REST/Store"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.te.eg/",
}

def get_data(url):
    response = requests.get(url, headers=headers, timeout=10)
    return response.json()

cities = {
    "Aswan": 5345, "Assiut": 5344, "Alexandria": 5343,
    "Ismailia": 5354, "Luxor": 5356, "Red Sea": 5364,
    "Beheira": 5350, "Giza": 5353, "Dakahlia": 5348,
    "Suez": 5366, "Sharqia": 5342, "Gharbia": 5352,
    "Fayoum": 5351, "Cairo": 5347, "Qalyubia": 5341,
    "Menofia": 5358, "Minya": 5359, "New Valley": 5360,
    "Beni Suef": 5346, "Port Said": 5362, "South Sinai": 5365,
    "Damietta": 5349, "Sohag": 5367, "North Sinai": 5361,
    "Qena": 5363, "Kafr El-Sheikh": 5355, "Matrouh": 5357,
}

all_stores = []

for city_name, city_id in cities.items():
    areas = get_data(f"{BASE}/getAreaByCityId/{city_id}")
    
    for area in areas:
        area_name = area["areaEnglish"]  
        area_id   = area["areaID"]
        
        stores = get_data(f"{BASE}/getStoreByAreaid/{area_id}")
        
        for store in stores:
            all_stores.append({
                "Governorate":    city_name,
                "City ID":        city_id,
                "Area":           area_name,
                "Exchange Name":  store["englishName"],       
                "Address":        store["englishAddress"],   
                "Latitude":       store["latitude"],
                "Longitude":      store["longitude"],
                "Working Hours":  store["englishWorkingDays_Hours"], 
            })
        
        time.sleep(1)
    print(f"{city_name} - {len(areas)} areas")

df = pd.DataFrame(all_stores)
df.to_excel("WE_English.xlsx", index=False)
print(f"\n Done! Total stores: {len(all_stores)}")
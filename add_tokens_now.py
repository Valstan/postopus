#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое добавление VK токенов в Postopus
"""
import requests
import json

# URL вашего приложения
BASE_URL = "https://postopus-web-only.onrender.com"

def add_token(region, token, group_id, description):
    """Добавляет токен через API"""
    try:
        url = f"{BASE_URL}/api/vk/api/vk/tokens"
        data = {
            "region": region,
            "token": token,
            "group_id": group_id,
            "description": description
        }
        
        print(f"📝 Добавляем токен для региона: {region}")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"✅ Токен для региона {region} добавлен успешно")
            return True
        else:
            print(f"❌ Ошибка при добавлении токена {region}: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при добавлении токена {region}: {e}")
        return False

def test_connections():
    """Тестирует VK подключения"""
    try:
        url = f"{BASE_URL}/api/vk/api/vk/test-connections"
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ VK подключения работают")
            return True
        else:
            print(f"❌ Ошибка при тестировании подключений: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании подключений: {e}")
        return False

def main():
    print("🚀 Добавление VK токенов в Postopus...")
    print("=" * 60)
    
    # VK токены
    tokens = [
        {
            "region": "olga",
            "token": "vk1.a.YB3vu9mP072pkadsec7VVBDaIjke_VByDUks3QnLaWsbbu28M5SkhDvik6I_97VsdQs9-gSvPQ1U6FBr4a-a866Gu7xcXcPRLWU2UKmThfqAwJXoSS4cfDgap-frRec_Yqg3jZLyl29a-xNcQSsZN74ydv0W7swkFNrr8UHIlkoNQZjiDNJvqB2SxuIuBu3uGU2AiGqdasw9SBN9kDFXAA",
            "group_id": "-123456789",
            "description": "VK токен для Olga"
        },
        {
            "region": "valstan", 
            "token": "vk1.a.gczp291vx4VkA5hZRP9lwpJVtSCTx-c79D7zGM3pmAub0YszQXL-DIK5mY0xry-XEKWbiTzSiADxNAEQRHfUzCH1XsEh-BoCStWNNOp_TBY_GOOzhkQtPfDxbbntkuVHSBy3Jeunedmp_om-28OvYgZy51IPi2jfyh5yic7-oTutbe8NMVsNdAyhfhpcAUPy8J2wiTOWrR0L0QE8KMudrQ",
            "group_id": "-123456789",
            "description": "VK токен для Valstan"
        },
        {
            "region": "vita",
            "token": "vk1.a.h8ZMyCgenUYgB6Ci8MKpi6AFVS9lXy4ndWrVPJu0BT4uncFFM3vmi8qJeUGpW-7X0DBhBWfQHs9qrIzo5CS2LkbpOnNo563B4XtY5DT-JPLYguCRQkmrEdcx7YQQQgzIALlB8bbQeyub32BJtZQvEs12xdcYXBHD85SUxJ2l6cuYjVj0gL5pqMR17xmlbxav3tx83eikViL1JH80Twipdw",
            "group_id": "-123456789",
            "description": "VK токен для Vita"
        },
        {
            "region": "dran",
            "token": "vk1.a.gpR4VWqecUt5pVpregmjWHGCo7S8M4KxLvGLIVj0GTV7W4dDeZLDNIt85RaIIr4goudrvIi__l4w0KyNy1Ve8nxbi87nff8CbLnnZzVmitqC1buw8yd-RnoimfZE27EZDMT3ml738aHPmwXnM9HjQGP0YOUFehhld31BjAiqxLZ35KxShuvSAUTRueJKF9PQpMSblL5LPNCeRry9UvyNJQ",
            "group_id": "-123456789",
            "description": "VK токен для Dran"
        }
    ]
    
    # Добавляем токены
    success_count = 0
    for token_data in tokens:
        if add_token(**token_data):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Результат: {success_count}/{len(tokens)} токенов добавлено")
    
    if success_count > 0:
        print("\n🔍 Тестируем VK подключения...")
        test_connections()
    
    print("\n🎉 Готово!")

if __name__ == "__main__":
    main()

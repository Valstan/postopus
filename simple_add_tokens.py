#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple VK token addition script
"""
import requests
import json

BASE_URL = "https://postopus-web-only.onrender.com"

def add_token(region, token, group_id, description):
    try:
        url = f"{BASE_URL}/api/vk/api/vk/tokens"
        data = {
            "region": region,
            "token": token,
            "group_id": group_id,
            "description": description
        }
        
        print(f"Adding token for region: {region}")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"SUCCESS: Token for region {region} added")
            return True
        else:
            print(f"ERROR: Failed to add token {region}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR: Exception adding token {region}: {e}")
        return False

def main():
    print("Adding VK tokens to Postopus...")
    print("=" * 50)
    
    tokens = [
        {
            "region": "olga",
            "token": "vk1.a.YB3vu9mP072pkadsec7VVBDaIjke_VByDUks3QnLaWsbbu28M5SkhDvik6I_97VsdQs9-gSvPQ1U6FBr4a-a866Gu7xcXcPRLWU2UKmThfqAwJXoSS4cfDgap-frRec_Yqg3jZLyl29a-xNcQSsZN74ydv0W7swkFNrr8UHIlkoNQZjiDNJvqB2SxuIuBu3uGU2AiGqdasw9SBN9kDFXAA",
            "group_id": "-123456789",
            "description": "VK token for Olga"
        },
        {
            "region": "valstan", 
            "token": "vk1.a.gczp291vx4VkA5hZRP9lwpJVtSCTx-c79D7zGM3pmAub0YszQXL-DIK5mY0xry-XEKWbiTzSiADxNAEQRHfUzCH1XsEh-BoCStWNNOp_TBY_GOOzhkQtPfDxbbntkuVHSBy3Jeunedmp_om-28OvYgZy51IPi2jfyh5yic7-oTutbe8NMVsNdAyhfhpcAUPy8J2wiTOWrR0L0QE8KMudrQ",
            "group_id": "-123456789",
            "description": "VK token for Valstan"
        },
        {
            "region": "vita",
            "token": "vk1.a.h8ZMyCgenUYgB6Ci8MKpi6AFVS9lXy4ndWrVPJu0BT4uncFFM3vmi8qJeUGpW-7X0DBhBWfQHs9qrIzo5CS2LkbpOnNo563B4XtY5DT-JPLYguCRQkmrEdcx7YQQQgzIALlB8bbQeyub32BJtZQvEs12xdcYXBHD85SUxJ2l6cuYjVj0gL5pqMR17xmlbxav3tx83eikViL1JH80Twipdw",
            "group_id": "-123456789",
            "description": "VK token for Vita"
        },
        {
            "region": "dran",
            "token": "vk1.a.gpR4VWqecUt5pVpregmjWHGCo7S8M4KxLvGLIVj0GTV7W4dDeZLDNIt85RaIIr4goudrvIi__l4w0KyNy1Ve8nxbi87nff8CbLnnZzVmitqC1buw8yd-RnoimfZE27EZDMT3ml738aHPmwXnM9HjQGP0YOUFehhld31BjAiqxLZ35KxShuvSAUTRueJKF9PQpMSblL5LPNCeRry9UvyNJQ",
            "group_id": "-123456789",
            "description": "VK token for Dran"
        }
    ]
    
    success_count = 0
    for token_data in tokens:
        if add_token(**token_data):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"Result: {success_count}/{len(tokens)} tokens added")
    print("Done!")

if __name__ == "__main__":
    main()

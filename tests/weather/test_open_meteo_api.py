#!/usr/bin/env python3
"""
Test script to check Open-Meteo API directly
"""

import requests

def test_api_directly():
    """Test Open-Meteo API directly to diagnose the issue"""
    print("Testing Open-Meteo API directly...")
    print("=" * 50)
    
    # Test coordinates for Shanghai
    latitude = 31.22222
    longitude = 121.45806
    
    # Test 1: Minimal current weather request
    print("\n1. Testing minimal current weather request:")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "timezone": "Asia/Shanghai"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Forecast request
    print("\n2. Testing forecast request:")
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Shanghai",
        "forecast_days": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_directly()
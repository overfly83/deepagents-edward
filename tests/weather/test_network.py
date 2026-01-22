#!/usr/bin/env python3
"""
Test basic network connectivity to external APIs.
"""
import requests
import time

def test_network_connectivity():
    """Test basic network connectivity."""
    print("Testing network connectivity...")
    
    # List of test URLs with their expected response codes
    test_urls = [
        ("https://www.google.com", 200),
        ("https://api.github.com", 200),
        ("https://geocoding-api.open-meteo.com/v1/search?name=Beijing", 200),
        ("https://api.open-meteo.com/v1/forecast?latitude=39.9042&longitude=116.4074&current=temperature_2m", 200)
    ]
    
    for url, expected_code in test_urls:
        print(f"\nTesting {url}...")
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            
            print(f"  Status code: {response.status_code}")
            print(f"  Expected: {expected_code}")
            print(f"  Response time: {end_time - start_time:.2f}s")
            
            if response.status_code == expected_code:
                print("  ✓ SUCCESS")
                # Print first 100 chars of response if successful
                if response.content:
                    try:
                        content = response.text[:100] + "..." if len(response.text) > 100 else response.text
                        print(f"  Response snippet: {content}")
                    except:
                        print("  Response: (binary data)")
            else:
                print("  ✗ FAIL - wrong status code")
                
        except requests.exceptions.Timeout:
            print(f"  ✗ FAIL - timeout after 5 seconds")
        except requests.exceptions.ConnectionError:
            print(f"  ✗ FAIL - connection error")
        except Exception as e:
            print(f"  ✗ FAIL - unexpected error: {e}")

if __name__ == "__main__":
    test_network_connectivity()
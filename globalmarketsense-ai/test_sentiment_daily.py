#!/usr/bin/env python3
"""Test sentiment daily endpoint"""
import urllib.request
import json

def test_sentiment_daily():
    print("Testing /api/sentiment/daily endpoint")
    print("=" * 60)
    
    # Test sentiment/daily endpoint
    url = 'http://localhost:8000/api/sentiment/daily?limit=30'
    req = urllib.request.Request(url, method='GET')
    
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        
        print(f"✓ Endpoint responded\n")
        print(f"Response keys: {list(result.keys())}")
        
        rows = result.get('rows', [])
        print(f"Number of rows: {len(rows)}")
        
        if rows:
            print(f"\nSample row (first):")
            for key, value in list(rows[0].items())[:5]:
                print(f"  {key}: {value}")
            
            print(f"\nSample row (last):")
            for key, value in list(rows[-1].items())[:5]:
                print(f"  {key}: {value}")
        else:
            print("\n✗ No rows returned!")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    return len(rows) > 0

if __name__ == '__main__':
    has_data = test_sentiment_daily()
    print("\n" + "=" * 60)
    if has_data:
        print("✓ Price Sentiment Trend data is AVAILABLE")
    else:
        print("✗ Price Sentiment Trend data is EMPTY")

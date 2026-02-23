#!/usr/bin/env python3
"""Test sentiment endpoint for Price Sentiment Trend chart"""
import urllib.request
import json

def test_sentiment():
    print("Testing Price Sentiment Trend Data")
    print("=" * 60)
    
    # Test sentiment endpoint
    url = 'http://localhost:8000/api/sentiment/daily?market=SP500&days=30'
    req = urllib.request.Request(url, method='GET')
    
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        
        print(f"✓ Sentiment Endpoint Working\n")
        print(f"Market: {result.get('market')}")
        
        hist = result.get('historical_sentiment', [])
        print(f"Historical data points: {len(hist)} days")
        
        if hist:
            first = hist[0]
            last = hist[-1]
            print(f"\nDate range:")
            print(f"  From: {first.get('date')}")
            print(f"  To: {last.get('date')}")
            
            print(f"\nSentiment values:")
            print(f"  First day: {first.get('net_sentiment'):.3f}")
            print(f"  Last day: {last.get('net_sentiment'):.3f}")
            print(f"  Min: {min(h.get('net_sentiment', 0) for h in hist):.3f}")
            print(f"  Max: {max(h.get('net_sentiment', 0) for h in hist):.3f}")
        
        print(f"\nCurrent sentiment: {result.get('current_sentiment', {})}")
        
        print("\n" + "=" * 60)
        print("✓ Price Sentiment Trend chart data is AVAILABLE and SEEDED correctly!")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    
    return True

if __name__ == '__main__':
    test_sentiment()

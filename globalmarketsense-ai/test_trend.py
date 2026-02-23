#!/usr/bin/env python3
"""Test sentiment endpoint with detailed output"""
import urllib.request
import json

def test_sentiment_trend():
    print("Testing Price Sentiment Trend Data")
    print("=" * 70)
    
    url = 'http://localhost:8000/api/sentiment/daily?limit=100'
    req = urllib.request.Request(url, method='GET')
    
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        
        rows = result.get('rows', [])
        print(f"Total rows returned: {len(rows)}")
        
        if rows:
            # Group by date
            by_date = {}
            for row in rows:
                date = row.get('sentiment_date', 'UNKNOWN')
                if date not in by_date:
                    by_date[date] = 0
                by_date[date] += 1
            
            print(f"\nUnique dates: {len(by_date)}")
            print("\nDate range (first 5):")
            for i, date in enumerate(sorted(by_date.keys(), reverse=True)[:5]):
                print(f"  {date}: {by_date[date]} entries")
            
            print("\nSample data (first 3 rows):")
            for i, row in enumerate(rows[:3]):
                print(f"\n  Row {i+1}:")
                for key in ['sentiment_date', 'market', 'sentiment_index', 'change_percent']:
                    if key in row:
                        val = row[key]
                        if isinstance(val, float):
                            print(f"    {key}: {val:.4f}")
                        else:
                            print(f"    {key}: {val}")
            
            # Check if we have the expected markets
            markets_found = set()
            for row in rows:
                if 'market' in row:
                    markets_found.add(row['market'])
            
            print(f"\nMarkets in data: {sorted(markets_found)}")
            
            # Check if data spans multiple dates
            dates_found = set(row.get('sentiment_date') for row in rows)
            print(f"Date span: {len(dates_found)} unique dates")
            if len(dates_found) > 1:
                print(f"✓ GOOD: Data spans {len(dates_found)} dates (multi-day trend available)")
            else:
                print(f"✗ ISSUE: Data only has {len(dates_found)} date(s) - no trend visible")
        else:
            print("✗ ERROR: No rows returned")
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sentiment_trend()

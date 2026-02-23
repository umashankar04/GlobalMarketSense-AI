#!/usr/bin/env python3
"""Check the raw historical data"""
import sys
sys.path.insert(0, 'd:/GlobalMarketSense AI/globalmarketsense-ai')

from backend.realtime_simulator import _history, _state
import json

def check_history():
    print("Checking Raw Historical Data")
    print("=" * 70)
    
    print(f"Total entries in _history: {len(_history)}")
    
    if _history:
        # Group by date
        by_date = {}
        for entry in _history:
            date = entry.get('sentiment_date', 'UNKNOWN')
            if date not in by_date:
                by_date[date] = 0
            by_date[date] += 1
        
        print(f"Unique dates in history: {len(by_date)}")
        print("\nDate breakdown (all):")
        for date in sorted(by_date.keys(), reverse=True):
            print(f"  {date}: {by_date[date]} entries")
        
        print("\nFirst 3 historical entries:")
        for i, entry in enumerate(_history[:3]):
            print(f"\n  Entry {i+1}:")
            for key, val in entry.items():
                if isinstance(val, float):
                    print(f"    {key}: {val:.6f}")
                else:
                    print(f"    {key}: {val}")
    else:
        print("✗ History is empty!")
    
    print(f"\nCurrent state count: {len(_state)}")

if __name__ == '__main__':
    check_history()

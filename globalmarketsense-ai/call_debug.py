#!/usr/bin/env python3
"""Check debug endpoint"""
import urllib.request
import json

def check_debug():
    resp = urllib.request.urlopen('http://localhost:8000/api/debug/history-info')
    data = json.load(resp)
    
    print('History Debug Info:')
    print(f'  Total entries: {data.get("history_total_entries")}')
    print(f'  Unique dates: {data.get("unique_dates")}')
    print(f'  Dates with counts: {data.get("dates")}')
    print(f'  State count: {data.get("state_count")}')

if __name__ == '__main__':
    check_debug()

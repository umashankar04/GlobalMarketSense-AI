#!/usr/bin/env python3
"""Test endpoint paths"""
import urllib.request
import json

paths = [
    'http://localhost:8000/api/debug/history-info',
    'http://localhost:8000/debug/history-info',
    'http://localhost:8000/api/sentiment/daily',
]

for path in paths:
    try:
        resp = urllib.request.urlopen(path)
        endpoint = path.split('/')[-1]
        print(f'✓ {endpoint}: OK')
    except Exception as e:
        endpoint = path.split('/')[-1]
        if hasattr(e, 'code'):
            print(f'✗ {endpoint}: {e.code}')
        else:
            print(f'✗ {endpoint}: {e}')

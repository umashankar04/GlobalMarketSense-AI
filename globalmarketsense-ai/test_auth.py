#!/usr/bin/env python3
"""Test authentication endpoints"""
import urllib.request
import json

def test_auth():
    print("Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test REGISTER
    print("\n1. Testing POST /auth/register")
    data = {
        'username': 'demouser',
        'email': 'demo@example.com',
        'password': 'demo123456'
    }
    req = urllib.request.Request(
        'http://localhost:8000/auth/register',
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ SUCCESS - User registered")
        print(f"     - User ID: {result.get('user_id')}")
        print(f"     - Token: {result.get('access_token', '')[:30]}...")
        token = result.get('access_token')
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
        return
    
    # Test LOGIN
    print("\n2. Testing POST /auth/login")
    data = {
        'email': 'demo@example.com',
        'password': 'demo123456'
    }
    req = urllib.request.Request(
        'http://localhost:8000/auth/login',
        data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ LOGIN SUCCESS")
        print(f"     - User ID: {result.get('user_id')}")
        print(f"     - Token: {result.get('access_token', '')[:30]}...")
        token = result.get('access_token')
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
        return
    
    # Test PORTFOLIO - Add stock
    print("\n3. Testing POST /portfolio/add")
    data = {
        'symbol': 'SP500',
        'quantity': 10,
        'entry_price': 4500
    }
    req = urllib.request.Request(
        'http://localhost:8000/portfolio/add',
        data=json.dumps(data).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ ADDED TO PORTFOLIO")
        print(f"     - Portfolio ID: {result.get('portfolio_id')}")
        print(f"     - Symbol: {result.get('symbol')}")
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
    
    # Test GET Portfolio
    print("\n4. Testing GET /portfolio")
    req = urllib.request.Request(
        'http://localhost:8000/portfolio',
        headers={'Authorization': f'Bearer {token}'},
        method='GET'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ PORTFOLIO RETRIEVED")
        holdings = result.get('holdings', [])
        print(f"     - Holdings: {len(holdings)}")
        if holdings:
            h = holdings[0]
            print(f"       • Symbol: {h.get('symbol')}")
            print(f"       • Quantity: {h.get('quantity')}")
            print(f"       • Entry Price: {h.get('entry_price')}")
            print(f"       • Current Price: {h.get('current_price'):.2f}")
            print(f"       • Gain: {h.get('gain'):.2f}")
            print(f"       • Gain %: {h.get('gain_percent'):.2f}%")
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
    
    # Test WATCHLIST - Add stock
    print("\n5. Testing POST /watchlist/add")
    data = {'symbol': 'NIFTY50', 'authorization': token}
    req = urllib.request.Request(
        'http://localhost:8000/watchlist/add',
        data=json.dumps(data).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ ADDED TO WATCHLIST")
        print(f"     - Symbol: {result.get('symbol')}")
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
    
    # Test GET Watchlist
    print("\n6. Testing GET /watchlist")
    req = urllib.request.Request(
        'http://localhost:8000/watchlist',
        headers={'Authorization': f'Bearer {token}'},
        method='GET'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ WATCHLIST RETRIEVED")
        items = result.get('watchlist', [])
        print(f"     - Items: {len(items)}")
        if items:
            item = items[0]
            print(f"       • Symbol: {item.get('symbol')}")
            print(f"       • Price: {item.get('price'):.2f}")
            print(f"       • Sentiment: {item.get('sentiment', {}).get('net', 0):.2f}")
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
    
    # Test NEWS endpoint
    print("\n7. Testing GET /news")
    req = urllib.request.Request(
        'http://localhost:8000/news?category=markets&limit=3',
        method='GET'
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.load(resp)
        print(f"   ✓ NEWS RETRIEVED")
        articles = result.get('articles', [])
        print(f"     - Articles: {len(articles)}")
        if articles:
            article = articles[0]
            print(f"       • Title: {article.get('title', '')[:50]}...")
            print(f"       • Category: {article.get('category')}")
            print(f"       • Source: {article.get('source')}")
    except urllib.error.HTTPError as e:
        print(f"   ✗ FAILED - {e.code}: {e.read().decode()}")
    
    print("\n" + "=" * 50)
    print("✓ All authentication and feature tests completed!")

if __name__ == '__main__':
    test_auth()

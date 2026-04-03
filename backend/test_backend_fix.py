import requests

def test_backend():
    print("=== TESTING BACKEND FIX ===")
    
    # Test root endpoint
    try:
        r = requests.get('http://localhost:5000/', timeout=5)
        print(f'Root endpoint: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(f'Message: {data.get("message", "N/A")}')
            print(f'Status: {data.get("status", "N/A")}')
            print(f'Frontend URL: {data.get("frontend_url", "N/A")}')
    except Exception as e:
        print(f'Root endpoint: ERROR - {e}')

    # Test health endpoint
    try:
        r2 = requests.get('http://localhost:5000/api/health', timeout=5)
        print(f'Health endpoint: {r2.status_code}')
    except Exception as e:
        print(f'Health endpoint: ERROR - {e}')

if __name__ == "__main__":
    test_backend()

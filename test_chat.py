import requests
try:
    res = requests.post('http://127.0.0.1:5000/chat', json={"query": "Hello", "notebook_id": 6})
    print("STATUS", res.status_code)
    try:
        print("JSON", res.json())
    except Exception as e:
        print("RAW", res.text)
except Exception as e:
    print("ERROR", str(e))

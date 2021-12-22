pip3 install -r requirements.txt

uvicorn main:app\
    --reload\
    --port 8000\
    --host 0.0.0.0\
    --proxy-headers\
    --forwarded-allow-ips='172.27.1.11'\
    --log-level debug

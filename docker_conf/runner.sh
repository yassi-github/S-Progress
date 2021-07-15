pip3 install -r requirements.txt

uvicorn main:app\
    --reload\
    --port 8000\
    --host 0.0.0.0\
    --proxy-headers\
    --log-level debug

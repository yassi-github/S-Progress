pip3 install -r requirements.txt

ls docker_conf/
ls docker_conf/nginx/
ls docker_conf/nginx/ssl

uvicorn main:app\
    --reload\
    --port 8000\
    --host 0.0.0.0\
    --proxy-headers\
    --forwarded-allow-ips='*'\
    --log-level debug

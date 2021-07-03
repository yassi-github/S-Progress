# S-Progress

# prepare

```bash
openssl genrsa 4096 > docker_conf/nginx/ssl/server.key
openssl req -new -key docker_conf/nginx/ssl/server.key > docker_conf/nginx/ssl/server.csr
openssl x509 -req -days 3650 -signkey docker_conf/nginx/ssl/server.key < docker_conf/nginx/ssl/server.csr > docker_conf/nginx/ssl/server.crt
```

# ref

[FastAPI + SQLAlchemy（postgresql）によるCRUD API実装ハンズオン - Qiita](https://qiita.com/Butterthon/items/a55daa0e7f168fee7ef0)  
[FastAPIを使ってCRUD APIを作成する - Qiita](https://qiita.com/t-iguchi/items/d01b24fed05db43fd0b8)

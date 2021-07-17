# S-Progress

# requirements

- docker compose

# build

```bash
# start
sudo ./build.sh

# end
docker-compose down
# truncate db, dockerimages
sudo ./.resetall
```

access to:

https://localhost

or

https://your.domain

# usage

Follow the question text and  enter a shell script.

I provide files for solving problems.  
These are placed in the current directory with a name like `q_1.txt`.

# ref

[Request Files - FastAPI](https://fastapi.tiangolo.com/tutorial/request-files/)

[FastAPI + SQLAlchemy（postgresql）によるCRUD API実装ハンズオン - Qiita](https://qiita.com/Butterthon/items/a55daa0e7f168fee7ef0)  
[FastAPIを使ってCRUD APIを作成する - Qiita](https://qiita.com/t-iguchi/items/d01b24fed05db43fd0b8)

[Databases](https://www.encode.io/databases/)

[Deployment - Uvicorn](https://www.uvicorn.org/deployment/)

[Docker SDK for Python — Docker SDK for Python 5.0.0 documentation](https://docker-py.readthedocs.io/en/stable/index.html)
[Docker (ファイル/CPU/メモリ/プロセス) のリソースを制限する方法まとめ - Qiita](https://qiita.com/okamu_/items/2b8b30a76f2aa814ba14#%E3%83%97%E3%83%AD%E3%82%BB%E3%82%B9%E6%95%B0%E3%81%AE%E5%88%B6%E9%99%90)
[logs — Docker-docs-ja 19.03 ドキュメント](https://docs.docker.jp/engine/reference/commandline/logs.html)
[Dockerfile リファレンス — Docker-docs-ja 19.03 ドキュメント](https://docs.docker.jp/engine/reference/builder.html)

[billyteves/ubuntu-dind: Docker-in-Docker](https://github.com/billyteves/ubuntu-dind)

[how to get STDOUT when the container exit with non-zero code? · Issue #2745 · docker/docker-py](https://github.com/docker/docker-py/issues/2745#issuecomment-812238987)

[pnpnpn/timeout-decorator: Timeout decorator for Python](https://github.com/pnpnpn/timeout-decorator)

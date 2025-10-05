# wydra

### run formatter & mypy
```shell
ruff format backend/ && ruff check backend/ && mypy backend/ --strict
```

### alembic migrations
#### create migration file
```shell
docker compose exec dispatch alembic revision --autogenerate -m "file_name"
```
####
```shell
docker compose exec dispatch alembic upgrade head
```


## CLI

### Auth token
```shell
docker compsoe exec dispatch python cli.py token -e 365 -r admin
```

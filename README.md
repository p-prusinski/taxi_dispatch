# Notes to recruiter / known issues
I focused on creating dispatch service in a readable, tested, well organised manner. Taxi microservice simulator was much more rushed and it follows some bad conventions, it was due to time restriction. Also there are no integration tests because of the same reason.

For Taxi model, there is no "currently working" or "offline" status, so I just delete them on teardown. Downside is, because of FK to Trips, I had to make trips.taxi_id nullable and set `ondelete="SET NULL"`. These IDs are still saved in events table as it saves them as integers.
Also shutting down all containers probably won't delete those taxis, so it's best to use `docker compose down -v` in between runs.

Client simulator is not implemented yet - again, lack of time. I might add it to a separate branch after work and edit this note saying these changes were post due date.

PS. I also added .env files to repository to make startup smoother - obviously not something to be done on production.

# taxi dispatch

### start service
First run min-docker-compose so taxi_dispatch doesn't throw errors and apply migrations:
```
docker compose -f min-docker-compose.yaml
docker compose exec dispatch alembic upgrade head
```
Next we can run regular docker-compose.yaml with taxi_service:
```
docker compose up --build
docker compose up --scale taxi_service=20
```
### run formatter & mypy
```shell
ruff format backend/ && ruff check backend/ && mypy backend/ --strict
```
### run tests
```shell
python3 -m pytest backend
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

Go to this project directory, then run the container detached, you might want to use `sudo`:
```bash
docker compose up --build -d
```

To stop the container:
```bash
docker compose down
```

voila!

See what's inside the mongoDB database using mongosh:
```bash
docker exec -it <container_id> mongosh -u <user_name> -p <password>

# OR

docker compose exec mongo mongosh -u <user_name> -p <password>
```

Swagger Docs: `localhost:8000/docs`

Tech stack:
- Python
- uv
- Flask
- Swagger
- Gunicorn
- pymongo
- Docker

Docker images:
- uv
- python 3.12.11 slim bookworm
- mongo 7.0
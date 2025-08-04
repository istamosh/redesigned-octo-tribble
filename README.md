run the container detached, you might want to use `sudo`:
```bash
docker compose up --build -d
```

voila!

see what's inside the mongoDB database using mongosh:
```bash
docker exec -it <container_id> mongosh -u <user_name> -p <password>

# OR

docker compose exec mongo mongosh -u <user_name> -p <password>
```

Swagger Docs: `localhost:8000/docs`
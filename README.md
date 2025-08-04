activate the virtual environment using `source .venv/bin/activate`, or `.venv/Scripts/activate.ps1` in Windows

if you are using uv, run it using `uv sync`

run the application with `flask run`
OR
run with debug mode `flask run --debug`

voila!

initializing mongo docker container:
```bash
sudo docker run -d --name mongo-demo \
> -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
> -e MONGO_INITDB_ROOT_PASSWORD=passw0rd \
> -p 27017:27017 -v mongodemo:/data/db \
> mongo:7.0
```

see what's inside the running container:
```bash
docker exec -it <container_id> mongosh -u <user_name> -p <password>
```
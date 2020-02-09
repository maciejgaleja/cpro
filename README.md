# Building
```bash
git fetch --tags
docker-compose build
docker-compose run --rm -u $UID build "python3 deploy.py"
```

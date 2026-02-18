# Translating Bullet

We use standard Django localization. To regenerate locale files, use:

```shell
docker compose run --rm web ./manage.py makemessages --no-wrap -l <language>
```

Then to compile them use:

```shell
docker compose run --rm web ./manage.py compilemessages
```

# Translating Bullet

We use standard Django localization. To regenerate locale files, use:

```shell
./helper.py cmd makemessages --no-wrap -l <language>
```

Then to compile them use:

```shell
./helper.py cmd compilemessages
```

# Import schools

Schools are imported by custom command.

```shell
./helper.py cmd importschools
```

First argument is importer, usually country code like `sk`. Second argument is file with data in correct format,
located in `bullet` sub-directory.

## Slovak school import

- Download latest data form <https://crinfo.iedu.sk/RISPortal/register/ExportCSV?id=1>.
- Saved it as `bullet/sk.csv`
- run
```shell
./helper.py cmd importschools sk bullet/sk.csv
```

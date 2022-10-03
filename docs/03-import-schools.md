# Import schools

Schools are imported by custom command.

```shell
./helper.py cmd importschools
```

First argument is importer, usually country code like `sk`. Second argument is file with data in correct format,
located in `bullet` sub-directory.

## Available importers

| Country  | Importer | Data source                                                                                                                                                                                                               |
|----------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Slovakia | `sk`     | [crinfo.iedu.sk](https://crinfo.iedu.sk/RISPortal/register/ExportCSV?id=1)                                                                                                                                                |
| Czech    | `cz`     | [stistko.uiv.cz](http://stistko.uiv.cz/registr/vybskolrn.asp) -> Vyhledat -> Export do Excelu -> Seznam škol (convert to classic CSV)                                                                                     |
| Spain    | `es`     | [Náboj Junior GDrive](https://drive.google.com/file/d/10ezwc0om1DMWmeO3xV6N6ryV9sdx4sRv/view)                                                                                                                             |
| Poland   | `pl`     | [rspo.gov.pl](https://rspo.gov.pl) -> Wyszukiwarka zaawansowana -> Typ szkoły/placówki -> Add "Liceum ogólnokształcące, Liceum sztuk plastycznych, Szkoła podstawowa, Technikum" -> Szukaj -> Pobierz plik CSV s wynikami |
| Croatia  | `hr`     | [mzos.hr](http://mzos.hr/dbApp/pregled.aspx?appName=OS) -> press "excel" icon (convert to classic CSV)                                                                                                                    |
| France   | `fr`     | [Náboj Junior GDrive](https://docs.google.com/spreadsheets/d/1p4SW5Bu0XPgffXnlTyzBEe8yklPxWpfg/edit#gid=628139957) (convert to classic CSV)                                                                               |

## Index schools

To index schools in meilisearch (required to working registration) you need to run

```shell
./helper.py cmd indexschools
```


### Full example to import and index slovak schools

```shell
./helper.py cmd importschools sk sk.csv
./helper.py cmd indexschools
```

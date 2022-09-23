# Import schools

Schools are imported by custom command.

```shell
./helper.py cmd importschools
```

First argument is importer, usually country code like `sk`. Second argument is file with data in correct format,
located in `bullet` sub-directory.

## Available importers

| Country  | Importer | Data source                                                                                                                                                |
|----------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Slovakia | `sk`     | [crinfo.iedu.sk](https://crinfo.iedu.sk/RISPortal/register/ExportCSV?id=1)                                                                                 |
| Czech    | `cz`     | [stistko.uiv.cz](http://stistko.uiv.cz/registr/vybskolrn.asp) -> Vyhledat -> Export do Excelu -> Seznam škol (convert to classic CSV)                      |
| Spain    | `es`     | [Náboj Junior GDrive](https://drive.google.com/file/d/10ezwc0om1DMWmeO3xV6N6ryV9sdx4sRv/view)                                                              |
| Poland   | `pl`     | [rspo.gov.pl](https://rspo.gov.pl) -> Wyszukiwarka zaawansowana -> Typ szkoły/placówki -> Add "Szkola podstawowa" -> Szukaj -> Pobierz plik CSV s wynikami |

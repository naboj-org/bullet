# Installation

## Windows

System requirements:
- [Python 3.6](https://www.python.org/downloads/) or newer (I strongly recommend checking "Add Python to PATH" when installing)
- [MariaDB server](https://downloads.mariadb.org/mariadb/10.5.10/), you can follow [this installation tutorial](https://mid.as/kb/00197/install-configure-mariadb-on-windows)

**(Instructions for Windows not tested yet, will test next week.)**

After cloning `bullet` repository, create a virtual environment, activate it and install
Python requirements from `requirements.txt`:

(run in cloned directory)
```shell
python3 -m venv venv
venv\Scripts\activate.bat
python3 -m pip install -r requirements.txt
```

*(now continue with common instructions below)*

## Linux

System requirements:
- Python 3.6 or newer
- MariaDB server (`mariadb-server mariadb-client` on Debian)
- [mysqlclient requirements](https://github.com/PyMySQL/mysqlclient#linux)

After cloning `bullet` repository, create a virtual environment, activate it and install
Python requirements from `requirements.txt`:

(run in cloned directory)
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(now continue with common instructions below)*

## Common

Next, you should prepare a database and user on your local MariaDB instance:

```shell
mysql -u root -p
```
```sql
CREATE DATABASE bullet;
CREATE USER bullet IDENTIFIED BY 'secret';
GRANT ALL ON bullet.* TO bullet;
```

Now, you need to create your `.env` file in `bullet` directory. The easiest way to do that
it to copy `.env.example`. Then you should be able to migrate the database and start
the development server:

(run in `bullet` subfolder)
```shell
python manage.py migrate
python manage.py runserver
```

Don't forget to activate the virtual environment whenever you open new terminal session:
```shell
source venv/bin/activate
```

Now, let's look at your [code editor](02-ide.md).

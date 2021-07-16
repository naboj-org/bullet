Dump table content into an importable SQL:

``pg_dump -U bullet bullet --data-only --no-owner --no-acl --table public.TABLE_NAME > FILENAME.sql``
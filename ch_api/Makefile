CUR_DIR = $(CURDIR)
PG_ENV_FILE = $(CUR_DIR)/pg_env.sh

pg_env:
	tail -n4 $(CUR_DIR)/db/database.ini > $(PG_ENV_FILE)

createdb-command:
	. $(PG_ENV_FILE); \
	/usr/bin/psql "postgresql://$$user:$$password@$$host:5432" -c "CREATE DATABASE $$database OWNER $$user;"

create_db: pg_env createdb-command

psql:
	. $(PG_ENV_FILE); \
	/usr/bin/psql "postgresql://$$user:$$password@$$host:5432/$$database"

clean:
	rm $(PG_ENV_FILE)
CUR_DIR = $(CURDIR)
PG_ENV_FILE = $(CUR_DIR)/pg_env.sh

pg_env:
	tail -n4 $(CUR_DIR)/db/database.ini > $(PG_ENV_FILE)

create-db:
	. $(PG_ENV_FILE); \
	/usr/bin/psql "postgresql://$$user:$$password@$$host:5432" -c "CREATE DATABASE $$database OWNER $$user;"

psql:
	. $(PG_ENV_FILE); \
	/usr/bin/psql "postgresql://$$user:$$password@$$host:5432/$$database"

clean:
	rm $(PG_ENV_FILE)
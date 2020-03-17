from db.pg_engine import MyDb

engine = MyDb(db_config_file="database.ini", db_section_name="PostgreSQL", schema="test")

# create table
engine.execute(query="CREATE TABLE IF NOT EXISTS {table} (unique_id serial PRIMARY KEY, num INT, data TEXT);",
               mode="write",
               table="table_test")

# populate table from tuple - NOTE: You need to pass the "fields" argument.
engine.execute(query="INSERT INTO {table} ({fields}) VALUES ({placeholders})",
               mode="write",
               table="table_test",
               fields=["num", "data"],
               data=(100, "insert from tuple: OK"))

# populate table from dictionary - NOTE: do not pass the "fields" argument.
dict_to_insert = {"num": 101, "data": "insert from dictionary: OK", "ignore_me": [], "ignore_me_too!": {}}

engine.execute(query="INSERT INTO {table} ({fields}) VALUES ({placeholders})",
               mode="write",
               table="table_test",
               data=dict_to_insert,
               drop_keys=["ignore_me", "ignore_me_too!"])

# read/update db, using an optional kwarg (id).
selected_data = engine.execute(query="SELECT {fields} FROM {table} "
                                     "WHERE {id} = %s "
                                     "OR {id} = %s;",
                               mode="read",
                               table="table_test",
                               fields=["num", "data"],
                               data=(1, 2),
                               id="unique_id")  # optional kwarg

for i in selected_data:
    print(i)

# (100, 'insert from tuple: OK')
# (101, 'insert from dictionary: OK')

engine.execute(query="UPDATE {table} SET {fields} = %s WHERE {id} = %s;",
               mode="write",
               table="table_test",
               fields=["data"],
               data=("updated data", 100),
               id="num",)  # 100 is the id.

select_updated_data = engine.execute(query="SELECT {fields} FROM {table} WHERE {id} = %s;",
                                     mode="read",
                                     table="table_test",
                                     fields=["data"],
                                     data=(100,),
                                     id="num")

for i in select_updated_data:
    print(i)
# ('updated data',)

# more complex statements can be done, just pass optional keyword arguments.

select_updated_data_2 = engine.execute(query="SELECT {fields} FROM {table} WHERE {id} = %s AND {num} = %s;",
                                       mode="read",
                                       table="table_test",
                                       fields=["unique_id", "data"],
                                       data=(1, 100),
                                       id="unique_id",  # optional
                                       num="num")       # optional

for i in select_updated_data_2:
    print(i)
# (1, 'updated data')

# optional kwargs can also be iterables.
select_updated_data_3 = engine.execute(query="SELECT DISTINCT {p_key} FROM {table};",
                                       mode="read",
                                       table="table_test",
                                       p_key=["unique_id", "data"])  # optional

for i in select_updated_data_3:
    print(i)
# (2, 'insert from dictionary: OK')
# (1, 'updated data')

# finally, you can pass "write and read" queries.
select_updated_data_4 = engine.execute(query="INSERT INTO {table} ({fields}) VALUES ({placeholders}) " \
                                              "RETURNING {p_key};",
                                       mode="write + read",
                                       table="table_test",
                                       fields=["num", "data"],
                                       data=(103, "insert from tuple: OK"),
                                       p_key=["unique_id", "num"])

for i in select_updated_data_4:
    print(i)

# (3, 103)

engine.execute(mode="write", query="DROP SCHEMA {schema} CASCADE;", schema="test")

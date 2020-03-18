## The `companies-house-api/db/` folder

This folder contains the the modules and the initialisation file for the connection to a PostgreSQL instance. 

```
.
├── database.ini
├── pg_constants.py
├── pg_engine.py
├── pg_engine_test.py
├── pg_tables.py
└── README.md
```

#### The file structure

`database.ini` contains the variables you need to build the connection URI (see section 
[33.1.1.2. Connection URIs](https://www.postgresql.org/docs/12/libpq-connect.html) in the official documentation).

`pg_constants` contains the constants used by `pg_engine.py`:
- the schema name: if a schema is not present, it will be created and the engine will return a connection with the path 
set to that schema. 
- the **absolute** path to the file `database.ini` file. 
- the configuration section to be read from the `database.ini` file. Set to "PostgreSQL" and should not be touched. 

`pg_engine.py` is the module where the query parameterization happens using `psycopg2`. 
The way `pg_engine,py` works is the following:
```
from db.pg_engine import MyDb

# create engine 
engine = MyDb(db_config_file="database.ini", db_section_name="PostgreSQL", schema="test")

# choose a mode between "read", "write", "read + write"
# pass the string query and the parameters to engine.execute()

data = engine.execute(mode="read",
                      query="SELECT {fields} FROM {table} WHERE {id} = %s OR {id} = %s;",
                      table="table_test",
                      fields=["field_1", "field_2"], 
                      data=(1, 2), 
                      id="unique_id")
```

`pg_tables.py` is a python file containing the variables with the create statements as strings.  

`README.md` this readme. 


#### Parameterization specs in `pg_engine`


##### semi-optional kwargs

Not all the following are mandatory, but if passed, all these arguments should be named like expected.

- **"mode"**: mandatory, should be `"read"`, `"write"` or `"read + write"`.   
- **"query"**: mandatory, string of query to be completed.  

  ###### How to correctly compose query strings? <br />

  Example of SELECT: `"SELECT FROM somewhere¹ WHERE something² = something_else³"`  
  ¹ *somewhere* is just the name of the table where we are inserting into, encased by `{}` as all 
  [named argument in psycopg2](https://www.psycopg.org/docs/usage.html?highlight=gunpoint#passing-parameters-to-sql-queries). <br />
  ² *something* is the column of the table we want to select from, it should be passed with the named argument `{fields}`. <br />
  ³ *something_else* can be a string or a number, so we want to pass it using the "data" argument and adding a 'placeholder' 
  in the query string. <br />    
         
  So the query finally becomes:
  `"SELECT FROM {table} WHERE {fields} = %s"` <br />
      
  Example of INSERT: `"INSERT INTO somewhere¹ (matching_some_keys)² VALUES (somevalues³)"`  
  ¹ *somewhere* is just the name of the table where we are inserting into encased by `{}` 
  since it's a named argument.  
  ² *matching_some_keys* needs to passed to tell psycopg2 into which columns should the data be inserted. As before, we 
  need to pass the named argument `{fields}`.  
  ³ *somevalues* is a collection of placeholders, since we are inserting a bunch of data at once. The right way to pass
  this argument is by using the named argument `{placeholders}`  
  
  **NB:** `pg_engine.py` expects `{fields}` and `{placeholders}` named arguments to be called like this. 
  So even if you are selecting/inserting   on one column only, you should use the plural.
  
  So the query finally becomes:
  `"INSERT INTO {table} ({fields}) VALUES ({placeholders})` <br /> 
 
- **"schema"**: defaulted to `None` if not passed. Simply the string to the schema to either connect to, or automatically 
create and connect to. If not passed, `pg_engine.connect()` will return a connection to the public schema. 

- **"table"**: defaulted to `None` if not passed. Simply the string to the table to connect to. The table must be present in the database. 

- **"fields"**: defaulted to `None` if not passed. Can be dropped if you are performing an INSERT from a dictionary. 
In which case the fields will be created automatically using the dictionary keys. <br />
If you are performing an INSERT from an iterable then "fields" should be passed explicitly. <br />
   
Example INSERT from dictionary:  
```
    engine.execute(query="INSERT INTO {table} ({fields}) VALUES ({placeholders})",
                   mode="write",
                   table="table_test",
                   data={"field1_": 1, "field_2": "string inserted from dict", "ignore_this": []},
                   drop_keys=["ignore_this"])
```  
Example INSERT from tuple:  
    
```
    engine.execute(query="INSERT INTO {table} ({fields}) VALUES ({placeholders})",
                   mode="write",
                   table="table_test",
                   fields=["field_1", "field_2"],  # explicitly pass the fields.
                   data=(1, "string inserted from a tuple"))
```
- **"data"**: defaulted to `None` if not passed. Can be either a dictionary, an iterable (list). <br />
          

- **"drop_keys"**: defaulted to `None` if not passed. As shown above under the "fields" argument explanation, 
"drop_keys" should be passed in case there are some keys from the dictionary which need to be dropped.

##### fully optional kwargs.

Once you have passed all the arguments you needed from the semi-optional ones, you can still pass any other additional
argument needed to complete your query. <br />

Example:
```
select_updated_data_4 = engine.execute(query=("INSERT INTO {table} ({fields}) VALUES ({placeholders}) "
                                              "RETURNING {some_fields_to_return};"),
                                       mode="write + read",
                                       table="table_test",
                                       fields=["unique_id", "field_2"],
                                       data=(2, "string inserted from tuple"),
                                       p_key="unique_id")  # would work also with ["unique_id", "field_2"]
```

**NB**: these optional arguments can be named whatever you want, and can be passed as a single string or an iterable. 

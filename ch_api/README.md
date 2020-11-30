## Option 2: deploy on your machine with pip + psql.

`ch_api/prog.py` is a python programme with  a command line interface allowing the user to launch the download of resources
 in companies house API, insert them automatically in a postresql database and create excel files of the tables.  

#### configuration:

##### the interpreter
- clone the repository to a local folder. 
- make sure you `cd` into `ch_api` and set that as root folder (if you're using PyCharm for example).
- create a new virtual environment with **python 3.6+** (previous versions won't work as the programme uses [f-string literals](https://realpython.com/python-f-strings/))   
`python3 -m venv venv && source venv/bin/activate`.
- install the requirements  
 `pip3 install -r requirements.txt`. 

##### the database

- if you don't have PostgreSQL installed, install it, if it is below version 10, upgrade. The development of the
 programme has used PostgreSQL 12.  
 [How to intall PostgreSQL for the first time](https://www.postgresql.org/download/)  
 [How to upgrade PostgreSQL](https://www.postgresql.org/docs/9/install-upgrading.html)  
- make sure that the `ch_api/db/database.ini` file is filled with the following:  
> host=[choose host - you probably want to just use `localhost`]  
database=[choose db name]   
user=[choose user name]    
password=[choose password]   

- if you have not created the target database yet, simply create it with the `ch_api/Makefile` recipe `make create_db`. 
A side-effect of this recipe will be to create a `ch_api/pg_env.sh` to be sourced for the psql connection - remove it by
simply calling `make clean` (or just `rm` it). 

- make sure that you choose the `DB_SCHEMA` in `ch_api/db/pg_constants.py`. The schema will be created if it doesn't exist 
and the connection object will be set to the schema.

- run the programme from within the environment:

```textmate
(venv) prompt$ python3 <path/to/prgoramme> <path/to/url_file> <optional flags>
(venv) prompt$ python3 prog.py url_file.txt --psc --excel
```

- check that the data was correctly inserted in postgres, connect with the `ch_api/Makefile` recipe `make psql`

##### flags

###### for the input data 
- The url_id for the following flags is the uniquely identifiable company_code. Example: **OC362072**  
`--psc`: for person of significant interest in the companies house API. See resource here.  
`--ol`: for officers list in the companies house API. See resource here.  
`--cp`: for company profile in the companies house API. See resource here. 

- The url_id for the following flag is companies house officer_id. Example: **/officers/RY_RJjPR0uGi0pOJuJi7dyCCTzo/appointments**  
`--al`: for appointment list in the companies house API. See resource here. 

###### for the output data

`--excel`: to automatically dump the postgres tables to excel files. Each Excel file will contain several tabs. 
Download an example here.  


##### errors

- the file extensions for the file containing the urls can be either `txt` or `csv`. Relatively messy file can be parsed, 
 ideally write a url_id per line. No need to end the line with a comma. 
 
- if you try to form URI for the appointments resource using a company code or viceversa, an officer_id for a company 
resource, the programme will throw an error at you.

- flags which use the same type of url_id can be cumulative, conversely they collide and an error will be thrown.  
legal: `python3 pipeline.py <url_file_containing_company_codes.csv> --psc --ol --cp`  
illegal: `python3 pipeline.py <url_file_containing_company_codes.csv> --al --cp`  


##### psql

Imagine you have used the pipeline to download the officer list based on company codes. Now you want to download the 
appointment list but you don't want to manually create a file containing the officer_ids. 

You can use the following trick:

```
(venv) prompt$ python3 prog.py $(psql -U <user> -d <databasename> -1 -t -o queryresults.txt \  
-c "select links_officer_appointments from <schema>.ol_items"\   
&& readlink -e ./queryresults.txt)\  
--al
```

`$(...)` gives the output of a command  
`-U <username>` user <username>  
`-d <name>` database name <name>   
`-1` use one transaction  
`-t` tuples only (makes sure do no get headers or column names in the results. We only want the tuples.)  
`-c "sql"` command "sql"  
`-o <file>` write query results to output file named <file>  
`&&` will execute command after it if previous command was successful  
`readlink -e <file>` will print the absolute path to the file to the console (which will be passed to `prog.py`)

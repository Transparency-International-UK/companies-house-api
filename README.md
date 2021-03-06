## Option 1: run with Docker. 

- Clone the repository and set the root folder to `project` (`cd` into it).
- Follow the configuration steps below. 
- Run for the first time, from the root folder run:  
`docker-compose run ch_app [--cp, --ol, --psc, --al, --excel]` (for an explanation of what each flag does and how they 
work check out the [`project/ch_api/README`](https://github.com/Transparency-International-UK/companies-house-api/blob/master/ch_api/README.md))
- If you got your data, [backed it up](https://stackoverflow.com/questions/24718706/backup-restore-a-dockerized-postgresql-database) 
and you are done with it and want to clean your machine, use the `project/Makefile` recipe to `make clean_all`- or 
the other clean recipes for the level of cleaning you need. 
- If you want to continue building the database with new data coming from new url_id **you stored in the 
`project/ch_api/url_file.txt` file**, just re run the docker-compose run command, the named `project_postgres_data` 
volume will ensure data persistence:  
`docker-compose run ch_app [--cp, --ol, --psc, --al, --excel]`  
The application performs [upsertion](https://www.postgresqltutorial.com/postgresql-upsert/) overwrite existing data if 
the unique id of the resource you have is already present, otherwise new unseen data will be added.
- If you want to restore a pg_dump from a previous docker-compose run, follow [these steps](https://simkimsia.com/how-to-restore-database-dumps-for-postgres-in-docker-container/). 

#### Configuration

- make sure that the `project/ch_api/db/database.ini` file is filled with the following:  
> host=ch_pg  
database=choose db name   
user=choose user name    
password=choose password  

The `host` will be the name of the database service, in this case, `ch_pg`. 

- Ensure that the postgres configuration in the `project/docker-compose.yml` environment is the same one as the one in 
the `project/ch-api/db/database.ini`.

> POSTGRES_PASSWORD: here you choose db password    
> POSTGRES_USER: here you choose user name    
> POSTGRES_DB: here you choose db name  

- Ensure that the recipe `make psql` of the `project/Makefile` is also aligned:  
> psql postgres://POSTGRES_USER:POSTGRES_PASSWORD@$$IP:5432/POSTGRES_DB 

- Ensure that the name of the file where you have stored the url ids to compose the [Companies House Unique Resource 
Identifier](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/426891/uniformResourceIdentifiersCustomerGuide.pdf)
is correctly inserted in the `folder/docker-compose.yml` (ln.  37):  
> /ch-api/here goes the name of file containing the url ids 

- Go to the `utils/api_key` file and copy your the key generated by the 
[registration](https://developer.companieshouse.gov.uk/developer/applications/register) to Companies House API.

- Go to the `db/pg_constants.py` file and assign to the `DB_SCHEMA` constant the name of the schema you want to be created/
connected to. 

- If you run several times either service but forget to clean the container namespace - make sure that the name of the 
`ch_pg` service container is the same atop the `project/Makefile` - runs will be appended with the cardinal number.

#### Danger zone: **do not change any folder names** 

- If you rename the root `project/` folder or any of the services in the `project/docker-compose.yml` you will have to 
ensure consistency with the named volumes, containers and images in the `project/Makefile`, as the daemon creates names 
using the name of the folder where the context files are located (`project/`).

- Same goes for the `project/postgres_data` folder, changing the name of this folder will need to be reflected in the 
`project/Makefile` and the `project/docker-compose.yml`. This folder is empty before running the app container, as it 
will be bind-mounted as volume for the persistence of the database files. 

- If you change the name of the services, `ch_pg` and `ch_app` this will need to be reflected in the `/project/Makefile`.

- If you change the name of the `project/ch_api` folder to `project/new_name` ensure that `new_name` is refactored in the 
`project/docker-compose.yml` for:
> entrypoint: (ln. 36-37)  
> volumes: (ln. 43)  
> device: (ln. 63)   

- And in the `project/Dockerfile`: 
> COPY ./ch_api /ch_api # ./ch_api has to be new_name, /ch_api has to be...      
> WORKDIR /ch_api  # ...the same as this one 

Just don't change any name.

## Option 2: deploy on your machine with pip + psql.

- Clone this repo and set the root directory to `ch_api` (`cd` into it).
- Furhter follow the instructions of the [`/ch_api/README.md`](https://github.com/Transparency-International-UK/companies-house-api/blob/master/ch_api/README.md)  
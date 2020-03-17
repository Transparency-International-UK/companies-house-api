PG_CONTAINER=project_ch_pg_1

psql:
	# get the id of the container and connect to it using the URI.
	IP=$$(docker exec -it $(PG_CONTAINER) hostname -i); \
	psql postgres://ch_user:ch_pass@$$IP:5432/ch_db

up:
	docker-compose up -d

# remove containers, volumes and networks.
down:
	docker-compose down

# remove image
rmi:
	# "project_ch_app" is the name of the image.
	# Change accordingly if you change the name of the foler or the app service.
	docker image rm -f project_ch_app

# launch non detached, allows debugging.
debug:
	docker-compose up

# remove folder to mount and docker volume.
rm_pg_mount:
	sudo rm -r postgres_data

rm_pgv:
	docker volume rm project_postgres_data

rm_appv:
	docker volume rm project_ch_app_data

# make new mount folder.
new_pg_mount:
	mkdir postgres_data

# rm and make new folder to mount as volumne.
clean_vol: rm_pgv rm_pg_mount new_pg_mount

# remove all containers/images/network/volume of the dockerized app.
clean_app: down rmi rm_appv

# with this order, cannot remove volumes before stopping containers.
clean_all: clean_app clean_vol

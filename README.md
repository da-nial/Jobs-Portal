## How to run project?

1. [Install Docker Compose](https://docs.docker.com/compose/install/)
2. Clone this repository
3. Run only the project container for development `docker-compose up`
4. Run in backend `docker-compose up -d` (not recommended for debugging)
5. Terminate the containers with `docker-compose down`
6. Build images `docker-compose build`
7. Build and run `docker-compose up --build`
8. Running containers list `docker-compose ps`

## Advance usage
1. development docker compose with all containers prefix command `make docker-compose dev`
2. deployment docker compose prefix command `make docker-compose prod`
3. two above commands should be used instead of `docker-compose` command
4. if a specific docker compose is running you should only use its specific command before calling `down` 
and notice that other won't give you the proper result. 
   1. example: `make docker-compose dev up` & `make docker-compose dev ps` & `make docker-compose dev down`
   2. if you use another docker compose command it can break the normal flow 
   than you should remove containers and network manually
5. if you want to use -arg or --arg inside your command while using a `make docker-compose`, 
you should use ` -- ` somewhere before all of them
   1. right usage: `make docker-compose dev up -- -d --build` & `make -- docker-compose dev up -d --build`
   2. wrong usage: `make docker-compose dev up -d --build` & `make docker-compose dev up -d -- --build`
6. if you want to set value for a kwarg in your command while using a `make docker-compose`,
you should use `*` instead of `=`
   1. right usage: `make docker-compose prod exec db psql -- --username*jobs_website_user --dbname*jobs_main_db`
   2. wrong usage: `make docker-compose prod exec db psql -- --username=jobs_website_user --dbname=jobs_main_db`
7. don't change docker-compose and .env files while a docker-compose is running
8. if you are using a development docker compose (`docker-compose` or `make docker-compose dev`), 
code changes will apply immediately. feel free to change the code
9. production docker compose code changes only show up after rebuild

## Task tracker test task

### Purpose

Implementation of a REST endpoint to handle with task tracking system and users



## Package selection

### Web framework - FastAPI

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints





### Task Queue - Celery

`celery` is selected as an abstraction layer over the message queue to handle task enqueuing and consumption. This package does create additional complexity and requires additional dependencies, but it is robust, easily scalable, well documented and allows for a faster development time.



### Message backend - Redis

Although `redis` is simpler and more lightweight, it does not (easily) provide persistency



### Service orchestration - Docker-compose

`docker-compose` is an obvious choice to orchestrate several heterogeneous services and make them interoperate in an ensebmle, regardless of the environment.



### Python dependency management - poetry

`poetry` is suggested, because it resolves and locks Python dependencies, and manages virtual environments. `pip-tools` + `venv` can do the same, in two packages, but with a bit more manual work.



## Code organization

- `docker-compose.yml` - service images used in the project;
- `pyproject.toml` - python requirements for the app;
- `.env` - environment variables for **test task purposes only** it's in github project folder;
- `data/` - for services data(will appear after first run);
- `data/worker_data/` - for mock emails when will change tasks status
- `app/` - application folder;
- `app/docker/Dockerfile` - to build the app image;
- `app/exceptions.py` - custom exceptions;
- `app/config.py` - config for project, default DEBUG=True to mock email send;
- `app/database.py` - database settings;
- `app/services/` - celery, tasks and sending mail services;
- `app/tasks/` - the REST endpoints for tasks;
- `app/users/` - the REST endpoints for users;



## How to run

- `git clone https://github.com/BezuglyR/TaskTracker.git`
- `cd TaskTracker`
- `docker-compose up` - *docker must be installed on your system*
- http://127.0.0.1:8000/docs - after all containers up and initialized


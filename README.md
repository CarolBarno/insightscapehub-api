# insightscapehub-api

Welcome to InsightScapeHub, your central platform for data analysis and insights. InsightScapeHub empowers users to explore, analyze, and visualize their datasets with advanced tools and techniques. Whether you're a data scientist, analyst, or business user, InsightScapeHub provides the tools you need to unlock valuable insights from your data.

#### Setup using docker

> Run `docker-compose up --build --detach`

#### Local development
> Setup virtualenv with python 3.8+

> Run `pip install -r requirements.txt`

> Run `./bin/prestart.sh`

> Run `uvicorn app.main:app --reload --host 0.0.0.0`

#### Running Test
> Run `python ./bin/test.py`

#### Generating migrations
> Run `alembic revision --autogenerate -m "migration name"`

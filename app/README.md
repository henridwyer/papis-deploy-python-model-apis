# Background

We trained a python model to classify whether or not a review is real or spam. Now we want to use this model to detect deceitful reviews.

The model is stored in model as ```model.pkl```.


# Version 3.2 - Docker Swarm

Create a docker machine to serve as the swarm manager.
```
docker-machine create -d digitalocean --digitalocean-private-networking --digitalocean-region "nyc3" --digitalocean-size "512mb" manager
```

Note the swarm manager IP address - it's required in order to add more nodes to the swarm.
Now let's create a swarm:

```
eval $(docker-machine env manager)
docker swarm init --advertise-addr <MANAGER-IP>
Swarm initialized: current node (5dq73iaqxlf84) is now a manager.

To add a worker to this swarm, run the following command:
    docker swarm join \
    --token SWMTKN-1-5ywsue5d3gtj671jks7ypyoh96vwko36y5ouz2egd01b5sd-01z6g00kdcbeq043 \
    104.236.120.126:2377

To add a manager to this swarm, run the following command:
    docker swarm join \
    --token SWMTKN-1-5ywsue5d3gtj671jks7ypyoh96vwko36y5ouz2egd01b5sd-91memvgblpri \
    104.236.120.126:2377

```

The output shows the commands to add nodes to the swarm.
Create 2 more docker machines to serve as swarm nodes, and have them join the swarm.

Worker 1:
```
docker-machine create -d digitalocean --digitalocean-private-networking --digitalocean-region "nyc3" --digitalocean-size "8gb" worker1
eval $(docker-machine env worker1)
swarm join \
--token SWMTKN-1-5ywsue5d3gtj671jks7ypyoh96vwko36y5ouz2egd01b5sd-01z6g00kdcbeq043 \
104.236.120.126:2377
```

Worker 2:
```
docker-machine create -d digitalocean --digitalocean-private-networking --digitalocean-region "nyc3" --digitalocean-size "8gb" worker1
eval $(docker-machine env worker1)
swarm join \
--token SWMTKN-1-5ywsue5d3gtj671jks7ypyoh96vwko36y5ouz2egd01b5sd-01z6g00kdcbeq043 \
104.236.120.126:2377
```

Now it's time to run the containers!
```
docker service create --name flask -p 5000:5000 --network python-api henridwyer/papis_python_api
docker service create --name redis --network python-api redis:alpine
docker service create --name celery  -e "CELERY_WORKER=true" -e "C_FORCE_ROOT=True" --network python-api henridwyer/papis_python_api celery worker -A predict_celery:celery -l DEBUG -c 1
```

## Benchmarks

```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~5.0 requests/s

# Version 3.1 - Docker Machine

Create the machine. First set your api token to the environment variable:
DIGITALOCEAN_ACCESS_TOKEN, then run
```
docker-machine create -d digitalocean --digitalocean-private-networking --digitalocean-region "nyc3" --digitalocean-size "512mb" python-api
docker-machine env python-api
```

Now let's push our app container to a docker registry

```
docker login
docker tag app henridwyer/papis_python_api
docker push henridwyer/papis_python_api
```

Finally, we start the app on the docker machine.

```
docker network create python-api
docker run --name flask -d -p 5000:5000 --network python-api henridwyer/papis_python_api
docker run --name redis -d --network python-api redis:alpine
docker run --name celery -d -e "CELERY_WORKER=true" -e "C_FORCE_ROOT=True" --network python-api henridwyer/papis_python_api celery worker -A predict_celery:celery -l DEBUG -c 1
```

## Benchmarks

```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~3.0 requests/s

# Version 3 - Docker

Create shared network:
```
docker network create python-api
```

Build and start the webserver container:
```
docker build -t app app
docker run --rm -p 5000:5000 --network python-api --name flask app
```

Start the redis container:
```
docker run --rm --network python-api --name redis redis:alpine
```

Start the celery worker:
```
docker run --rm -e "CELERY_WORKER=true" -e "C_FORCE_ROOT=True" --network python-api --name celery app celery worker -A predict_celery:celery -l DEBUG -c 3
```

## Benchmarks

```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~2.0 requests/s

# Version 2 - Celery

Start the webserver:
```
gunicorn -w 1 -b 127.0.0.1:5000 -k gevent api:app
```

Start redis:
```
redis-server
```

Start celery worker
```
CELERY_WORKER=true celery worker -A predict_celery:celery -l DEBUG -c 1
```

## Benchmarks

```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~2.75 requests/s

# Version 1.1 - Flask + gunicorn

We can run flask using gunicorn and scale the number of workers.

```bash
gunicorn -w 3 -b :5000 api:app
```

## Benchmarks
```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~1.0 requests/s


## Benchmarks
```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```
~2.75 requests/s

# Version 1 - Flask

We can set up a flask server to serve the model.

```bash
FLASK_APP=api.py flask run
```

Now we can send requests to the Flask server:
```bash
curl -X POST localhost:5000/predict \
-H "Content-Type: application/json" \
-d '{"text": "I will NEVER stay in this hotel again!"}'
```

## Benchmarks

How many predictions can our setup handle?

Using Apache Bench:

```bash
ab -n 10 -p data.json -T application/json 127.0.0.1:5000/predict
```

```
Concurrency Level:      1
Time taken for tests:   6.457 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      1980 bytes
Total body sent:        1930
HTML transferred:       500 bytes
Requests per second:    1.55 [#/sec] (mean)
Time per request:       645.709 [ms] (mean)
Time per request:       645.709 [ms] (mean, across all concurrent requests)
```

```bash
ab -n 10 -c 10 -p data.json \
-T application/json \
127.0.0.1:5000/predict
```

```
Concurrency Level:      10
Time taken for tests:   5.980 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      1980 bytes
Total body sent:        1930
HTML transferred:       500 bytes
Requests per second:    1.67 [#/sec] (mean)
Time per request:       5979.502 [ms] (mean)
Time per request:       597.950 [ms] (mean, across all concurrent requests)
Transfer rate:          0.32 [Kbytes/sec] received
                        0.32 kb/s sent
                        0.64 kb/s total
```

## Profiling the requests

Add the profiler to the app, and then run a prediction and look at the profiler output:

```
   Ordered by: cumulative time
   List reduced from 381 to 30 due to restriction <30>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.832    0.832 /Users/henri/projects/papis_talk/api_env/lib/python2.7/site-packages/werkzeug/contrib/profiler.py:95(runapp)
        1    0.000    0.000    0.832    0.832 /Users/henri/projects/papis_talk/api_env/lib/python2.7/site-packages/flask/app.py:1958(wsgi_app)
        1    0.000    0.000    0.832    0.832 /Users/henri/projects/papis_talk/api_env/lib/python2.7/site-packages/flask/app.py:1627(full_dispatch_request)
        1    0.000    0.000    0.831    0.831 /Users/henri/projects/papis_talk/api_env/lib/python2.7/site-packages/flask/app.py:1605(dispatch_request)
        1    0.000    0.000    0.831    0.831 /Users/henri/projects/papis_talk/api.py:15(predict_api)
        1    0.000    0.000    0.831    0.831 /Users/henri/projects/papis_talk/api.py:22(predict_text)
      2/1    0.000    0.000    0.831    0.831 /Users/henri/projects/papis_talk/api_env/lib/python2.7/site-packages/sklearn/utils/metaestimators.py:37(<lambda>)
```

Nearly all of the request time takes place in the ```predict_text``` function!

## Setting up the environment

1. Set up python environment

Python 2:
```bash
python -m virtualenv api_env
```

Python 3:
```bash
pyvenv api_env
```

source api_env/bin/activate

2. Install the requirements

```python
pip install -r requirements.txt
```

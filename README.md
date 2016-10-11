# Background

We trained a python model to classify whether or not a review is real or spam. Now we want to use this model to detect deceitful reviews.

The model is stored in model as ```model.pkl```.

# Version 1.1 - Flask + gunicorn

We can run flask using gunicorn and scale the number of workers.

```bash
gunicorn -w 3 -b :5000 api:app
```

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

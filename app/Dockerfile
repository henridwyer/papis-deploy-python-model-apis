FROM python:3-onbuild
EXPOSE 5000
CMD ["gunicorn", "-w 3", "-k gevent", "-b 0.0.0.0:5000", "api:app"]

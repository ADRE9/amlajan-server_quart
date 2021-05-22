FROM tiangolo/uvicorn-gunicorn:python3.8




COPY ./app /app
COPY ./requirements.txt /app
RUN pip install  -r requirements.txt


EXPOSE 80

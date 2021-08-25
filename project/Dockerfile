FROM python:2.7

WORKDIR /home/techtrends

COPY ./techtrends .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "init_db.py"]

CMD ["python", "app.py"]

EXPOSE 3111
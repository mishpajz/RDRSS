FROM python:3.10-slim-bullseye
WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./RDRSS.py .
VOLUME /app/RDRSSconfig
CMD ["/app/RDRSS.py"]
ENTRYPOINT ["python3"]
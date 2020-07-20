FROM alpine:3.11.2
RUN apk add --no-cache python3-dev && pip3 install --upgrade pip
WORKDIR /app
COPY . /app
RUN pip3 --no-cache install -r requirements.txt 
CMD ["python3", "src/main.py"]
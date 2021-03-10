# Use standard Python image to install and build dependencies
FROM python:3.9.1-buster AS builder
WORKDIR /usr/src/app
COPY requirements.txt .
RUN python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
COPY . .

# Use minimal Python image to run endrpi and keep the image size small
FROM python:3.9-alpine
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app .
EXPOSE 5000
CMD [ "venv/bin/python", "endr.py" ]
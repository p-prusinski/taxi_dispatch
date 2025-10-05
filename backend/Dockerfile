FROM python:3.13

WORKDIR /backend

COPY . ./
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["fastapi", "dev", "main.py"]
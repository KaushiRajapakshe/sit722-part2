FROM python:3.11-slim

WORKDIR /app
COPY ./book_catalog .
RUN pip install -r requirements.txt
EXPOSE 8081
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]

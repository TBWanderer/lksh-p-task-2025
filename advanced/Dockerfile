FROM python:3.11-slim
WORKDIR /app
COPY src/ /app/
RUN pip install flask requests
EXPOSE 8000
CMD ["python", "app.py"]

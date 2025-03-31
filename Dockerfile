FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

#페이지로 분할하는 경우
CMD ["python", "src/pageSplit.py"]

#사이즈로 분할하는 경우
#CMD ["python", "src/sizeSplit.py"]


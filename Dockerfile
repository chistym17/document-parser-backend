FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN tesseract --list-langs && \
    ls -l /usr/share/tesseract-ocr/5/tessdata/eng.traineddata

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

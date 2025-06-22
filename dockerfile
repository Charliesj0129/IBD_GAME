FROM python:3.10-slim
WORKDIR /app

# 安裝相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有檔案
COPY . .

# 暴露 5000 埠口
EXPOSE 5000

# 使用 Gunicorn 作為 production server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

# 1. 軽量なPythonベースイメージを使用
FROM python:3.11-slim

# 2. 作業ディレクトリ作成
WORKDIR /app

# 3. 必要なパッケージインストール（PDF関連ではlibmagicも念のため）
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. プロジェクトファイルをコンテナにコピー
COPY . /app

# 5. 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# 6. Flaskアプリを起動（ホストとポートを明示）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 7. コンテナ起動時のコマンド
CMD ["flask", "run"]

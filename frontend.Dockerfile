# ビルドステージ
FROM node:18-alpine AS builder

WORKDIR /app

# 依存関係をインストール
COPY package*.json ./
RUN npm install --legacy-peer-deps

# アプリケーションのソースをコピー
COPY . .


# 本番用ビルド
RUN npm run build

# 本番イメージ
FROM node:18-alpine AS runner
WORKDIR /app

# 本番用の依存関係のみをインストール
ENV NODE_ENV production
RUN npm install -g serve

# ビルド成果物をコピー
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# ポートを公開
EXPOSE 3000

# アプリケーションを起動
CMD ["npx", "serve", "-s", ".next", "-p", "3000"]

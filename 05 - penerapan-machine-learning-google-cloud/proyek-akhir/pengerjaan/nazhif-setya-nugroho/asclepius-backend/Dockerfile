# Cloud Run container for the Asclepius backend.
FROM node:20-slim

WORKDIR /app

# Install production deps first for better layer caching.
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY src ./src

ENV NODE_ENV=production
# Cloud Run injects PORT (defaults to 8080); server.js reads process.env.PORT.
ENV PORT=8080
EXPOSE 8080

CMD ["node", "src/server.js"]

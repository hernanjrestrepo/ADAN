FROM node:22-slim

WORKDIR /app

# Dependencias exactas del lockfile (react-router 8 exige Node 22)
COPY package.json package-lock.json ./
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci

# Copy source
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM node:22-slim

WORKDIR /app

# Install dependencies (reproducible: respeta package-lock.json)
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

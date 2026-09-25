# Etapas: deps → development (docker-compose.yml) · build → production (nginx, docker-compose.prod.yml)
FROM node:22-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci

FROM deps AS development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM deps AS build
COPY . .
RUN npm run build

# Producción: archivos estáticos + proxy al backend, sin root (puerto 8080)
FROM nginxinc/nginx-unprivileged:stable-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY proxy_hide.inc /etc/nginx/conf.d/proxy_hide.inc
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO /dev/null http://127.0.0.1:8080/ || exit 1

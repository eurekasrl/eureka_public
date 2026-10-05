FROM node:24-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Vite inlines VITE_* variables at build time.
ARG VITE_API_BASE_URL
ARG VITE_API_KEY
RUN npm run build

FROM node:24-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=build /app/dist .
CMD ["serve", "-s", ".", "-l", "3000"]

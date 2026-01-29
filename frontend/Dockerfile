# frontend/Dockerfile

# Stage 1: Build
# CHANGED: Upgraded from 18 to 22-alpine to support Vite v7+
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve (Using light web server)
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Custom Nginx config to handle React Router (SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
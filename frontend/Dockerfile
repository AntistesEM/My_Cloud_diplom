# Для разработки

# FROM node:22.12.0-alpine

# # Set the working directory inside the container
# WORKDIR /frontend

# # Copy package.json and package-lock.json
# COPY package*.json ./

# # Install dependencies
# RUN npm install

# # Copy the rest of your application files
# COPY . .

# # Expose the port your app runs on
# EXPOSE 3000

# # Define the command to run your app
# CMD ["npm", "run", "dev"]
# # CMD ["npm", "run", "dev", "--", "--host"]

# Для продакшена
# Build Stage
FROM node:22.12.0-alpine AS build
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production Stage
FROM nginx:stable-alpine AS production
COPY --from=build /frontend/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# Use Node.js as base image for frontend build
FROM node:18 AS frontend-build

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/ .

# Install dependencies and build
RUN npm install
RUN npm run build

# Use Python as the base image for final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files
COPY . .

# Copy the built frontend from previous stage
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/package*.json ./frontend/

# Install production dependencies for frontend serving
WORKDIR /app/frontend
RUN npm install --production

# Back to app root
WORKDIR /app

# Create a script to run both services
RUN echo '#!/bin/bash\ncd /app/frontend && npm start & \ncd /app && python client.py' > /app/start.sh
RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 3000
EXPOSE 7777

# Set environment variable for uvicorn to work in container
ENV PYTHONUNBUFFERED=1

# Start both services
CMD ["/app/start.sh"]
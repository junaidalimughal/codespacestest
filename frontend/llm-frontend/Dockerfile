# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in package.json
RUN npm install

# Build the app for production to the build folder
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Command to run the app
CMD ["serve", "-s", "build", "-l", "3000"]

# Expose the port the app runs on
EXPOSE 3000


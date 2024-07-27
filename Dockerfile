# Use an official Python runtime as a parent image
FROM python:3.12.2

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make sure the build and run scripts are executable
RUN chmod +x build.sh run.sh

# Run the build script
RUN ./build.sh

# Default command to run the simulator
# You can override this when you run the container
ENTRYPOINT ["./run.sh"]

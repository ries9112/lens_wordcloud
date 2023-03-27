# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the application files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8501

# Start the Streamlit application
CMD ["streamlit", "run", "lens_user_word_cloud.py"]

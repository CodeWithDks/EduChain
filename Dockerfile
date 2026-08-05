# 1. Use an official, lightweight Python runtime base image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy only the requirements file first (Leverages Docker caching for fast builds)
COPY requirements.txt .

# 4. Install the Python dependencies inside the container
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code into the container
COPY . .

# 6. Set the PYTHONPATH so python knows where to find the 'educhain' folder
ENV PYTHONPATH=/app

# 7. The command that runs when the container starts (executes your test suite)
CMD ["python", "tests/test_all_features.py"]

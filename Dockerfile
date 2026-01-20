# Use AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies into Lambda task root
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt -t ${LAMBDA_TASK_ROOT}

# Copy application code
COPY app ${LAMBDA_TASK_ROOT}/app
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/lambda_handler.py

# Optional: Copy any additional configuration files if needed
# COPY .env ${LAMBDA_TASK_ROOT}/.env

# Set the Lambda handler entry point
# This tells Lambda which function to invoke
CMD ["lambda_handler.lambda_handler"]

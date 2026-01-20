"""
AWS Lambda Handler for Visitor Management System API
This handler wraps the FastAPI application for Lambda deployment using Mangum
"""

import logging
import os
import json
from mangum import Mangum

# Set production environment for Lambda
os.environ["ENVIRONMENT"] = "production"

from app.main import app

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Mangum handler instance with proper configuration
# Mangum is an ASGI adapter that allows FastAPI to run on AWS Lambda
handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events (startup/shutdown) as Lambda handles this
    api_gateway_base_path="/"  # API Gateway strips /prod, Lambda sees paths starting with /
)

# Lambda handler function - this is the entry point for Lambda
def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event object (API Gateway event)
        context: Lambda context object
        
    Returns:
        API Gateway response
    """
    # Log the full event for debugging
    logger.info(f"Lambda invoked - Request ID: {context.aws_request_id}")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Check if this is an API Gateway event
        if 'requestContext' not in event:
            logger.warning("Event does not contain requestContext - not an API Gateway event")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": '{"error": "Invalid event format"}'
            }
        
        # Log request details
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')
        path = event.get('path') or event.get('rawPath', 'UNKNOWN')
        logger.info(f"Processing request: {http_method} {path}")
        
        # Process the event through Mangum
        response = handler(event, context)
        
        # Log response
        status_code = response.get('statusCode', 'UNKNOWN')
        logger.info(f"Response status: {status_code}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing Lambda event: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e),
                "type": type(e).__name__
            })
        }

"""
AWS Lambda Handler for Visitor Management System API
This handler wraps the FastAPI application for Lambda deployment using Mangum
"""

import logging
from mangum import Mangum
from app.main import app

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Mangum handler instance
# Mangum is an ASGI adapter that allows FastAPI to run on AWS Lambda
handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events (startup/shutdown) as Lambda handles this
    api_gateway_base_path="/"  # Base path for API Gateway
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
    logger.info(f"Lambda event received: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', 'UNKNOWN')}")
    
    try:
        # Process the event through Mangum
        response = handler(event, context)
        logger.info(f"Lambda response status: {response.get('statusCode', 'UNKNOWN')}")
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
            "body": '{"error": "Internal server error", "message": "' + str(e) + '"}'
        }

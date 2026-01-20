"""
Simple test Lambda handler to debug the issue
"""
import json
import os

def lambda_handler(event, context):
    """Ultra simple handler for debugging"""
    
    # Log environment variables
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL", "NOT SET"),
        "JWT_SECRET": os.getenv("JWT_SECRET", "NOT SET")[:10] + "..." if os.getenv("JWT_SECRET") else "NOT SET",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT SET"),
        "PYTHONPATH": os.getenv("PYTHONPATH", "NOT SET"),
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "message": "Debug Lambda Handler",
            "event_path": event.get("path", "unknown"),
            "event_method": event.get("httpMethod", "unknown"),
            "environment_variables": env_vars,
            "event_keys": list(event.keys())
        })
    }

#!/usr/bin/env python3
"""
Test script to verify Bedrock Agent Runtime connection and basic functionality.
"""

import os
import json
import boto3
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_bedrock_connection():
    """Test the Bedrock Agent Runtime connection."""
    try:
        # Initialize the Bedrock Agent Runtime client
        bedrock_agent_runtime = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        logger.info("✅ Bedrock Agent Runtime client initialized successfully")
        
        # Test with a sample agent ID (you'll need to replace this with a real one)
        test_agent_id = os.getenv('KYC_COORDINATOR_AGENT_ID')
        
        if not test_agent_id:
            logger.warning("⚠️  No agent ID configured. Please set KYC_COORDINATOR_AGENT_ID in your .env file")
            return False
        
        logger.info(f"Testing with agent ID: {test_agent_id}")
        
        # Prepare test input
        test_input = {
            "input": {
                "customer_data": {
                    "name": "Test Customer",
                    "customer_id": "TEST001",
                    "documents": {
                        "id_proof": "test_passport",
                        "address_proof": "test_utility_bill",
                        "employment_proof": "test_salary_slip"
                    }
                },
                "timestamp": "2024-03-20T10:00:00Z"
            }
        }
        
        input_body = json.dumps(test_input)
        
        logger.info("Attempting to invoke Bedrock agent...")
        
        # Try to invoke the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=test_agent_id,
            agentAliasId='TSTALIASID',
            sessionId='test_session_001',
            inputText=input_body
        )
        
        # Handle the EventStream response
        response_body = ""
        try:
            # Iterate through the event stream to collect the response
            for event in response:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        # Decode the bytes to get the text
                        chunk_text = chunk['bytes'].decode('utf-8')
                        response_body += chunk_text
                    elif 'text' in chunk:
                        response_body += chunk['text']
        except Exception as stream_error:
            logger.warning(f"Error processing event stream: {stream_error}")
            # Fallback: try to get completion directly
            if hasattr(response, 'completion'):
                response_body = response.completion
            else:
                response_body = str(response)
        
        logger.info("✅ Agent invocation successful!")
        logger.info(f"Response: {response_body}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing Bedrock connection: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Provide helpful debugging information
        if "NoSuchAgent" in str(e):
            logger.error("This error suggests the agent ID is incorrect or the agent doesn't exist")
        elif "AccessDenied" in str(e):
            logger.error("This error suggests insufficient permissions to access Bedrock")
        elif "InvalidParameter" in str(e):
            logger.error("This error suggests invalid parameters in the API call")
        
        return False

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID', 
        'AWS_SECRET_ACCESS_KEY',
        'KYC_COORDINATOR_AGENT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def main():
    """Main test function."""
    print("=== Bedrock Agent Runtime Connection Test ===\n")
    
    # Check environment
    if not check_environment():
        return
    
    # Test connection
    success = test_bedrock_connection()
    
    if success:
        print("\n✅ All tests passed! Bedrock Agent Runtime is working correctly.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 
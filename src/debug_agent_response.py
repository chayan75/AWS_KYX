#!/usr/bin/env python3
"""
Debug script to test different input formats for Bedrock agents.
Fixed version with proper response handling.
"""

import os
import json
import boto3
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_agent_with_different_inputs():
    """Test an agent with different input formats to see what works."""
    
    # Initialize the Bedrock Agent Runtime client
    bedrock_agent_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    test_agent_id = os.getenv('KYC_COORDINATOR_AGENT_ID')
    
    if not test_agent_id:
        logger.error("No agent ID configured")
        return
    
    # Test different input formats
    test_inputs = [
        {
            "name": "JSON Object Input",
            "input": json.dumps({
                "customer_data": {
                    "name": "John Smith",
                    "customer_id": "TEST001",
                    "documents": {
                        "id_proof": "US_Passport_123456",
                        "address_proof": "Utility_Bill_789",
                        "employment_proof": "Salary_Slip_456"
                    }
                }
            })
        },
        {
            "name": "Simple Text Input",
            "input": "Hello, I need help with KYC processing for customer John Smith."
        },
        {
            "name": "Structured Text Input", 
            "input": """
Customer: John Smith
ID: TEST001
Documents: Passport, Utility Bill, Salary Slip
Please process this KYC request.
"""
        },
        {
            "name": "Direct Question",
            "input": "What is your role in KYC processing?"
        },
        {
            "name": "Task Delegation Request",
            "input": "I need to validate documents and perform risk analysis for a new customer. Please coordinate the necessary agents."
        }
    ]
    
    for i, test_case in enumerate(test_inputs, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            print(f"Input: {repr(test_case['input'])}")
            
            response = bedrock_agent_runtime.invoke_agent(
                agentId=test_agent_id,
                agentAliasId='TSTALIASID',
                sessionId=f'debug_session_{i}',
                inputText=test_case['input']
            )
            
            # Process the streaming response correctly
            response_body = ""
            event_count = 0
            
            print("Processing response stream...")
            
            # The response is a streaming response - iterate through the EventStream
            if 'completion' in response:
                for event in response['completion']:
                    event_count += 1
                    print(f"  Event {event_count}: {list(event.keys())}")
                    
                    # Handle different event types
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            chunk_text = chunk['bytes'].decode('utf-8')
                            response_body += chunk_text
                            print(f"    Chunk bytes: {repr(chunk_text)}")
                        elif 'attribution' in chunk:
                            print(f"    Attribution: {chunk['attribution']}")
                    
                    elif 'trace' in event:
                        trace = event['trace']
                        print(f"    Trace: {trace}")
                        
                    elif 'returnControl' in event:
                        return_control = event['returnControl']
                        print(f"    Return Control: {return_control}")
                        
                    elif 'internalServerException' in event:
                        error = event['internalServerException']
                        print(f"    Internal Server Exception: {error}")
                        
                    elif 'validationException' in event:
                        error = event['validationException']
                        print(f"    Validation Exception: {error}")
                        
                    elif 'resourceNotFoundException' in event:
                        error = event['resourceNotFoundException']
                        print(f"    Resource Not Found Exception: {error}")
                        
                    elif 'accessDeniedException' in event:
                        error = event['accessDeniedException']
                        print(f"    Access Denied Exception: {error}")
                        
                    elif 'conflictException' in event:
                        error = event['conflictException']
                        print(f"    Conflict Exception: {error}")
                        
                    elif 'dependencyFailedException' in event:
                        error = event['dependencyFailedException']
                        print(f"    Dependency Failed Exception: {error}")
                        
                    elif 'badGatewayException' in event:
                        error = event['badGatewayException']
                        print(f"    Bad Gateway Exception: {error}")
                        
                    elif 'throttlingException' in event:
                        error = event['throttlingException']
                        print(f"    Throttling Exception: {error}")
                        
                    elif 'serviceQuotaExceededException' in event:
                        error = event['serviceQuotaExceededException']
                        print(f"    Service Quota Exceeded Exception: {error}")
                        
                    else:
                        print(f"    Unknown event type: {event}")
            
            print(f"\nTotal events processed: {event_count}")
            print(f"Response body length: {len(response_body)}")
            print(f"Response body: {repr(response_body)}")
            
            if response_body.strip():
                print("✅ SUCCESS: Agent returned content")
                print(f"Final Response:\n{response_body}")
            else:
                print("❌ FAILURE: Agent returned empty response")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            logger.exception("Full error details:")

def test_simple_invoke():
    """Test with a very simple invoke to isolate issues."""
    
    bedrock_agent_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    test_agent_id = os.getenv('KYC_COORDINATOR_AGENT_ID')
    
    print("\n" + "="*60)
    print("SIMPLE INVOKE TEST")
    print("="*60)
    
    try:
        print("Making simple invoke_agent call...")
        
        response = bedrock_agent_runtime.invoke_agent(
            agentId=test_agent_id,
            agentAliasId='TSTALIASID',
            sessionId='simple_test_session',
            inputText='Hello, what can you help me with?'
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys())}")
        
        # Check if we have the expected structure
        if 'completion' in response:
            print("✅ Found 'completion' in response")
            completion = response['completion']
            print(f"Completion type: {type(completion)}")
            
            # Try to read the stream
            full_response = ""
            for event in completion:
                print(f"Event keys: {list(event.keys())}")
                if 'chunk' in event and 'bytes' in event['chunk']:
                    chunk_text = event['chunk']['bytes'].decode('utf-8')
                    full_response += chunk_text
                    print(f"Chunk: {repr(chunk_text)}")
            
            print(f"Full response: {repr(full_response)}")
            
        else:
            print("❌ No 'completion' found in response")
            print("Available keys:", list(response.keys()))
            
    except Exception as e:
        print(f"❌ ERROR in simple invoke: {str(e)}")
        logger.exception("Full error details:")

def test_list_agents():
    """Test listing agents to verify connection."""
    
    bedrock_agent = boto3.client(
        service_name='bedrock-agent',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    print("\n" + "="*60)
    print("AGENT LIST TEST")
    print("="*60)
    
    try:
        response = bedrock_agent.list_agents()
        agents = response.get('agentSummaries', [])
        
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent.get('agentName', 'Unknown')} (ID: {agent.get('agentId', 'Unknown')})")
            print(f"    Status: {agent.get('agentStatus', 'Unknown')}")
            
        # Check if our test agent exists
        test_agent_id = os.getenv('KYC_COORDINATOR_AGENT_ID')
        if test_agent_id:
            matching_agents = [a for a in agents if a.get('agentId') == test_agent_id]
            if matching_agents:
                print(f"✅ Found test agent: {matching_agents[0]}")
            else:
                print(f"❌ Test agent {test_agent_id} not found in list")
        
    except Exception as e:
        print(f"❌ ERROR listing agents: {str(e)}")
        logger.exception("Full error details:")

def main():
    """Main function."""
    print("=== Bedrock Agent Response Debug (Fixed Version) ===\n")
    
    # Check environment
    required_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'KYC_COORDINATOR_AGENT_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return
    
    print("✅ Environment variables configured")
    print(f"Agent ID: {os.getenv('KYC_COORDINATOR_AGENT_ID')}")
    print(f"Region: {os.getenv('AWS_REGION')}")
    
    # Test basic connectivity first
    test_list_agents()
    
    # Test simple invoke
    test_simple_invoke()
    
    # Run full tests
    test_agent_with_different_inputs()
    
    print(f"\n{'='*60}")
    print("DEBUG COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
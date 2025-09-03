#!/usr/bin/env python3
"""
Test script to verify KYC agents provide actual analysis instead of generic responses.
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

def test_risk_analysis_agent():
    """Test the risk analysis agent with specific KYC data."""
    
    bedrock_agent_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    risk_agent_id = os.getenv('RISK_ANALYSIS_AGENT_ID')
    
    if not risk_agent_id:
        logger.error("No risk analysis agent ID configured")
        return
    
    # Test case 1: High-risk PEP customer
    pep_customer = {
        "name": "Dr. Maria Rodriguez",
        "customer_id": "CUST003",
        "dob": "1975-03-20",
        "nationality": "Spain",
        "address": "45 Diplomat Ave, Madrid, Spain",
        "occupation": "Government Official",
        "position": "Deputy Minister of Finance",
        "annual_income": 250000,
        "source_of_funds": "government_salary",
        "pep_status": True,
        "documents": {
            "id_proof": "Spanish_Passport_789",
            "address_proof": "Government_ID_456",
            "employment_proof": "Ministry_Letter_123"
        }
    }
    
    print("="*80)
    print("TESTING RISK ANALYSIS AGENT - PEP CUSTOMER")
    print("="*80)
    
    # Create specific input for risk analysis
    risk_input = f"""
KYC Risk Analysis Request

Customer Information:
- Name: {pep_customer['name']}
- Customer ID: {pep_customer['customer_id']}
- Date of Birth: {pep_customer['dob']}
- Nationality: {pep_customer['nationality']}
- Address: {pep_customer['address']}
- Occupation: {pep_customer['occupation']}
- Position: {pep_customer['position']}
- Annual Income: {pep_customer['annual_income']}
- Source of Funds: {pep_customer['source_of_funds']}
- PEP Status: {pep_customer['pep_status']}

Documents Provided:
{json.dumps(pep_customer['documents'], indent=2)}

Please perform a comprehensive risk analysis for this customer and provide your assessment in the following JSON format:

{{
  "risk_classification": "Low|Medium|High",
  "risk_score": 0-100,
  "risk_factors": ["factor1", "factor2", ...],
  "recommendations": ["recommendation1", "recommendation2", ...],
  "requires_edd": true/false,
  "analysis_details": "Detailed risk analysis"
}}

Analyze the customer based on:
1. Geographic risk (country of residence/nationality)
2. Source of funds and income stability
3. Occupation and business type
4. PEP status and political exposure
5. Document completeness and validity
6. Transaction patterns and volumes
7. Any other relevant risk indicators

Provide a detailed risk assessment with specific reasoning.
"""
    
    try:
        print("Sending request to risk analysis agent...")
        
        response = bedrock_agent_runtime.invoke_agent(
            agentId=risk_agent_id,
            agentAliasId='TSTALIASID',
            sessionId='test_pep_risk_analysis',
            inputText=risk_input
        )
        
        # Process the response
        response_body = ""
        if 'completion' in response:
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        chunk_text = chunk['bytes'].decode('utf-8')
                        response_body += chunk_text
        
        print(f"\nAgent Response:")
        print(f"Length: {len(response_body)}")
        print(f"Content: {response_body}")
        
        # Try to parse as JSON
        try:
            result = json.loads(response_body)
            print(f"\n✅ Parsed JSON Response:")
            print(json.dumps(result, indent=2))
            
            # Check if it's a proper risk analysis
            if 'risk_classification' in result and 'risk_score' in result:
                print(f"\n✅ VALID RISK ANALYSIS RECEIVED!")
                print(f"Risk Level: {result['risk_classification']}")
                print(f"Risk Score: {result['risk_score']}")
            else:
                print(f"\n❌ Response missing required risk analysis fields")
                
        except json.JSONDecodeError:
            print(f"\n❌ Response is not valid JSON")
            print(f"Raw response: {repr(response_body)}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        logger.exception("Full error details:")

def test_document_validation_agent():
    """Test the document validation agent."""
    
    bedrock_agent_runtime = boto3.client(
        service_name='bedrock-agent-runtime',
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    validation_agent_id = os.getenv('DOCUMENT_VALIDATION_AGENT_ID')
    
    if not validation_agent_id:
        logger.error("No document validation agent ID configured")
        return
    
    print("\n" + "="*80)
    print("TESTING DOCUMENT VALIDATION AGENT")
    print("="*80)
    
    validation_input = """
Document Validation Request

Customer: John Smith (CUST001)
Documents to validate:
- ID Proof: US_Passport_123456
- Address Proof: Utility_Bill_789  
- Employment Proof: Salary_Slip_456

Please validate these documents and provide your assessment in JSON format:

{
  "validation_status": "complete|incomplete|error",
  "missing_fields": ["field1", "field2"],
  "invalid_fields": ["field1", "field2"],
  "validation_report": "Detailed validation report",
  "next_actions": ["action1", "action2"]
}

Check for:
1. Document completeness
2. Document validity and authenticity
3. Required information presence
4. Document expiration dates
5. Consistency across documents
"""
    
    try:
        print("Sending request to document validation agent...")
        
        response = bedrock_agent_runtime.invoke_agent(
            agentId=validation_agent_id,
            agentAliasId='TSTALIASID',
            sessionId='test_document_validation',
            inputText=validation_input
        )
        
        # Process the response
        response_body = ""
        if 'completion' in response:
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        chunk_text = chunk['bytes'].decode('utf-8')
                        response_body += chunk_text
        
        print(f"\nAgent Response:")
        print(f"Length: {len(response_body)}")
        print(f"Content: {response_body}")
        
        # Try to parse as JSON
        try:
            result = json.loads(response_body)
            print(f"\n✅ Parsed JSON Response:")
            print(json.dumps(result, indent=2))
            
            if 'validation_status' in result:
                print(f"\n✅ VALID DOCUMENT VALIDATION RECEIVED!")
                print(f"Status: {result['validation_status']}")
            else:
                print(f"\n❌ Response missing required validation fields")
                
        except json.JSONDecodeError:
            print(f"\n❌ Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        logger.exception("Full error details:")

def main():
    """Main function."""
    print("=== KYC Agent Analysis Test ===\n")
    
    # Check environment
    required_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return
    
    print("✅ Environment variables configured")
    
    # Test risk analysis agent
    test_risk_analysis_agent()
    
    # Test document validation agent
    test_document_validation_agent()
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 
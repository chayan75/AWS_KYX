#!/usr/bin/env python3
"""
Test script for LLM-based validation integration with API server.
"""

import sys
import os
import json
import requests

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

def test_llm_validation_api():
    """Test the LLM-based validation through the API endpoint."""
    print("=== Testing LLM-Based Validation API Integration ===\n")
    
    # Test cases for API validation
    test_cases = [
        {
            "name": "Name Matching - Nickname via API",
            "extracted_data": {
                "first_name": "bill",
                "last_name": "johnson",
                "dob": "1985-03-15",
                "nationality": "US"
            },
            "user_data": {
                "name": "William Johnson",
                "email": "bill.johnson@email.com",
                "phone": "+1-555-0101",
                "address": "123 Main Street, New York, NY 10001"
            },
            "document_type": "id_proof",
            "expected_match": True,
            "description": "William vs Bill (nickname) via API"
        },
        {
            "name": "Address Matching - Abbreviation via API",
            "extracted_data": {
                "full_address": "123 Main St, New York, NY 10001",
                "account_holder_name": "William Johnson"
            },
            "user_data": {
                "name": "William Johnson",
                "email": "bill.johnson@email.com",
                "phone": "+1-555-0101",
                "address": "123 Main Street, New York, NY 10001"
            },
            "document_type": "address_proof",
            "expected_match": True,
            "description": "St vs Street (address abbreviation) via API"
        },
        {
            "name": "Complete Mismatch via API",
            "extracted_data": {
                "first_name": "jane",
                "last_name": "doe",
                "dob": "1985-03-15",
                "nationality": "US"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0102",
                "address": "123 Main Street, New York, NY 10001"
            },
            "document_type": "id_proof",
            "expected_match": False,
            "description": "Completely different names via API"
        }
    ]
    
    api_url = "http://localhost:8000/api/customer/validate-document"
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"🧪 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            # Prepare the request payload
            payload = {
                "extracted_data": test_case['extracted_data'],
                "user_data": test_case['user_data'],
                "document_type": test_case['document_type']
            }
            
            # Make API request
            response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   Overall Match: {result['overall_match']}")
                print(f"   Confidence Score: {result['confidence_score']}%")
                print(f"   Discrepancies: {len(result['discrepancies'])}")
                
                # Check if validation details are available
                if 'validation_details' in result:
                    details = result['validation_details']
                    if 'name_match' in details:
                        name_match = details['name_match']
                        print(f"   Name Match: {name_match.get('matches', 'N/A')} (confidence: {name_match.get('confidence', 'N/A')}%)")
                        if 'reason' in name_match:
                            print(f"   Name Reason: {name_match['reason']}")
                    
                    if 'address_match' in details:
                        address_match = details['address_match']
                        print(f"   Address Match: {address_match.get('matches', 'N/A')} (confidence: {address_match.get('confidence', 'N/A')}%)")
                        if 'reason' in address_match:
                            print(f"   Address Reason: {address_match['reason']}")
                
                # Check for discrepancies
                if result['discrepancies']:
                    print("   Discrepancy Details:")
                    for disc in result['discrepancies']:
                        print(f"     - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
                        if 'reason' in disc:
                            print(f"       Reason: {disc['reason']}")
                
                # Validate the result
                if result['overall_match'] == test_case['expected_match']:
                    print(f"   ✅ PASSED: Expected {test_case['expected_match']}, got {result['overall_match']}")
                    passed += 1
                else:
                    print(f"   ❌ FAILED: Expected {test_case['expected_match']}, got {result['overall_match']}")
                    failed += 1
                    
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR: Could not connect to API server at {api_url}")
            print(f"   Make sure the API server is running with: python src/api_server.py")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
        
        print("-" * 60)
    
    print(f"\n📊 API Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All API tests passed! LLM-based validation is working correctly via API.")
        return True
    else:
        print("⚠️  Some API tests failed. Please review the implementation.")
        return False

def test_direct_validation():
    """Test direct validation without API."""
    print("\n=== Testing Direct LLM Validation ===\n")
    
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        
        # Test case
        extracted_data = {
            "first_name": "bill",
            "last_name": "johnson",
            "dob": "1985-03-15",
            "nationality": "US"
        }
        
        user_data = {
            "name": "William Johnson",
            "email": "bill.johnson@email.com",
            "phone": "+1-555-0101",
            "address": "123 Main Street, New York, NY 10001"
        }
        
        print("🧪 Testing direct LLM validation...")
        result = processor.validate_document_data(extracted_data, user_data, "id_proof")
        
        print(f"   Overall Match: {result['overall_match']}")
        print(f"   Confidence Score: {result['confidence_score']}%")
        print(f"   Discrepancies: {len(result['discrepancies'])}")
        
        if result['overall_match']:
            print("   ✅ PASSED: Direct validation working correctly")
            return True
        else:
            print("   ❌ FAILED: Direct validation not working as expected")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting LLM-based validation integration tests...\n")
    
    # Check if AWS credentials are available
    if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        sys.exit(1)
    
    # Test direct validation first
    direct_success = test_direct_validation()
    
    # Test API validation
    api_success = test_llm_validation_api()
    
    if direct_success and api_success:
        print("\n🎉 All integration tests passed! LLM-based validation is working correctly.")
    else:
        print("\n⚠️  Some integration tests failed. Please review the implementation.") 
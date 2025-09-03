#!/usr/bin/env python3
"""
Test script for LLM-based document validation functionality.
Tests name and address matching using LLM for better accuracy.
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from document_processor import DocumentProcessor

def test_llm_validation():
    """Test the LLM-based validation functionality."""
    print("=== Testing LLM-Based Document Validation ===\n")
    
    processor = DocumentProcessor()
    
    # Test cases for different scenarios
    test_cases = [
        {
            "name": "Name Matching - Nickname",
            "document_type": "id_proof",
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
            "expected_match": True,
            "description": "William vs Bill (nickname)"
        },
        {
            "name": "Name Matching - Name Variation",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "jon",
                "last_name": "smith",
                "dob": "1990-05-15",
                "nationality": "US"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0102",
                "address": "456 Oak Avenue, Los Angeles, CA 90210"
            },
            "expected_match": True,
            "description": "John vs Jon (name variation)"
        },
        {
            "name": "Address Matching - Abbreviation",
            "document_type": "address_proof",
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
            "expected_match": True,
            "description": "St vs Street (address abbreviation)"
        },
        {
            "name": "Address Matching - Different Address",
            "document_type": "address_proof",
            "extracted_data": {
                "full_address": "456 Oak Avenue, Los Angeles, CA 90210",
                "account_holder_name": "John Smith"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0102",
                "address": "123 Main Street, New York, NY 10001"
            },
            "expected_match": False,
            "description": "Different addresses (should not match)"
        },
        {
            "name": "Employment Matching - Business Abbreviation",
            "document_type": "employment_proof",
            "extracted_data": {
                "employer_name": "Tech Corp",
                "employee_name": "William Johnson",
                "position": "Software Engineer"
            },
            "user_data": {
                "name": "William Johnson",
                "email": "bill.johnson@email.com",
                "phone": "+1-555-0101",
                "address": "123 Main Street, New York, NY 10001",
                "employer": "Tech Corporation",
                "occupation": "Software Engineer"
            },
            "expected_match": True,
            "description": "Corp vs Corporation (business abbreviation)"
        },
        {
            "name": "Complete Mismatch",
            "document_type": "id_proof",
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
            "expected_match": False,
            "description": "Completely different names (should not match)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"🧪 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            # Perform LLM-based validation
            result = processor.validate_document_data(
                test_case['extracted_data'],
                test_case['user_data'],
                test_case['document_type']
            )
            
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
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            failed += 1
        
        print("-" * 60)
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! LLM-based validation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

def test_llm_validation_edge_cases():
    """Test edge cases for LLM validation."""
    print("\n=== Testing LLM Validation Edge Cases ===\n")
    
    processor = DocumentProcessor()
    
    edge_cases = [
        {
            "name": "Empty Data",
            "document_type": "id_proof",
            "extracted_data": {},
            "user_data": {},
            "description": "Empty data should not crash"
        },
        {
            "name": "Partial Data",
            "document_type": "id_proof",
            "extracted_data": {"first_name": "john"},
            "user_data": {"name": "John Smith"},
            "description": "Partial data should be handled gracefully"
        },
        {
            "name": "Special Characters",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "maría",
                "last_name": "rodríguez"
            },
            "user_data": {
                "name": "Maria Rodriguez"
            },
            "description": "Special characters and accents"
        }
    ]
    
    for case in edge_cases:
        print(f"🧪 Testing: {case['name']}")
        print(f"   Description: {case['description']}")
        
        try:
            result = processor.validate_document_data(
                case['extracted_data'],
                case['user_data'],
                case['document_type']
            )
            
            print(f"   Result: {result['overall_match']} (confidence: {result['confidence_score']}%)")
            print(f"   ✅ PASSED: No errors occurred")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        print("-" * 40)

def test_llm_response_parsing():
    """Test LLM response parsing functionality."""
    print("\n=== Testing LLM Response Parsing ===\n")
    
    processor = DocumentProcessor()
    
    # Test valid JSON response
    valid_response = {
        "content": [
            {
                "text": '''
                {
                    "overall_match": true,
                    "confidence_score": 85,
                    "discrepancies": [],
                    "warnings": [],
                    "validation_details": {
                        "name_match": {
                            "matches": true,
                            "confidence": 90,
                            "reason": "Names match with nickname variation"
                        }
                    }
                }
                '''
            }
        ]
    }
    
    try:
        result = processor._parse_llm_validation_response(valid_response)
        print(f"✅ Valid JSON parsing: {result['overall_match']} (confidence: {result['confidence_score']}%)")
    except Exception as e:
        print(f"❌ Valid JSON parsing failed: {str(e)}")
    
    # Test invalid JSON response
    invalid_response = {
        "content": [
            {
                "text": "This is not valid JSON"
            }
        ]
    }
    
    try:
        result = processor._parse_llm_validation_response(invalid_response)
        print(f"❌ Invalid JSON should have failed but didn't")
    except Exception as e:
        print(f"✅ Invalid JSON correctly rejected: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting LLM-based validation tests...\n")
    
    # Check if AWS credentials are available
    if not os.getenv('AWS_ACCESS_KEY_ID') or not os.getenv('AWS_SECRET_ACCESS_KEY'):
        print("❌ AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        sys.exit(1)
    
    success = test_llm_validation()
    test_llm_validation_edge_cases()
    test_llm_response_parsing()
    
    if success:
        print("\n🎉 LLM-based validation is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.") 
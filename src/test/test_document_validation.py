#!/usr/bin/env python3
"""
Test script for document validation functionality.
"""

import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from document_processor import DocumentProcessor

def test_document_validation():
    """Test the document validation functionality."""
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Test data
    test_cases = [
        {
            "name": "ID Proof Validation - Matching Names",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "John",
                "last_name": "Smith",
                "dob": "1990-05-15",
                "nationality": "British"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "1234567890",
                "address": "123 Main St, London"
            },
            "expected_match": True
        },
        {
            "name": "ID Proof Validation - Mismatched Names",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "John",
                "last_name": "Smith",
                "dob": "1990-05-15",
                "nationality": "British"
            },
            "user_data": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "1234567890",
                "address": "123 Main St, London"
            },
            "expected_match": False
        },
        {
            "name": "Address Proof Validation - Matching Address",
            "document_type": "address_proof",
            "extracted_data": {
                "full_address": "123 Main Street, London, UK",
                "document_type": "utility_bill",
                "account_holder_name": "John Smith"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "1234567890",
                "address": "123 Main Street, London"
            },
            "expected_match": True
        },
        {
            "name": "Address Proof Validation - Mismatched Address",
            "document_type": "address_proof",
            "extracted_data": {
                "full_address": "456 Oak Avenue, Manchester, UK",
                "document_type": "utility_bill",
                "account_holder_name": "John Smith"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "1234567890",
                "address": "123 Main Street, London"
            },
            "expected_match": False
        },
        {
            "name": "Employment Proof Validation - Matching Employer",
            "document_type": "employment_proof",
            "extracted_data": {
                "employer_name": "Tech Corp Ltd",
                "employee_name": "John Smith",
                "position": "Software Engineer"
            },
            "user_data": {
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "1234567890",
                "address": "123 Main Street, London",
                "employer": "Tech Corp Ltd",
                "occupation": "Software Engineer"
            },
            "expected_match": True
        }
    ]
    
    print("🧪 Testing Document Validation Functionality")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Perform validation
            result = processor.validate_document_data(
                test_case["extracted_data"],
                test_case["user_data"],
                test_case["document_type"]
            )
            
            # Check results
            actual_match = result["overall_match"]
            expected_match = test_case["expected_match"]
            
            print(f"✅ Overall Match: {actual_match}")
            print(f"📊 Confidence Score: {result['confidence_score']}%")
            
            if result["discrepancies"]:
                print(f"⚠️  Discrepancies Found: {len(result['discrepancies'])}")
                for disc in result["discrepancies"]:
                    print(f"   - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
            
            if result["warnings"]:
                print(f"🔔 Warnings: {len(result['warnings'])}")
                for warning in result["warnings"]:
                    print(f"   - {warning.get('message', warning)}")
            
            # Check if test passed
            if actual_match == expected_match:
                print(f"✅ PASS: Expected {expected_match}, got {actual_match}")
                passed += 1
            else:
                print(f"❌ FAIL: Expected {expected_match}, got {actual_match}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Document validation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the validation logic.")
        return False

def test_fuzzy_matching():
    """Test the fuzzy matching functionality."""
    
    processor = DocumentProcessor()
    
    test_cases = [
        ("John Smith", "John Smith", True),
        ("John Smith", "john smith", True),
        ("John Smith", "John S. Smith", True),
        ("John Smith", "Jane Doe", False),
        ("123 Main St", "123 Main Street", True),
        ("Tech Corp Ltd", "Tech Corporation Limited", True),
        ("Software Engineer", "Software Developer", True),
    ]
    
    print("\n🧪 Testing Fuzzy Matching")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    for str1, str2, expected in test_cases:
        result = processor._fuzzy_match(str1, str2)
        if result == expected:
            print(f"✅ '{str1}' vs '{str2}': {result} (expected {expected})")
            passed += 1
        else:
            print(f"❌ '{str1}' vs '{str2}': {result} (expected {expected})")
            failed += 1
    
    print(f"\n📊 Fuzzy Matching Results: {passed} passed, {failed} failed")
    return failed == 0

def test_customer_portal_validation():
    """Test document validation as used by the customer portal."""
    print("\n=== Testing Customer Portal Validation ===")
    
    # Test data that would be entered by customer
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001"
    }
    
    # Test ID proof validation
    print("\n--- Testing ID Proof Validation ---")
    id_proof_data = {
        "first_name": "jane",  # Mismatched name
        "last_name": "doe",    # Mismatched name
        "dob": "1985-03-15",
        "nationality": "US"
    }
    
    result = processor.validate_document_data(id_proof_data, customer_data, "id_proof")
    print(f"ID Proof Validation Result:")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    for disc in result['discrepancies']:
        print(f"    - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
    
    # Test address proof validation
    print("\n--- Testing Address Proof Validation ---")
    address_proof_data = {
        "full_address": "456 Oak Avenue, Los Angeles, CA 90210",  # Mismatched address
        "account_holder_name": "John Smith"
    }
    
    result = processor.validate_document_data(address_proof_data, customer_data, "address_proof")
    print(f"Address Proof Validation Result:")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    for disc in result['discrepancies']:
        print(f"    - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
    
    # Test employment proof validation
    print("\n--- Testing Employment Proof Validation ---")
    employment_proof_data = {
        "employer_name": "Tech Corp",
        "employee_name": "John Smith",
        "position": "Software Engineer"
    }
    
    result = processor.validate_document_data(employment_proof_data, customer_data, "employment_proof")
    print(f"Employment Proof Validation Result:")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    for disc in result['discrepancies']:
        print(f"    - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Document Validation Tests")
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Run tests
    validation_success = test_document_validation()
    portal_validation_success = test_customer_portal_validation()
    
    if validation_success and portal_validation_success:
        print("\n🎉 All document validation tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some document validation tests failed!")
        sys.exit(1) 
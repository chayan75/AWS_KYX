#!/usr/bin/env python3
"""
Test script for customer submission with limited data from customer portal.
"""

import json
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from main import KYCProcessor
from database import KYCCase
from database import db_manager
from document_processor import DocumentProcessor

def test_customer_submission_with_limited_data():
    """Test customer submission with only basic data (name, email, phone, address)."""
    
    # Initialize KYC processor
    processor = KYCProcessor()
    
    # Test data that matches what the customer portal sends
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1234567890",
        "address": "123 Main Street, New York, NY 10001",
        "documents": {
            "id_proof": "test_id_123",
            "address_proof": "test_address_456",
            "employment_proof": "test_employment_789"
        }
    }
    
    print("🧪 Testing Customer Submission with Limited Data")
    print("=" * 60)
    print(f"Customer Data: {json.dumps(customer_data, indent=2)}")
    print("-" * 60)
    
    try:
        # Test the submission
        result = processor.process_customer_submission(customer_data)
        
        print(f"✅ Submission Result: {result['status']}")
        
        if result['status'] == 'success':
            print(f"📋 Customer ID: {result['customer_id']}")
            print(f"📋 Case ID: {result['case_id']}")
            print(f"📋 Final Status: {result['final_status']}")
            print(f"📋 Risk Level: {result['risk_level']}")
            print("🎉 Customer submission test passed!")
            return True
        else:
            print(f"❌ Submission failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during submission: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_document_validation_with_limited_data():
    """Test document validation with limited customer data."""
    
    processor = DocumentProcessor()
    
    # Test data that matches what the customer portal sends
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1234567890",
        "address": "123 Main Street, New York, NY 10001"
    }
    
    # Mock extracted data from documents
    test_cases = [
        {
            "name": "ID Proof - Matching Name",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "John",
                "last_name": "Smith",
                "dob": "1990-05-15",
                "nationality": "US"
            },
            "expected_match": True
        },
        {
            "name": "ID Proof - Mismatched Name",
            "document_type": "id_proof",
            "extracted_data": {
                "first_name": "Jane",
                "last_name": "Doe",
                "dob": "1990-05-15",
                "nationality": "US"
            },
            "expected_match": False
        },
        {
            "name": "Address Proof - Matching Address",
            "document_type": "address_proof",
            "extracted_data": {
                "full_address": "123 Main Street, New York, NY 10001",
                "document_type": "utility_bill",
                "account_holder_name": "John Smith"
            },
            "expected_match": True
        },
        {
            "name": "Address Proof - Mismatched Address",
            "document_type": "address_proof",
            "extracted_data": {
                "full_address": "456 Oak Avenue, Los Angeles, CA 90210",
                "document_type": "utility_bill",
                "account_holder_name": "John Smith"
            },
            "expected_match": False
        }
    ]
    
    print("\n🧪 Testing Document Validation with Limited Customer Data")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print("-" * 40)
        
        try:
            result = processor.validate_document_data(
                test_case["extracted_data"],
                customer_data,
                test_case["document_type"]
            )
            
            actual_match = result["overall_match"]
            expected_match = test_case["expected_match"]
            
            print(f"✅ Overall Match: {actual_match}")
            print(f"📊 Confidence Score: {result['confidence_score']}%")
            
            if result["discrepancies"]:
                print(f"⚠️  Discrepancies Found: {len(result['discrepancies'])}")
                for disc in result["discrepancies"]:
                    print(f"   - {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}' (severity: {disc['severity']})")
            
            if actual_match == expected_match:
                print(f"✅ PASS: Expected {expected_match}, got {actual_match}")
                passed += 1
            else:
                print(f"❌ FAIL: Expected {expected_match}, got {actual_match}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
    
    print(f"\n📊 Validation Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_multiple_customer_submissions():
    """Test that multiple customer submissions get different customer IDs."""
    print("\n=== Testing Multiple Customer Submissions ===")
    
    # Create processor instance
    processor = KYCProcessor()
    
    # Create multiple different customer submissions
    customers = [
        {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0101",
            "address": "123 Main St, New York, NY 10001",
            "dob": "1985-03-15",
            "nationality": "US",
            "occupation": "Software Engineer",
            "employer": "Tech Corp",
            "annual_income": 85000,
            "source_of_funds": "Employment",
            "pep_status": False
        },
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "+1-555-0102",
            "address": "456 Oak Ave, Los Angeles, CA 90210",
            "dob": "1990-07-22",
            "nationality": "US",
            "occupation": "Marketing Manager",
            "employer": "Marketing Inc",
            "annual_income": 75000,
            "source_of_funds": "Employment",
            "pep_status": False
        },
        {
            "name": "Maria Garcia",
            "email": "maria.garcia@email.com",
            "phone": "+1-555-0103",
            "address": "789 Pine St, Miami, FL 33101",
            "dob": "1988-11-08",
            "nationality": "US",
            "occupation": "Financial Analyst",
            "employer": "Finance Corp",
            "annual_income": 90000,
            "source_of_funds": "Employment",
            "pep_status": False
        }
    ]
    
    customer_ids = []
    
    for i, customer_data in enumerate(customers, 1):
        print(f"\n--- Processing Customer {i}: {customer_data['name']} ---")
        
        # Process the customer submission
        result = processor.process_customer_submission(customer_data)
        
        print(f"Result: {result}")
        
        if result['status'] == 'success':
            customer_id = result['customer_id']
            customer_ids.append(customer_id)
            print(f"✅ Customer {i} assigned ID: {customer_id}")
        else:
            print(f"❌ Customer {i} failed: {result.get('error', 'Unknown error')}")
    
    # Verify all customer IDs are unique
    unique_ids = set(customer_ids)
    print(f"\n=== Results Summary ===")
    print(f"Total customers processed: {len(customer_ids)}")
    print(f"Unique customer IDs: {len(unique_ids)}")
    print(f"Customer IDs: {customer_ids}")
    
    if len(customer_ids) == len(unique_ids):
        print("✅ All customer IDs are unique!")
    else:
        print("❌ Duplicate customer IDs found!")
        duplicates = [id for id in customer_ids if customer_ids.count(id) > 1]
        print(f"Duplicate IDs: {duplicates}")
    
    return len(customer_ids) == len(unique_ids)

def test_customer_submission_with_validation_warnings():
    """Test that customer submissions with validation warnings create pending cases."""
    print("\n=== Testing Customer Submission with Validation Warnings ===")
    
    # Create processor instance
    processor = KYCProcessor()
    
    # Test customer data with mismatched information
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001",
        "documents": {
            "id_proof": "test_id_mismatch",
            "address_proof": "test_address_mismatch"
        }
    }
    
    print(f"Customer Data: {json.dumps(customer_data, indent=2)}")
    print("=" * 60)
    
    # Process the customer submission
    result = processor.process_customer_submission(customer_data)
    
    print(f"Result: {result}")
    
    if result['status'] == 'success':
        customer_id = result['customer_id']
        case_id = result['case_id']
        
        print(f"✅ Submission Result: {result['status']}")
        print(f"📋 Customer ID: {customer_id}")
        print(f"📋 Case ID: {case_id}")
        print(f"📋 Final Status: {result['final_status']}")
        print(f"📋 Risk Level: {result['risk_level']}")
        
        # Check if the case was created in the database
        session = db_manager.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
            if case:
                print(f"✅ Case found in database")
                print(f"📋 Database Status: {case.status}")
                print(f"📋 Database Risk Level: {case.final_risk_level}")
                print(f"📋 Validation Status: {case.validation_status}")
                
                # Verify that the case has pending status due to validation warnings
                if case.status == "pending" and "validation warning" in (case.validation_status or "").lower():
                    print("✅ Case correctly set to pending status with validation warnings")
                    return True
                else:
                    print("❌ Case not properly set to pending status")
                    return False
            else:
                print("❌ Case not found in database")
                return False
        finally:
            session.close()
    else:
        print(f"❌ Submission failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Customer Portal Integration Tests")
    
    # Test document validation with limited data
    validation_success = test_document_validation_with_limited_data()
    
    # Test customer submission with limited data
    submission_success = test_customer_submission_with_limited_data()
    
    # Test multiple customer submissions
    multiple_submissions_success = test_multiple_customer_submissions()
    
    # Test customer submission with validation warnings
    validation_warnings_success = test_customer_submission_with_validation_warnings()
    
    if validation_success and submission_success and multiple_submissions_success and validation_warnings_success:
        print("\n🎉 All customer portal integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some customer portal integration tests failed!")
        sys.exit(1) 
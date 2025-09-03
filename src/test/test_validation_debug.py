#!/usr/bin/env python3
"""
Debug script to test validation logic step by step.
"""

import json
import sys
from document_processor import document_processor
from database import db_manager
from database import Document as DBDocument

def test_validation_logic():
    """Test the validation logic step by step."""
    print("=== Testing Validation Logic Step by Step ===")
    
    # Test data that should definitely trigger validation warnings
    test_customer_data = {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001"
    }
    
    # Test extracted data that doesn't match
    test_extracted_data = {
        "first_name": "MARIA",
        "last_name": "RODRIGUEZ",
        "dob": "1975-03-20",
        "nationality": "ESPAÑOLA"
    }
    
    print(f"Customer data: {json.dumps(test_customer_data, indent=2)}")
    print(f"Extracted data: {json.dumps(test_extracted_data, indent=2)}")
    
    # Test 1: Direct validation
    print("\n1. Testing direct validation...")
    validation_result = document_processor.validate_document_data(
        test_extracted_data, 
        test_customer_data, 
        "id_proof"
    )
    
    print(f"Validation result: {json.dumps(validation_result, indent=2)}")
    
    if validation_result["overall_match"]:
        print("❌ Validation should have detected mismatches!")
        return False
    else:
        print("✅ Validation correctly detected mismatches!")
    
    # Test 2: Check if documents exist in database
    print("\n2. Checking database for documents...")
    session = db_manager.get_session()
    try:
        documents = session.query(DBDocument).all()
        print(f"Found {len(documents)} documents in database:")
        for doc in documents:
            print(f"  - {doc.document_id}: {doc.document_type} - {doc.validation_status}")
            if doc.extracted_data:
                try:
                    extracted = json.loads(doc.extracted_data)
                    print(f"    Extracted: {extracted.get('first_name', 'N/A')} {extracted.get('last_name', 'N/A')}")
                except:
                    print(f"    Extracted data: {doc.extracted_data[:100]}...")
    finally:
        session.close()
    
    # Test 3: Test validation with real document from database
    print("\n3. Testing validation with real document...")
    session = db_manager.get_session()
    try:
        # Find a document with extracted data
        document = session.query(DBDocument).filter(
            DBDocument.extracted_data.isnot(None)
        ).first()
        
        if document:
            print(f"Using document: {document.document_id} ({document.document_type})")
            try:
                extracted_data = json.loads(document.extracted_data)
                print(f"Extracted data: {json.dumps(extracted_data, indent=2)}")
                
                # Test validation
                validation_result = document_processor.validate_document_data(
                    extracted_data,
                    test_customer_data,
                    document.document_type
                )
                
                print(f"Validation result: {json.dumps(validation_result, indent=2)}")
                
                if not validation_result["overall_match"]:
                    print("✅ Validation detected mismatches with real document!")
                else:
                    print("❌ Validation did not detect mismatches with real document!")
                    
            except Exception as e:
                print(f"Error testing validation: {e}")
        else:
            print("No documents with extracted data found in database")
    finally:
        session.close()
    
    return True

def test_api_validation_flow():
    """Test the API validation flow."""
    print("\n=== Testing API Validation Flow ===")
    
    import requests
    
    # Test the validation endpoint directly
    validation_data = {
        "extracted_data": {
            "first_name": "MARIA",
            "last_name": "RODRIGUEZ",
            "dob": "1975-03-20",
            "nationality": "ESPAÑOLA"
        },
        "user_data": {
            "name": "John Smith",
            "email": "john.smith@email.com",
            "phone": "+1-555-0101",
            "address": "123 Main St, New York, NY 10001"
        },
        "document_type": "id_proof"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/customer/validate-document",
            json=validation_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Validation endpoint response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Validation result: {json.dumps(result, indent=2)}")
            
            if not result.get("overall_match"):
                print("✅ API validation correctly detected mismatches")
                return True
            else:
                print("❌ API validation did not detect mismatches")
                return False
        else:
            print(f"❌ Validation endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API validation: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Validation Debug Tests")
    
    # Test validation logic
    logic_success = test_validation_logic()
    
    # Test API validation flow
    api_success = test_api_validation_flow()
    
    if logic_success and api_success:
        print("\n🎉 All validation debug tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some validation debug tests failed!")
        sys.exit(1) 
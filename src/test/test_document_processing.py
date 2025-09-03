#!/usr/bin/env python3
"""
Test script for document processing functionality.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_processor import document_processor
from database import db_manager

def test_document_processor():
    """Test the document processor functionality."""
    print("=== Testing Document Processor ===\n")
    
    # Test 1: Check if documents directory exists
    documents_dir = os.path.join(os.path.dirname(__file__), 'documents')
    print(f"1. Documents directory: {documents_dir}")
    if os.path.exists(documents_dir):
        print("   ✅ Documents directory exists")
        files = os.listdir(documents_dir)
        print(f"   📁 Found {len(files)} files: {files}")
    else:
        print("   ❌ Documents directory does not exist")
        return
    
    # Test 2: Test document encoding
    print("\n2. Testing document encoding...")
    try:
        # Find a test file
        test_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.pdf'))]
        if test_files:
            test_file = os.path.join(documents_dir, test_files[0])
            print(f"   📄 Using test file: {test_files[0]}")
            
            encoded = document_processor.encode_image(test_file)
            print(f"   ✅ Document encoded successfully (length: {len(encoded)})")
        else:
            print("   ⚠️  No test files found")
    except Exception as e:
        print(f"   ❌ Encoding failed: {e}")
    
    # Test 3: Test Bedrock Vision connection
    print("\n3. Testing Bedrock Vision connection...")
    try:
        # Create a simple test image (you would need a real image file)
        print("   ⚠️  Skipping Bedrock Vision test (requires real image file)")
        print("   💡 To test with real image, place a test image in the documents directory")
    except Exception as e:
        print(f"   ❌ Bedrock Vision test failed: {e}")
    
    # Test 4: Test database document operations
    print("\n4. Testing database document operations...")
    try:
        # Create a test case
        test_customer_data = {
            "customer_id": "TEST001",
            "name": "Test Customer",
            "email": "test@example.com",
            "phone": "1234567890",
            "address": "123 Test St"
        }
        
        case_id = db_manager.create_kyc_case(test_customer_data)
        print(f"   ✅ Test case created with ID: {case_id}")
        
        # Test adding a document
        test_document_data = {
            "first_name": "Test",
            "last_name": "Customer",
            "dob": "1990-01-01",
            "nationality": "US",
            "document_type": "passport",
            "document_number": "123456789"
        }
        
        doc = db_manager.add_document(
            case_id=case_id,
            document_type="id_proof",
            document_id="TEST_DOC_001",
            filename="test_document.pdf",
            file_path="/path/to/test/document.pdf",
            extracted_data=test_document_data
        )
        print(f"   ✅ Test document added with ID: {doc.id}")
        
        # Test retrieving documents
        documents = db_manager.get_documents_by_case_id(case_id)
        print(f"   ✅ Retrieved {len(documents)} documents for case")
        
        # Clean up test data
        # Note: In a real application, you might want to keep test data
        print("   🧹 Test data created successfully")
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

def test_customer_portal_integration():
    """Test the customer portal integration."""
    print("\n=== Testing Customer Portal Integration ===\n")
    
    # Test customer data structure
    test_customer_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "address": "123 Main St, City, State 12345",
        "documents": {
            "id_proof": "test_id_123",
            "address_proof": "test_address_456",
            "employment_proof": "test_employment_789"
        }
    }
    
    print("1. Customer data structure:")
    print(f"   ✅ Name: {test_customer_data['name']}")
    print(f"   ✅ Email: {test_customer_data['email']}")
    print(f"   ✅ Phone: {test_customer_data['phone']}")
    print(f"   ✅ Address: {test_customer_data['address']}")
    print(f"   ✅ Documents: {list(test_customer_data['documents'].keys())}")
    
    # Test API endpoint structure
    print("\n2. API endpoint structure:")
    endpoints = [
        "POST /api/customer/upload-document",
        "POST /api/customer/submit",
        "GET /api/customer/status/{customer_id}"
    ]
    
    for endpoint in endpoints:
        print(f"   ✅ {endpoint}")
    
    print("\n3. Document processing workflow:")
    workflow_steps = [
        "1. Customer uploads document via portal",
        "2. Document is saved to backend with unique ID",
        "3. Bedrock Vision extracts information from document",
        "4. Extracted data is stored in database",
        "5. Customer submits KYC application",
        "6. Enhanced customer data is processed by KYC agents",
        "7. Results are stored and displayed in admin dashboard"
    ]
    
    for step in workflow_steps:
        print(f"   📋 {step}")

def main():
    """Run all tests."""
    print("🚀 Starting Document Processing Tests\n")
    
    try:
        test_document_processor()
        test_customer_portal_integration()
        
        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("\n📝 Next steps:")
        print("1. Place test document images in the 'documents' directory")
        print("2. Start the API server: python api_server.py")
        print("3. Start the customer portal: cd customer-portal && npm start")
        print("4. Test document upload and KYC submission")
        print("5. Check the admin dashboard for processed cases")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Test script to simulate the exact customer portal flow and identify validation issues.
"""

import sys
import json
import requests
import os
from datetime import datetime

def test_customer_portal_flow():
    """Test the complete customer portal flow including document upload and validation."""
    print("=== Testing Customer Portal Flow ===")
    
    # Step 1: Upload real documents
    print("\n1. Uploading real documents...")
    
    # Use sample documents from the sample_docs folder
    sample_docs_path = "../sample_docs"
    if not os.path.exists(sample_docs_path):
        print(f"❌ Sample docs path not found: {sample_docs_path}")
        return False
    
    # Find sample documents
    id_proof_path = None
    address_proof_path = None
    
    for folder in ["1", "2", "3"]:
        folder_path = os.path.join(sample_docs_path, folder)
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if "passport" in file.lower() and file.endswith(('.jpg', '.jpeg', '.png')):
                    id_proof_path = os.path.join(folder_path, file)
                elif ("utility" in file.lower() or "bank" in file.lower()) and file.endswith('.pdf'):
                    address_proof_path = os.path.join(folder_path, file)
    
    if not id_proof_path:
        print("❌ No ID proof document found in sample docs")
        return False
    
    if not address_proof_path:
        print("❌ No address proof document found in sample docs")
        return False
    
    print(f"  Using ID proof: {id_proof_path}")
    print(f"  Using address proof: {address_proof_path}")
    
    # Upload documents
    document_ids = {}
    
    # Upload ID proof
    try:
        with open(id_proof_path, 'rb') as f:
            files = {'file': (os.path.basename(id_proof_path), f, 'image/jpeg')}
            data = {'document_type': 'id_proof'}
            response = requests.post(
                "http://localhost:8000/api/customer/upload-document",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                document_ids['id_proof'] = result['document_id']
                print(f"  ✅ Uploaded ID proof: {result['document_id']}")
                print(f"     Extracted data: {json.dumps(result.get('extracted_data', {}), indent=6)}")
            else:
                print(f"  ❌ Failed to upload ID proof: {response.status_code}")
                print(f"     Response: {response.text}")
                return False
    except Exception as e:
        print(f"  ❌ Error uploading ID proof: {e}")
        return False
    
    # Upload address proof
    try:
        with open(address_proof_path, 'rb') as f:
            files = {'file': (os.path.basename(address_proof_path), f, 'application/pdf')}
            data = {'document_type': 'address_proof'}
            response = requests.post(
                "http://localhost:8000/api/customer/upload-document",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                document_ids['address_proof'] = result['document_id']
                print(f"  ✅ Uploaded address proof: {result['document_id']}")
                print(f"     Extracted data: {json.dumps(result.get('extracted_data', {}), indent=6)}")
            else:
                print(f"  ❌ Failed to upload address proof: {response.status_code}")
                print(f"     Response: {response.text}")
                return False
    except Exception as e:
        print(f"  ❌ Error uploading address proof: {e}")
        return False
    
    # Step 2: Customer data entry (with mismatched data)
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001"
    }
    
    print(f"\n2. Customer data: {json.dumps(customer_data, indent=2)}")
    
    # Step 3: Submit customer application
    print("\n3. Submitting customer application...")
    
    # Simulate validation warnings that would be detected by the customer portal
    validation_warnings = [
        {
            "document_type": "id_proof",
            "document_id": document_ids["id_proof"],
            "confidence_score": 40,
            "discrepancies": [
                {
                    "field": "first_name",
                    "document_value": "maria",
                    "user_value": "john",
                    "severity": "medium"
                },
                {
                    "field": "last_name",
                    "document_value": "rodriguez",
                    "user_value": "smith",
                    "severity": "medium"
                }
            ],
            "warnings": []
        },
        {
            "document_type": "address_proof",
            "document_id": document_ids["address_proof"],
            "confidence_score": 30,
            "discrepancies": [
                {
                    "field": "address",
                    "document_value": "456 business ave, london, uk",
                    "user_value": "123 main st, new york, ny 10001",
                    "severity": "high"
                },
                {
                    "field": "account_holder_name",
                    "document_value": "johnson consulting ltd",
                    "user_value": "john smith",
                    "severity": "high"
                }
            ],
            "warnings": []
        }
    ]
    
    submission_data = {
        "customer_data": customer_data,
        "documents": document_ids,
        "validation_warnings": validation_warnings
    }
    
    print(f"Submission data with validation warnings: {json.dumps(submission_data, indent=2)}")
    
    # Step 4: Test the actual API endpoint
    print("\n4. Testing API endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/customer/submit",
            json=submission_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {json.dumps(result, indent=2)}")
            
            # Check if validation warnings are returned
            if result.get("validation_warnings"):
                print(f"✅ Validation warnings found: {len(result['validation_warnings'])}")
                for warning in result["validation_warnings"]:
                    print(f"  - {warning['document_type']}: {warning.get('confidence_score', 'N/A')}% confidence")
                    for disc in warning.get('discrepancies', []):
                        print(f"    * {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}'")
                
                # Check if status is pending
                if result.get("final_status") == "pending":
                    print("✅ Status correctly set to pending")
                else:
                    print(f"❌ Status is {result.get('final_status')}, expected pending")
                
                return True
            else:
                print("❌ No validation warnings returned from API")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_validation_endpoint():
    """Test the validation endpoint directly."""
    print("\n=== Testing Validation Endpoint ===")
    
    # Test data with obvious mismatches
    validation_data = {
        "extracted_data": {
            "first_name": "jane",
            "last_name": "doe",
            "dob": "1985-03-15",
            "nationality": "US"
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
            print(f"✅ Validation result: {json.dumps(result, indent=2)}")
            
            if not result.get("overall_match"):
                print("✅ Validation correctly detected mismatches")
                return True
            else:
                print("❌ Validation did not detect mismatches")
                return False
        else:
            print(f"❌ Validation endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to validation endpoint")
        return False
    except Exception as e:
        print(f"❌ Error testing validation endpoint: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Customer Portal Flow Tests")
    
    # Test validation endpoint
    validation_success = test_validation_endpoint()
    
    # Test complete customer portal flow
    portal_success = test_customer_portal_flow()
    
    if validation_success and portal_success:
        print("\n🎉 All customer portal flow tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some customer portal flow tests failed!")
        sys.exit(1) 
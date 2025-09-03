#!/usr/bin/env python3
"""
Test script to verify the complete validation flow including API server logic.
"""

import sys
import json
import requests
from main import KYCProcessor
from database import db_manager, KYCCase
from document_processor import DocumentProcessor

def test_api_validation_flow():
    """Test the complete API validation flow."""
    print("=== Testing API Validation Flow ===")
    
    # Step 1: Create test documents with mismatched data
    print("\n1. Creating test documents with mismatched data...")
    
    test_documents = {
        "id_proof": {
            "first_name": "jane",  # Mismatched
            "last_name": "doe",    # Mismatched
            "dob": "1985-03-15",
            "nationality": "US"
        },
        "address_proof": {
            "full_address": "456 Oak Avenue, Los Angeles, CA 90210",  # Mismatched
            "account_holder_name": "John Smith"
        }
    }
    
    # Step 2: Customer data entry
    customer_data = {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main St, New York, NY 10001"
    }
    
    print(f"Customer Data: {json.dumps(customer_data, indent=2)}")
    
    # Step 3: Simulate document validation (API server logic)
    print("\n2. Simulating document validation (API server logic)...")
    
    processor = DocumentProcessor()
    
    validation_warnings = []
    for doc_type, extracted_data in test_documents.items():
        validation_result = processor.validate_document_data(extracted_data, customer_data, doc_type)
        if not validation_result["overall_match"]:
            validation_warnings.append({
                "document_type": doc_type,
                "document_id": f"test_{doc_type}_id",
                "confidence_score": validation_result["confidence_score"],
                "discrepancies": validation_result["discrepancies"],
                "warnings": validation_result["warnings"]
            })
    
    print(f"Validation warnings found: {len(validation_warnings)}")
    for warning in validation_warnings:
        print(f"  - {warning['document_type']}: {warning['confidence_score']}% confidence")
        for disc in warning.get('discrepancies', []):
            print(f"    * {disc['field']}: '{disc['document_value']}' vs '{disc['user_value']}'")
    
    # Step 4: Process customer submission
    print("\n3. Processing customer submission...")
    
    kyc_processor = KYCProcessor()
    
    # Add test documents to customer data
    customer_data["documents"] = {
        "id_proof": "test_id_proof_id",
        "address_proof": "test_address_proof_id"
    }
    
    result = kyc_processor.process_customer_submission(customer_data)
    
    print(f"Submission result: {result}")
    
    if result['status'] == 'success':
        customer_id = result['customer_id']
        case_id = result['case_id']
        
        print(f"✅ Customer ID: {customer_id}")
        print(f"✅ Case ID: {case_id}")
        print(f"✅ Initial Status: {result['final_status']}")
        print(f"✅ Initial Risk Level: {result['risk_level']}")
        
        # Step 5: Apply validation warnings (exact API server logic)
        print("\n4. Applying validation warnings (API server logic)...")
        
        if validation_warnings:
            session = db_manager.get_session()
            try:
                case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
                if case:
                    # Set status to pending for manual review
                    case.status = "pending"
                    case.final_risk_level = "pending"
                    case.completion_time = None  # Remove completion time since it needs manual review
                    
                    # Add validation warnings to case notes
                    validation_note = f"Document Validation Warnings ({datetime.now().strftime('%Y-%m-%d %H:%M')}): "
                    validation_note += f"Found {len(validation_warnings)} document(s) with discrepancies requiring manual review. "
                    
                    for warning in validation_warnings:
                        validation_note += f"{warning['document_type']}: {warning.get('confidence_score', 'N/A')}% confidence. "
                        if warning.get('discrepancies'):
                            for disc in warning['discrepancies']:
                                validation_note += f"{disc['field']} mismatch (doc: {disc['document_value']}, user: {disc['user_value']}). "
                    
                    current_validation = case.validation_status or ""
                    case.validation_status = f"{current_validation}; {validation_note}".strip('; ')
                    session.commit()
                    
                    # Update the result to reflect the pending status
                    result["final_status"] = "pending"
                    result["risk_level"] = "pending"
                    
                    print(f"✅ Case updated to pending status")
                    print(f"📋 Final Database Status: {case.status}")
                    print(f"📋 Final Database Risk Level: {case.final_risk_level}")
                    print(f"📋 Validation Status: {case.validation_status}")
                    
                    # Check if case appears in admin dashboard
                    dashboard_data = db_manager.get_dashboard_data()
                    case_found = any(c['id'] == customer_id for c in dashboard_data.get('cases', []))
                    
                    if case_found:
                        print("✅ Case appears in admin dashboard")
                        
                        # Verify it's in pending status
                        dashboard_case = next(c for c in dashboard_data.get('cases', []) if c['id'] == customer_id)
                        if dashboard_case['status'] == 'pending':
                            print("✅ Case correctly shows as pending in dashboard")
                            
                            # Check if validation warnings are detected by admin UI
                            if "Document Validation Warnings" in (case.validation_status or ""):
                                print("✅ Validation warnings detected in case data")
                                return True
                            else:
                                print("❌ Validation warnings not found in case data")
                                return False
                        else:
                            print(f"❌ Case shows as {dashboard_case['status']} in dashboard, expected pending")
                            return False
                    else:
                        print("❌ Case not found in admin dashboard")
                        return False
                else:
                    print("❌ Case not found in database")
                    return False
            finally:
                session.close()
        else:
            print("❌ No validation warnings found")
            return False
    else:
        print(f"❌ Submission failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    success = test_api_validation_flow()
    
    if success:
        print("\n🎉 API validation flow test passed!")
        sys.exit(0)
    else:
        print("\n❌ API validation flow test failed!")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Test script to verify compliance monitoring agent receives correct input structure.
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main_simulate import KYCProcessor

def test_compliance_agent_input():
    """Test that compliance agent receives proper input structure."""
    print("=== Testing Compliance Agent Input Structure ===\n")
    
    # Initialize the processor
    processor = KYCProcessor()
    
    # Test customer data
    test_customer_data = {
        "customer_id": "CUST001",
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-0123",
        "address": "123 Main St, New York, NY 10001",
        "dob": "1985-06-15",
        "nationality": "US",
        "occupation": "Software Engineer",
        "employer": "Tech Corp",
        "annual_income": 120000,
        "source_of_funds": "employment",
        "documents": {
            "id_proof": "US_Passport_123456",
            "address_proof": "Utility_Bill_789",
            "employment_proof": "Salary_Slip_456"
        }
    }
    
    # Simulate the processing steps to get agent results
    print("1. Simulating Document Validation...")
    doc_validation_result = processor.simulate_document_validation_response(test_customer_data)
    print(f"   Result: {doc_validation_result.get('validation_status', 'unknown')}")
    
    print("\n2. Simulating Risk Analysis...")
    risk_analysis_result = processor.simulate_risk_analysis_response(test_customer_data)
    print(f"   Result: {risk_analysis_result.get('risk_classification', 'unknown')}")
    
    print("\n3. Simulating Sanction Screening...")
    sanction_screening_result = processor.simulate_sanction_screening_response(test_customer_data)
    print(f"   Result: {sanction_screening_result.get('screening_status', 'unknown')}")
    
    # Create the input structure that should be passed to compliance agent
    compliance_input_data = {
        'customer_data': test_customer_data,
        'agent_results': {
            'document_validation': doc_validation_result,
            'risk_analysis': risk_analysis_result,
            'sanction_screening': sanction_screening_result
        },
        'processing_timeline': {
            'document_validation_time': datetime.now().isoformat(),
            'risk_analysis_time': datetime.now().isoformat(),
            'sanction_screening_time': datetime.now().isoformat()
        }
    }
    
    print("\n4. Testing Compliance Agent with Complete Input...")
    compliance_result = processor.simulate_compliance_response(compliance_input_data)
    
    print(f"\n=== Compliance Agent Input Structure ===")
    print(f"Input keys: {list(compliance_input_data.keys())}")
    print(f"Agent results keys: {list(compliance_input_data['agent_results'].keys())}")
    
    print(f"\n=== Compliance Agent Response ===")
    print(f"Compliance Status: {compliance_result.get('compliance_status', 'unknown')}")
    print(f"Violations: {compliance_result.get('violations', [])}")
    print(f"Regulatory Report: {compliance_result.get('regulatory_report', 'N/A')}")
    
    print(f"\n=== Audit Entries ===")
    for entry in compliance_result.get('audit_entries', []):
        print(f"  - {entry['action']} by {entry['agent']}: {entry['result']}")
    
    # Verify that the compliance agent used the previous agent results
    regulatory_report = compliance_result.get('regulatory_report', '')
    if 'Document validation:' in regulatory_report and 'Risk assessment:' in regulatory_report and 'Sanction screening:' in regulatory_report:
        print(f"\n✅ SUCCESS: Compliance agent properly used previous agent results")
    else:
        print(f"\n❌ FAILURE: Compliance agent did not use previous agent results")
    
    print(f"\n=== Test Complete ===")

if __name__ == "__main__":
    test_compliance_agent_input() 
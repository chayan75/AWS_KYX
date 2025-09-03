#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced data format with comprehensive customer information.
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import KYCProcessor
from database import db_manager

def test_enhanced_data_format():
    """Test the enhanced data format with comprehensive customer information."""
    print("=== Testing Enhanced Data Format ===\n")
    
    # Initialize the KYC processor
    kyc_processor = KYCProcessor()
    
    # Test Case 1: Standard Individual with Complete Information
    print("1. Standard Individual with Complete Information")
    print("=" * 60)
    
    individual_data = {
        "customer_id": "CUST001",
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+1-555-123-4567",
        "address": "123 Main Street, New York, NY 10001",
        "dob": "1985-06-15",
        "nationality": "US",
        "occupation": "Software Engineer",
        "employer": "Tech Solutions Inc.",
        "annual_income": 120000,
        "source_of_funds": "employment",
        "documents": {
            "id_proof": "US_Passport_123456",
            "address_proof": "Utility_Bill_789",
            "employment_proof": "Salary_Slip_456"
        }
    }
    
    print("Input Data:")
    print(json.dumps(individual_data, indent=2))
    
    # Process the submission
    enhanced_data = kyc_processor.enhance_customer_data_with_documents(individual_data)
    
    print("\nEnhanced Data:")
    print(json.dumps(enhanced_data, indent=2))
    
    print(f"\nCustomer Type: {enhanced_data.get('customer_type')}")
    print(f"Estimated Risk Level: {enhanced_data.get('estimated_risk_level')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 2: Business Owner
    print("2. Business Owner")
    print("=" * 60)
    
    business_data = {
        "customer_id": "CUST002",
        "name": "Sarah Johnson",
        "email": "sarah.johnson@business.com",
        "phone": "+44-20-7123-4567",
        "address": "456 Business Avenue, London, UK SW1A 1AA",
        "dob": "1980-08-22",
        "nationality": "UK",
        "occupation": "Business Owner",
        "business_name": "Johnson Consulting Ltd",
        "position": "CEO",
        "annual_income": 250000,
        "source_of_funds": "business_income",
        "documents": {
            "id_proof": "UK_Passport_789",
            "address_proof": "Bank_Statement_456",
            "employment_proof": "Business_Registration_123"
        }
    }
    
    print("Input Data:")
    print(json.dumps(business_data, indent=2))
    
    enhanced_business_data = kyc_processor.enhance_customer_data_with_documents(business_data)
    
    print("\nEnhanced Data:")
    print(json.dumps(enhanced_business_data, indent=2))
    
    print(f"\nCustomer Type: {enhanced_business_data.get('customer_type')}")
    print(f"Estimated Risk Level: {enhanced_business_data.get('estimated_risk_level')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 3: PEP (Politically Exposed Person)
    print("3. PEP (Politically Exposed Person)")
    print("=" * 60)
    
    pep_data = {
        "customer_id": "CUST003",
        "name": "Dr. Maria Rodriguez",
        "email": "maria.rodriguez@government.es",
        "phone": "+34-91-123-4567",
        "address": "45 Diplomat Avenue, Madrid, Spain 28001",
        "dob": "1975-03-20",
        "nationality": "Spain",
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
    
    print("Input Data:")
    print(json.dumps(pep_data, indent=2))
    
    enhanced_pep_data = kyc_processor.enhance_customer_data_with_documents(pep_data)
    
    print("\nEnhanced Data:")
    print(json.dumps(enhanced_pep_data, indent=2))
    
    print(f"\nCustomer Type: {enhanced_pep_data.get('customer_type')}")
    print(f"Estimated Risk Level: {enhanced_pep_data.get('estimated_risk_level')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 4: Student
    print("4. Student")
    print("=" * 60)
    
    student_data = {
        "customer_id": "CUST004",
        "name": "Alex Chen",
        "email": "alex.chen@student.edu",
        "phone": "+1-555-987-6543",
        "address": "789 University Blvd, Boston, MA 02115",
        "dob": "2000-12-10",
        "nationality": "US",
        "occupation": "Student",
        "university": "Boston University",
        "annual_income": 15000,
        "source_of_funds": "student_loan",
        "documents": {
            "id_proof": "US_Driver_License_456",
            "address_proof": "Student_Housing_789",
            "employment_proof": "Student_ID_123"
        }
    }
    
    print("Input Data:")
    print(json.dumps(student_data, indent=2))
    
    enhanced_student_data = kyc_processor.enhance_customer_data_with_documents(student_data)
    
    print("\nEnhanced Data:")
    print(json.dumps(enhanced_student_data, indent=2))
    
    print(f"\nCustomer Type: {enhanced_student_data.get('customer_type')}")
    print(f"Estimated Risk Level: {enhanced_student_data.get('estimated_risk_level')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Test Case 5: High Net Worth Individual
    print("5. High Net Worth Individual")
    print("=" * 60)
    
    hni_data = {
        "customer_id": "CUST005",
        "name": "Michael Thompson",
        "email": "michael.thompson@wealth.com",
        "phone": "+1-555-456-7890",
        "address": "1000 Luxury Lane, Beverly Hills, CA 90210",
        "dob": "1970-04-15",
        "nationality": "US",
        "occupation": "Investment Banker",
        "employer": "Goldman Sachs",
        "annual_income": 750000,
        "source_of_funds": "investment_income",
        "documents": {
            "id_proof": "US_Passport_999",
            "address_proof": "Property_Deed_888",
            "employment_proof": "Investment_Statement_777"
        }
    }
    
    print("Input Data:")
    print(json.dumps(hni_data, indent=2))
    
    enhanced_hni_data = kyc_processor.enhance_customer_data_with_documents(hni_data)
    
    print("\nEnhanced Data:")
    print(json.dumps(enhanced_hni_data, indent=2))
    
    print(f"\nCustomer Type: {enhanced_hni_data.get('customer_type')}")
    print(f"Estimated Risk Level: {enhanced_hni_data.get('estimated_risk_level')}")

def test_database_integration():
    """Test database integration with enhanced data."""
    print("\n=== Testing Database Integration ===\n")
    
    # Create a test case with enhanced data
    test_data = {
        "customer_id": "TEST001",
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "+1-555-000-0000",
        "address": "123 Test Street, Test City, TC 12345",
        "dob": "1990-01-01",
        "nationality": "US",
        "occupation": "Test Engineer",
        "employer": "Test Company",
        "annual_income": 100000,
        "source_of_funds": "employment",
        "customer_type": "Individual",
        "estimated_risk_level": "Low",
        "documents": {
            "id_proof": "TEST_ID_001",
            "address_proof": "TEST_ADDRESS_001",
            "employment_proof": "TEST_EMPLOYMENT_001"
        }
    }
    
    try:
        # Create case in database
        case_id = db_manager.create_kyc_case(test_data)
        print(f"✅ Test case created with ID: {case_id}")
        
        # Retrieve case details
        case = db_manager.get_case_by_id(case_id)
        print(f"✅ Case retrieved: {case.name} ({case.customer_type})")
        print(f"   Customer ID: {case.customer_id}")
        print(f"   Email: {case.email}")
        print(f"   Phone: {case.phone}")
        print(f"   Estimated Risk: {case.estimated_risk_level}")
        print(f"   Status: {case.status}")
        
        # Get case details as dictionary
        case_details = db_manager.get_case_details_by_customer_id(case.customer_id)
        print(f"\n✅ Case details retrieved:")
        print(f"   Customer ID: {case_details['customer_id']}")
        print(f"   Customer Type: {case_details['customer_type']}")
        print(f"   Estimated Risk Level: {case_details['estimated_risk_level']}")
        print(f"   Documents: {len(case_details['documents'])}")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Data Format\n")
    
    try:
        test_enhanced_data_format()
        test_database_integration()
        
        print("\n" + "="*80)
        print("✅ Enhanced Data Format Test Complete!")
        print("\n📋 Summary of Enhanced Data Structure:")
        print("• Basic Information: name, email, phone, address")
        print("• Personal Details: dob, nationality, customer_id")
        print("• Employment: occupation, employer, annual_income, source_of_funds")
        print("• Business: business_name, position, university")
        print("• Risk Assessment: pep_status, customer_type, estimated_risk_level")
        print("• Documents: documents mapping + document_details with extracted data")
        print("• Processing: submission_time, processing_status")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
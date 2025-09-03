#!/usr/bin/env python3
"""
KYC Agentic Flow Demo - Three Scenarios
This script demonstrates the complete KYC workflow from customer portal to admin portal.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_simulate import KYCProcessor
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_customer_portal_view(customer_data, step):
    """Simulate customer portal view."""
    print(f"\n📱 CUSTOMER PORTAL - Step {step}")
    print("-" * 50)
    print(f"Customer: {customer_data['name']}")
    print(f"Documents Uploaded:")
    for doc_type, doc_name in customer_data['documents'].items():
        print(f"  ✓ {doc_type.replace('_', ' ').title()}: {doc_name}")
    print(f"Status: Processing...")

def print_admin_portal_view(kyc_processor, customer_id):
    """Simulate admin portal view."""
    print(f"\n🖥️  ADMIN PORTAL - Case {customer_id}")
    print("-" * 50)
    
    # Get case details
    case = kyc_processor.kyc_cases.get(customer_id, {})
    customer_data = case.get('customer_data', {})
    
    print(f"Customer: {customer_data.get('name', 'N/A')}")
    print(f"Type: {kyc_processor.get_customer_type(customer_data)}")
    print(f"Status: {case.get('status', 'Unknown')}")
    
    # Show processing steps
    print(f"\nProcessing Steps:")
    for i, step in enumerate(case.get('processing_steps', []), 1):
        step_name = step['step'].replace('_', ' ').title()
        result = step['result']
        
        if step['step'] == 'risk_analysis':
            risk_level = result.get('risk_classification', 'Unknown')
            print(f"  {i}. {step_name}: {risk_level} Risk")
        elif step['step'] == 'document_validation':
            status = result.get('validation_status', 'Unknown')
            print(f"  {i}. {step_name}: {status.title()}")
        elif step['step'] == 'compliance_check':
            status = result.get('compliance_status', 'Unknown')
            print(f"  {i}. {step_name}: {status.title()}")
        else:
            print(f"  {i}. {step_name}: Completed")

def run_scenario_1():
    """Scenario 1: Standard Individual Account (Low Risk)"""
    print_header("SCENARIO 1: Standard Individual Account (Low Risk)")
    
    # Initialize KYC processor
    kyc_processor = KYCProcessor()
    
    # Customer Portal: Document Upload
    scenario1_data = {
        "name": "John Smith",
        "dob": "1985-06-15",
        "nationality": "US",
        "address": "123 Main St, New York, NY 10001",
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
    
    print_customer_portal_view(scenario1_data, 1)
    
    # Process the submission
    print(f"\n🔄 Processing KYC submission...")
    result = kyc_processor.process_customer_submission(scenario1_data)
    
    # Admin Portal: View results
    print_admin_portal_view(kyc_processor, result['customer_id'])
    
    print(f"\n✅ Final Result: {result['final_status'].upper()}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Validation: {result['validation_status']}")
    print(f"   Compliance: {result['compliance_status']}")
    
    return kyc_processor

def run_scenario_2():
    """Scenario 2: Small Business Owner (Medium Risk)"""
    print_header("SCENARIO 2: Small Business Owner (Medium Risk)")
    
    # Initialize KYC processor
    kyc_processor = KYCProcessor()
    
    # Customer Portal: Document Upload
    scenario2_data = {
        "name": "Sarah Johnson",
        "customer_id": "CUST002",
        "dob": "1980-08-22",
        "nationality": "UK",
        "address": "456 Business Ave, London, UK",
        "occupation": "Business Owner",
        "business_name": "Johnson Consulting Ltd",
        "annual_income": 250000,
        "source_of_funds": "business_income",
        "documents": {
            "id_proof": "UK_Passport_789",
            "address_proof": "Bank_Statement_456",
            "employment_proof": "Business_Registration_123"
        }
    }
    
    print_customer_portal_view(scenario2_data, 1)
    
    # Process the submission
    print(f"\n🔄 Processing KYC submission...")
    result = kyc_processor.process_customer_submission(scenario2_data)
    
    # Admin Portal: View results
    print_admin_portal_view(kyc_processor, result['customer_id'])
    
    print(f"\n✅ Final Result: {result['final_status'].upper()}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Validation: {result['validation_status']}")
    print(f"   Compliance: {result['compliance_status']}")
    
    return kyc_processor

def run_scenario_3():
    """Scenario 3: PEP Account (High Risk)"""
    print_header("SCENARIO 3: PEP Account (High Risk)")
    
    # Initialize KYC processor
    kyc_processor = KYCProcessor()
    
    # Customer Portal: Document Upload
    scenario3_data = {
        "name": "Dr. Maria Rodriguez",
        "dob": "1975-03-20",
        "nationality": "Spain",
        "customer_id": "CUST003",
        "address": "45 Diplomat Ave, Madrid, Spain",
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
    
    print_customer_portal_view(scenario3_data, 1)
    
    # Process the submission
    print(f"\n🔄 Processing KYC submission...")
    result = kyc_processor.process_customer_submission(scenario3_data)
    
    # Admin Portal: View results
    print_admin_portal_view(kyc_processor, result['customer_id'])
    
    print(f"\n✅ Final Result: {result['final_status'].upper()}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Validation: {result['validation_status']}")
    print(f"   Compliance: {result['compliance_status']}")
    
    return kyc_processor

def show_admin_dashboard():
    """Show the complete admin dashboard with all scenarios."""
    print_header("ADMIN DASHBOARD - Complete Overview")
    
    # Run all scenarios and collect data
    kyc_processor = KYCProcessor()
    
    # Scenario 1
    scenario1_data = {
        "name": "John Smith",
        "dob": "1985-06-15",
        "nationality": "US",
        "address": "123 Main St, New York, NY 10001",
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
    result1 = kyc_processor.process_customer_submission(scenario1_data)
    
    # Scenario 2
    scenario2_data = {
        "name": "Sarah Johnson",
        "dob": "1980-08-22",
        "nationality": "UK",
        "address": "456 Business Ave, London, UK",
        "occupation": "Business Owner",
        "business_name": "Johnson Consulting Ltd",
        "annual_income": 250000,
        "source_of_funds": "business_income",
        "documents": {
            "id_proof": "UK_Passport_789",
            "address_proof": "Bank_Statement_456",
            "employment_proof": "Business_Registration_123"
        }
    }
    result2 = kyc_processor.process_customer_submission(scenario2_data)
    
    # Scenario 3
    scenario3_data = {
        "name": "Dr. Maria Rodriguez",
        "dob": "1975-03-20",
        "nationality": "Spain",
        "address": "45 Diplomat Ave, Madrid, Spain",
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
    result3 = kyc_processor.process_customer_submission(scenario3_data)
    
    # Get dashboard data
    dashboard_data = kyc_processor.get_admin_dashboard_data()
    
    # Display summary
    print(f"\n📊 SUMMARY STATISTICS")
    print("-" * 30)
    print(f"Total Cases: {dashboard_data['summary']['total_cases']}")
    print(f"Pending Cases: {dashboard_data['summary']['pending_cases']}")
    print(f"Approved Cases: {dashboard_data['summary']['approved_cases']}")
    print(f"High Risk Cases: {dashboard_data['summary']['high_risk_cases']}")
    
    # Display case details
    print(f"\n📋 CASE DETAILS")
    print("-" * 30)
    for case in dashboard_data['cases']:
        status_emoji = "✅" if case['status'] == 'approved' else "⏳"
        risk_emoji = "🔴" if case['riskLevel'] == 'high' else "🟡" if case['riskLevel'] == 'medium' else "🟢"
        
        print(f"{status_emoji} {case['id']}: {case['name']}")
        print(f"   Type: {case['type']} | Risk: {risk_emoji} {case['riskLevel'].upper()}")
        print(f"   Status: {case['status'].upper()} | Progress: {case['progress']}%")
        print(f"   Documents: {', '.join(case['documents'])}")
        print()

def main():
    """Run the complete demo."""
    print("🚀 KYC Agentic Flow Demo - Customer Portal to Admin Portal")
    print("=" * 80)
    
    # Run individual scenarios
    print("\nRunning individual scenarios...")
    
    print("\n" + "="*80)
    run_scenario_1()
    
    print("\n" + "="*80)
    run_scenario_2()
    
    print("\n" + "="*80)
    run_scenario_3()
    
    # Show complete admin dashboard
    print("\n" + "="*80)
    show_admin_dashboard()
    
    print_header("DEMO COMPLETE")
    print("✅ All scenarios processed successfully!")
    print("📱 Customer Portal: Document upload and status tracking")
    print("🖥️  Admin Portal: Complete KYC workflow monitoring")
    print("🤖 Agentic Flow: Coordinated processing across multiple agents")

if __name__ == "__main__":
    main() 
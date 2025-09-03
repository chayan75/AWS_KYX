#!/usr/bin/env python3
"""
Test script for enhanced fuzzy matching functionality.
Tests name and address matching with 80% threshold.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from document_processor import DocumentProcessor

def test_enhanced_fuzzy_matching():
    """Test the enhanced fuzzy matching functionality."""
    print("=== Testing Enhanced Fuzzy Matching (80% threshold) ===\n")
    
    processor = DocumentProcessor()
    
    # Test cases for name matching
    name_test_cases = [
        # Exact matches
        ("John Smith", "John Smith", True, "Exact match"),
        ("john smith", "John Smith", True, "Case insensitive"),
        ("JOHN SMITH", "john smith", True, "All caps vs lowercase"),
        
        # Nickname variations
        ("William Johnson", "Bill Johnson", True, "William -> Bill"),
        ("Robert Wilson", "Bob Wilson", True, "Robert -> Bob"),
        ("Elizabeth Brown", "Liz Brown", True, "Elizabeth -> Liz"),
        ("Michael Davis", "Mike Davis", True, "Michael -> Mike"),
        ("Christopher Lee", "Chris Lee", True, "Christopher -> Chris"),
        
        # Name variations
        ("John Smith", "Johnny Smith", True, "John -> Johnny"),
        ("Joseph Wilson", "Joe Wilson", True, "Joseph -> Joe"),
        ("Thomas Brown", "Tom Brown", True, "Thomas -> Tom"),
        ("Charles Davis", "Charlie Davis", True, "Charles -> Charlie"),
        
        # Middle name variations
        ("John A Smith", "John Smith", True, "With/without middle initial"),
        ("John Smith", "John A Smith", True, "Without/with middle initial"),
        ("John Alexander Smith", "John A Smith", True, "Full middle name vs initial"),
        
        # Name order variations
        ("Smith, John", "John Smith", True, "Last, First format"),
        ("John Smith", "Smith, John", True, "First Last vs Last, First"),
        
        # Slight variations
        ("John Smith", "Jon Smith", True, "John vs Jon"),
        ("Sarah Johnson", "Sara Johnson", True, "Sarah vs Sara"),
        ("Katherine Wilson", "Katherine Wilson", True, "Katherine vs Katherine"),
        
        # Should not match
        ("John Smith", "Jane Smith", False, "Different first names"),
        ("John Smith", "John Doe", False, "Different last names"),
        ("John Smith", "Mary Johnson", False, "Completely different names"),
        ("John Smith", "John Smith Jr", False, "With/without suffix"),
    ]
    
    # Test cases for address matching
    address_test_cases = [
        # Exact matches
        ("123 Main St", "123 Main St", True, "Exact match"),
        ("123 Main Street", "123 Main St", True, "Street vs St"),
        ("123 Main St", "123 Main Street", True, "St vs Street"),
        
        # Address variations
        ("123 Main Street", "123 Main St", True, "Full vs abbreviated"),
        ("123 Main Ave", "123 Main Avenue", True, "Ave vs Avenue"),
        ("123 Main Rd", "123 Main Road", True, "Rd vs Road"),
        ("123 Main Dr", "123 Main Drive", True, "Dr vs Drive"),
        
        # Case and spacing variations
        ("123 MAIN ST", "123 main st", True, "Case insensitive"),
        ("123 Main St", "123  Main  St", True, "Extra spaces"),
        ("123 Main St.", "123 Main St", True, "With/without period"),
        
        # Partial matches (same street, different apartment)
        ("123 Main St Apt 1", "123 Main St", True, "With apartment"),
        ("123 Main St", "123 Main St Apt 1", True, "Without apartment"),
        ("123 Main St Unit 2", "123 Main St", True, "With unit"),
        
        # Business variations
        ("Tech Corp", "Tech Corporation", True, "Corp vs Corporation"),
        ("Tech Corp Ltd", "Tech Corporation Limited", True, "Multiple abbreviations"),
        ("Tech Corp Inc", "Tech Corporation Incorporated", True, "Inc vs Incorporated"),
        
        # Should not match
        ("123 Main St", "456 Main St", False, "Different street numbers"),
        ("123 Main St", "123 Oak St", False, "Different street names"),
        ("123 Main St", "123 Main Ave", False, "Different street types"),
        ("123 Main St", "456 Oak Ave", False, "Completely different addresses"),
    ]
    
    print("🧪 Testing Name Matching")
    print("-" * 50)
    
    name_passed = 0
    name_failed = 0
    
    for name1, name2, expected, description in name_test_cases:
        result = processor._fuzzy_match(name1, name2, threshold=0.8, match_type="name")
        if result == expected:
            print(f"✅ '{name1}' vs '{name2}': {result} (expected {expected}) - {description}")
            name_passed += 1
        else:
            print(f"❌ '{name1}' vs '{name2}': {result} (expected {expected}) - {description}")
            name_failed += 1
    
    print(f"\n📊 Name Matching Results: {name_passed} passed, {name_failed} failed")
    
    print("\n🧪 Testing Address Matching")
    print("-" * 50)
    
    address_passed = 0
    address_failed = 0
    
    for addr1, addr2, expected, description in address_test_cases:
        result = processor._fuzzy_match(addr1, addr2, threshold=0.8, match_type="address")
        if result == expected:
            print(f"✅ '{addr1}' vs '{addr2}': {result} (expected {expected}) - {description}")
            address_passed += 1
        else:
            print(f"❌ '{addr1}' vs '{addr2}': {result} (expected {expected}) - {description}")
            address_failed += 1
    
    print(f"\n📊 Address Matching Results: {address_passed} passed, {address_failed} failed")
    
    # Test document validation with the new fuzzy matching
    print("\n🧪 Testing Document Validation with Enhanced Fuzzy Matching")
    print("-" * 70)
    
    test_customer_data = {
        "name": "William Johnson",
        "email": "bill.johnson@email.com",
        "phone": "+1-555-0101",
        "address": "123 Main Street, New York, NY 10001"
    }
    
    # Test ID proof with nickname
    id_proof_data = {
        "first_name": "bill",  # Should match "William"
        "last_name": "johnson",
        "dob": "1985-03-15",
        "nationality": "US"
    }
    
    result = processor.validate_document_data(id_proof_data, test_customer_data, "id_proof")
    print(f"ID Proof Validation (William vs Bill):")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    
    # Test address proof with abbreviation
    address_proof_data = {
        "full_address": "123 Main St, New York, NY 10001",  # Should match "123 Main Street"
        "account_holder_name": "William Johnson"
    }
    
    result = processor.validate_document_data(address_proof_data, test_customer_data, "address_proof")
    print(f"\nAddress Proof Validation (Street vs St):")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    
    # Test employment proof with business abbreviation
    employment_proof_data = {
        "employer_name": "Tech Corp",  # Should match "Tech Corporation"
        "employee_name": "William Johnson",
        "position": "Software Engineer"
    }
    
    result = processor.validate_document_data(employment_proof_data, test_customer_data, "employment_proof")
    print(f"\nEmployment Proof Validation (Corp vs Corporation):")
    print(f"  Overall Match: {result['overall_match']}")
    print(f"  Confidence Score: {result['confidence_score']}%")
    print(f"  Discrepancies: {len(result['discrepancies'])}")
    
    print(f"\n=== Test Summary ===")
    print(f"Name Matching: {name_passed}/{name_passed + name_failed} passed")
    print(f"Address Matching: {address_passed}/{address_passed + address_failed} passed")
    
    total_tests = len(name_test_cases) + len(address_test_cases)
    total_passed = name_passed + address_passed
    
    if total_passed == total_tests:
        print(f"\n🎉 All {total_tests} tests passed!")
        return True
    else:
        print(f"\n❌ {total_tests - total_passed} tests failed out of {total_tests}")
        return False

def test_threshold_variations():
    """Test different threshold levels to ensure 80% is working correctly."""
    print("\n=== Testing Threshold Variations ===")
    
    processor = DocumentProcessor()
    
    # Test cases that should pass at 80% but fail at higher thresholds
    threshold_test_cases = [
        ("John Smith", "Jon Smith", 0.8, True, "Should pass at 80%"),
        ("John Smith", "Jon Smith", 0.9, False, "Should fail at 90%"),
        ("123 Main St", "123 Main Street", 0.8, True, "Should pass at 80%"),
        ("123 Main St", "123 Main Street", 0.95, False, "Should fail at 95%"),
    ]
    
    for str1, str2, threshold, expected, description in threshold_test_cases:
        result = processor._fuzzy_match(str1, str2, threshold=threshold, match_type="general")
        if result == expected:
            print(f"✅ '{str1}' vs '{str2}' at {threshold*100}%: {result} - {description}")
        else:
            print(f"❌ '{str1}' vs '{str2}' at {threshold*100}%: {result} (expected {expected}) - {description}")

if __name__ == "__main__":
    success = test_enhanced_fuzzy_matching()
    test_threshold_variations()
    
    if success:
        print("\n🎉 Enhanced fuzzy matching is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.") 
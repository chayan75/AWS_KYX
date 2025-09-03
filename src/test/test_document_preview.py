#!/usr/bin/env python3
"""
Test script to verify document preview functionality.
"""

import requests
import json
from database import db_manager
from database import Document as DBDocument

def test_document_preview():
    """Test document preview functionality."""
    print("🔍 Testing Document Preview Functionality")
    
    # Get documents from database
    session = db_manager.get_session()
    documents = session.query(DBDocument).filter(DBDocument.file_path.isnot(None)).all()
    session.close()
    
    print(f"Found {len(documents)} documents with file paths")
    
    for doc in documents:
        print(f"\nTesting document: {doc.document_id} ({doc.document_type})")
        print(f"  File path: {doc.file_path}")
        
        # Test the document file endpoint
        url = f"http://localhost:8000/api/documents/{doc.document_id}/file"
        
        try:
            response = requests.get(url)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type')}")
            print(f"  Content-Length: {response.headers.get('content-length')}")
            
            if response.status_code == 200:
                print(f"  ✅ Document preview working")
            else:
                print(f"  ❌ Document preview failed: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Error testing document: {e}")
    
    # Test with a non-existent document
    print(f"\nTesting non-existent document:")
    try:
        response = requests.get("http://localhost:8000/api/documents/nonexistent/file")
        print(f"  Status: {response.status_code}")
        if response.status_code == 404:
            print(f"  ✅ Correctly returns 404 for non-existent document")
        else:
            print(f"  ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"  ❌ Error testing non-existent document: {e}")

def test_case_documents():
    """Test getting case documents."""
    print("\n🔍 Testing Case Documents")
    
    # Get case details
    try:
        response = requests.get(
            "http://localhost:8000/api/cases/CUST001",
            headers={"Authorization": "Bearer test-token"}
        )
        
        if response.status_code == 200:
            case_data = response.json()
            print(f"Case: {case_data['customer_id']} - {case_data['name']}")
            print(f"Documents: {len(case_data['documents'])}")
            
            for doc in case_data['documents']:
                print(f"  {doc['document_id']}: {doc['document_type']} - {doc['file_path']}")
                
                # Test each document
                doc_url = f"http://localhost:8000/api/documents/{doc['document_id']}/file"
                doc_response = requests.get(doc_url)
                print(f"    Status: {doc_response.status_code}")
                
        else:
            print(f"Failed to get case details: {response.status_code}")
            
    except Exception as e:
        print(f"Error testing case documents: {e}")

if __name__ == "__main__":
    test_document_preview()
    test_case_documents() 
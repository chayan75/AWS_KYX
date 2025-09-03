#!/usr/bin/env python3
"""
Script to fix document file paths and clean up duplicate records.
"""

import os
import json
from database import db_manager
from database import Document as DBDocument

def fix_document_paths():
    """Fix document file paths and clean up duplicate records."""
    print("🔧 Fixing document file paths and cleaning up duplicates...")
    
    session = db_manager.get_session()
    
    try:
        # Get all documents
        all_documents = session.query(DBDocument).all()
        print(f"Found {len(all_documents)} total documents")
        
        # Group documents by document_id
        documents_by_id = {}
        for doc in all_documents:
            if doc.document_id not in documents_by_id:
                documents_by_id[doc.document_id] = []
            documents_by_id[doc.document_id].append(doc)
        
        # Process each group
        documents_dir = os.path.join(os.path.dirname(__file__), "documents")
        fixed_count = 0
        deleted_count = 0
        
        for document_id, docs in documents_by_id.items():
            print(f"\nProcessing document ID: {document_id}")
            
            # Find the document with the best file_path
            best_doc = None
            for doc in docs:
                if doc.file_path and os.path.exists(doc.file_path):
                    best_doc = doc
                    break
            
            # If no document with valid file_path, try to find the file
            if not best_doc:
                possible_files = []
                if os.path.exists(documents_dir):
                    for filename in os.listdir(documents_dir):
                        if document_id in filename:
                            possible_files.append(os.path.join(documents_dir, filename))
                
                if possible_files:
                    # Use the first document and update its file_path
                    best_doc = docs[0]
                    best_doc.file_path = possible_files[0]
                    best_doc.filename = os.path.basename(possible_files[0])
                    print(f"  ✅ Fixed file path: {best_doc.file_path}")
                    fixed_count += 1
                else:
                    print(f"  ❌ No file found for document {document_id}")
                    continue
            
            # Delete duplicate records (keep only the best one)
            for doc in docs:
                if doc.id != best_doc.id:
                    print(f"  🗑️  Deleting duplicate record: {doc.id}")
                    session.delete(doc)
                    deleted_count += 1
        
        session.commit()
        print(f"\n✅ Fixed {fixed_count} documents, deleted {deleted_count} duplicates")
        
        # Verify the fix
        print("\n📋 Verifying document status:")
        final_docs = session.query(DBDocument).all()
        for doc in final_docs:
            exists = doc.file_path and os.path.exists(doc.file_path) if doc.file_path else False
            print(f"  {doc.document_id}: {doc.document_type} - {doc.file_path} - Exists: {exists}")
        
    except Exception as e:
        print(f"❌ Error fixing document paths: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_document_paths() 
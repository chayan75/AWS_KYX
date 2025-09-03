from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import db_manager, Document as DBDocument, KYCCase
from document_processor import document_processor
from main import KYCProcessor
from email_service import email_service
from auth_service import auth_service, AuthService
import json
from datetime import datetime
import uvicorn
import os

app = FastAPI(
    title="KYC Admin Dashboard API",
    description="API for KYC process management and admin dashboard",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global auth service instance
auth_service = AuthService()

# Authentication dependency
async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Get current user from authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.split(" ")[1]
        user_info = auth_service.verify_token(token)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Admin-only dependency
async def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current user and verify admin role."""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Pydantic models for request/response validation
class ManualReviewRequest(BaseModel):
    action: str  # 'approve', 'reject', 'request_info'
    notes: Optional[str] = ""

class DocumentValidationRequest(BaseModel):
    extracted_data: Dict[str, Any]
    user_data: Dict[str, Any]
    document_type: str

class AdminDocumentValidationRequest(BaseModel):
    status: str  # 'pending', 'valid', 'invalid'
    notes: Optional[str] = ""

class CaseArchiveRequest(BaseModel):
    notes: str  # Mandatory notes for archiving

class CaseUpdateRequest(BaseModel):
    risk_level: Optional[str] = None  # 'low', 'medium', 'high'
    pep_status: Optional[bool] = None
    case_status: Optional[str] = None  # 'submitted', 'pending', 'approved', 'rejected', 'archived'
    notes: str  # Mandatory notes for updates

class ProcessingStep(BaseModel):
    id: int
    step_name: str
    agent_type: str
    agent_id: str
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    processing_duration: Optional[float]
    input_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    error_message: Optional[str]

class Document(BaseModel):
    id: int
    document_type: str
    document_id: str
    validation_status: str
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    upload_time: Optional[str] = None

class CaseDetails(BaseModel):
    id: int
    customer_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    dob: Optional[str]
    nationality: Optional[str]
    address: Optional[str]
    occupation: Optional[str]
    employer: Optional[str]
    annual_income: Optional[float]
    source_of_funds: Optional[str]
    pep_status: bool
    business_name: Optional[str]
    position: Optional[str]
    university: Optional[str]
    customer_type: Optional[str]
    estimated_risk_level: Optional[str]
    status: str
    submission_time: Optional[str]
    completion_time: Optional[str]
    final_risk_level: Optional[str]
    validation_status: Optional[str]
    compliance_status: Optional[str]
    processing_steps: List[ProcessingStep]
    documents: List[Document]

class DashboardResponse(BaseModel):
    summary: Dict[str, int]
    cases: List[Dict[str, Any]]

# Customer Portal Models
class CustomerData(BaseModel):
    name: str
    email: str
    phone: str
    address: str

class DocumentUploadResponse(BaseModel):
    status: str
    document_id: str
    filename: str
    extracted_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CustomerSubmissionRequest(BaseModel):
    customer_data: CustomerData
    documents: Dict[str, str]  # document_type -> document_id mapping
    validation_warnings: Optional[List[Dict[str, Any]]] = None

class CustomerSubmissionResponse(BaseModel):
    status: str
    customer_id: str
    case_id: int
    final_status: str
    risk_level: str
    message: str
    validation_warnings: Optional[List[Dict[str, Any]]] = None

class EmailRequest(BaseModel):
    email_type: str  # 'status_update', 'document_request', 'approval', 'rejection', 'custom'
    subject: Optional[str] = None  # For custom emails
    message: Optional[str] = None  # For custom emails
    additional_notes: str = ""
    required_documents: Optional[List[str]] = None  # For document request emails
    reason: Optional[str] = None  # For document request or rejection emails

class AuditLogEntry(BaseModel):
    id: int
    action_type: str
    action_details: Dict[str, Any]
    performed_by: str
    timestamp: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    session_id: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class UserInfo(BaseModel):
    username: str
    role: str
    full_name: str
    email: str

@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get dashboard data from database."""
    try:
        print("🔍 Fetching dashboard data...")
        dashboard_data = db_manager.get_dashboard_data()
        print(f"✅ Dashboard data retrieved: {len(dashboard_data.get('cases', []))} cases")
        return dashboard_data
    except Exception as e:
        print(f"❌ Error in dashboard endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/cases/{customer_id}", response_model=CaseDetails)
async def get_case_details(customer_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get detailed case information including processing steps."""
    try:
        case_data = db_manager.get_case_details_by_customer_id(customer_id)
        if not case_data:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Convert the dictionary data to Pydantic models
        processing_steps = [ProcessingStep(**step) for step in case_data['processing_steps']]
        documents = [Document(**doc) for doc in case_data['documents']]
        
        # Create the CaseDetails object
        case_details = CaseDetails(
            id=case_data['id'],
            customer_id=case_data['customer_id'],
            name=case_data['name'],
            email=case_data['email'],
            phone=case_data['phone'],
            dob=case_data['dob'],
            nationality=case_data['nationality'],
            address=case_data['address'],
            occupation=case_data['occupation'],
            employer=case_data['employer'],
            annual_income=case_data['annual_income'],
            source_of_funds=case_data['source_of_funds'],
            pep_status=case_data['pep_status'],
            business_name=case_data['business_name'],
            position=case_data['position'],
            university=case_data['university'],
            customer_type=case_data['customer_type'],
            estimated_risk_level=case_data['estimated_risk_level'],
            status=case_data['status'],
            submission_time=case_data['submission_time'],
            completion_time=case_data['completion_time'],
            final_risk_level=case_data['final_risk_level'],
            validation_status=case_data['validation_status'],
            compliance_status=case_data['compliance_status'],
            processing_steps=processing_steps,
            documents=documents
        )
        
        return case_details
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in case details endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/cases/{customer_id}/manual-review")
async def manual_review(customer_id: str, review_request: ManualReviewRequest, 
                       current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Perform manual review of a KYC case (admin only)."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Update case based on review action
        if review_request.action == "approve":
            case.status = "approved"
            case.final_risk_level = case.estimated_risk_level or "low"
            case.completion_time = datetime.now()
        elif review_request.action == "reject":
            case.status = "rejected"
            case.completion_time = datetime.now()
        elif review_request.action == "request_info":
            case.status = "pending"
        
        # Add review notes
        current_validation = case.validation_status or ""
        review_note = f"Manual Review ({datetime.now().strftime('%Y-%m-%d %H:%M')}): {review_request.notes}"
        case.validation_status = f"{current_validation}; {review_note}".strip('; ')
        
        session.commit()
        session.close()
        
        return {
            "status": "success",
            "message": f"Case {review_request.action}ed successfully",
            "customer_id": customer_id,
            "action": review_request.action,
            "review_notes": review_request.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in manual review: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{customer_id}/retry")
async def retry_processing(customer_id: str, current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Retry processing for a KYC case (admin only)."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Reset case status for retry
        case.status = "pending"
        case.completion_time = None
        
        session.commit()
        session.close()
        
        return {
            "status": "success",
            "message": "Case processing retry initiated",
            "customer_id": customer_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in retry processing: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Customer Portal Endpoints
@app.post("/api/customer/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload and process a document for the customer portal."""
    try:
        # Validate document type
        valid_types = ["id_proof", "address_proof", "employment_proof"]
        if document_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {valid_types}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {allowed_extensions}")
        
        # Process document upload
        result = document_processor.process_document_upload(file, document_type)
        
        if result["status"] == "success":
            return DocumentUploadResponse(
                status="success",
                document_id=result["file_info"]["document_id"],
                filename=result["file_info"]["filename"],
                extracted_data=result["extracted_data"]
            )
        elif result["status"] == "partial_success":
            return DocumentUploadResponse(
                status="partial_success",
                document_id=result["file_info"]["document_id"],
                filename=result["file_info"]["filename"],
                error=result["extraction_error"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in document upload: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customer/validate-document")
async def validate_document_data(validation_request: DocumentValidationRequest):
    """Validate extracted document data against user-entered information."""
    try:
        validation_result = document_processor.validate_document_data(
            validation_request.extracted_data,
            validation_request.user_data,
            validation_request.document_type
        )
        
        return validation_result
        
    except Exception as e:
        print(f"❌ Error in document validation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customer/submit", response_model=CustomerSubmissionResponse)
async def submit_customer_kyc(submission: CustomerSubmissionRequest):
    """Submit customer KYC application with uploaded documents and validation."""
    try:
        # Initialize KYC processor
        kyc_processor = KYCProcessor()
        
        # Prepare customer data for processing
        customer_data = {
            "name": submission.customer_data.name,
            "email": submission.customer_data.email,
            "phone": submission.customer_data.phone,
            "address": submission.customer_data.address,
            "documents": submission.documents
        }
        
        # Use validation warnings from frontend if provided, otherwise validate
        validation_warnings = []
        
        if submission.validation_warnings:
            # Use validation warnings sent from frontend
            validation_warnings = submission.validation_warnings
            print(f"Using validation warnings from frontend: {len(validation_warnings)} warnings")
        else:
            # Fallback: validate documents against user-entered data
            print("No validation warnings from frontend, performing validation...")
            session = db_manager.get_session()
            try:
                for document_type, document_id in submission.documents.items():
                    document = session.query(DBDocument).filter(DBDocument.document_id == document_id).first()
                    if document and document.extracted_data:
                        try:
                            extracted_data = json.loads(document.extracted_data)
                            validation_result = document_processor.validate_document_data(
                                extracted_data, 
                                customer_data, 
                                document_type
                            )
                            
                            # Add warnings for discrepancies
                            if not validation_result["overall_match"]:
                                validation_warnings.append({
                                    "document_type": document_type,
                                    "document_id": document_id,
                                    "confidence_score": validation_result["confidence_score"],
                                    "discrepancies": validation_result["discrepancies"],
                                    "warnings": validation_result["warnings"]
                                })
                        except Exception as e:
                            print(f"Error validating document {document_id}: {e}")
                            validation_warnings.append({
                                "document_type": document_type,
                                "document_id": document_id,
                                "error": f"Validation failed: {str(e)}"
                            })
            finally:
                session.close()
        
        # Process the customer submission
        result = kyc_processor.process_customer_submission(customer_data)
        
        if result["status"] == "success":
            # If there are validation warnings, override the status to "pending" for manual review
            if validation_warnings:
                case_id = result["case_id"]
                session = db_manager.get_session()
                try:
                    case = session.query(KYCCase).filter(KYCCase.id == case_id).first()
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
                        
                        print(f"✅ Case {case.customer_id} set to pending due to validation warnings")
                finally:
                    session.close()
            
            return CustomerSubmissionResponse(
                status="success",
                customer_id=result["customer_id"],
                case_id=result["case_id"],
                final_status=result["final_status"],
                risk_level=result["risk_level"],
                message="KYC application submitted successfully" + 
                       (f" with {len(validation_warnings)} document validation warning(s) - requires manual review" if validation_warnings else ""),
                validation_warnings=validation_warnings if validation_warnings else None
            )
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in customer submission: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customer/status/{customer_id}")
async def get_customer_status(customer_id: str):
    """Get customer KYC status."""
    try:
        case_data = db_manager.get_case_details_by_customer_id(customer_id)
        if not case_data:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "status": "success",
            "customer_id": customer_id,
            "case_status": case_data["status"],
            "risk_level": case_data["final_risk_level"],
            "submission_time": case_data["submission_time"],
            "completion_time": case_data["completion_time"],
            "documents": case_data["documents"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting customer status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint with database status."""
    try:
        # Check database connection
        db_connection = db_manager.check_database_connection()
        db_info = db_manager.get_database_info()
        
        return {
            "status": "healthy" if db_connection else "degraded",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "connected": db_connection,
                "info": db_info
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/api/database/init")
async def initialize_database():
    """Initialize database tables and structure."""
    try:
        # This will create tables if they don't exist
        db_manager.create_tables()
        db_info = db_manager.get_database_info()
        
        return {
            "status": "success",
            "message": "Database initialized successfully",
            "database_info": db_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

@app.get("/api/database/info")
async def get_database_info():
    """Get database information."""
    try:
        db_info = db_manager.get_database_info()
        return db_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database info: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "KYC Admin Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/documents/{document_id}/file")
async def get_document_file(document_id: str):
    """Get document file for preview."""
    try:
        # Get document from database - find the one with a valid file_path
        session = db_manager.get_session()
        document = session.query(DBDocument).filter(
            DBDocument.document_id == document_id,
            DBDocument.file_path.isnot(None)
        ).first()
        
        # If no document with file_path found, try to find any document with this ID
        if not document:
            document = session.query(DBDocument).filter(DBDocument.document_id == document_id).first()
        
        session.close()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.file_path or not os.path.exists(document.file_path):
            # Try to find the file in the documents directory
            documents_dir = os.path.join(os.path.dirname(__file__), "documents")
            possible_files = []
            
            if os.path.exists(documents_dir):
                for filename in os.listdir(documents_dir):
                    if document_id in filename:
                        possible_files.append(os.path.join(documents_dir, filename))
            
            if possible_files:
                # Use the first found file
                document.file_path = possible_files[0]
                print(f"Found file for document {document_id}: {document.file_path}")
            else:
                raise HTTPException(status_code=404, detail="Document file not found")
        
        # Determine content type based on file extension
        file_extension = os.path.splitext(document.file_path)[1].lower()
        media_type = None
        
        if file_extension in ['.jpg', '.jpeg']:
            media_type = 'image/jpeg'
        elif file_extension == '.png':
            media_type = 'image/png'
        elif file_extension == '.pdf':
            media_type = 'application/pdf'
        
        return FileResponse(
            path=document.file_path,
            media_type=media_type,
            filename=document.filename or document.original_filename or os.path.basename(document.file_path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in document file retrieval: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{customer_id}/archive")
async def archive_case(customer_id: str, archive_request: CaseArchiveRequest, 
                      request: Request, current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Archive a KYC case (admin only)."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Check if case is already archived
        if case.status == "archived":
            session.close()
            raise HTTPException(
                status_code=400, 
                detail="Case is already archived and cannot be archived again"
            )
        
        # Update case status to archived
        case.status = "archived"
        case.completion_time = datetime.now()
        
        # Add archive notes to case data (you might want to store this in a separate field)
        # For now, we'll add it to the validation_status field as a note
        case.validation_status = f"Archived: {archive_request.notes}"
        
        # Get case ID before closing session
        case_id = case.id
        
        session.commit()
        session.close()
        
        # Log the archive action
        audit_details = {
            "previous_status": "active",  # You might want to store the previous status
            "new_status": "archived",
            "archive_notes": archive_request.notes,
            "completion_time": datetime.now().isoformat(),
            "performed_by": current_user['username']
        }
        
        db_manager.add_audit_log(
            case_id=case_id,
            action_type="case_archived",
            action_details=audit_details,
            performed_by=current_user['username'],
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "status": "success",
            "message": "Case archived successfully",
            "customer_id": customer_id,
            "archive_notes": archive_request.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in case archiving: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{customer_id}/update")
async def update_case(customer_id: str, update_request: CaseUpdateRequest, 
                     request: Request, current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Update case parameters manually (admin only)."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Update case parameters if provided
        if update_request.risk_level is not None:
            case.final_risk_level = update_request.risk_level
        
        if update_request.pep_status is not None:
            case.pep_status = update_request.pep_status
        
        if update_request.case_status is not None:
            case.status = update_request.case_status
            if update_request.case_status in ['approved', 'rejected']:
                case.completion_time = datetime.now()
        
        # Store update notes in validation_status field (you might want a separate field for this)
        current_validation = case.validation_status or ""
        update_note = f"Manual Update ({datetime.now().strftime('%Y-%m-%d %H:%M')}): {update_request.notes}"
        case.validation_status = f"{current_validation}; {update_note}".strip('; ')
        
        # Get case ID before closing session
        case_id = case.id
        
        session.commit()
        session.close()
        
        # Log the update action
        audit_details = {
            "updated_fields": {
                "risk_level": update_request.risk_level,
                "pep_status": update_request.pep_status,
                "case_status": update_request.case_status
            },
            "update_notes": update_request.notes,
            "update_timestamp": datetime.now().isoformat(),
            "performed_by": current_user['username']
        }
        
        db_manager.add_audit_log(
            case_id=case_id,
            action_type="case_updated",
            action_details=audit_details,
            performed_by=current_user['username'],
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "status": "success",
            "message": "Case updated successfully",
            "customer_id": customer_id,
            "updated_fields": {
                "risk_level": update_request.risk_level,
                "pep_status": update_request.pep_status,
                "case_status": update_request.case_status
            },
            "update_notes": update_request.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in case update: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cases/{customer_id}/send-email")
async def send_email_to_customer(customer_id: str, email_request: EmailRequest, 
                                request: Request, current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Send email to customer with audit logging (admin only)."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        if not case.email:
            session.close()
            raise HTTPException(status_code=400, detail="Customer email not found")
        
        # Send email based on type
        email_result = None
        
        if email_request.email_type == "status_update":
            email_result = email_service.send_status_update_email(
                case.email, case.name, customer_id, case.status, 
                case.final_risk_level or case.estimated_risk_level or "Not determined",
                email_request.additional_notes
            )
        elif email_request.email_type == "document_request":
            if not email_request.required_documents or not email_request.reason:
                raise HTTPException(status_code=400, detail="Required documents and reason are mandatory for document request emails")
            email_result = email_service.send_document_request_email(
                case.email, case.name, customer_id, email_request.required_documents, 
                email_request.reason
            )
        elif email_request.email_type == "approval":
            email_result = email_service.send_approval_email(
                case.email, case.name, customer_id,
                case.final_risk_level or case.estimated_risk_level or "Not determined",
                email_request.additional_notes
            )
        elif email_request.email_type == "rejection":
            if not email_request.reason:
                raise HTTPException(status_code=400, detail="Reason is mandatory for rejection emails")
            email_result = email_service.send_rejection_email(
                case.email, case.name, customer_id, case.status, 
                email_request.reason, email_request.additional_notes
            )
        elif email_request.email_type == "custom":
            if not email_request.message:
                raise HTTPException(status_code=400, detail="Message is mandatory for custom emails")
            email_result = email_service.send_custom_email(
                case.email, case.name, email_request.message, 
                email_request.subject or "KYC Application Update"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Invalid email type: {email_request.email_type}")
        
        session.close()
        
        # Log the email action
        audit_details = {
            "email_type": email_request.email_type,
            "email_result": email_result,
            "additional_notes": email_request.additional_notes,
            "required_documents": email_request.required_documents,
            "reason": email_request.reason,
            "custom_subject": email_request.subject,
            "custom_message": email_request.message,
            "sent_by": current_user['username']
        }
        
        db_manager.add_audit_log(
            case_id=case.id,
            action_type="email_sent",
            action_details=audit_details,
            performed_by=current_user['username'],
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return {
            "status": "success",
            "message": f"Email sent successfully to {case.email}",
            "email_result": email_result,
            "audit_logged": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in email sending: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{customer_id}/audit-logs", response_model=List[AuditLogEntry])
async def get_case_audit_logs(customer_id: str):
    """Get audit logs for a case."""
    try:
        # Get case from database
        session = db_manager.get_session()
        case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
        
        if not case:
            session.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        session.close()
        
        # Get audit logs
        audit_logs = db_manager.get_audit_logs_by_case_id(case.id)
        
        # Convert to Pydantic models
        log_entries = []
        for log in audit_logs:
            log_entries.append(AuditLogEntry(**log))
        
        return log_entries
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in audit logs retrieval: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return login response."""
    try:
        result = auth_service.login(login_request.username, login_request.password)
        return LoginResponse(**result)
    except Exception as e:
        print(f"❌ Error in login: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/auth/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user), 
                session_id: Optional[str] = Header(None)):
    """Logout user and invalidate session."""
    try:
        if session_id:
            auth_service.logout(session_id)
        return {
            "success": True,
            "message": "Logout successful"
        }
    except Exception as e:
        print(f"❌ Error in logout: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@app.get("/api/auth/me", response_model=UserInfo)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    return UserInfo(**current_user)

@app.get("/api/auth/users")
async def list_users(current_user: Dict[str, Any] = Depends(get_admin_user)):
    """List all users (admin only)."""
    try:
        users = auth_service.list_users()
        return {
            "success": True,
            "users": users
        }
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@app.post("/api/documents/{document_id}/validate")
async def validate_document(document_id: str, validation_request: AdminDocumentValidationRequest,
                          current_user: Dict[str, Any] = Depends(get_admin_user)):
    """Update document validation status (admin only)."""
    try:
        # Get document from database
        session = db_manager.get_session()
        document = session.query(DBDocument).filter(DBDocument.document_id == document_id).first()
        
        if not document:
            session.close()
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update validation status
        document.validation_status = validation_request.status
        
        # Add notes to extracted_data if provided
        if validation_request.notes:
            current_data = json.loads(document.extracted_data) if document.extracted_data else {}
            current_data['validation_notes'] = validation_request.notes
            current_data['validation_timestamp'] = datetime.now().isoformat()
            current_data['validated_by'] = current_user['username']
            document.extracted_data = json.dumps(current_data)
        
        session.commit()
        session.close()
        
        return {
            "status": "success",
            "message": f"Document validation updated to {validation_request.status}",
            "document_id": document_id,
            "validation_status": validation_request.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in document validation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 
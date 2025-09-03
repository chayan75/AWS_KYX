import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Create database engine with absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(current_dir, 'kyc_database.db')}"
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class KYCCase(Base):
    """Model for storing KYC case information."""
    __tablename__ = "kyc_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)  # Customer email
    phone = Column(String)  # Customer phone
    dob = Column(String)
    nationality = Column(String)
    address = Column(Text)
    occupation = Column(String)
    employer = Column(String)
    annual_income = Column(Float)
    source_of_funds = Column(String)
    pep_status = Column(Boolean, default=False)
    business_name = Column(String)
    position = Column(String)
    university = Column(String)
    customer_type = Column(String)  # Individual, Business, PEP, Student, etc.
    estimated_risk_level = Column(String)  # Low, Medium, High
    
    # Case metadata
    status = Column(String, default="submitted")  # submitted, pending, approved, rejected
    submission_time = Column(DateTime, default=datetime.utcnow)
    completion_time = Column(DateTime)
    final_risk_level = Column(String)  # Low, Medium, High
    validation_status = Column(String)
    compliance_status = Column(String)
    
    # Relationships
    processing_steps = relationship("ProcessingStep", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")

class ProcessingStep(Base):
    """Model for storing individual processing steps for each KYC case."""
    __tablename__ = "processing_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("kyc_cases.id"), nullable=False)
    step_name = Column(String, nullable=False)  # coordinator_initiation, document_validation, etc.
    agent_id = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)  # coordinator, document_validation, risk_analysis, etc.
    
    # Timing
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    processing_duration = Column(Float)  # in seconds
    
    # Results
    status = Column(String, default="pending")  # pending, success, error
    input_data = Column(Text)  # JSON string of input data
    response_data = Column(Text)  # JSON string of response data
    error_message = Column(Text)
    
    # Relationships
    case = relationship("KYCCase", back_populates="processing_steps")

class Document(Base):
    """Model for storing document information for each KYC case."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("kyc_cases.id"), nullable=False)
    document_type = Column(String, nullable=False)  # id_proof, address_proof, employment_proof, etc.
    document_id = Column(String, nullable=False)  # actual document identifier
    filename = Column(String)  # stored filename
    original_filename = Column(String)  # original uploaded filename
    file_path = Column(String)  # path to stored file
    validation_status = Column(String, default="pending")  # pending, valid, invalid, missing
    extracted_data = Column(Text)  # JSON string of extracted data from document
    upload_time = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    case = relationship("KYCCase", back_populates="documents")

class AuditLog(Base):
    """Model for storing audit trail of all case activities."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("kyc_cases.id"), nullable=False)
    action_type = Column(String, nullable=False)  # status_update, email_sent, manual_review, case_archive, etc.
    action_details = Column(Text)  # JSON string with action details
    performed_by = Column(String, default="system")  # admin user or system
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)  # IP address of the user who performed the action
    user_agent = Column(String)  # User agent string
    
    # Relationships
    case = relationship("KYCCase", back_populates="audit_logs")

class DatabaseManager:
    """Manager class for database operations."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the database file exists and is properly initialized."""
        try:
            # Get the database file path
            db_path = self.engine.url.database
            if db_path != ':memory:':  # Skip for in-memory databases
                db_dir = os.path.dirname(db_path)
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"📁 Created database directory: {db_dir}")
            
            # Create tables if they don't exist
            self.create_tables()
            print(f"✅ Database initialized successfully: {db_path}")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise
    
    def create_tables(self):
        """Create all database tables if they don't exist."""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created/verified successfully")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise
    
    def check_database_connection(self) -> bool:
        """Check if the database connection is working."""
        try:
            session = self.get_session()
            # Try a simple query using SQLAlchemy text
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """Get database information."""
        try:
            db_path = self.engine.url.database
            db_exists = os.path.exists(db_path) if db_path != ':memory:' else True
            db_size = os.path.getsize(db_path) if db_exists and db_path != ':memory:' else 0
            
            session = self.get_session()
            case_count = session.query(KYCCase).count()
            document_count = session.query(Document).count()
            step_count = session.query(ProcessingStep).count()
            session.close()
            
            return {
                "database_path": db_path,
                "database_exists": db_exists,
                "database_size_bytes": db_size,
                "database_size_mb": round(db_size / (1024 * 1024), 2) if db_size > 0 else 0,
                "total_cases": case_count,
                "total_documents": document_count,
                "total_processing_steps": step_count
            }
        except Exception as e:
            return {
                "error": str(e),
                "database_path": self.engine.url.database
            }
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def create_kyc_case(self, customer_data: dict) -> int:
        """Create a new KYC case in the database and return its ID."""
        session = self.get_session()
        try:
            # Create the case
            case = KYCCase(
                customer_id=customer_data.get('customer_id'),
                name=customer_data.get('name'),
                email=customer_data.get('email'),
                phone=customer_data.get('phone'),
                dob=customer_data.get('dob'),
                nationality=customer_data.get('nationality'),
                address=customer_data.get('address'),
                occupation=customer_data.get('occupation'),
                employer=customer_data.get('employer'),
                annual_income=customer_data.get('annual_income'),
                source_of_funds=customer_data.get('source_of_funds'),
                pep_status=customer_data.get('pep_status', False),
                business_name=customer_data.get('business_name'),
                position=customer_data.get('position'),
                university=customer_data.get('university'),
                customer_type=customer_data.get('customer_type'),
                estimated_risk_level=customer_data.get('estimated_risk_level')
            )
            
            session.add(case)
            session.commit()
            case_id = case.id
            
            # Add documents
            documents = customer_data.get('documents', {})
            for doc_type, doc_id in documents.items():
                document = Document(
                    case_id=case_id,
                    document_type=doc_type,
                    document_id=doc_id
                )
                session.add(document)
            
            session.commit()
            return case_id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_processing_step(self, case_id: int, step_name: str, agent_id: str, 
                          agent_type: str, input_data: dict, response_data: dict = None,
                          error_message: str = None) -> ProcessingStep:
        """Add a processing step to a KYC case."""
        session = self.get_session()
        try:
            step = ProcessingStep(
                case_id=case_id,
                step_name=step_name,
                agent_id=agent_id,
                agent_type=agent_type,
                input_data=json.dumps(input_data),
                response_data=json.dumps(response_data) if response_data else None,
                error_message=error_message
            )
            
            session.add(step)
            session.commit()
            session.refresh(step)
            return step
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_processing_step(self, step_id: int, end_time: datetime = None, 
                             status: str = None, response_data: dict = None,
                             error_message: str = None):
        """Update a processing step with results."""
        session = self.get_session()
        try:
            step = session.query(ProcessingStep).filter(ProcessingStep.id == step_id).first()
            if step:
                if end_time:
                    step.end_time = end_time
                    step.processing_duration = (end_time - step.start_time).total_seconds()
                if status:
                    step.status = status
                if response_data:
                    step.response_data = json.dumps(response_data)
                if error_message:
                    step.error_message = error_message
                
                session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_case_status(self, case_id: int, status: str = None, 
                          final_risk_level: str = None, validation_status: str = None,
                          compliance_status: str = None, completion_time: datetime = None,
                          pep_status: bool = None):
        """Update the status of a KYC case."""
        session = self.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.id == case_id).first()
            if case:
                if status:
                    case.status = status
                if final_risk_level:
                    case.final_risk_level = final_risk_level
                if validation_status:
                    case.validation_status = validation_status
                if compliance_status:
                    case.compliance_status = compliance_status
                if completion_time:
                    case.completion_time = completion_time
                if pep_status is not None:
                    case.pep_status = pep_status
                
                session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_all_cases(self) -> list:
        """Get all KYC cases with their processing steps."""
        session = self.get_session()
        try:
            cases = session.query(KYCCase).all()
            return cases
        finally:
            session.close()
    
    def get_case_by_id(self, case_id: int) -> KYCCase:
        """Get a specific KYC case by ID."""
        session = self.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.id == case_id).first()
            return case
        finally:
            session.close()
    
    def get_case_by_customer_id(self, customer_id: str) -> KYCCase:
        """Get a specific KYC case by customer ID."""
        session = self.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
            return case
        finally:
            session.close()
    
    def get_case_details_by_customer_id(self, customer_id: str) -> dict:
        """Get case details with all relationships loaded as a dictionary."""
        session = self.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
            if not case:
                return None
            
            # Load all relationships while session is still open
            processing_steps = []
            for step in case.processing_steps:
                step_data = {
                    'id': step.id,
                    'step_name': step.step_name,
                    'agent_type': step.agent_type,
                    'agent_id': step.agent_id,
                    'status': step.status,
                    'start_time': step.start_time.isoformat() if step.start_time else None,
                    'end_time': step.end_time.isoformat() if step.end_time else None,
                    'processing_duration': step.processing_duration,
                    'input_data': json.loads(step.input_data) if step.input_data else None,
                    'response_data': json.loads(step.response_data) if step.response_data else None,
                    'error_message': step.error_message
                }
                processing_steps.append(step_data)
            
            documents = []
            for doc in case.documents:
                doc_data = {
                    'id': doc.id,
                    'document_type': doc.document_type,
                    'document_id': doc.document_id,
                    'validation_status': doc.validation_status,
                    'filename': doc.filename,
                    'original_filename': doc.original_filename,
                    'file_path': doc.file_path,
                    'extracted_data': json.loads(doc.extracted_data) if doc.extracted_data else None,
                    'upload_time': doc.upload_time.isoformat() if doc.upload_time else None
                }
                documents.append(doc_data)
            
            case_data = {
                'id': case.id,
                'customer_id': case.customer_id,
                'name': case.name,
                'email': case.email,
                'phone': case.phone,
                'dob': case.dob,
                'nationality': case.nationality,
                'address': case.address,
                'occupation': case.occupation,
                'employer': case.employer,
                'annual_income': case.annual_income,
                'source_of_funds': case.source_of_funds,
                'pep_status': case.pep_status,
                'business_name': case.business_name,
                'position': case.position,
                'university': case.university,
                'customer_type': case.customer_type,
                'estimated_risk_level': case.estimated_risk_level,
                'status': case.status,
                'submission_time': case.submission_time.isoformat() if case.submission_time else None,
                'completion_time': case.completion_time.isoformat() if case.completion_time else None,
                'final_risk_level': case.final_risk_level,
                'validation_status': case.validation_status,
                'compliance_status': case.compliance_status,
                'processing_steps': processing_steps,
                'documents': documents
            }
            
            return case_data
            
        finally:
            session.close()
    
    def customer_exists(self, customer_id: str) -> bool:
        """Check if a customer ID already exists in the database."""
        session = self.get_session()
        try:
            case = session.query(KYCCase).filter(KYCCase.customer_id == customer_id).first()
            return case is not None
        finally:
            session.close()
    
    def generate_unique_customer_id(self) -> str:
        """Generate a unique customer ID by finding the highest existing number and incrementing it."""
        session = self.get_session()
        try:
            # Get all existing customer IDs that match the CUST pattern
            existing_customers = session.query(KYCCase.customer_id).filter(
                KYCCase.customer_id.like('CUST%')
            ).all()
            
            if not existing_customers:
                # No existing customers, start with CUST001
                return "CUST001"
            
            # Extract numbers from existing customer IDs
            customer_numbers = []
            for (customer_id,) in existing_customers:
                if customer_id and customer_id.startswith('CUST'):
                    try:
                        # Extract the number part after "CUST"
                        number_part = customer_id[4:]  # Remove "CUST" prefix
                        if number_part.isdigit():
                            customer_numbers.append(int(number_part))
                    except (ValueError, IndexError):
                        continue
            
            if not customer_numbers:
                # No valid numbered customers found, start with CUST001
                return "CUST001"
            
            # Find the highest number and increment
            next_number = max(customer_numbers) + 1
            return f"CUST{next_number:03d}"
            
        finally:
            session.close()
    
    def get_or_create_case(self, customer_data: dict) -> int:
        """Get existing case ID or create a new one if it doesn't exist."""
        customer_id = customer_data.get('customer_id')
        if customer_id and self.customer_exists(customer_id):
            # Return existing case ID
            case = self.get_case_by_customer_id(customer_id)
            return case.id
        else:
            # Create new case
            return self.create_kyc_case(customer_data)
    
    def get_dashboard_data(self) -> dict:
        """Get data for the admin dashboard."""
        session = self.get_session()
        try:
            # Get summary statistics
            total_cases = session.query(KYCCase).count()
            pending_cases = session.query(KYCCase).filter(KYCCase.status == "pending").count()
            approved_cases = session.query(KYCCase).filter(KYCCase.status == "approved").count()
            high_risk_cases = session.query(KYCCase).filter(KYCCase.final_risk_level == "High").count()
            
            # Get all cases for dashboard
            cases = session.query(KYCCase).all()
            dashboard_cases = []
            
            for case in cases:
                # Calculate progress based on processing steps
                total_steps = len(case.processing_steps)
                completed_steps = len([step for step in case.processing_steps if step.status == "success"])
                progress = min(100, (completed_steps / max(total_steps, 1)) * 100)
                
                # Get documents
                documents = [doc.document_type for doc in case.documents]
                
                dashboard_cases.append({
                    'id': case.customer_id,
                    'name': case.name,
                    'type': self._get_customer_type(case),
                    'status': case.status,
                    'riskLevel': case.final_risk_level.lower() if case.final_risk_level else 'unknown',
                    'submittedDate': case.submission_time.strftime('%Y-%m-%d') if case.submission_time else 'N/A',
                    'lastUpdated': case.completion_time.strftime('%Y-%m-%d') if case.completion_time else case.submission_time.strftime('%Y-%m-%d'),
                    'documents': documents,
                    'progress': int(progress)
                })
            
            return {
                'summary': {
                    'total_cases': total_cases,
                    'pending_cases': pending_cases,
                    'approved_cases': approved_cases,
                    'high_risk_cases': high_risk_cases
                },
                'cases': dashboard_cases
            }
            
        finally:
            session.close()
    
    def _get_customer_type(self, case: KYCCase) -> str:
        """Determine customer type based on case data."""
        if case.pep_status:
            return 'PEP'
        elif case.business_name:
            return 'Business'
        elif case.university:
            return 'Student'
        elif case.occupation == 'Freelance Developer':
            return 'Freelancer'
        else:
            return 'Individual'
    
    def add_document(self, case_id: int, document_type: str, document_id: str, 
                    filename: str = None, original_filename: str = None, 
                    file_path: str = None, extracted_data: dict = None) -> Document:
        """Add a document to a KYC case."""
        session = self.get_session()
        try:
            document = Document(
                case_id=case_id,
                document_type=document_type,
                document_id=document_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                extracted_data=json.dumps(extracted_data) if extracted_data else None
            )
            
            session.add(document)
            session.commit()
            session.refresh(document)
            return document
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_document(self, document_id: int, validation_status: str = None, 
                       extracted_data: dict = None):
        """Update document information."""
        session = self.get_session()
        try:
            document = session.query(Document).filter(Document.id == document_id).first()
            if document:
                if validation_status:
                    document.validation_status = validation_status
                if extracted_data:
                    document.extracted_data = json.dumps(extracted_data)
                
                session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_documents_by_case_id(self, case_id: int) -> list:
        """Get all documents for a specific case."""
        session = self.get_session()
        try:
            documents = session.query(Document).filter(Document.case_id == case_id).all()
            return documents
        finally:
            session.close()
    
    def get_document_by_id(self, document_id: int) -> Document:
        """Get document by ID."""
        session = self.get_session()
        document = session.query(Document).filter(Document.id == document_id).first()
        session.close()
        return document
    
    def add_audit_log(self, case_id: int, action_type: str, action_details: dict, 
                     performed_by: str = "system", ip_address: str = None, 
                     user_agent: str = None) -> AuditLog:
        """Add an audit log entry."""
        session = self.get_session()
        try:
            audit_log = AuditLog(
                case_id=case_id,
                action_type=action_type,
                action_details=json.dumps(action_details),
                performed_by=performed_by,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(audit_log)
            session.commit()
            session.refresh(audit_log)
            return audit_log
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_audit_logs_by_case_id(self, case_id: int) -> list:
        """Get all audit logs for a case."""
        session = self.get_session()
        try:
            audit_logs = session.query(AuditLog).filter(
                AuditLog.case_id == case_id
            ).order_by(AuditLog.timestamp.desc()).all()
            
            # Convert to dictionary format
            logs = []
            for log in audit_logs:
                logs.append({
                    "id": log.id,
                    "action_type": log.action_type,
                    "action_details": json.loads(log.action_details) if log.action_details else {},
                    "performed_by": log.performed_by,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent
                })
            
            return logs
        finally:
            session.close()
    
    def get_audit_logs_by_action_type(self, action_type: str, limit: int = 100) -> list:
        """Get audit logs by action type."""
        session = self.get_session()
        try:
            audit_logs = session.query(AuditLog).filter(
                AuditLog.action_type == action_type
            ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
            
            # Convert to dictionary format
            logs = []
            for log in audit_logs:
                logs.append({
                    "id": log.id,
                    "case_id": log.case_id,
                    "action_type": log.action_type,
                    "action_details": json.loads(log.action_details) if log.action_details else {},
                    "performed_by": log.performed_by,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent
                })
            
            return logs
        finally:
            session.close()

# Create database manager instance
db_manager = DatabaseManager() 
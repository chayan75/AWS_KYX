import os
import json
import boto3
from dotenv import load_dotenv
from typing import Dict, List, Any
import logging
from datetime import datetime
import time
from database import db_manager
from document_processor import document_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class KYCProcessor:
    def __init__(self):
        """Initialize the KYC processor with Bedrock client and agent configurations."""
        # Database is automatically initialized by DatabaseManager
        print("🔧 Initializing KYC Processor...")
        
        self.bedrock_agent_runtime = boto3.client(
            service_name='bedrock-agent-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Agent IDs from environment variables (removed data_storage and workflow_automation)
        self.agent_ids = {
            'coordinator': os.getenv('KYC_COORDINATOR_AGENT_ID'),
            'document_validation': os.getenv('DOCUMENT_VALIDATION_AGENT_ID'),
            'risk_analysis': os.getenv('RISK_ANALYSIS_AGENT_ID'),
            'compliance': os.getenv('COMPLIANCE_AGENT_ID'),
            'customer_interaction': os.getenv('CUSTOMER_INTERACTION_AGENT_ID'),
            'real_time_feedback': os.getenv('REAL_TIME_FEEDBACK_AGENT_ID'),
            'task_prioritization': os.getenv('TASK_PRIORITIZATION_AGENT_ID'),
            'sanction_screening': os.getenv('SANCTION_SCREENING_AGENT_ID'),
            'feedback_learning': os.getenv('FEEDBACK_LOOP_LEARNING_AGENT_ID')
        }
        
        # Initialize session state
        self.session_state = {}
        self.kyc_cases = {}
        
        print("✅ KYC Processor initialized successfully")

    def invoke_bedrock_agent(self, agent_id: str, input_data: Dict[str, Any], case_id: int = None, step_name: str = None, agent_type: str = None) -> Dict[str, Any]:
        """
        Invoke a Bedrock agent with the given input data.
        
        Args:
            agent_id: The ID of the Bedrock agent to invoke
            input_data: The input data for the agent
            case_id: Database case ID for tracking
            step_name: Name of the processing step
            agent_type: Type of agent (coordinator, document_validation, etc.)
            
        Returns:
            The agent's response
        """
        start_time = datetime.now()
        processing_step = None
        
        try:
            if not agent_id:
                logger.warning(f"Agent ID not configured for agent type")
                return {"status": "error", "message": "Agent ID not configured"}
            
            # Create processing step in database if case_id is provided
            if case_id and step_name and agent_type:
                processing_step = db_manager.add_processing_step(
                    case_id=case_id,
                    step_name=step_name,
                    agent_id=agent_id,
                    agent_type=agent_type,
                    input_data=input_data
                )
            
            # Prepare the input for the Bedrock agent
            agent_input = {
                "input": {
                    "customer_data": input_data.get('customer_data', {}),
                    "session_context": self.session_state.get(agent_id, {}),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # Convert to JSON string
            input_body = json.dumps(agent_input)
            
            logger.info(f"Invoking Bedrock agent {agent_id} with input: {input_body[:200]}...")
            
            # Make the API call to Bedrock Agent Runtime
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId='TSTALIASID',  # Use the test alias ID
                sessionId=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                inputText=input_body
            )
            
            # Handle the streaming response correctly
            response_body = ""
            event_count = 0
            
            try:
                # The response is a streaming response - iterate through the EventStream
                if 'completion' in response:
                    for event in response['completion']:
                        event_count += 1
                        logger.debug(f"Event {event_count}: {list(event.keys())}")
                        
                        # Handle different event types
                        if 'chunk' in event:
                            chunk = event['chunk']
                            if 'bytes' in chunk:
                                chunk_text = chunk['bytes'].decode('utf-8')
                                response_body += chunk_text
                                logger.debug(f"Added chunk bytes: {chunk_text}")
                            elif 'attribution' in chunk:
                                logger.debug(f"Attribution: {chunk['attribution']}")
                        
                        elif 'trace' in event:
                            trace = event['trace']
                            logger.debug(f"Trace: {trace}")
                            
                        elif 'returnControl' in event:
                            return_control = event['returnControl']
                            logger.debug(f"Return Control: {return_control}")
                            
                        elif 'internalServerException' in event:
                            error = event['internalServerException']
                            logger.error(f"Internal Server Exception: {error}")
                            
                        elif 'validationException' in event:
                            error = event['validationException']
                            logger.error(f"Validation Exception: {error}")
                            
                        elif 'resourceNotFoundException' in event:
                            error = event['resourceNotFoundException']
                            logger.error(f"Resource Not Found Exception: {error}")
                            
                        elif 'accessDeniedException' in event:
                            error = event['accessDeniedException']
                            logger.error(f"Access Denied Exception: {error}")
                            
                        elif 'conflictException' in event:
                            error = event['conflictException']
                            logger.error(f"Conflict Exception: {error}")
                            
                        elif 'dependencyFailedException' in event:
                            error = event['dependencyFailedException']
                            logger.error(f"Dependency Failed Exception: {error}")
                            
                        elif 'badGatewayException' in event:
                            error = event['badGatewayException']
                            logger.error(f"Bad Gateway Exception: {error}")
                            
                        elif 'throttlingException' in event:
                            error = event['throttlingException']
                            logger.error(f"Throttling Exception: {error}")
                            
                        elif 'serviceQuotaExceededException' in event:
                            error = event['serviceQuotaExceededException']
                            logger.error(f"Service Quota Exceeded Exception: {error}")
                            
                        else:
                            logger.debug(f"Unknown event type: {event}")
                else:
                    logger.warning("No 'completion' found in response")
                    logger.debug(f"Available keys: {list(response.keys())}")
                        
            except Exception as stream_error:
                logger.warning(f"Error processing event stream: {stream_error}")
                # Fallback: try to get completion directly
                if hasattr(response, 'completion'):
                    response_body = response.completion
                else:
                    response_body = str(response)
            
            logger.info(f"Processed {event_count} events")
            logger.info(f"Raw response body length: {len(response_body)}")
            logger.info(f"Raw response body: {repr(response_body)}")
            
            # If response is empty, try a simpler input format
            if not response_body.strip():
                logger.warning("Empty response received, trying simpler input format...")
                return self.try_simple_input_format(agent_id, input_data, case_id, processing_step)
            
            try:
                # Try to parse as JSON first
                result = json.loads(response_body)
            except json.JSONDecodeError:
                # If not JSON, treat as plain text and create a structured response
                result = {
                    "status": "success",
                    "response_text": response_body,
                    "raw_response": response_body
                }
            
            # Update session state
            self.session_state[agent_id] = {
                "last_invocation": datetime.now().isoformat(),
                "input_data": input_data,
                "response": result
            }
            
            # Update processing step in database
            if processing_step:
                db_manager.update_processing_step(
                    step_id=processing_step.id,
                    end_time=datetime.now(),
                    status="success",
                    response_data=result
                )
            
            logger.info(f"Agent {agent_id} response received successfully")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            error_result = {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update processing step with error
            if processing_step:
                db_manager.update_processing_step(
                    step_id=processing_step.id,
                    end_time=end_time,
                    status="error",
                    error_message=str(e)
                )
            
            logger.error(f"Error invoking Bedrock agent {agent_id}: {str(e)}")
            return error_result

    def try_simple_input_format(self, agent_id: str, input_data: Dict[str, Any], case_id: int = None, processing_step = None) -> Dict[str, Any]:
        """Try a simpler input format if the complex format returns empty response."""
        try:
            customer_data = input_data.get('customer_data', {})
            
            # Create a simple text input
            simple_input = f"""
Customer Information:
Name: {customer_data.get('name', 'N/A')}
Customer ID: {customer_data.get('customer_id', 'N/A')}
Documents: {list(customer_data.get('documents', {}).keys())}

Please process this KYC request and provide your analysis.
"""
            
            logger.info(f"Trying simple input format for agent {agent_id}")
            
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId='TSTALIASID',
                sessionId=f"session_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                inputText=simple_input
            )
            
            response_body = ""
            if 'completion' in response:
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            response_body += chunk['bytes'].decode('utf-8')
                        elif 'attribution' in chunk:
                            logger.debug(f"Attribution: {chunk['attribution']}")
            
            logger.info(f"Simple format response: {repr(response_body)}")
            
            if response_body.strip():
                result = {
                    "status": "success",
                    "response_text": response_body,
                    "raw_response": response_body,
                    "input_format": "simple"
                }
                
                # Update processing step in database
                if processing_step:
                    db_manager.update_processing_step(
                        step_id=processing_step.id,
                        end_time=datetime.now(),
                        status="success",
                        response_data=result
                    )
                
                return result
            else:
                error_result = {
                    "status": "error",
                    "message": "Agent returned empty response with both input formats",
                    "agent_id": agent_id
                }
                
                # Update processing step in database
                if processing_step:
                    db_manager.update_processing_step(
                        step_id=processing_step.id,
                        end_time=datetime.now(),
                        status="error",
                        error_message="Agent returned empty response with both input formats"
                    )
                
                return error_result
                
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "agent_id": agent_id,
                "input_format": "simple"
            }
            
            # Update processing step in database
            if processing_step:
                db_manager.update_processing_step(
                    step_id=processing_step.id,
                    end_time=datetime.now(),
                    status="error",
                    error_message=str(e)
                )
            
            logger.error(f"Error with simple input format: {str(e)}")
            return error_result

    def process_customer_submission(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a customer submission from the customer portal.
        
        Args:
            customer_data: The customer data submitted through the portal
            
        Returns:
            The processing result
        """
        try:
            # Generate customer ID if not provided
            if 'customer_id' not in customer_data:
                customer_data['customer_id'] = db_manager.generate_unique_customer_id()
            
            customer_id = customer_data['customer_id']
            
            # Enhance customer data with extracted document information
            enhanced_customer_data = self.enhance_customer_data_with_documents(customer_data)
            
            # Create case in database
            case_id = db_manager.get_or_create_case(enhanced_customer_data)
            
            # Add documents to database if they exist
            self.add_documents_to_database(case_id, customer_data.get('documents', {}))
            
            print(f"\n=== Customer Portal: New KYC Submission ===")
            print(f"Customer ID: {customer_id}")
            print(f"Name: {enhanced_customer_data.get('name', 'N/A')}")
            print(f"Email: {enhanced_customer_data.get('email', 'N/A')}")
            print(f"Phone: {enhanced_customer_data.get('phone', 'N/A')}")
            print(f"Address: {enhanced_customer_data.get('address', 'N/A')}")
            print(f"Documents: {list(customer_data.get('documents', {}).keys())}")
            
            # 1. Start with the KYC Coordinator
            print(f"\n1. KYC Coordinator: Initiating workflow...")
            coordinator_response = self.invoke_bedrock_agent(
                self.agent_ids['coordinator'],
                {'customer_data': enhanced_customer_data},
                case_id=case_id,
                step_name='coordinator_initiation',
                agent_type='coordinator'
            )
            
            # 2. Document Validation
            print(f"2. Document Validation: Processing documents...")
            validation_response = self.invoke_bedrock_agent(
                self.agent_ids['document_validation'],
                {'customer_data': enhanced_customer_data},
                case_id=case_id,
                step_name='document_validation',
                agent_type='document_validation'
            )
            
            # 3. Risk Analysis
            print(f"3. Risk Analysis: Evaluating risk profile...")
            risk_response = self.invoke_bedrock_agent(
                self.agent_ids['risk_analysis'],
                {'customer_data': enhanced_customer_data},
                case_id=case_id,
                step_name='risk_analysis',
                agent_type='risk_analysis'
            )
            
            # 4. Sanction Screening (for all cases to be thorough)
            print(f"4. Sanction Screening: Checking against sanction lists...")
            sanction_response = self.invoke_bedrock_agent(
                self.agent_ids['sanction_screening'],
                {'customer_data': enhanced_customer_data},
                case_id=case_id,
                step_name='sanction_screening',
                agent_type='sanction_screening'
            )
            
            # Extract PEP status from sanction screening results and update customer data
            sanction_results = self.extract_agent_results(sanction_response, 'sanction_screening_results')
            if sanction_results and isinstance(sanction_results, dict):
                # Check if PEP match was found
                if sanction_results.get('screening_status') == 'match_found':
                    matches = sanction_results.get('matches', [])
                    for match in matches:
                        if match.get('source') == 'PEP':
                            enhanced_customer_data['pep_status'] = True
                            enhanced_customer_data['pep_details'] = match.get('match_details', '')
                            print(f"⚠️  PEP Status Detected: {match.get('entity_name')} - {match.get('match_details')}")
                            
                            # Update database with PEP status
                            db_manager.update_case_status(
                                case_id=case_id,
                                pep_status=True
                            )
                            print(f"✅ PEP Status updated in database for case {case_id}")
                            break
            
            # 5. Compliance Check
            print(f"5. Compliance Check: Ensuring regulatory compliance...")
            
            # Prepare comprehensive data for compliance check including all previous agent results
            compliance_input_data = {
                'customer_data': enhanced_customer_data,
                'agent_results': {
                    'document_validation': self.extract_agent_results(validation_response, 'document_validation_results'),
                    'risk_analysis': self.extract_agent_results(risk_response, 'risk_analysis_results'),
                    'sanction_screening': self.extract_agent_results(sanction_response, 'sanction_screening_results')
                },
                'processing_timeline': {
                    'document_validation_time': datetime.now().isoformat(),
                    'risk_analysis_time': datetime.now().isoformat(),
                    'sanction_screening_time': datetime.now().isoformat()
                }
            }
            
            compliance_response = self.invoke_bedrock_agent(
                self.agent_ids['compliance'],
                compliance_input_data,
                case_id=case_id,
                step_name='compliance_check',
                agent_type='compliance'
            )
            
            # Determine final status based on agent responses
            validation_status = self.extract_status_from_response(validation_response, 'validation_status')
            compliance_status = self.extract_status_from_response(compliance_response, 'compliance_status')
            
            final_status = 'approved'
            if validation_status == 'incomplete' or compliance_status == 'warning':
                final_status = 'pending'
            elif validation_status == 'error' or compliance_status == 'violation':
                final_status = 'rejected'
            
            # Extract risk level from risk response
            risk_level = self.extract_risk_level(risk_response)
            
            # Update case status in database
            db_manager.update_case_status(
                case_id=case_id,
                status=final_status,
                final_risk_level=risk_level,
                validation_status=validation_status,
                compliance_status=compliance_status,
                completion_time=datetime.now(),
                pep_status=enhanced_customer_data.get('pep_status', False)
            )
            
            print(f"\n=== Processing Complete ===")
            print(f"Final Status: {final_status}")
            print(f"Risk Level: {risk_level}")
            
            return {
                'status': 'success',
                'customer_id': customer_id,
                'case_id': case_id,
                'final_status': final_status,
                'risk_level': risk_level,
                'validation_status': validation_status,
                'compliance_status': compliance_status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing customer submission: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'customer_id': customer_data.get('customer_id', 'Unknown'),
                'timestamp': datetime.now().isoformat()
            }

    def extract_status_from_response(self, response: Dict[str, Any], status_key: str) -> str:
        """Extract status from agent response."""
        if isinstance(response, dict):
            return response.get(status_key, 'unknown')
        elif isinstance(response, str):
            # Try to extract status from text response
            if 'complete' in response.lower() or 'success' in response.lower():
                return 'complete'
            elif 'incomplete' in response.lower() or 'pending' in response.lower():
                return 'incomplete'
            elif 'error' in response.lower() or 'failed' in response.lower():
                return 'error'
        return 'unknown'

    def extract_risk_level(self, risk_response: Dict[str, Any]) -> str:
        """Extract risk level from risk analysis response."""
        if isinstance(risk_response, dict):
            # Check for nested structure first
            if 'risk_analysis_results' in risk_response:
                return risk_response['risk_analysis_results'].get('risk_classification', 'Unknown')
            # Check direct structure
            elif 'risk_classification' in risk_response:
                return risk_response.get('risk_classification', 'Unknown')
            # Check in response_text if it's a string
            elif 'response_text' in risk_response and isinstance(risk_response['response_text'], str):
                response_text = risk_response['response_text']
                try:
                    # Try to parse JSON from response_text
                    import json
                    parsed = json.loads(response_text)
                    if 'risk_analysis_results' in parsed:
                        return parsed['risk_analysis_results'].get('risk_classification', 'Unknown')
                    elif 'risk_classification' in parsed:
                        return parsed.get('risk_classification', 'Unknown')
                except:
                    pass
        elif isinstance(risk_response, str):
            # Try to extract risk level from text response
            if 'high' in risk_response.lower():
                return 'High'
            elif 'medium' in risk_response.lower():
                return 'Medium'
            elif 'low' in risk_response.lower():
                return 'Low'
        return 'Unknown'

    def extract_agent_results(self, response: Dict[str, Any], result_key: str) -> Dict[str, Any]:
        """Extract actual results from agent response."""
        if isinstance(response, dict):
            if result_key in response:
                return response[result_key]
            elif 'response_text' in response and isinstance(response['response_text'], str):
                try:
                    import json
                    parsed = json.loads(response['response_text'])
                    if result_key in parsed:
                        return parsed[result_key]
                except:
                    pass
        return response

    def enhance_customer_data_with_documents(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance customer data with information extracted from documents."""
        enhanced_data = customer_data.copy()
        
        # Initialize comprehensive data structure
        comprehensive_data = {
            # Basic customer information
            "name": customer_data.get('name', ''),
            "email": customer_data.get('email', ''),
            "phone": customer_data.get('phone', ''),
            "address": customer_data.get('address', ''),
            
            # ID and personal information
            "customer_id": customer_data.get('customer_id', ''),
            "dob": customer_data.get('dob', ''),
            "nationality": customer_data.get('nationality', ''),
            
            # Employment and financial information
            "occupation": customer_data.get('occupation', ''),
            "employer": customer_data.get('employer', ''),
            "annual_income": customer_data.get('annual_income'),
            "source_of_funds": customer_data.get('source_of_funds', ''),
            
            # Business information (if applicable)
            "business_name": customer_data.get('business_name', ''),
            "position": customer_data.get('position', ''),
            "university": customer_data.get('university', ''),
            
            # Risk and compliance information
            "pep_status": customer_data.get('pep_status', False),
            
            # Document information
            "documents": customer_data.get('documents', {}),
            "document_details": {},
            
            # Processing metadata
            "submission_time": datetime.now().isoformat(),
            "processing_status": "submitted"
        }
        
        # Get documents from the documents directory
        documents_dir = os.path.join(os.path.dirname(__file__), 'documents')
        
        for doc_type, doc_id in customer_data.get('documents', {}).items():
            # Find the document file
            for filename in os.listdir(documents_dir):
                if filename.startswith(f"{doc_type}_{doc_id}"):
                    file_path = os.path.join(documents_dir, filename)
                    
                    # Extract information from the document
                    extract_result = document_processor.extract_info_from_document(file_path, doc_type)
                    
                    if extract_result["status"] == "success":
                        extracted_data = extract_result["data"]
                        
                        # Store document details
                        comprehensive_data["document_details"][doc_type] = {
                            "document_id": doc_id,
                            "filename": filename,
                            "extracted_data": extracted_data,
                            "validation_status": "pending"
                        }
                        
                        # Enhance customer data based on document type
                        if doc_type == "id_proof":
                            comprehensive_data.update({
                                'name': f"{extracted_data.get('first_name', '')} {extracted_data.get('last_name', '')}".strip() or comprehensive_data['name'],
                                'dob': extracted_data.get('dob') or comprehensive_data['dob'],
                                'nationality': extracted_data.get('nationality') or comprehensive_data['nationality'],
                            })
                            
                        elif doc_type == "address_proof":
                            comprehensive_data.update({
                                'address': extracted_data.get('full_address') or comprehensive_data['address'],
                            })
                            
                        elif doc_type == "employment_proof":
                            comprehensive_data.update({
                                'employer': extracted_data.get('employer_name') or comprehensive_data['employer'],
                                'occupation': extracted_data.get('position') or comprehensive_data['occupation'],
                                'annual_income': self.parse_salary(extracted_data.get('annual_salary')) or comprehensive_data['annual_income'],
                            })
                    
                    else:
                        # Document extraction failed, but still store basic info
                        comprehensive_data["document_details"][doc_type] = {
                            "document_id": doc_id,
                            "filename": filename,
                            "extracted_data": None,
                            "validation_status": "extraction_failed",
                            "error": extract_result.get("error", "Unknown error")
                        }
                    
                    break
        
        # Determine customer type based on enhanced data
        comprehensive_data["customer_type"] = self.determine_customer_type(comprehensive_data)
        
        # Calculate estimated risk level based on available data
        comprehensive_data["estimated_risk_level"] = self.calculate_estimated_risk(comprehensive_data)
        
        return comprehensive_data

    def determine_customer_type(self, customer_data: Dict[str, Any]) -> str:
        """Determine customer type based on available data."""
        if customer_data.get('pep_status'):
            return 'PEP'
        elif customer_data.get('business_name'):
            return 'Business'
        elif customer_data.get('university'):
            return 'Student'
        elif customer_data.get('occupation') == 'Freelance Developer':
            return 'Freelancer'
        elif customer_data.get('annual_income') is not None and customer_data.get('annual_income', 0) > 200000:
            return 'High_Net_Worth'
        else:
            return 'Individual'

    def calculate_estimated_risk(self, customer_data: Dict[str, Any]) -> str:
        """Calculate estimated risk level based on available data."""
        risk_score = 0
        
        # PEP status (high risk)
        if customer_data.get('pep_status'):
            risk_score += 50
        
        # High income (medium risk)
        annual_income = customer_data.get('annual_income')
        if annual_income is not None:  # Only compare if annual_income is not None
            if annual_income > 500000:
                risk_score += 30
            elif annual_income > 200000:
                risk_score += 15
        
        # Business owner (medium risk)
        if customer_data.get('business_name'):
            risk_score += 20
        
        # Government position (medium risk)
        if customer_data.get('position') and 'government' in customer_data.get('position', '').lower():
            risk_score += 25
        
        # Missing documents (increased risk)
        required_docs = ['id_proof', 'address_proof', 'employment_proof']
        missing_docs = len([doc for doc in required_docs if doc not in customer_data.get('documents', {})])
        risk_score += missing_docs * 10
        
        # Determine risk level
        if risk_score >= 50:
            return 'High'
        elif risk_score >= 25:
            return 'Medium'
        else:
            return 'Low'

    def add_documents_to_database(self, case_id: int, documents: Dict[str, str]):
        """Add documents to the database."""
        documents_dir = os.path.join(os.path.dirname(__file__), 'documents')
        
        for doc_type, doc_id in documents.items():
            # Find the document file
            for filename in os.listdir(documents_dir):
                if filename.startswith(f"{doc_type}_{doc_id}"):
                    file_path = os.path.join(documents_dir, filename)
                    
                    # Extract information from the document
                    extract_result = document_processor.extract_info_from_document(file_path, doc_type)
                    
                    # Add document to database
                    db_manager.add_document(
                        case_id=case_id,
                        document_type=doc_type,
                        document_id=doc_id,
                        filename=filename,
                        file_path=file_path,
                        extracted_data=extract_result.get("data") if extract_result["status"] == "success" else None
                    )
                    break

    def parse_salary(self, salary_str: str) -> float:
        """Parse salary string to float."""
        if not salary_str:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = salary_str.replace('$', '').replace(',', '').replace('£', '').replace('€', '')
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the admin dashboard.
        
        Returns:
            Dashboard data with all KYC cases and statistics
        """
        return db_manager.get_dashboard_data()

def main():
    """Run the KYC processing scenarios."""
    # Initialize the KYC processor
    kyc_processor = KYCProcessor()
    
    print("=== KYC Agentic Flow Demo ===\n")
    
    # Scenario 1: Standard Individual Account
    print("SCENARIO 1: Standard Individual Account (Low Risk)")
    print("=" * 50)
    
    scenario1_data = {
        "name": "John Smith",
        "customer_id": "CUST001",
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
    if result1['status'] == 'success':
        print(f"\nScenario 1 Result: {result1['final_status']}")
    else:
        print(f"\nScenario 1 Error: {result1.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Scenario 2: Small Business Owner
    print("SCENARIO 2: Small Business Owner (Medium Risk)")
    print("=" * 50)
    
    scenario2_data = {
        "name": "Sarah Johnson",
        "dob": "1980-08-22",
        "customer_id": "CUST002",
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
    if result2['status'] == 'success':
        print(f"\nScenario 2 Result: {result2['final_status']}")
    else:
        print(f"\nScenario 2 Error: {result2.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Scenario 3: PEP Account
    print("SCENARIO 3: PEP Account (High Risk)")
    print("=" * 50)
    
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
    
    result3 = kyc_processor.process_customer_submission(scenario3_data)
    if result3['status'] == 'success':
        print(f"\nScenario 3 Result: {result3['final_status']}")
    else:
        print(f"\nScenario 3 Error: {result3.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Display Admin Dashboard Data
    print("ADMIN DASHBOARD DATA")
    print("=" * 50)
    
    dashboard_data = kyc_processor.get_admin_dashboard_data()
    
    print(f"\nSummary:")
    print(f"- Total Cases: {dashboard_data['summary']['total_cases']}")
    print(f"- Pending Cases: {dashboard_data['summary']['pending_cases']}")
    print(f"- Approved Cases: {dashboard_data['summary']['approved_cases']}")
    print(f"- High Risk Cases: {dashboard_data['summary']['high_risk_cases']}")
    
    print(f"\nCase Details:")
    for case in dashboard_data['cases']:
        print(f"- {case['id']}: {case['name']} ({case['type']}) - {case['status'].upper()} - Risk: {case['riskLevel'].upper()} - Progress: {case['progress']}%")
    
    print(f"\n=== Demo Complete ===")

if __name__ == "__main__":
    main() 
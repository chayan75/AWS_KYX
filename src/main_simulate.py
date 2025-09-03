import os
import json
import boto3
from dotenv import load_dotenv
from typing import Dict, List, Any
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class KYCProcessor:
    def __init__(self):
        """Initialize the KYC processor with Bedrock client and agent configurations."""
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Agent IDs from environment variables
        self.agent_ids = {
            'coordinator': os.getenv('KYC_COORDINATOR_AGENT_ID'),
            'document_validation': os.getenv('DOCUMENT_VALIDATION_AGENT_ID'),
            'risk_analysis': os.getenv('RISK_ANALYSIS_AGENT_ID'),
            'compliance': os.getenv('COMPLIANCE_AGENT_ID'),
            'customer_interaction': os.getenv('CUSTOMER_INTERACTION_AGENT_ID'),
            'real_time_feedback': os.getenv('REAL_TIME_FEEDBACK_AGENT_ID'),
            'workflow_automation': os.getenv('WORKFLOW_AUTOMATION_AGENT_ID'),
            'task_prioritization': os.getenv('TASK_PRIORITIZATION_AGENT_ID'),
            'sanction_screening': os.getenv('SANCTION_SCREENING_AGENT_ID'),
            'data_storage': os.getenv('DATA_STORAGE_AUDIT_AGENT_ID'),
            'feedback_learning': os.getenv('FEEDBACK_LOOP_LEARNING_AGENT_ID')
        }
        
        # Initialize session state and case tracking
        self.session_state = {}
        self.kyc_cases = {}
        self.case_counter = 1

    def invoke_bedrock_agent(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a Bedrock agent with the given input data.
        
        Args:
            agent_id: The ID of the Bedrock agent to invoke
            input_data: The input data for the agent
            
        Returns:
            The agent's response
        """
        try:
            # For demo purposes, simulate agent responses based on the updated YAML templates
            return self.simulate_agent_response(agent_id, input_data)
        except Exception as e:
            logger.error(f"Error invoking Bedrock agent {agent_id}: {str(e)}")
            raise

    def simulate_agent_response(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent responses based on the updated YAML templates."""
        customer_data = input_data.get('customer_data', {})
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        if agent_id == self.agent_ids.get('coordinator'):
            return self.simulate_coordinator_response(customer_data)
        elif agent_id == self.agent_ids.get('document_validation'):
            return self.simulate_document_validation_response(customer_data)
        elif agent_id == self.agent_ids.get('risk_analysis'):
            return self.simulate_risk_analysis_response(customer_data)
        elif agent_id == self.agent_ids.get('compliance'):
            return self.simulate_compliance_response(input_data)
        elif agent_id == self.agent_ids.get('customer_interaction'):
            return self.simulate_customer_interaction_response(customer_data)
        elif agent_id == self.agent_ids.get('real_time_feedback'):
            return self.simulate_real_time_feedback_response(customer_data)
        elif agent_id == self.agent_ids.get('workflow_automation'):
            return self.simulate_workflow_automation_response(customer_data)
        elif agent_id == self.agent_ids.get('task_prioritization'):
            return self.simulate_task_prioritization_response(customer_data)
        elif agent_id == self.agent_ids.get('sanction_screening'):
            return self.simulate_sanction_screening_response(customer_data)
        elif agent_id == self.agent_ids.get('data_storage'):
            return self.simulate_data_storage_response(customer_data)
        elif agent_id == self.agent_ids.get('feedback_learning'):
            return self.simulate_feedback_learning_response(customer_data)
        else:
            return {"status": "unknown_agent", "message": f"Agent {agent_id} not found"}

    def simulate_coordinator_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate KYC Coordinator response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        return {
            "selected_agents": ["document_validation_agent", "risk_analysis_agent", "compliance_monitoring_agent"],
            "agent_tasks": {
                "document_validation_agent": "Validate customer documents for completeness and accuracy",
                "risk_analysis_agent": "Evaluate customer risk profile using KYC/AML rules",
                "compliance_monitoring_agent": "Ensure regulatory compliance throughout the process"
            },
            "workflow_status": "initiated",
            "customer_id": customer_id
        }

    def simulate_document_validation_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Document Validation Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        # Different validation results based on customer type
        if 'CUST001' in customer_id:
            return {
                "validation_status": "complete",
                "missing_fields": [],
                "invalid_fields": [],
                "validation_report": "All required documents and information are present and valid. Documents include valid US passport, recent utility bill, and employment verification.",
                "next_actions": ["Proceed with risk assessment", "Initiate standard monitoring"]
            }
        elif 'CUST002' in customer_id:
            return {
                "validation_status": "complete",
                "missing_fields": [],
                "invalid_fields": [],
                "validation_report": "All required documents are present and valid. Includes valid UK passport, current bank statement, and business registration documents.",
                "next_actions": ["Proceed with risk assessment", "Initiate enhanced monitoring for business account"]
            }
        elif 'CUST003' in customer_id:
            return {
                "validation_status": "complete",
                "missing_fields": [],
                "invalid_fields": [],
                "validation_report": "All required documents are present and valid. Includes valid government ID, ministry letter, and current address proof. PEP status properly documented.",
                "next_actions": ["Proceed with enhanced due diligence", "Escalate to senior management", "Initiate strict monitoring"]
            }
        else:
            return {
                "validation_status": "incomplete",
                "missing_fields": ["Student visa documentation"],
                "invalid_fields": ["Bank statement (older than 3 months)"],
                "validation_report": "Missing student visa documentation. Bank statement needs to be more recent (within 3 months).",
                "next_actions": ["Request valid student visa", "Request current bank statement (within 3 months)"]
            }

    def simulate_risk_analysis_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Risk Analysis Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        if 'CUST001' in customer_id:
            return {
                "risk_classification": "Low",
                "risk_score": 15,
                "risk_factors": ["Employment-based income", "Low-risk country (US)", "Standard transaction patterns"],
                "recommendations": ["Standard monitoring", "Annual review"],
                "requires_edd": False,
                "analysis_details": "Customer presents low risk due to stable employment, US residency, and standard financial profile."
            }
        elif 'CUST002' in customer_id:
            return {
                "risk_classification": "Medium",
                "risk_score": 45,
                "risk_factors": ["Business income source", "Higher transaction volumes", "Business ownership complexity"],
                "recommendations": ["Enhanced due diligence", "Quarterly review", "Transaction monitoring"],
                "requires_edd": True,
                "analysis_details": "Medium risk due to business ownership and higher transaction volumes. Requires enhanced monitoring."
            }
        elif 'CUST003' in customer_id:
            return {
                "risk_classification": "High",
                "risk_score": 85,
                "risk_factors": ["PEP status", "Government position", "High-value transactions"],
                "recommendations": ["Senior management approval", "Enhanced due diligence", "Monthly review", "Strict transaction monitoring"],
                "requires_edd": True,
                "analysis_details": "High risk due to PEP status and government position. Requires strict monitoring and senior approval."
            }
        else:
            return {
                "risk_classification": "Medium",
                "risk_score": 35,
                "risk_factors": ["Foreign national", "Family funding source", "Limited transaction history"],
                "recommendations": ["Regular monitoring", "Documentation review", "Transaction limits"],
                "requires_edd": False,
                "analysis_details": "Medium risk due to foreign status and family funding. Requires regular monitoring and documentation review."
            }

    def simulate_compliance_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Compliance Monitoring Agent response."""
        # Extract customer data and agent results from input
        customer_data = input_data.get('customer_data', {})
        agent_results = input_data.get('agent_results', {})
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        # Get results from previous agents
        doc_validation = agent_results.get('document_validation', {})
        risk_analysis = agent_results.get('risk_analysis', {})
        sanction_screening = agent_results.get('sanction_screening', {})
        
        if 'CUST003' in customer_id:  # PEP case
            return {
                "compliance_status": "compliant",
                "violations": [],
                "audit_entries": [
                    {"timestamp": "2024-03-20T10:00:00Z", "action": "Document validation completed", "agent": "document_validation_agent", "result": "success"},
                    {"timestamp": "2024-03-20T10:01:00Z", "action": "Risk assessment completed", "agent": "risk_analysis_agent", "result": "success"},
                    {"timestamp": "2024-03-20T10:02:00Z", "action": "PEP screening completed", "agent": "sanction_list_screening_agent", "result": "success"}
                ],
                "regulatory_report": f"All compliance requirements met. Document validation: {doc_validation.get('validation_status', 'unknown')}, Risk assessment: {risk_analysis.get('risk_classification', 'unknown')}, PEP screening: {sanction_screening.get('screening_status', 'unknown')}. Enhanced due diligence required as per PEP regulations."
            }
        elif 'CUST004' in customer_id:  # Student case
            return {
                "compliance_status": "warning",
                "violations": ["Missing student visa documentation", "Outdated bank statement"],
                "audit_entries": [
                    {"timestamp": "2024-03-20T10:00:00Z", "action": "Document validation completed", "agent": "document_validation_agent", "result": "incomplete"},
                    {"timestamp": "2024-03-20T10:01:00Z", "action": "Risk assessment completed", "agent": "risk_analysis_agent", "result": "success"},
                    {"timestamp": "2024-03-20T10:02:00Z", "action": "Sanction screening completed", "agent": "sanction_list_screening_agent", "result": "success"}
                ],
                "regulatory_report": f"Compliance warning: Document validation incomplete ({doc_validation.get('validation_status', 'unknown')}), Risk assessment: {risk_analysis.get('risk_classification', 'unknown')}, Sanction screening: {sanction_screening.get('screening_status', 'unknown')}. Additional documents required before approval."
            }
        else:
            return {
                "compliance_status": "compliant",
                "violations": [],
                "audit_entries": [
                    {"timestamp": "2024-03-20T10:00:00Z", "action": "Document validation completed", "agent": "document_validation_agent", "result": "success"},
                    {"timestamp": "2024-03-20T10:01:00Z", "action": "Risk assessment completed", "agent": "risk_analysis_agent", "result": "success"},
                    {"timestamp": "2024-03-20T10:02:00Z", "action": "Sanction screening completed", "agent": "sanction_list_screening_agent", "result": "success"}
                ],
                "regulatory_report": f"All compliance requirements met. Document validation: {doc_validation.get('validation_status', 'unknown')}, Risk assessment: {risk_analysis.get('risk_classification', 'unknown')}, Sanction screening: {sanction_screening.get('screening_status', 'unknown')}. Standard monitoring recommended."
            }

    def simulate_customer_interaction_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Customer Interaction Agent response."""
        return {
            "interaction_type": "email",
            "customer_query": "What documents do I need to provide?",
            "response": "You need to provide three types of documents: 1) ID Proof (passport, driver's license, or national ID), 2) Address Proof (utility bill or bank statement), and 3) Employment/Income Proof (salary slip, employment letter, or tax return).",
            "next_steps": ["Upload ID proof", "Upload address proof", "Upload employment proof"],
            "escalation_required": False,
            "interaction_status": "resolved"
        }

    def simulate_real_time_feedback_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Real-time Feedback Agent response."""
        return {
            "notification_type": "app_notification",
            "message": "Great! Your ID proof has been successfully validated.",
            "action_required": "Continue with remaining documents",
            "upload_link": "https://kyc-portal.com/upload",
            "status": "sent"
        }

    def simulate_workflow_automation_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Workflow Automation Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        if 'CUST003' in customer_id:  # PEP case
            return {
                "workflow_id": f"WF_{customer_id}_001",
                "current_state": "escalated",
                "next_actions": ["Escalate to senior management", "Initiate strict monitoring"],
                "triggered_agents": ["document_validation_agent", "risk_analysis_agent", "sanction_list_screening_agent", "compliance_monitoring_agent"],
                "dependencies_met": True,
                "execution_log": "Document validation completed. Risk assessment: High risk (PEP). Sanction screening: Clear. Escalated for senior approval."
            }
        else:
            return {
                "workflow_id": f"WF_{customer_id}_001",
                "current_state": "completed",
                "next_actions": ["Initiate standard monitoring", "Schedule annual review"],
                "triggered_agents": ["document_validation_agent", "risk_analysis_agent", "compliance_monitoring_agent"],
                "dependencies_met": True,
                "execution_log": "Document validation completed successfully. Risk assessment: Low risk. Compliance check: Passed. Workflow completed."
            }

    def simulate_task_prioritization_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Task Prioritization Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        if 'CUST003' in customer_id:  # PEP case
            return {
                "task_queue": [
                    {
                        "task_id": f"TASK_{customer_id}_001",
                        "priority_level": 1,
                        "urgency_score": 95,
                        "deadline": "2024-03-21T10:00:00Z",
                        "assigned_agent": "risk_analysis_agent",
                        "estimated_duration": "30 minutes"
                    }
                ],
                "escalations": [f"TASK_{customer_id}_001"],
                "load_balance_recommendations": "PEP case requires immediate attention. Assign to senior agents."
            }
        else:
            return {
                "task_queue": [
                    {
                        "task_id": f"TASK_{customer_id}_001",
                        "priority_level": 3,
                        "urgency_score": 50,
                        "deadline": "2024-03-23T10:00:00Z",
                        "assigned_agent": "document_validation_agent",
                        "estimated_duration": "15 minutes"
                    }
                ],
                "escalations": [],
                "load_balance_recommendations": "Standard processing. Can be handled by any available agent."
            }

    def simulate_sanction_screening_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Sanction List Screening Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        if 'CUST003' in customer_id:  # PEP case
            return {
                "screening_status": "match_found",
                "matches": [
                    {
                        "source": "PEP",
                        "match_type": "exact",
                        "confidence_score": 100,
                        "entity_name": "Dr. Maria Rodriguez",
                        "match_details": "Deputy Minister of Finance, Spain - Confirmed PEP status"
                    }
                ],
                "recommendation": "investigate",
                "screening_date": "2024-03-20T10:00:00Z"
            }
        else:
            return {
                "screening_status": "clear",
                "matches": [],
                "recommendation": "proceed",
                "screening_date": "2024-03-20T10:00:00Z"
            }

    def simulate_data_storage_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Data Storage and Audit Agent response."""
        customer_id = customer_data.get('customer_id', 'UNKNOWN')
        
        return {
            "storage_status": "stored",
            "database_record_id": f"{customer_id}_20240320_001",
            "audit_log_entries": [
                {
                    "timestamp": "2024-03-20T10:00:00Z",
                    "agent": "document_validation_agent",
                    "action": "Document validation completed",
                    "data_affected": "Customer documents validated",
                    "result": "success"
                },
                {
                    "timestamp": "2024-03-20T10:01:00Z",
                    "agent": "risk_analysis_agent",
                    "action": "Risk assessment completed",
                    "data_affected": "Risk profile created",
                    "result": "success"
                }
            ],
            "compliance_flags": ["GDPR_compliant", "data_encrypted"],
            "retention_policy": "Retain for 7 years as per regulatory requirements"
        }

    def simulate_feedback_learning_response(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Feedback Loop and Learning Agent response."""
        return {
            "learning_insights": [
                {
                    "area": "Document Validation Accuracy",
                    "current_performance": "92% accuracy",
                    "improvement_suggestion": "Implement OCR enhancement for better text extraction from utility bills",
                    "confidence_level": 85
                }
            ],
            "model_updates": [
                {
                    "model_type": "document_validation",
                    "update_type": "parameter_adjust",
                    "expected_improvement": "Increase accuracy to 95% for address proof validation"
                }
            ],
            "workflow_optimizations": ["Automate utility bill validation", "Reduce manual review by 30%"],
            "implementation_priority": "high"
        }

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
                customer_data['customer_id'] = f"CUST{self.case_counter:03d}"
                self.case_counter += 1
            
            customer_id = customer_data['customer_id']
            
            # Store the case
            self.kyc_cases[customer_id] = {
                'customer_data': customer_data,
                'status': 'submitted',
                'submission_time': datetime.now().isoformat(),
                'processing_steps': []
            }
            
            print(f"\n=== Customer Portal: New KYC Submission ===")
            print(f"Customer ID: {customer_id}")
            print(f"Name: {customer_data.get('name', 'N/A')}")
            print(f"Documents: {list(customer_data.get('documents', {}).keys())}")
            
            # 1. Start with the KYC Coordinator
            print(f"\n1. KYC Coordinator: Initiating workflow...")
            coordinator_response = self.invoke_bedrock_agent(
                self.agent_ids['coordinator'],
                {'customer_data': customer_data}
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'coordinator_initiation',
                'timestamp': datetime.now().isoformat(),
                'result': coordinator_response
            })
            
            # 2. Document Validation
            print(f"2. Document Validation: Processing documents...")
            validation_response = self.invoke_bedrock_agent(
                self.agent_ids['document_validation'],
                {'customer_data': customer_data}
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'document_validation',
                'timestamp': datetime.now().isoformat(),
                'result': validation_response
            })
            
            # 3. Risk Analysis
            print(f"3. Risk Analysis: Evaluating risk profile...")
            risk_response = self.invoke_bedrock_agent(
                self.agent_ids['risk_analysis'],
                {'customer_data': customer_data}
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'risk_analysis',
                'timestamp': datetime.now().isoformat(),
                'result': risk_response
            })
            
            # 4. Sanction Screening (for PEP cases)
            if 'CUST003' in customer_id:  # PEP case
                print(f"4. Sanction Screening: Checking PEP status...")
                sanction_response = self.invoke_bedrock_agent(
                    self.agent_ids['sanction_screening'],
                    {'customer_data': customer_data}
                )
                self.kyc_cases[customer_id]['processing_steps'].append({
                    'step': 'sanction_screening',
                    'timestamp': datetime.now().isoformat(),
                    'result': sanction_response
                })
            
            # 5. Compliance Check
            print(f"5. Compliance Check: Ensuring regulatory compliance...")
            
            # Prepare comprehensive data for compliance check including all previous agent results
            compliance_input_data = {
                'customer_data': customer_data,
                'agent_results': {
                    'document_validation': validation_response,
                    'risk_analysis': risk_response,
                    'sanction_screening': sanction_response
                },
                'processing_timeline': {
                    'document_validation_time': datetime.now().isoformat(),
                    'risk_analysis_time': datetime.now().isoformat(),
                    'sanction_screening_time': datetime.now().isoformat()
                }
            }
            
            compliance_response = self.invoke_bedrock_agent(
                self.agent_ids['compliance'],
                compliance_input_data
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'compliance_check',
                'timestamp': datetime.now().isoformat(),
                'result': compliance_response
            })
            
            # 6. Workflow Automation
            print(f"6. Workflow Automation: Orchestrating process...")
            workflow_response = self.invoke_bedrock_agent(
                self.agent_ids['workflow_automation'],
                {'customer_data': customer_data}
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'workflow_automation',
                'timestamp': datetime.now().isoformat(),
                'result': workflow_response
            })
            
            # 7. Data Storage
            print(f"7. Data Storage: Storing customer record...")
            storage_response = self.invoke_bedrock_agent(
                self.agent_ids['data_storage'],
                {'customer_data': customer_data}
            )
            self.kyc_cases[customer_id]['processing_steps'].append({
                'step': 'data_storage',
                'timestamp': datetime.now().isoformat(),
                'result': storage_response
            })
            
            # Update case status
            final_status = 'approved' if validation_response.get('validation_status') == 'complete' else 'pending'
            self.kyc_cases[customer_id]['status'] = final_status
            self.kyc_cases[customer_id]['completion_time'] = datetime.now().isoformat()
            
            print(f"\n=== Processing Complete ===")
            print(f"Final Status: {final_status}")
            print(f"Risk Level: {risk_response.get('risk_classification', 'Unknown')}")
            
            return {
                'status': 'success',
                'customer_id': customer_id,
                'final_status': final_status,
                'risk_level': risk_response.get('risk_classification', 'Unknown'),
                'validation_status': validation_response.get('validation_status', 'Unknown'),
                'compliance_status': compliance_response.get('compliance_status', 'Unknown'),
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

    def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for the admin dashboard.
        
        Returns:
            Dashboard data with all KYC cases and statistics
        """
        total_cases = len(self.kyc_cases)
        pending_cases = len([case for case in self.kyc_cases.values() if case['status'] == 'pending'])
        approved_cases = len([case for case in self.kyc_cases.values() if case['status'] == 'approved'])
        
        # Get high-risk cases
        high_risk_cases = []
        for customer_id, case in self.kyc_cases.items():
            for step in case.get('processing_steps', []):
                if step['step'] == 'risk_analysis':
                    risk_result = step['result']
                    if risk_result.get('risk_classification') == 'High':
                        high_risk_cases.append(customer_id)
                    break
        
        # Format cases for dashboard
        dashboard_cases = []
        for customer_id, case in self.kyc_cases.items():
            customer_data = case['customer_data']
            
            # Get risk level
            risk_level = 'Unknown'
            for step in case.get('processing_steps', []):
                if step['step'] == 'risk_analysis':
                    risk_level = step['result'].get('risk_classification', 'Unknown')
                    break
            
            # Get documents
            documents = list(customer_data.get('documents', {}).keys())
            
            # Calculate progress
            total_steps = len(case.get('processing_steps', []))
            progress = min(100, (total_steps / 7) * 100)  # Assuming 7 main steps
            
            dashboard_cases.append({
                'id': customer_id,
                'name': customer_data.get('name', 'N/A'),
                'type': self.get_customer_type(customer_data),
                'status': case['status'],
                'riskLevel': risk_level.lower(),
                'submittedDate': case['submission_time'][:10],
                'lastUpdated': case.get('completion_time', case['submission_time'])[:10],
                'documents': documents,
                'progress': int(progress)
            })
        
        return {
            'summary': {
                'total_cases': total_cases,
                'pending_cases': pending_cases,
                'approved_cases': approved_cases,
                'high_risk_cases': len(high_risk_cases)
            },
            'cases': dashboard_cases
        }

    def get_customer_type(self, customer_data: Dict[str, Any]) -> str:
        """Determine customer type based on data."""
        if customer_data.get('pep_status'):
            return 'PEP'
        elif customer_data.get('business_name'):
            return 'Business'
        elif customer_data.get('university'):
            return 'Student'
        elif customer_data.get('occupation') == 'Freelance Developer':
            return 'Freelancer'
        else:
            return 'Individual'

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
    print(f"\nScenario 1 Result: {result1['final_status']}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Scenario 2: Small Business Owner
    print("SCENARIO 2: Small Business Owner (Medium Risk)")
    print("=" * 50)
    
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
    print(f"\nScenario 2 Result: {result2['final_status']}")
    
    print("\n" + "=" * 80 + "\n")
    
    # Scenario 3: PEP Account
    print("SCENARIO 3: PEP Account (High Risk)")
    print("=" * 50)
    
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
    print(f"\nScenario 3 Result: {result3['final_status']}")
    
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
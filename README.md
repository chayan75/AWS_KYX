# KYC Agentic Flow System

A comprehensive Know Your Customer (KYC) processing system using AWS Bedrock agents with customer portal and admin dashboard integration.

## 🏗️ Architecture

The system consists of:

### Frontend Applications
- **Customer Portal**: React-based interface for document upload and status tracking
- **Admin Dashboard**: React-based interface for monitoring KYC processes

### Backend System
- **KYC Processor**: Python-based orchestrator for AWS Bedrock agents
- **Agent Templates**: YAML configurations for 11 specialized KYC agents

### Agent Types
1. **KYC Coordinator** - Supervises the entire KYC process
2. **Document Validation Agent** - Validates customer documents
3. **Risk Analysis Agent** - Evaluates customer risk profiles
4. **Compliance Monitoring Agent** - Ensures regulatory compliance
5. **Customer Interaction Agent** - Handles customer communication
6. **Real-time Feedback Agent** - Provides immediate feedback
7. **Workflow Automation Agent** - Orchestrates KYC workflows
8. **Task Prioritization Agent** - Manages task scheduling
9. **Sanction List Screening Agent** - Screens against watchlists
10. **Data Storage and Audit Agent** - Manages data and audit trails
11. **Feedback Loop and Learning Agent** - Continuous improvement

## 📋 Required Documents

The system processes three types of documents:
- **ID Proof**: Government-issued identification (passport, driver's license, national ID)
- **Address Proof**: Utility bills, bank statements, or government correspondence
- **Employment/Income Proof**: Salary slips, employment letters, tax returns, or business registration

## 🚀 Quick Start

### 1. AWS Bedrock Setup

Before running the system, you need to set up AWS Bedrock agents:

#### Prerequisites
- AWS Account with Bedrock access
- AWS CLI configured with appropriate permissions
- Python 3.8+ installed

#### Create Bedrock Agents
1. **Access AWS Bedrock Console**: Go to AWS Bedrock console in your region
2. **Create Agents**: Create 11 agents using the YAML templates in `src/templates/`
3. **Deploy Agents**: Deploy each agent and note their Agent IDs
4. **Create Test Alias**: Create a test alias for each agent (default: `TSTALIASID`)

#### Agent Creation Steps
```bash
# For each agent template in src/templates/
aws bedrock create-agent \
  --agent-name "KYC Coordinator" \
  --description "Coordinates KYC workflow" \
  --instruction "Use the provided YAML template content"
```

### 2. Environment Setup

Create a `.env` file in the root directory using the template:

```bash
# Copy the environment template
cp env_template.txt .env

# Edit the .env file with your actual values
```

Required environment variables:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

# Bedrock Agent IDs (replace with your actual agent IDs)
KYC_COORDINATOR_AGENT_ID=your_kyc_coordinator_agent_id
DOCUMENT_VALIDATION_AGENT_ID=your_document_validation_agent_id
RISK_ANALYSIS_AGENT_ID=your_risk_analysis_agent_id
COMPLIANCE_AGENT_ID=your_compliance_agent_id
CUSTOMER_INTERACTION_AGENT_ID=your_customer_interaction_agent_id
REAL_TIME_FEEDBACK_AGENT_ID=your_real_time_feedback_agent_id
WORKFLOW_AUTOMATION_AGENT_ID=your_workflow_automation_agent_id
TASK_PRIORITIZATION_AGENT_ID=your_task_prioritization_agent_id
SANCTION_SCREENING_AGENT_ID=your_sanction_screening_agent_id
DATA_STORAGE_AUDIT_AGENT_ID=your_data_storage_audit_agent_id
FEEDBACK_LOOP_LEARNING_AGENT_ID=your_feedback_loop_learning_agent_id
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test Bedrock Connection

Before running the main application, test your Bedrock agent connection:

```bash
cd src
python test_bedrock_connection.py
```

This will verify:
- ✅ AWS credentials are properly configured
- ✅ Bedrock Agent Runtime client can be initialized
- ✅ Agent IDs are correctly set
- ✅ Basic agent invocation works

### 5. Run the Demo Scenarios

```bash
cd src
python demo_scenarios.py
```

### 6. Run with Live Bedrock Agents

```bash
cd src
python main.py
```

## 📊 Demo Scenarios

The system includes three comprehensive scenarios:

### Scenario 1: Standard Individual Account (Low Risk)
- **Customer**: John Smith, US Software Engineer
- **Documents**: US Passport, Utility Bill, Salary Slip
- **Risk Level**: Low
- **Expected Outcome**: Approved with standard monitoring

### Scenario 2: Small Business Owner (Medium Risk)
- **Customer**: Sarah Johnson, UK Business Owner
- **Documents**: UK Passport, Bank Statement, Business Registration
- **Risk Level**: Medium
- **Expected Outcome**: Approved with enhanced monitoring

### Scenario 3: PEP Account (High Risk)
- **Customer**: Dr. Maria Rodriguez, Spanish Government Official
- **Documents**: Spanish Passport, Government ID, Ministry Letter
- **Risk Level**: High
- **Expected Outcome**: Approved with strict monitoring and senior management approval

## 🔄 Workflow Process

### Customer Portal Flow
1. **Document Upload**: Customer uploads three required documents
2. **Real-time Feedback**: Immediate validation feedback
3. **Status Tracking**: Real-time status updates
4. **Communication**: Automated notifications and guidance

### Admin Portal Flow
1. **Case Monitoring**: Real-time view of all KYC cases
2. **Risk Assessment**: Automated risk classification
3. **Compliance Check**: Regulatory compliance validation
4. **Decision Making**: Final approval/rejection with reasoning

### Agentic Processing Flow
1. **KYC Coordinator** initiates the workflow
2. **Document Validation Agent** validates submitted documents
3. **Risk Analysis Agent** evaluates customer risk profile
4. **Sanction Screening Agent** checks against watchlists (for high-risk cases)
5. **Compliance Monitoring Agent** ensures regulatory compliance
6. **Workflow Automation Agent** orchestrates the process
7. **Data Storage Agent** securely stores customer records
8. **Real-time Feedback Agent** provides customer updates

## 🛠️ Development

### Running Individual Components

#### Backend Processing with Live Agents
```bash
cd src
python main.py
```

#### Backend Processing with Simulation
```bash
cd src
python main_simulate.py
```

#### Customer Portal (React)
```bash
cd customer-portal
npm install
npm start
```

#### Admin Dashboard (React)
```bash
cd admin-dashboard
npm install
npm start
```

### Agent Template Structure

Each agent template (`src/templates/*.yaml`) contains:
- **Agent Configuration**: Name, description, role, goals
- **Instructions**: Detailed processing instructions
- **Sample Data**: Realistic use cases and responses
- **Output Format**: Expected response structure

## 📈 Features

### Customer Portal Features
- ✅ Step-by-step document upload
- ✅ Real-time validation feedback
- ✅ Progress tracking
- ✅ Status notifications
- ✅ Mobile-responsive design

### Admin Dashboard Features
- ✅ Real-time case monitoring
- ✅ Risk level indicators
- ✅ Progress tracking
- ✅ Document status overview
- ✅ Compliance reporting
- ✅ Filtering and search

### Agentic Features
- ✅ Coordinated multi-agent processing
- ✅ Intelligent risk assessment
- ✅ Automated compliance checking
- ✅ Real-time feedback generation
- ✅ Audit trail maintenance
- ✅ Continuous learning and improvement

## 🔒 Security & Compliance

- **Data Encryption**: All data encrypted at rest and in transit
- **Access Controls**: Role-based access control
- **Audit Trails**: Complete audit logging
- **GDPR Compliance**: Privacy and data protection
- **Regulatory Compliance**: AML/KYC regulatory adherence

## 📝 API Documentation

The system provides RESTful APIs for:
- Customer document submission
- Status checking
- Admin dashboard data
- Agent interaction

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request



## 🔮 Future Enhancements

- [ ] Machine learning-based risk scoring
- [ ] Advanced document OCR
- [ ] Blockchain integration for audit trails
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Advanced analytics dashboard 
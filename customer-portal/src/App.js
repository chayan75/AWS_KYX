import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [customerData, setCustomerData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
  });
  const [documents, setDocuments] = useState({
    idProof: null,
    addressProof: null,
    employmentProof: null,
  });
  const [uploadStatus, setUploadStatus] = useState({});
  const [verificationStatus, setVerificationStatus] = useState('pending');
  const [submissionResult, setSubmissionResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationWarnings, setValidationWarnings] = useState([]);
  const [showValidationDialog, setShowValidationDialog] = useState(false);

  const steps = ['Personal Information', 'Document Upload', 'Verification Status'];

  const handleCustomerDataChange = (e) => {
    setCustomerData({
      ...customerData,
      [e.target.name]: e.target.value,
    });
  };

  const handleDocumentUpload = (documentType) => async (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadStatus({
        ...uploadStatus,
        [documentType]: 'uploading',
      });

      try {
        // Convert camelCase to snake_case for API
        const apiDocumentType = documentType
          .replace(/([A-Z])/g, '_$1')
          .toLowerCase()
          .replace(/^_/, ''); // Remove leading underscore

        const formData = new FormData();
        formData.append('document_type', apiDocumentType);
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/customer/upload-document`, {
          method: 'POST',
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          setDocuments({
            ...documents,
            [documentType]: {
              file: file,
              documentId: result.document_id,
              filename: result.filename,
              extractedData: result.extracted_data,
            },
          });
          setUploadStatus({
            ...uploadStatus,
            [documentType]: 'success',
          });
          
          // Validate document against entered customer data
          if (result.extracted_data && Object.keys(customerData).some(key => customerData[key])) {
            await validateDocumentAgainstCustomerData(result.extracted_data, apiDocumentType);
          }
        } else {
          setUploadStatus({
            ...uploadStatus,
            [documentType]: 'error',
          });
          console.error('Upload failed:', result);
        }
      } catch (error) {
        setUploadStatus({
          ...uploadStatus,
          [documentType]: 'error',
        });
        console.error('Upload error:', error);
      }
    }
  };

  const validateDocumentAgainstCustomerData = async (extractedData, documentType) => {
    try {
      const validationData = {
        extracted_data: extractedData,
        user_data: customerData,
        document_type: documentType
      };

      const response = await fetch(`${API_BASE_URL}/customer/validate-document`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(validationData),
      });

      if (response.ok) {
        const validationResult = await response.json();
        if (!validationResult.overall_match) {
          // Show validation warning immediately
          const warning = {
            type: 'document_mismatch',
            documentType: documentType,
            confidenceScore: validationResult.confidence_score,
            message: `${documentType.replace(/_/g, ' ').toUpperCase()} validation failed`,
            details: validationResult.discrepancies?.map(disc => 
              `${disc.field}: Document shows "${disc.document_value}" but you entered "${disc.user_value}"`
            ).join('; ') || 'Information mismatch detected',
            severity: validationResult.discrepancies?.some(d => d.severity === 'high') ? 'high' : 'medium'
          };
          
          setValidationWarnings([warning]);
          setShowValidationDialog(true);
        }
      }
    } catch (error) {
      console.error('Validation error:', error);
    }
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmitKYC = async () => {
    // Check if there are any validation warnings before submitting
    if (validationWarnings.length > 0) {
      setShowValidationDialog(true);
      return;
    }

    setIsSubmitting(true);
    try {
      // Prepare documents mapping with snake_case keys for API
      const documentsMapping = {};
      Object.keys(documents).forEach(key => {
        if (documents[key] && documents[key].documentId) {
          // Convert camelCase to snake_case for API
          const apiKey = key
            .replace(/([A-Z])/g, '_$1')
            .toLowerCase()
            .replace(/^_/, ''); // Remove leading underscore
          documentsMapping[apiKey] = documents[key].documentId;
        }
      });

      // Collect all validation warnings from uploaded documents
      const allValidationWarnings = [];
      
      // Validate each uploaded document against customer data
      for (const [docKey, docData] of Object.entries(documents)) {
        if (docData && docData.extractedData) {
          const apiDocType = docKey
            .replace(/([A-Z])/g, '_$1')
            .toLowerCase()
            .replace(/^_/, '');
          
          try {
            const validationData = {
              extracted_data: docData.extractedData,
              user_data: customerData,
              document_type: apiDocType
            };

            const validationResponse = await fetch(`${API_BASE_URL}/customer/validate-document`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(validationData),
            });

            if (validationResponse.ok) {
              const validationResult = await validationResponse.json();
              if (!validationResult.overall_match) {
                allValidationWarnings.push({
                  document_type: apiDocType,
                  document_id: docData.documentId,
                  confidence_score: validationResult.confidence_score,
                  discrepancies: validationResult.discrepancies,
                  warnings: validationResult.warnings
                });
              }
            }
          } catch (error) {
            console.error(`Validation error for ${apiDocType}:`, error);
          }
        }
      }

      const submissionData = {
        customer_data: customerData,
        documents: documentsMapping,
        validation_warnings: allValidationWarnings.length > 0 ? allValidationWarnings : null
      };

      const response = await fetch(`${API_BASE_URL}/customer/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submissionData),
      });

      const result = await response.json();

      if (response.ok) {
        // Check if there are validation warnings in the response
        if (result.validation_warnings && result.validation_warnings.length > 0) {
          // Process detailed validation warnings
          const detailedWarnings = result.validation_warnings.map(warning => {
            const discrepancies = warning.discrepancies || [];
            const discrepancyDetails = discrepancies.map(disc => 
              `${disc.field}: Document shows "${disc.document_value}" but you entered "${disc.user_value}"`
            ).join('; ');
            
            return {
              type: 'document_mismatch',
              documentType: warning.document_type,
              confidenceScore: warning.confidence_score,
              message: `${warning.document_type.replace(/_/g, ' ').toUpperCase()} validation failed`,
              details: discrepancyDetails || 'Information mismatch detected',
              severity: warning.discrepancies?.some(d => d.severity === 'high') ? 'high' : 'medium'
            };
          });
          
          setValidationWarnings(detailedWarnings);
          setShowValidationDialog(true);
          setIsSubmitting(false);
          return;
        }
        
        // Only set submission result and complete if no validation warnings
        setSubmissionResult(result);
        setVerificationStatus('completed');
      } else {
        setSubmissionResult({ status: 'error', message: result.detail || 'Submission failed' });
      }
    } catch (error) {
      setSubmissionResult({ status: 'error', message: 'Network error occurred' });
      console.error('Submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProceedWithWarnings = async () => {
    setShowValidationDialog(false);
    // Don't allow proceeding with warnings - user must fix the issues
    // The submission will be blocked until validation warnings are resolved
  };

  const handleFixValidationIssues = () => {
    setShowValidationDialog(false);
    setValidationWarnings([]);
    // Go back to step 1 to allow user to fix the issues
    setActiveStep(1);
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Personal Information
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Full Name"
                name="name"
                value={customerData.name}
                onChange={handleCustomerDataChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={customerData.email}
                onChange={handleCustomerDataChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Phone Number"
                name="phone"
                value={customerData.phone}
                onChange={handleCustomerDataChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Address"
                name="address"
                value={customerData.address}
                onChange={handleCustomerDataChange}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Document Upload
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Please upload the required documents. Our AI will automatically extract information from your documents.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    ID Proof
                  </Typography>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUploadIcon />}
                    fullWidth
                    disabled={uploadStatus.idProof === 'uploading'}
                  >
                    Upload ID
                    <input
                      type="file"
                      hidden
                      onChange={handleDocumentUpload('idProof')}
                      accept=".pdf,.jpg,.jpeg,.png"
                    />
                  </Button>
                  {uploadStatus.idProof === 'uploading' && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="body2">Processing...</Typography>
                    </Box>
                  )}
                  {uploadStatus.idProof === 'success' && (
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="success" icon={<CheckCircleIcon />}>
                        Uploaded successfully
                      </Alert>
                      {documents.idProof?.extractedData && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="textSecondary">
                            Extracted: {documents.idProof.extractedData.first_name} {documents.idProof.extractedData.last_name}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}
                  {uploadStatus.idProof === 'error' && (
                    <Alert severity="error" icon={<ErrorIcon />} sx={{ mt: 2 }}>
                      Upload failed
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Address Proof
                  </Typography>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUploadIcon />}
                    fullWidth
                    disabled={uploadStatus.addressProof === 'uploading'}
                  >
                    Upload Address Proof
                    <input
                      type="file"
                      hidden
                      onChange={handleDocumentUpload('addressProof')}
                      accept=".pdf,.jpg,.jpeg,.png"
                    />
                  </Button>
                  {uploadStatus.addressProof === 'uploading' && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="body2">Processing...</Typography>
                    </Box>
                  )}
                  {uploadStatus.addressProof === 'success' && (
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="success" icon={<CheckCircleIcon />}>
                        Uploaded successfully
                      </Alert>
                      {documents.addressProof?.extractedData && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="textSecondary">
                            Extracted: {documents.addressProof.extractedData.document_type}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}
                  {uploadStatus.addressProof === 'error' && (
                    <Alert severity="error" icon={<ErrorIcon />} sx={{ mt: 2 }}>
                      Upload failed
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Employment Proof
                  </Typography>
                  <Button
                    variant="contained"
                    component="label"
                    startIcon={<CloudUploadIcon />}
                    fullWidth
                    disabled={uploadStatus.employmentProof === 'uploading'}
                  >
                    Upload Employment Proof
                    <input
                      type="file"
                      hidden
                      onChange={handleDocumentUpload('employmentProof')}
                      accept=".pdf,.jpg,.jpeg,.png"
                    />
                  </Button>
                  {uploadStatus.employmentProof === 'uploading' && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      <Typography variant="body2">Processing...</Typography>
                    </Box>
                  )}
                  {uploadStatus.employmentProof === 'success' && (
                    <Box sx={{ mt: 2 }}>
                      <Alert severity="success" icon={<CheckCircleIcon />}>
                        Uploaded successfully
                      </Alert>
                      {documents.employmentProof?.extractedData && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="caption" color="textSecondary">
                            Extracted: {documents.employmentProof.extractedData.employer_name}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}
                  {uploadStatus.employmentProof === 'error' && (
                    <Alert severity="error" icon={<ErrorIcon />} sx={{ mt: 2 }}>
                      Upload failed
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Verification Status
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  {!submissionResult ? (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        Ready to Submit
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Please review your information and documents before submitting your KYC application.
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Personal Information
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Typography variant="body2"><strong>Name:</strong> {customerData.name}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2"><strong>Email:</strong> {customerData.email}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2"><strong>Phone:</strong> {customerData.phone}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="body2"><strong>Address:</strong> {customerData.address}</Typography>
                          </Grid>
                        </Grid>
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Documents
                        </Typography>
                        <Grid container spacing={1}>
                          {Object.keys(documents).map((docType) => (
                            <Grid item xs={12} key={docType}>
                              <Chip
                                label={`${docType.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}: ${documents[docType] ? 'Uploaded' : 'Not uploaded'}`}
                                color={documents[docType] ? 'success' : 'default'}
                                size="small"
                              />
                            </Grid>
                          ))}
                        </Grid>
                      </Box>
                      <Box sx={{ mt: 3 }}>
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={handleSubmitKYC}
                          disabled={isSubmitting}
                          fullWidth
                        >
                          {isSubmitting ? (
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <CircularProgress size={20} sx={{ mr: 1 }} />
                              Submitting...
                            </Box>
                          ) : (
                            'Submit KYC Application'
                          )}
                        </Button>
                      </Box>
                    </Box>
                  ) : (
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        Submission Result
                      </Typography>
                      {submissionResult.status === 'success' ? (
                        <Alert severity="success" sx={{ mb: 2 }}>
                          <Typography variant="h6">Application Submitted Successfully!</Typography>
                          <Typography variant="body2">
                            Your KYC application has been submitted and is being processed.
                          </Typography>
                        </Alert>
                      ) : (
                        <Alert severity="error" sx={{ mb: 2 }}>
                          <Typography variant="h6">Submission Failed</Typography>
                          <Typography variant="body2">
                            {submissionResult.message}
                          </Typography>
                        </Alert>
                      )}
                      {submissionResult.status === 'success' && (
                        <Box>
                          <Typography variant="subtitle2" gutterBottom>
                            Application Details
                          </Typography>
                          <Grid container spacing={2}>
                            <Grid item xs={6}>
                              <Typography variant="body2"><strong>Customer ID:</strong> {submissionResult.customer_id}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2"><strong>Case ID:</strong> {submissionResult.case_id}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2"><strong>Status:</strong> {submissionResult.final_status}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="body2"><strong>Risk Level:</strong> {submissionResult.risk_level}</Typography>
                            </Grid>
                          </Grid>
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="body2" color="textSecondary">
                              You can track your application status using your Customer ID: <strong>{submissionResult.customer_id}</strong>
                            </Typography>
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          KYC Verification Portal
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          {activeStep < steps.length - 1 && (
            <Button
              variant="contained"
              onClick={handleNext}
            >
              Next
            </Button>
          )}
        </Box>
      </Paper>

      {/* Validation Warning Dialog */}
      <Dialog
        open={showValidationDialog}
        onClose={() => setShowValidationDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', color: 'error.main' }}>
          <ErrorIcon sx={{ mr: 1 }} />
          Document Validation Errors
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="body1" gutterBottom>
              We found discrepancies between your entered information and the documents you uploaded.
            </Typography>
            <Typography variant="body2">
              <strong>You must fix these issues before submitting your KYC application.</strong>
            </Typography>
          </Alert>
          
          <Typography variant="h6" gutterBottom>
            Validation Details:
          </Typography>
          
          <List>
            {validationWarnings.map((warning, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="subtitle1" color={warning.severity === 'high' ? 'error.main' : 'warning.main'}>
                          {warning.message}
                        </Typography>
                        <Chip 
                          label={`${warning.confidenceScore}% confidence`}
                          color={warning.confidenceScore > 70 ? 'success' : warning.confidenceScore > 50 ? 'warning' : 'error'}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                          <strong>Document Type:</strong> {warning.documentType.replace(/_/g, ' ').toUpperCase()}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          <strong>Discrepancies:</strong> {warning.details}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < validationWarnings.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
          
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Action Required:</strong> Please review your entered information and uploaded documents. 
              Make sure the names, addresses, and other details match exactly between your form and documents.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowValidationDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleFixValidationIssues}
            variant="contained"
            color="primary"
          >
            Fix Issues & Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App; 
import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import Login from './Login';
import { apiFetch } from './api';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Snackbar,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Schedule,
  Person,
  Business,
  School,
  Work,
  Visibility,
  Refresh,
  ThumbUp,
  ThumbDown,
  Help,
  ExpandMore,
  Timer,
  Security,
  Description,
  Assessment,
  Search,
  ZoomIn,
  ZoomOut,
  Download,
  Cancel,
} from '@mui/icons-material';

const API_BASE_URL = 'http://localhost:8000/api';

function DashboardApp() {
  const { user, loading, logout, hasPermission } = useAuth();
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [kycCases, setKycCases] = useState([]);
  const [dashboardLoading, setDashboardLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseDetailsOpen, setCaseDetailsOpen] = useState(false);
  const [manualReviewOpen, setManualReviewOpen] = useState(false);
  const [reviewAction, setReviewAction] = useState('');
  const [reviewNotes, setReviewNotes] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [showArchived, setShowArchived] = useState(false);
  
  // Document modal state
  const [documentModalOpen, setDocumentModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentContent, setDocumentContent] = useState(null);
  const [documentLoading, setDocumentLoading] = useState(false);
  const [imageZoom, setImageZoom] = useState(1);
  const [validationStatus, setValidationStatus] = useState('pending');
  const [validationNotes, setValidationNotes] = useState('');
  
  // Case management state
  const [caseManagementOpen, setCaseManagementOpen] = useState(false);
  const [caseManagementType, setCaseManagementType] = useState(''); // 'archive', 'update'
  const [caseUpdateData, setCaseUpdateData] = useState({
    risk_level: '',
    pep_status: false,
    case_status: '',
    notes: ''
  });
  
  // Email and audit state
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [auditModalOpen, setAuditModalOpen] = useState(false);
  const [emailData, setEmailData] = useState({
    email_type: 'status_update',
    subject: '',
    message: '',
    additional_notes: '',
    required_documents: [],
    reason: ''
  });
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditLoading, setAuditLoading] = useState(false);

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setDashboardLoading(true);
      const data = await apiFetch(`${API_BASE_URL}/dashboard`);
      setKycCases(data.cases || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setSnackbar({ open: true, message: 'Error loading dashboard data', severity: 'error' });
    } finally {
      setDashboardLoading(false);
    }
  };

  const fetchCaseDetails = async (customerId) => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${customerId}`);
      setSelectedCase(data);
      setCaseDetailsOpen(true);
    } catch (error) {
      console.error('Error fetching case details:', error);
      setSnackbar({ open: true, message: 'Error loading case details', severity: 'error' });
    }
  };

  const handleManualReview = async () => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${selectedCase.customer_id}/manual-review`, {
        method: 'POST',
        body: JSON.stringify({ action: reviewAction, notes: reviewNotes }),
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: data.message, severity: 'success' });
        setManualReviewOpen(false);
        setReviewAction('');
        setReviewNotes('');
        fetchDashboardData(); // Refresh data
      } else {
        setSnackbar({ open: true, message: data.error, severity: 'error' });
      }
    } catch (error) {
      console.error('Error performing manual review:', error);
      setSnackbar({ open: true, message: 'Error performing manual review', severity: 'error' });
    }
  };

  const handleRetryProcessing = async (customerId) => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${customerId}/retry`, {
        method: 'POST',
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: data.message, severity: 'success' });
        fetchDashboardData(); // Refresh data
      } else {
        setSnackbar({ open: true, message: data.error, severity: 'error' });
      }
    } catch (error) {
      console.error('Error retrying processing:', error);
      setSnackbar({ open: true, message: 'Error retrying processing', severity: 'error' });
    }
  };

  const handleDocumentValidation = async () => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/documents/${selectedDocument.document_id}/validate`, {
        method: 'POST',
        body: JSON.stringify({ 
          status: validationStatus, 
          notes: validationNotes 
        }),
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: data.message, severity: 'success' });
        setDocumentModalOpen(false);
        setValidationStatus('pending');
        setValidationNotes('');
        fetchDashboardData(); // Refresh data
      } else {
        setSnackbar({ open: true, message: data.error, severity: 'error' });
      }
    } catch (error) {
      console.error('Error validating document:', error);
      setSnackbar({ open: true, message: 'Error validating document', severity: 'error' });
    }
  };

  const handleCaseArchive = async () => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${selectedCase.customer_id}/archive`, {
        method: 'POST',
        body: JSON.stringify({ 
          notes: caseUpdateData.notes 
        }),
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: 'Case archived successfully', severity: 'success' });
        setCaseManagementOpen(false);
        setCaseUpdateData({ risk_level: '', pep_status: false, case_status: '', notes: '' });
        fetchDashboardData(); // Refresh data
      } else {
        setSnackbar({ open: true, message: data.error, severity: 'error' });
      }
    } catch (error) {
      console.error('Error archiving case:', error);
      setSnackbar({ open: true, message: 'Error archiving case', severity: 'error' });
    }
  };

  const handleCaseUpdate = async () => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${selectedCase.customer_id}/update`, {
        method: 'POST',
        body: JSON.stringify(caseUpdateData),
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: 'Case updated successfully', severity: 'success' });
        setCaseManagementOpen(false);
        setCaseUpdateData({ risk_level: '', pep_status: false, case_status: '', notes: '' });
        fetchDashboardData(); // Refresh data
        fetchCaseDetails(selectedCase.customer_id); // Refresh case details
      } else {
        setSnackbar({ open: true, message: data.error, severity: 'error' });
      }
    } catch (error) {
      console.error('Error updating case:', error);
      setSnackbar({ open: true, message: 'Error updating case', severity: 'error' });
    }
  };

  const handleDocumentClick = async (document) => {
    try {
      setDocumentLoading(true);
      setSelectedDocument(document);
      setDocumentModalOpen(true);
      
      // Initialize validation status and zoom
      setValidationStatus(document.validation_status || 'pending');
      setValidationNotes('');
      setImageZoom(1);
      
      // Use document data directly from API response
      setDocumentContent({
        type: 'metadata',
        data: {
          document_id: document.document_id,
          document_type: document.document_type,
          validation_status: document.validation_status,
          filename: document.filename || 'Unknown',
          original_filename: document.original_filename || 'Unknown',
          file_path: document.file_path || 'Unknown',
          extracted_data: document.extracted_data || null,
          upload_time: document.upload_time || null
        }
      });
    } catch (error) {
      console.error('Error loading document:', error);
      setSnackbar({ open: true, message: 'Error loading document', severity: 'error' });
    } finally {
      setDocumentLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle color="success" />;
      case 'pending':
        return <Schedule color="warning" />;
      case 'rejected':
        return <Error color="error" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  const getCustomerTypeIcon = (type) => {
    switch (type) {
      case 'Individual':
        return <Person />;
      case 'Business':
        return <Business />;
      case 'Student':
        return <School />;
      case 'PEP':
        return <Security />;
      default:
        return <Person />;
    }
  };

  const getAgentIcon = (agentType) => {
    switch (agentType) {
      case 'coordinator':
        return <Work />;
      case 'document_validation':
        return <Description />;
      case 'risk_analysis':
        return <Assessment />;
      case 'compliance':
        return <Security />;
      case 'sanction_screening':
        return <Search />;
      case 'manual_review':
        return <Person />;
      default:
        return <Work />;
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const getFilteredCases = () => {
    let filtered = kycCases;
    
    // Filter by status
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(c => c.status === selectedStatus);
    }
    
    // Filter archived cases
    if (!showArchived) {
      filtered = filtered.filter(c => c.status !== 'archived');
    }
    
    return filtered;
  };

  const getDashboardSummary = () => {
    const activeCases = kycCases.filter(c => c.status !== 'archived');
    return {
      total_cases: activeCases.length,
      pending_cases: activeCases.filter(c => c.status === 'pending').length,
      approved_cases: activeCases.filter(c => c.status === 'approved').length,
      rejected_cases: activeCases.filter(c => c.status === 'rejected').length,
      low_risk_cases: activeCases.filter(c => c.riskLevel === 'low').length,
      medium_risk_cases: activeCases.filter(c => c.riskLevel === 'medium').length,
      high_risk_cases: activeCases.filter(c => c.riskLevel === 'high').length,
      archived_cases: kycCases.filter(c => c.status === 'archived').length,
    };
  };

  const openCaseManagement = (type) => {
    setCaseManagementType(type);
    setCaseManagementOpen(true);
    
    if (type === 'update' && selectedCase) {
      // Pre-populate with current values
      setCaseUpdateData({
        risk_level: selectedCase.final_risk_level || selectedCase.estimated_risk_level || '',
        pep_status: selectedCase.pep_status || false,
        case_status: selectedCase.status || '',
        notes: ''
      });
    } else {
      setCaseUpdateData({ risk_level: '', pep_status: false, case_status: '', notes: '' });
    }
  };

  const handleSendEmail = async () => {
    try {
      const data = await apiFetch(`${API_BASE_URL}/cases/${selectedCase.customer_id}/send-email`, {
        method: 'POST',
        body: JSON.stringify(emailData),
      });
      
      if (data.status === 'success') {
        setSnackbar({ open: true, message: 'Email sent successfully', severity: 'success' });
        setEmailModalOpen(false);
        setEmailData({
          email_type: 'status_update',
          subject: '',
          message: '',
          additional_notes: '',
          required_documents: [],
          reason: ''
        });
      } else {
        setSnackbar({ open: true, message: data.error || 'Failed to send email', severity: 'error' });
      }
    } catch (error) {
      console.error('Error sending email:', error);
      setSnackbar({ open: true, message: 'Error sending email', severity: 'error' });
    }
  };

  const handleViewAuditLogs = async () => {
    try {
      setAuditLoading(true);
      const data = await apiFetch(`${API_BASE_URL}/cases/${selectedCase.customer_id}/audit-logs`);
      
      if (Array.isArray(data)) {
        setAuditLogs(data);
        setAuditModalOpen(true);
      } else {
        setSnackbar({ open: true, message: 'Error loading audit logs', severity: 'error' });
      }
    } catch (error) {
      console.error('Error loading audit logs:', error);
      setSnackbar({ open: true, message: 'Error loading audit logs', severity: 'error' });
    } finally {
      setAuditLoading(false);
    }
  };

  const openEmailModal = () => {
    setEmailModalOpen(true);
    setEmailData({
      email_type: 'status_update',
      subject: '',
      message: '',
      additional_notes: '',
      required_documents: [],
      reason: ''
    });
  };

  if (dashboardLoading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          KYC Process Dashboard
        </Typography>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header with user info and logout */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          KYC Process Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="textSecondary">
            Logged in as: <strong>{user?.username}</strong> ({user?.role})
          </Typography>
          <Button variant="outlined" size="small" onClick={logout}>
            Logout
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Cases
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().total_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Review
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().pending_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Risk Cases
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().high_risk_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approved Cases
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().approved_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Rejected Cases
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().rejected_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Archived Cases
              </Typography>
              <Typography variant="h5">
                {getDashboardSummary().archived_cases}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Controls */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Status</InputLabel>
          <Select
            value={selectedStatus}
            label="Filter by Status"
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value="submitted">Submitted</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="approved">Approved</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
            {showArchived && <MenuItem value="archived">Archived</MenuItem>}
          </Select>
        </FormControl>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant={showArchived ? "contained" : "outlined"}
            color="secondary"
            onClick={() => setShowArchived(!showArchived)}
            startIcon={<Visibility />}
          >
            {showArchived ? 'Hide Archived' : 'Show Archived'}
          </Button>
          <Button
            variant="outlined"
            onClick={fetchDashboardData}
            startIcon={<Refresh />}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Cases Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Case ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Risk Level</TableCell>
              <TableCell>Progress</TableCell>
              <TableCell>Submitted Date</TableCell>
              <TableCell>Last Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {getFilteredCases().map((case_) => (
              <TableRow key={case_.id}>
                <TableCell>{case_.id}</TableCell>
                <TableCell>{case_.name}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {getCustomerTypeIcon(case_.type)}
                    <Typography sx={{ ml: 1 }}>{case_.type}</Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(case_.status)}
                    <Chip 
                      label={case_.status.toUpperCase()} 
                      color={getStatusColor(case_.status)}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={case_.riskLevel.toUpperCase()} 
                    color={getRiskColor(case_.riskLevel)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress variant="determinate" value={case_.progress} />
                    </Box>
                    <Box sx={{ minWidth: 35 }}>
                      <Typography variant="body2" color="text.secondary">
                        {`${case_.progress}%`}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{case_.submittedDate}</TableCell>
                <TableCell>{case_.lastUpdated}</TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton 
                      onClick={() => fetchCaseDetails(case_.id)}
                      disabled={!hasPermission('view_case_details')}
                    >
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                  {case_.status === 'rejected' && hasPermission('retry_processing') && (
                    <>
                      <Tooltip title="Retry Processing">
                        <IconButton onClick={() => handleRetryProcessing(case_.id)}>
                          <Refresh />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Manual Review">
                        <IconButton onClick={() => {
                          setSelectedCase(case_);
                          setManualReviewOpen(true);
                        }}>
                          <Person />
                        </IconButton>
                      </Tooltip>
                    </>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Case Details Dialog */}
      <Dialog 
        open={caseDetailsOpen} 
        onClose={() => setCaseDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Case Details - {selectedCase?.customer_id}</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {hasPermission('update_case') && (
                <Button
                  variant="outlined"
                  color="primary"
                  size="small"
                  onClick={() => openCaseManagement('update')}
                  startIcon={<Visibility />}
                >
                  Update Case
                </Button>
              )}
              {hasPermission('send_email') && (
                <Button
                  variant="outlined"
                  color="info"
                  size="small"
                  onClick={openEmailModal}
                  startIcon={<Description />}
                >
                  Send Email
                </Button>
              )}
              {hasPermission('view_audit_logs') && (
                <Button
                  variant="outlined"
                  color="secondary"
                  size="small"
                  onClick={handleViewAuditLogs}
                  startIcon={<Assessment />}
                >
                  Audit Logs
                </Button>
              )}
              {hasPermission('archive_case') && (
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={() => openCaseManagement('archive')}
                  startIcon={<Cancel />}
                  disabled={selectedCase?.status === 'archived'}
                  title={selectedCase?.status === 'archived' ? 'Case is already archived' : 'Archive this case'}
                >
                  Archive Case
                </Button>
              )}
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedCase && (
            <Box>
              {/* Validation Warnings - Show prominently if any */}
              {selectedCase.validation_status && selectedCase.validation_status.includes('Document Validation Warnings') && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    ⚠️ Document Validation Warnings Detected
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    This case has document validation discrepancies that require manual review.
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem', mt: 1 }}>
                    {selectedCase.validation_status}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" color="warning.dark">
                      Action Required: Manual review of document discrepancies
                    </Typography>
                  </Box>
                </Alert>
              )}

              {/* Customer Information */}
              <Typography variant="h6" gutterBottom>Customer Information</Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography><strong>Name:</strong> {selectedCase.name}</Typography>
                  <Typography><strong>Nationality:</strong> {selectedCase.nationality}</Typography>
                  <Typography><strong>Occupation:</strong> {selectedCase.occupation}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography><strong>Status:</strong> {selectedCase.status}</Typography>
                  <Typography><strong>Risk Level:</strong> {selectedCase.final_risk_level || 'N/A'}</Typography>
                  <Typography><strong>PEP Status:</strong> {selectedCase.pep_status ? 'Yes' : 'No'}</Typography>
                </Grid>
              </Grid>

              {/* Processing Steps */}
              <Typography variant="h6" gutterBottom>Processing Steps</Typography>
              {selectedCase.processing_steps?.map((step, index) => (
                <Accordion key={step.id}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      {getAgentIcon(step.agent_type)}
                      <Typography sx={{ ml: 1, flexGrow: 1 }}>
                        {step.step_name.replace('_', ' ').toUpperCase()}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {step.status === 'success' && <CheckCircle color="success" />}
                        {step.status === 'error' && <Error color="error" />}
                        {step.status === 'pending' && <Schedule color="warning" />}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {formatDuration(step.processing_duration)}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2">Agent ID:</Typography>
                        <Typography variant="body2">{step.agent_id}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2">Duration:</Typography>
                        <Typography variant="body2">{formatDuration(step.processing_duration)}</Typography>
                      </Grid>
                      {step.error_message && (
                        <Grid item xs={12}>
                          <Alert severity="error">
                            <Typography variant="subtitle2">Error:</Typography>
                            <Typography variant="body2">{step.error_message}</Typography>
                          </Alert>
                        </Grid>
                      )}
                      {step.response_data && (
                        <Grid item xs={12}>
                          <Typography variant="subtitle2">Response:</Typography>
                          <Paper sx={{ p: 1, bgcolor: 'grey.50' }}>
                            <pre style={{ fontSize: '12px', overflow: 'auto' }}>
                              {JSON.stringify(step.response_data, null, 2)}
                            </pre>
                          </Paper>
                        </Grid>
                      )}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}

              {/* Documents */}
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Documents</Typography>
              <Grid container spacing={1}>
                {selectedCase.documents?.map((doc) => (
                  <Grid item key={doc.id}>
                    <Chip 
                      label={`${doc.document_type}: ${doc.document_id}`}
                      color={
                        doc.validation_status === 'valid' ? 'success' : 
                        doc.validation_status === 'invalid' ? 'error' : 
                        'default'
                      }
                      variant={doc.validation_status === 'pending' ? 'outlined' : 'filled'}
                      onClick={() => handleDocumentClick(doc)}
                      sx={{ 
                        cursor: 'pointer', 
                        '&:hover': { bgcolor: 'action.hover' },
                        fontWeight: doc.validation_status !== 'pending' ? 'medium' : 'normal'
                      }}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCaseDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Manual Review Dialog */}
      <Dialog open={manualReviewOpen} onClose={() => setManualReviewOpen(false)}>
        <DialogTitle>Manual Review - {selectedCase?.customer_id}</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Action</InputLabel>
            <Select
              value={reviewAction}
              label="Action"
              onChange={(e) => setReviewAction(e.target.value)}
            >
              <MenuItem value="approve">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ThumbUp color="success" sx={{ mr: 1 }} />
                  Approve
                </Box>
              </MenuItem>
              <MenuItem value="reject">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ThumbDown color="error" sx={{ mr: 1 }} />
                  Reject
                </Box>
              </MenuItem>
              <MenuItem value="request_info">
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Help color="warning" sx={{ mr: 1 }} />
                  Request More Information
                </Box>
              </MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Review Notes"
            value={reviewNotes}
            onChange={(e) => setReviewNotes(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManualReviewOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleManualReview}
            disabled={!reviewAction}
            variant="contained"
          >
            Submit Review
          </Button>
        </DialogActions>
      </Dialog>

      {/* Document Viewer Modal */}
      <Dialog 
        open={documentModalOpen} 
        onClose={() => setDocumentModalOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Document Viewer - {selectedDocument?.document_type?.replace('_', ' ').toUpperCase()}
        </DialogTitle>
        <DialogContent>
          {documentLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <LinearProgress />
            </Box>
          ) : selectedDocument && documentContent ? (
            <Box>
              {/* Document Header */}
              <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Document ID:</Typography>
                    <Typography variant="body1">{selectedDocument.document_id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Type:</Typography>
                    <Typography variant="body1">
                      {selectedDocument.document_type.replace('_', ' ').toUpperCase()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Status:</Typography>
                    <Chip 
                      label={selectedDocument.validation_status}
                      color={
                        selectedDocument.validation_status === 'valid' ? 'success' : 
                        selectedDocument.validation_status === 'invalid' ? 'error' : 
                        'default'
                      }
                      variant={selectedDocument.validation_status === 'pending' ? 'outlined' : 'filled'}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Filename:</Typography>
                    <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                      {documentContent.data.filename || 'Not available'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Original Filename:</Typography>
                    <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                      {documentContent.data.original_filename || 'Not available'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle2">Upload Time:</Typography>
                    <Typography variant="body2">
                      {documentContent.data.upload_time ? new Date(documentContent.data.upload_time).toLocaleString() : 'Not available'}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              {/* Extracted Data */}
              {documentContent.data.extracted_data && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>Extracted Information</Typography>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <pre style={{ fontSize: '12px', overflow: 'auto', margin: 0 }}>
                      {JSON.stringify(documentContent.data.extracted_data, null, 2)}
                    </pre>
                  </Paper>
                </Box>
              )}

              {/* Document Preview */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" gutterBottom>Document Preview</Typography>
                {selectedDocument && (
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    {(() => {
                      const filename = documentContent.data.filename || documentContent.data.original_filename || '';
                      const isImage = /\.(jpg|jpeg|png|gif)$/i.test(filename);
                      const isPdf = /\.pdf$/i.test(filename);
                      
                      if (isImage) {
                        return (
                          <Box sx={{ textAlign: 'center' }}>
                            {/* Zoom Controls */}
                            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1 }}>
                              <IconButton 
                                onClick={() => setImageZoom(prev => Math.max(0.5, prev - 0.25))}
                                disabled={imageZoom <= 0.5}
                                size="small"
                              >
                                <ZoomOut />
                              </IconButton>
                              <Typography variant="body2" sx={{ minWidth: '60px', textAlign: 'center' }}>
                                {Math.round(imageZoom * 100)}%
                              </Typography>
                              <IconButton 
                                onClick={() => setImageZoom(prev => Math.min(3, prev + 0.25))}
                                disabled={imageZoom >= 3}
                                size="small"
                              >
                                <ZoomIn />
                              </IconButton>
                              <IconButton 
                                onClick={() => setImageZoom(1)}
                                size="small"
                                sx={{ ml: 1 }}
                              >
                                <Typography variant="caption">Reset</Typography>
                              </IconButton>
                            </Box>
                            
                            {/* Image with Zoom */}
                            <Box sx={{ 
                              overflow: 'auto', 
                              maxHeight: '500px', 
                              border: '1px solid #ddd',
                              borderRadius: '4px',
                              bgcolor: 'white'
                            }}>
                              <img 
                                src={`${API_BASE_URL}/documents/${selectedDocument.document_id}/file`}
                                alt={`${selectedDocument.document_type} document`}
                                style={{ 
                                  width: `${imageZoom * 100}%`,
                                  height: 'auto',
                                  display: 'block'
                                }}
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'block';
                                }}
                              />
                              <Box sx={{ display: 'none', p: 2, textAlign: 'center' }}>
                                <Description sx={{ fontSize: 48, color: 'grey.500', mb: 1 }} />
                                <Typography variant="body2" color="textSecondary">
                                  Image preview not available
                                </Typography>
                              </Box>
                            </Box>
                            
                            {/* Download Link */}
                            <Box sx={{ mt: 1 }}>
                              <Button 
                                variant="outlined" 
                                size="small"
                                startIcon={<Download />}
                                onClick={() => window.open(`${API_BASE_URL}/documents/${selectedDocument.document_id}/file`, '_blank')}
                              >
                                Download Image
                              </Button>
                            </Box>
                          </Box>
                        );
                      } else if (isPdf) {
                        return (
                          <Box sx={{ textAlign: 'center' }}>
                            <iframe
                              src={`${API_BASE_URL}/documents/${selectedDocument.document_id}/file`}
                              width="100%"
                              height="500px"
                              style={{ border: '1px solid #ddd', borderRadius: '4px' }}
                              title={`${selectedDocument.document_type} document`}
                            />
                            <Box sx={{ mt: 1 }}>
                              <Button 
                                variant="outlined" 
                                size="small"
                                startIcon={<Download />}
                                onClick={() => window.open(`${API_BASE_URL}/documents/${selectedDocument.document_id}/file`, '_blank')}
                              >
                                Download PDF
                              </Button>
                            </Box>
                          </Box>
                        );
                      } else {
                        return (
                          <Box sx={{ textAlign: 'center', p: 3 }}>
                            <Description sx={{ fontSize: 48, color: 'grey.500', mb: 1 }} />
                            <Typography variant="body2" color="textSecondary">
                              Preview not available for this file type
                            </Typography>
                            <Typography variant="caption" color="textSecondary" display="block">
                              File: {filename || 'Unknown'}
                            </Typography>
                            {documentContent.data.file_path && (
                              <Typography variant="caption" color="textSecondary" display="block">
                                Path: {documentContent.data.file_path}
                              </Typography>
                            )}
                            <Box sx={{ mt: 2 }}>
                              <Button 
                                variant="outlined" 
                                size="small"
                                startIcon={<Download />}
                                onClick={() => window.open(`${API_BASE_URL}/documents/${selectedDocument.document_id}/file`, '_blank')}
                              >
                                Download File
                              </Button>
                            </Box>
                          </Box>
                        );
                      }
                    })()}
                  </Paper>
                )}
              </Box>

              {/* Document Validation Controls */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>Document Validation</Typography>
                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Validation Status</InputLabel>
                        <Select
                          value={validationStatus}
                          label="Validation Status"
                          onChange={(e) => setValidationStatus(e.target.value)}
                        >
                          <MenuItem value="pending">
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Schedule color="warning" sx={{ mr: 1 }} />
                              Pending
                            </Box>
                          </MenuItem>
                          <MenuItem value="valid">
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <CheckCircle color="success" sx={{ mr: 1 }} />
                              Valid
                            </Box>
                          </MenuItem>
                          <MenuItem value="invalid">
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Cancel color="error" sx={{ mr: 1 }} />
                              Invalid
                            </Box>
                          </MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Validation Notes"
                        value={validationNotes}
                        onChange={(e) => setValidationNotes(e.target.value)}
                        placeholder="Add notes about the validation decision..."
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button 
                          variant="contained" 
                          color="primary"
                          onClick={handleDocumentValidation}
                          startIcon={<CheckCircle />}
                        >
                          Update Validation
                        </Button>
                        <Button 
                          variant="outlined"
                          onClick={() => {
                            setValidationStatus(selectedDocument.validation_status || 'pending');
                            setValidationNotes('');
                          }}
                        >
                          Reset
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Box>
            </Box>
          ) : (
            <Typography>No document data available</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDocumentModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Case Management Dialog */}
      <Dialog open={caseManagementOpen} onClose={() => setCaseManagementOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {caseManagementType === 'archive' ? 'Archive Case' : 'Update Case Parameters'} - {selectedCase?.customer_id}
        </DialogTitle>
        <DialogContent>
          {caseManagementType === 'archive' ? (
            <Box sx={{ mt: 2 }}>
              {selectedCase?.status === 'archived' ? (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Already Archived:</Typography>
                  <Typography variant="body2">
                    This case is already archived and cannot be archived again.
                  </Typography>
                </Alert>
              ) : (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Warning:</Typography>
                  <Typography variant="body2">
                    Archiving a case will mark it as inactive and remove it from active processing. 
                    This action cannot be undone.
                  </Typography>
                </Alert>
              )}
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Archive Notes *"
                value={caseUpdateData.notes}
                onChange={(e) => setCaseUpdateData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Please provide a reason for archiving this case..."
                required
                error={!caseUpdateData.notes.trim()}
                helperText={!caseUpdateData.notes.trim() ? "Archive notes are mandatory" : ""}
                disabled={selectedCase?.status === 'archived'}
              />
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>Human-in-the-Loop Case Update</Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Update case parameters manually. All changes require mandatory notes for audit trail.
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Risk Level</InputLabel>
                    <Select
                      value={caseUpdateData.risk_level}
                      label="Risk Level"
                      onChange={(e) => setCaseUpdateData(prev => ({ ...prev, risk_level: e.target.value }))}
                    >
                      <MenuItem value="low">Low Risk</MenuItem>
                      <MenuItem value="medium">Medium Risk</MenuItem>
                      <MenuItem value="high">High Risk</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Case Status</InputLabel>
                    <Select
                      value={caseUpdateData.case_status}
                      label="Case Status"
                      onChange={(e) => setCaseUpdateData(prev => ({ ...prev, case_status: e.target.value }))}
                    >
                      <MenuItem value="submitted">Submitted</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="approved">Approved</MenuItem>
                      <MenuItem value="rejected">Rejected</MenuItem>
                      <MenuItem value="archived">Archived</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                <Grid item xs={12}>
                  <FormControl component="fieldset">
                    <Typography variant="subtitle2" gutterBottom>PEP Status</Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button
                        variant={caseUpdateData.pep_status ? "contained" : "outlined"}
                        color="error"
                        onClick={() => setCaseUpdateData(prev => ({ ...prev, pep_status: true }))}
                        startIcon={<Security />}
                      >
                        PEP Identified
                      </Button>
                      <Button
                        variant={!caseUpdateData.pep_status ? "contained" : "outlined"}
                        color="success"
                        onClick={() => setCaseUpdateData(prev => ({ ...prev, pep_status: false }))}
                        startIcon={<CheckCircle />}
                      >
                        No PEP
                      </Button>
                    </Box>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Update Notes *"
                    value={caseUpdateData.notes}
                    onChange={(e) => setCaseUpdateData(prev => ({ ...prev, notes: e.target.value }))}
                    placeholder="Please provide detailed notes explaining the reason for these changes..."
                    required
                    error={!caseUpdateData.notes.trim()}
                    helperText={!caseUpdateData.notes.trim() ? "Update notes are mandatory for audit trail" : ""}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCaseManagementOpen(false)}>Cancel</Button>
          <Button 
            onClick={caseManagementType === 'archive' ? handleCaseArchive : handleCaseUpdate}
            disabled={!caseUpdateData.notes.trim() || (caseManagementType === 'archive' && selectedCase?.status === 'archived')}
            variant="contained"
            color={caseManagementType === 'archive' ? 'error' : 'primary'}
          >
            {caseManagementType === 'archive' ? 'Archive Case' : 'Update Case'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Email Modal */}
      <Dialog open={emailModalOpen} onClose={() => setEmailModalOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Send Email to Customer - {selectedCase?.customer_id}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>Email Configuration</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Send automated or custom emails to the customer with audit logging.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Email Type</InputLabel>
                  <Select
                    value={emailData.email_type}
                    label="Email Type"
                    onChange={(e) => setEmailData(prev => ({ ...prev, email_type: e.target.value }))}
                  >
                    <MenuItem value="status_update">Status Update</MenuItem>
                    <MenuItem value="document_request">Document Request</MenuItem>
                    <MenuItem value="approval">Approval Notification</MenuItem>
                    <MenuItem value="rejection">Rejection Notification</MenuItem>
                    <MenuItem value="custom">Custom Email</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              {emailData.email_type === 'custom' && (
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Subject"
                    value={emailData.subject}
                    onChange={(e) => setEmailData(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="Enter email subject..."
                  />
                </Grid>
              )}
              
              {emailData.email_type === 'document_request' && (
                <>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Required Documents"
                      value={emailData.required_documents.join(', ')}
                      onChange={(e) => setEmailData(prev => ({ 
                        ...prev, 
                        required_documents: e.target.value.split(',').map(doc => doc.trim()).filter(doc => doc)
                      }))}
                      placeholder="Enter required documents (comma-separated)..."
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Reason for Request"
                      value={emailData.reason}
                      onChange={(e) => setEmailData(prev => ({ ...prev, reason: e.target.value }))}
                      placeholder="Explain why these documents are needed..."
                    />
                  </Grid>
                </>
              )}
              
              {emailData.email_type === 'rejection' && (
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Rejection Reason"
                    value={emailData.reason}
                    onChange={(e) => setEmailData(prev => ({ ...prev, reason: e.target.value }))}
                    placeholder="Provide the reason for rejection..."
                  />
                </Grid>
              )}
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Additional Notes"
                  value={emailData.additional_notes}
                  onChange={(e) => setEmailData(prev => ({ ...prev, additional_notes: e.target.value }))}
                  placeholder="Add any additional notes or custom message..."
                />
              </Grid>
              
              {emailData.email_type === 'custom' && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={6}
                    label="Custom Message"
                    value={emailData.message}
                    onChange={(e) => setEmailData(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Enter your custom email message..."
                  />
                </Grid>
              )}
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailModalOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleSendEmail}
            variant="contained"
            color="primary"
          >
            Send Email
          </Button>
        </DialogActions>
      </Dialog>

      {/* Audit Logs Modal */}
      <Dialog open={auditModalOpen} onClose={() => setAuditModalOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Audit Logs - {selectedCase?.customer_id}</DialogTitle>
        <DialogContent>
          {auditLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <LinearProgress />
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>Case Activity History</Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Complete audit trail of all actions performed on this case.
              </Typography>
              
              {auditLogs.length === 0 ? (
                <Alert severity="info">
                  No audit logs found for this case.
                </Alert>
              ) : (
                <List>
                  {auditLogs.map((log, index) => (
                    <React.Fragment key={log.id}>
                      <ListItem>
                        <ListItemIcon>
                          {log.action_type === 'case_archived' && <Cancel color="error" />}
                          {log.action_type === 'case_updated' && <Visibility color="primary" />}
                          {log.action_type === 'email_sent' && <Description color="info" />}
                          {log.action_type === 'manual_review' && <Assessment color="warning" />}
                          {log.action_type === 'document_validation' && <CheckCircle color="success" />}
                          {!['case_archived', 'case_updated', 'email_sent', 'manual_review', 'document_validation'].includes(log.action_type) && <Timer color="default" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="subtitle1">
                                {log.action_type.replace('_', ' ').toUpperCase()}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {new Date(log.timestamp).toLocaleString()}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Performed by:</strong> {log.performed_by}
                              </Typography>
                              {log.ip_address && (
                                <Typography variant="caption" display="block">
                                  <strong>IP Address:</strong> {log.ip_address}
                                </Typography>
                              )}
                              {log.user_agent && (
                                <Typography variant="caption" display="block">
                                  <strong>User Agent:</strong> {log.user_agent}
                                </Typography>
                              )}
                              {log.action_details && (
                                <Paper sx={{ p: 1, mt: 1, bgcolor: 'grey.50' }}>
                                  <pre style={{ fontSize: '11px', overflow: 'auto', margin: 0 }}>
                                    {JSON.stringify(log.action_details, null, 2)}
                                  </pre>
                                </Paper>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < auditLogs.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuditModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

// Main App wrapper with authentication
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

function AppContent() {
  const { user, loading, login } = useAuth();

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <Typography>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  if (!user) {
    return <Login onLogin={login} />;
  }

  return <DashboardApp />;
}

export default App; 
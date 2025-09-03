import os
import json
import base64
import boto3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import re
from werkzeug.utils import secure_filename
import uuid
import mimetypes
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with Bedrock client."""
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Create documents directory if it doesn't exist
        self.documents_dir = os.path.join(os.path.dirname(__file__), 'documents')
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def save_uploaded_file(self, file, document_type: str) -> Dict[str, Any]:
        """Save uploaded file and return file information."""
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
            
            # Create filename with format: UK_Passport_789.pdf
            original_filename = secure_filename(file.filename)
            file_extension = os.path.splitext(original_filename)[1]
            filename = f"{document_type}_{document_id}{file_extension}"
            
            # Save file to documents directory
            file_path = os.path.join(self.documents_dir, filename)
            
            # Read file content and write to disk (FastAPI UploadFile doesn't have .save())
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            logger.info(f"File saved: {file_path}")
            
            return {
                "status": "success",
                "document_id": document_id,
                "filename": filename,
                "file_path": file_path,
                "document_type": document_type,
                "original_filename": original_filename
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_file_type(self, file_path: str) -> str:
        """Get the MIME type of a file."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    def convert_pdf_to_image(self, pdf_path: str) -> str:
        """Convert PDF to image using pdf2image or similar library."""
        try:
            # Try to import pdf2image
            try:
                from pdf2image import convert_from_path
            except ImportError:
                logger.warning("pdf2image not available, trying alternative method")
                # Fallback: use a simple method or return error
                raise ImportError("pdf2image library not installed")
            
            # Convert PDF to image (only first page)
            images = convert_from_path(pdf_path, first_page=1, last_page=1)
            if not images:
                raise Exception("No pages found in PDF")
            
            # Convert PIL image to JPEG bytes
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            # Save the converted image temporarily
            temp_image_path = pdf_path.replace('.pdf', '_converted.jpg')
            with open(temp_image_path, 'wb') as f:
                f.write(img_byte_arr.getvalue())
            
            logger.info(f"PDF converted to image: {temp_image_path}")
            return temp_image_path
            
        except ImportError:
            # If pdf2image is not available, return the original path
            # and let the calling function handle it
            logger.warning("PDF conversion not available, using original file")
            return pdf_path
        except Exception as e:
            logger.error(f"Error converting PDF to image: {str(e)}")
            raise
    
    def encode_file(self, file_path: str) -> str:
        """Encode file (image or PDF) for Bedrock Claude Vision."""
        try:
            file_type = self.get_file_type(file_path)
            
            # Handle PDF files
            if file_type == 'application/pdf':
                logger.info("Processing PDF file, converting to image...")
                image_path = self.convert_pdf_to_image(file_path)
                if image_path != file_path:  # Conversion was successful
                    file_path = image_path
                    file_type = 'image/jpeg'
                else:
                    # Conversion failed, try to process as is
                    logger.warning("PDF conversion failed, attempting to process as is")
            
            # Handle image files
            if file_type.startswith('image/'):
                with open(file_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            else:
                raise Exception(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error encoding file: {str(e)}")
            raise
    
    def invoke_bedrock_vision(self, encoded_image: str, prompt: str, file_type: str = "jpeg") -> Dict:
        """Generic function to invoke Bedrock's vision model."""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "image": {
                                    "format": file_type,
                                    "source": {"bytes": encoded_image}
                                }
                            },
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-lite-v1:0",
                body=json.dumps(request_body).encode('utf-8')
            )
            
            response_body = json.loads(response.get('body').read().decode('utf-8'))
            
            # Temporary logging to debug response format
            logger.info(f"Raw LLM response: {json.dumps(response_body, indent=2)}")
            
            return response_body
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock vision: {str(e)}")
            raise
    
    def extract_info_from_document(self, document_path: str, document_type: str) -> Dict:
        """Extract information from document using Bedrock Vision."""
        try:
            file_type = self.get_file_type(document_path)
            
            # Handle PDF files
            if file_type == 'application/pdf':
                logger.info("Processing PDF document...")
                image_path = self.convert_pdf_to_image(document_path)
                if image_path != document_path:  # Conversion was successful
                    document_path = image_path
                    file_type = 'image/jpeg'
                else:
                    # Conversion failed, try to process as is
                    logger.warning("PDF conversion failed, attempting to process as is")
            
            # Encode the file
            encoded_image = self.encode_file(document_path)
            
            # Determine the format for Bedrock
            format_type = "jpeg" if file_type.startswith('image/') else "jpeg"  # Default to jpeg
            
            # Create document-specific prompts
            if document_type == "id_proof":
                prompt = """Analyze this ID document image and extract the following information in JSON format.
                Please extract and return only a JSON object with these fields:
                - first_name
                - last_name
                - dob (date of birth in YYYY-MM-DD format)
                - nationality
                - document_type (passport, driver_license, national_id, etc.)
                - document_number
                
                Important: Please return ONLY the raw JSON without any markdown formatting, code blocks, or additional text."""
            
            elif document_type == "address_proof":
                prompt = """Analyze this address proof document image and extract the following information in JSON format.
                Please extract and return only a JSON object with these fields:
                - full_address
                - document_type (utility_bill, bank_statement, lease_agreement, etc.)
                - document_date
                - account_holder_name
                
                Important: Please return ONLY the raw JSON without any markdown formatting, code blocks, or additional text."""
            
            elif document_type == "employment_proof":
                prompt = """Analyze this employment proof document image and extract the following information in JSON format.
                Please extract and return only a JSON object with these fields:
                - employer_name
                - employee_name
                - position
                - employment_date
                - annual_salary (if available)
                - document_type (employment_letter, payslip, contract, etc.)
                
                Important: Please return ONLY the raw JSON without any markdown formatting, code blocks, or additional text."""
            
            else:
                prompt = """Analyze this document image and extract any relevant information in JSON format.
                Please return a JSON object with any fields you can identify from the document."""
            
            response = self.invoke_bedrock_vision(encoded_image, prompt, format_type)
            
            response_text = response.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
            logger.info(f"Raw response from vision model: {response_text}")
            
            # Clean up the response text to handle markdown code blocks
            if response_text.strip().startswith('```') and '```' in response_text:
                pattern = r'```(?:json)?\n(.*?)\n```'
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    response_text = match.group(1)
                    logger.info(f"Extracted JSON from code block: {response_text}")
                else:
                    parts = response_text.split('```')
                    if len(parts) >= 3:
                        response_text = parts[1]
                        if response_text.startswith('json'):
                            response_text = response_text[4:].strip()
                        logger.info(f"Extracted JSON using string split: {response_text}")
            
            # Try to parse JSON
            try:
                json_pattern = r'({[\s\S]*})'
                json_match = re.search(json_pattern, response_text)
                if json_match:
                    clean_json = json_match.group(1)
                    parsed_data = json.loads(clean_json)
                    logger.info(f"Successfully parsed JSON with regex extraction")
                else:
                    parsed_data = json.loads(response_text)
                    logger.info(f"Successfully parsed JSON directly")
                
                return {
                    "status": "success",
                    "data": parsed_data
                }
                
            except json.JSONDecodeError:
                logger.error(f"JSON parsing failed. Attempting to fix malformed JSON")
                
                # Manual JSON reconstruction based on document type
                data = {}
                if document_type == "id_proof":
                    patterns = [
                        (r'"first_name":\s*"([^"]*)"', "first_name"),
                        (r'"last_name":\s*"([^"]*)"', "last_name"),
                        (r'"dob":\s*"([^"]*)"', "dob"),
                        (r'"nationality":\s*"([^"]*)"', "nationality"),
                        (r'"document_type":\s*"([^"]*)"', "document_type"),
                        (r'"document_number":\s*"([^"]*)"', "document_number")
                    ]
                elif document_type == "address_proof":
                    patterns = [
                        (r'"full_address":\s*"([^"]*)"', "full_address"),
                        (r'"document_type":\s*"([^"]*)"', "document_type"),
                        (r'"document_date":\s*"([^"]*)"', "document_date"),
                        (r'"account_holder_name":\s*"([^"]*)"', "account_holder_name")
                    ]
                elif document_type == "employment_proof":
                    patterns = [
                        (r'"employer_name":\s*"([^"]*)"', "employer_name"),
                        (r'"employee_name":\s*"([^"]*)"', "employee_name"),
                        (r'"position":\s*"([^"]*)"', "position"),
                        (r'"employment_date":\s*"([^"]*)"', "employment_date"),
                        (r'"annual_salary":\s*"([^"]*)"', "annual_salary"),
                        (r'"document_type":\s*"([^"]*)"', "document_type")
                    ]
                else:
                    patterns = []
                
                for pattern, field in patterns:
                    match = re.search(pattern, response_text)
                    if match:
                        data[field] = match.group(1)
                    else:
                        alt_pattern = fr'"{field}":\s*([^,\n\r}}]+)'
                        alt_match = re.search(alt_pattern, response_text)
                        if alt_match:
                            data[field] = alt_match.group(1).strip()
                
                if data:
                    logger.info(f"Reconstructed JSON manually: {data}")
                    return {
                        "status": "success",
                        "data": data
                    }
                else:
                    raise Exception("Could not extract JSON data from model response")
                
        except Exception as e:
            logger.error(f"Error extracting information: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}
    
    def process_document_upload(self, file, document_type: str) -> Dict[str, Any]:
        """Process document upload: save file and extract information."""
        try:
            # Save the uploaded file
            save_result = self.save_uploaded_file(file, document_type)
            if save_result["status"] != "success":
                return save_result
            
            # Extract information from the document
            extract_result = self.extract_info_from_document(
                save_result["file_path"], 
                document_type
            )
            
            if extract_result["status"] == "success":
                # Combine file info with extracted data
                result = {
                    "status": "success",
                    "file_info": save_result,
                    "extracted_data": extract_result["data"]
                }
            else:
                # File saved but extraction failed
                result = {
                    "status": "partial_success",
                    "file_info": save_result,
                    "extraction_error": extract_result["error"]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document upload: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def validate_document_data(self, extracted_data: Dict, user_data: Dict, document_type: str) -> Dict[str, Any]:
        """
        Validate extracted document data against user-entered information using LLM.
        Returns validation results with confidence scores and discrepancies.
        """
        try:
            # Use LLM-based validation for better accuracy and flexibility
            validation_results = self._validate_with_llm(extracted_data, user_data, document_type)
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating document data: {str(e)}")
            # Fallback to rule-based validation if LLM fails
            logger.info("Falling back to rule-based validation")
            return self._validate_with_rules(extracted_data, user_data, document_type)
    
    def _validate_with_llm(self, extracted_data: Dict, user_data: Dict, document_type: str) -> Dict[str, Any]:
        """Validate document data using LLM for intelligent matching."""
        try:
            # Prepare the validation prompt
            prompt = self._create_validation_prompt(extracted_data, user_data, document_type)
            
            # Invoke LLM for validation
            response = self._invoke_llm_validation(prompt)
            
            # Parse LLM response
            validation_results = self._parse_llm_validation_response(response)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"LLM validation failed: {str(e)}")
            raise
    
    def _create_validation_prompt(self, extracted_data: Dict, user_data: Dict, document_type: str) -> str:
        """Create a comprehensive validation prompt for the LLM."""
        
        prompt = f"""You are a KYC document validation expert. Your task is to validate if the information extracted from a {document_type} document matches the information provided by the user.

VALIDATION RULES:
1. Names should match with 80% confidence or higher (consider nicknames, abbreviations, middle names, name order)
2. Addresses should match with 80% confidence or higher (consider abbreviations like St/Street, Ave/Avenue, etc.)
3. Dates should match exactly (consider different date formats)
4. Other fields should match with appropriate confidence levels

DOCUMENT TYPE: {document_type}

EXTRACTED DATA FROM DOCUMENT:
{json.dumps(extracted_data, indent=2)}

USER PROVIDED DATA:
{json.dumps(user_data, indent=2)}

Please analyze the data and provide a validation result in the following JSON format:

{{
    "overall_match": true/false,
    "confidence_score": 0-100,
    "discrepancies": [
        {{
            "field": "field_name",
            "document_value": "value_from_document",
            "user_value": "value_from_user",
            "severity": "high/medium/low",
            "reason": "explanation_of_mismatch"
        }}
    ],
    "warnings": ["warning_messages"],
    "validation_details": {{
        "name_match": {{
            "matches": true/false,
            "confidence": 0-100,
            "reason": "explanation"
        }},
        "address_match": {{
            "matches": true/false,
            "confidence": 0-100,
            "reason": "explanation"
        }},
        "other_matches": {{
            "field_name": {{
                "matches": true/false,
                "confidence": 0-100,
                "reason": "explanation"
            }}
        }}
    }}
}}

IMPORTANT:
- Be flexible with name variations (e.g., "William" vs "Bill", "John" vs "Jon")
- Be flexible with address abbreviations (e.g., "St" vs "Street", "Ave" vs "Avenue")
- Consider cultural and regional naming conventions
- Provide detailed explanations for any mismatches
- Use 80% as the threshold for acceptable matches

Return only the JSON response, no additional text."""

        return prompt
    
    def _invoke_llm_validation(self, prompt: str) -> Dict:
        """Invoke LLM for validation."""
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-lite-v1:0",
                body=json.dumps(request_body).encode('utf-8')
            )
            
            response_body = json.loads(response.get('body').read().decode('utf-8'))
            
            # Temporary logging to debug response format
            logger.info(f"Raw LLM response: {json.dumps(response_body, indent=2)}")
            
            return response_body
            
        except Exception as e:
            logger.error(f"Error invoking LLM for validation: {str(e)}")
            raise
    
    def _parse_llm_validation_response(self, response: Dict) -> Dict[str, Any]:
        """Parse the LLM validation response."""
        import re
        try:
            # Log the response structure for debugging
            logger.debug(f"LLM Response structure: {json.dumps(response, indent=2)}")

            response_text = None

            # 1. Bedrock LLM: output.message.content[0].text
            if (
                'output' in response and
                'message' in response['output'] and
                'content' in response['output']['message'] and
                isinstance(response['output']['message']['content'], list) and
                len(response['output']['message']['content']) > 0 and
                'text' in response['output']['message']['content'][0]
            ):
                response_text = response['output']['message']['content'][0]['text']
            # 2. Previous logic
            elif 'content' in response and len(response['content']) > 0:
                content = response['content'][0]
                if 'text' in content:
                    response_text = content['text']
                elif isinstance(content, str):
                    response_text = content
            elif 'completion' in response:
                response_text = response['completion']
            elif 'text' in response:
                response_text = response['text']
            elif 'response' in response:
                response_text = response['response']
            else:
                logger.error(f"Unexpected response format: {json.dumps(response, indent=2)}")
                raise Exception("Invalid LLM response format")

            if not response_text:
                raise Exception("No text content in LLM response")

            logger.debug(f"Extracted response text: {response_text}")

            # Try to extract JSON from code block if present
            code_block_match = re.search(r'```(?:json)?\n([\s\S]+?)\n```', response_text)
            if code_block_match:
                json_str = code_block_match.group(1)
                try:
                    validation_result = json.loads(json_str)
                    logger.info(f"Extracted JSON from code block: {json_str}")
                except Exception as e:
                    logger.error(f"Failed to parse JSON from code block: {e}")
                    raise Exception("Invalid JSON in LLM code block")
            else:
                # Fallback: extract JSON from anywhere in the string
                try:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = response_text[json_start:json_end]
                        validation_result = json.loads(json_str)
                    else:
                        validation_result = json.loads(response_text)
                except Exception as e:
                    logger.error(f"Failed to parse JSON from LLM response: {e}")
                    logger.error(f"Response text: {response_text}")
                    raise Exception("Invalid JSON in LLM response")

            # Validate the response structure
            required_fields = ['overall_match', 'confidence_score', 'discrepancies', 'warnings']
            for field in required_fields:
                if field not in validation_result:
                    validation_result[field] = [] if field in ['discrepancies', 'warnings'] else False if field == 'overall_match' else 0

            # Ensure validation_details exists
            if 'validation_details' not in validation_result:
                validation_result['validation_details'] = {}

            logger.info(f"Successfully parsed JSON with regex extraction")
            return validation_result

        except Exception as e:
            logger.error(f"Error parsing LLM validation response: {str(e)}")
            raise
    
    def _validate_with_rules(self, extracted_data: Dict, user_data: Dict, document_type: str) -> Dict[str, Any]:
        """Fallback rule-based validation if LLM fails."""
        try:
            if document_type == "id_proof":
                validation_results = self._validate_id_proof(extracted_data, user_data)
            elif document_type == "address_proof":
                validation_results = self._validate_address_proof(extracted_data, user_data)
            elif document_type == "employment_proof":
                validation_results = self._validate_employment_proof(extracted_data, user_data)
            else:
                # Default validation for unknown document types
                validation_results = {
                    "overall_match": True,
                    "confidence_score": 100,
                    "discrepancies": [],
                    "warnings": [],
                    "validation_details": {}
                }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in rule-based validation: {str(e)}")
            return {
                "overall_match": False,
                "confidence_score": 0,
                "discrepancies": ["Validation error occurred"],
                "warnings": [f"Validation failed: {str(e)}"],
                "validation_details": {}
            }
    
    def _validate_id_proof(self, extracted_data: Dict, user_data: Dict) -> Dict[str, Any]:
        """Validate ID proof document data."""
        validation_results = {
            "overall_match": True,
            "confidence_score": 100,
            "discrepancies": [],
            "warnings": [],
            "validation_details": {}
        }
        
        # Extract names from user data
        user_full_name = f"{user_data.get('name', '')}".strip().lower()
        user_first_name = user_data.get('name', '').split()[0].lower() if user_data.get('name') else ''
        user_last_name = ' '.join(user_data.get('name', '').split()[1:]).lower() if len(user_data.get('name', '').split()) > 1 else ''
        
        # Extract names from document
        doc_first_name = extracted_data.get('first_name', '').strip().lower()
        doc_last_name = extracted_data.get('last_name', '').strip().lower()
        doc_full_name = f"{doc_first_name} {doc_last_name}".strip()
        
        # Validate names (only if user provided a name)
        if doc_first_name and user_first_name:
            if not self._fuzzy_match(doc_first_name, user_first_name, threshold=0.8, match_type="name"):
                validation_results["discrepancies"].append({
                    "field": "first_name",
                    "document_value": doc_first_name,
                    "user_value": user_first_name,
                    "severity": "medium"
                })
        
        if doc_last_name and user_last_name:
            if not self._fuzzy_match(doc_last_name, user_last_name, threshold=0.8, match_type="name"):
                validation_results["discrepancies"].append({
                    "field": "last_name",
                    "document_value": doc_last_name,
                    "user_value": user_last_name,
                    "severity": "medium"
                })
        
        # Validate date of birth (only if user provided DOB)
        doc_dob = extracted_data.get('dob', '')
        user_dob = user_data.get('dob', '')
        
        if doc_dob and user_dob:
            # Normalize date formats
            doc_dob_normalized = self._normalize_date(doc_dob)
            user_dob_normalized = self._normalize_date(user_dob)
            
            if doc_dob_normalized != user_dob_normalized:
                validation_results["discrepancies"].append({
                    "field": "date_of_birth",
                    "document_value": doc_dob,
                    "user_value": user_dob,
                    "severity": "high"
                })
        
        # Validate nationality (only if user provided nationality)
        doc_nationality = extracted_data.get('nationality', '').strip().lower()
        user_nationality = user_data.get('nationality', '').strip().lower()
        
        if doc_nationality and user_nationality:
            if not self._fuzzy_match(doc_nationality, user_nationality, threshold=0.8):
                validation_results["discrepancies"].append({
                    "field": "nationality",
                    "document_value": doc_nationality,
                    "user_value": user_nationality,
                    "severity": "low"
                })
        
        # Update overall match and confidence score
        if validation_results["discrepancies"]:
            validation_results["overall_match"] = False
            # Calculate confidence score based on number and severity of discrepancies
            total_discrepancies = len(validation_results["discrepancies"])
            high_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "high")
            medium_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "medium")
            
            # Penalize based on severity and count
            penalty = (high_severity * 30) + (medium_severity * 20) + (total_discrepancies * 10)
            validation_results["confidence_score"] = max(0, 100 - penalty)
        
        return validation_results
    
    def _validate_address_proof(self, extracted_data: Dict, user_data: Dict) -> Dict[str, Any]:
        """Validate address proof document data."""
        validation_results = {
            "overall_match": True,
            "confidence_score": 100,
            "discrepancies": [],
            "warnings": [],
            "validation_details": {}
        }
        
        # Extract address from document
        doc_address = extracted_data.get('full_address', '').strip().lower()
        user_address = user_data.get('address', '').strip().lower()
        
        # Validate address (only if user provided address)
        if doc_address and user_address:
            if not self._fuzzy_match(doc_address, user_address, threshold=0.8, match_type="address"):
                validation_results["discrepancies"].append({
                    "field": "address",
                    "document_value": doc_address,
                    "user_value": user_address,
                    "severity": "high"
                })
        
        # Check account holder name if available (only if user provided name)
        account_holder = extracted_data.get('account_holder_name', '').strip().lower()
        user_name = user_data.get('name', '').strip().lower()
        
        if account_holder and user_name:
            if not self._fuzzy_match(account_holder, user_name, threshold=0.8, match_type="name"):
                validation_results["discrepancies"].append({
                    "field": "account_holder_name",
                    "document_value": account_holder,
                    "user_value": user_name,
                    "severity": "high"
                })
        
        # Update overall match and confidence score
        if validation_results["discrepancies"]:
            validation_results["overall_match"] = False
            # Calculate confidence score based on number and severity of discrepancies
            total_discrepancies = len(validation_results["discrepancies"])
            high_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "high")
            medium_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "medium")
            
            # Penalize based on severity and count
            penalty = (high_severity * 30) + (medium_severity * 20) + (total_discrepancies * 10)
            validation_results["confidence_score"] = max(0, 100 - penalty)
        
        return validation_results
    
    def _validate_employment_proof(self, extracted_data: Dict, user_data: Dict) -> Dict[str, Any]:
        """Validate employment proof document data."""
        validation_results = {
            "overall_match": True,
            "confidence_score": 100,
            "discrepancies": [],
            "warnings": [],
            "validation_details": {}
        }
        
        # Validate employer name (only if user provided employer)
        doc_employer = extracted_data.get('employer_name', '').strip().lower()
        user_employer = user_data.get('employer', '').strip().lower()
        
        if doc_employer and user_employer:
            if not self._fuzzy_match(doc_employer, user_employer, threshold=0.7):
                validation_results["discrepancies"].append({
                    "field": "employer",
                    "document_value": doc_employer,
                    "user_value": user_employer,
                    "severity": "medium"
                })
        
        # Validate employee name (only if user provided name)
        doc_employee = extracted_data.get('employee_name', '').strip().lower()
        user_name = user_data.get('name', '').strip().lower()
        
        if doc_employee and user_name:
            if not self._fuzzy_match(doc_employee, user_name, threshold=0.8, match_type="name"):
                validation_results["discrepancies"].append({
                    "field": "employee_name",
                    "document_value": doc_employee,
                    "user_value": user_name,
                    "severity": "high"
                })
        
        # Validate position/occupation (only if user provided occupation)
        doc_position = extracted_data.get('position', '').strip().lower()
        user_occupation = user_data.get('occupation', '').strip().lower()
        
        if doc_position and user_occupation:
            if not self._fuzzy_match(doc_position, user_occupation, threshold=0.6):
                validation_results["discrepancies"].append({
                    "field": "position",
                    "document_value": doc_position,
                    "user_value": user_occupation,
                    "severity": "low"
                })
        
        # Update overall match and confidence score
        if validation_results["discrepancies"]:
            validation_results["overall_match"] = False
            # Calculate confidence score based on number and severity of discrepancies
            total_discrepancies = len(validation_results["discrepancies"])
            high_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "high")
            medium_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "medium")
            low_severity = sum(1 for d in validation_results["discrepancies"] if d["severity"] == "low")
            
            # Penalize based on severity and count
            penalty = (high_severity * 30) + (medium_severity * 20) + (low_severity * 10) + (total_discrepancies * 5)
            validation_results["confidence_score"] = max(0, 100 - penalty)
        
        return validation_results
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.8, match_type: str = "general") -> bool:
        """
        Perform fuzzy string matching using improved similarity.
        
        Args:
            str1: First string to compare
            str2: Second string to compare
            threshold: Minimum similarity threshold (default 0.8 = 80%)
            match_type: Type of matching - "name" for full name matching, "address" for address matching, "general" for other fields
        """
        if not str1 or not str2:
            return False
        
        # Convert to lowercase and remove extra spaces
        str1 = ' '.join(str1.lower().split())
        str2 = ' '.join(str2.lower().split())
        
        if str1 == str2:
            return True
        
        # Handle abbreviations and common variations
        str1_normalized = self._normalize_string(str1)
        str2_normalized = self._normalize_string(str2)
        
        if str1_normalized == str2_normalized:
            return True
        
        # Special handling for different match types
        if match_type == "name":
            return self._fuzzy_match_name(str1, str2, threshold)
        elif match_type == "address":
            return self._fuzzy_match_address(str1, str2, threshold)
        else:
            return self._fuzzy_match_general(str1, str2, threshold)
    
    def _fuzzy_match_name(self, str1: str, str2: str, threshold: float) -> bool:
        """Perform fuzzy matching specifically for names with full name consideration."""
        # Split into words for name comparison
        words1 = str1.split()
        words2 = str2.split()
        
        # Handle single word names
        if len(words1) == 1 and len(words2) == 1:
            return self._fuzzy_match_general(str1, str2, threshold)
        
        # For multi-word names, try different matching strategies
        # 1. Exact word order match
        if len(words1) == len(words2):
            exact_matches = sum(1 for w1, w2 in zip(words1, words2) if w1 == w2)
            if exact_matches == len(words1):
                return True
        
        # 2. Word set similarity (handles name order variations)
        word_similarity = self._word_similarity(str1, str2)
        if word_similarity >= threshold:
            return True
        
        # 3. Character-based similarity for the full name
        char_similarity = self._char_similarity(str1, str2)
        if char_similarity >= threshold:
            return True
        
        # 4. Check for common name variations (nicknames, abbreviations)
        if self._check_name_variations(str1, str2):
            return True
        
        # 5. Weighted combination for final check
        overall_similarity = (word_similarity * 0.6 + char_similarity * 0.4)
        return overall_similarity >= threshold
    
    def _fuzzy_match_address(self, str1: str, str2: str, threshold: float) -> bool:
        """Perform fuzzy matching specifically for addresses."""
        # Clean addresses for comparison
        str1_clean = self._clean_address(str1)
        str2_clean = self._clean_address(str2)
        
        if str1_clean == str2_clean:
            return True
        
        # Calculate address-specific similarities
        word_similarity = self._word_similarity(str1_clean, str2_clean)
        char_similarity = self._char_similarity(str1_clean, str2_clean)
        
        # Address matching is more lenient with word order
        if word_similarity >= threshold:
            return True
        
        # Check for partial address matches (e.g., same street but different apartment)
        if self._check_partial_address_match(str1_clean, str2_clean):
            return True
        
        # Weighted combination
        overall_similarity = (word_similarity * 0.7 + char_similarity * 0.3)
        return overall_similarity >= threshold
    
    def _fuzzy_match_general(self, str1: str, str2: str, threshold: float) -> bool:
        """Perform general fuzzy matching for other fields."""
        # Calculate multiple similarity metrics
        word_similarity = self._word_similarity(str1, str2)
        char_similarity = self._char_similarity(str1, str2)
        abbreviation_similarity = self._abbreviation_similarity(str1, str2)
        
        # Weighted average of similarities
        overall_similarity = (word_similarity * 0.5 + char_similarity * 0.3 + abbreviation_similarity * 0.2)
        
        return overall_similarity >= threshold
    
    def _normalize_string(self, text: str) -> str:
        """Normalize string by handling common abbreviations and variations."""
        # Common abbreviations mapping
        abbreviations = {
            'st': 'street',
            'ave': 'avenue',
            'rd': 'road',
            'dr': 'drive',
            'ln': 'lane',
            'blvd': 'boulevard',
            'corp': 'corporation',
            'ltd': 'limited',
            'inc': 'incorporated',
            'co': 'company',
            'eng': 'engineer',
            'dev': 'developer',
            'mgr': 'manager',
            'dir': 'director',
            'pres': 'president',
            'ceo': 'chief executive officer',
            'cto': 'chief technology officer',
            'cfo': 'chief financial officer',
        }
        
        # Replace abbreviations
        words = text.split()
        normalized_words = []
        for word in words:
            if word in abbreviations:
                normalized_words.append(abbreviations[word])
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def _word_similarity(self, str1: str, str2: str) -> float:
        """Calculate word-based similarity."""
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _char_similarity(self, str1: str, str2: str) -> float:
        """Calculate character-based similarity using Levenshtein distance."""
        if len(str1) == 0 and len(str2) == 0:
            return 1.0
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Simple character-based similarity
        chars1 = set(str1.replace(' ', ''))
        chars2 = set(str2.replace(' ', ''))
        
        if not chars1 or not chars2:
            return 0.0
        
        intersection = chars1.intersection(chars2)
        union = chars1.union(chars2)
        
        return len(intersection) / len(union)
    
    def _abbreviation_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity considering abbreviations."""
        # Check if one string is an abbreviation of the other
        words1 = str1.split()
        words2 = str2.split()
        
        if len(words1) == 1 and len(words2) > 1:
            # str1 might be an abbreviation of str2
            if self._is_abbreviation(words1[0], str2):
                return 0.9
        elif len(words2) == 1 and len(words1) > 1:
            # str2 might be an abbreviation of str1
            if self._is_abbreviation(words2[0], str1):
                return 0.9
        
        return 0.0
    
    def _is_abbreviation(self, abbrev: str, full_text: str) -> bool:
        """Check if abbrev is an abbreviation of full_text."""
        if len(abbrev) < 2:
            return False
        
        # Check if abbrev matches the first letters of words in full_text
        words = full_text.split()
        if len(words) == 1:
            return abbrev.lower() in words[0].lower()
        
        # Check acronym-style abbreviation
        first_letters = ''.join(word[0].lower() for word in words if word)
        if abbrev.lower() == first_letters:
            return True
        
        # Check if abbrev is a prefix of any word
        for word in words:
            if word.lower().startswith(abbrev.lower()):
                return True
        
        return False
    
    def _check_name_variations(self, name1: str, name2: str) -> bool:
        """Check for common name variations and nicknames."""
        # Common nickname mappings
        nicknames = {
            'william': ['bill', 'billy', 'will', 'willy'],
            'robert': ['bob', 'rob', 'robby', 'bobby'],
            'richard': ['rick', 'rich', 'dick', 'ricky'],
            'james': ['jim', 'jimmy', 'jamie'],
            'michael': ['mike', 'mikey', 'mick', 'mickey'],
            'david': ['dave', 'davey'],
            'christopher': ['chris', 'topher'],
            'daniel': ['dan', 'danny'],
            'matthew': ['matt', 'matty'],
            'andrew': ['andy', 'drew'],
            'elizabeth': ['liz', 'lizzy', 'beth', 'betty', 'lisa'],
            'margaret': ['maggie', 'meg', 'peggy'],
            'patricia': ['pat', 'patty', 'trish'],
            'jennifer': ['jen', 'jenny'],
            'susan': ['sue', 'suzie'],
            'jessica': ['jess', 'jessie'],
            'sarah': ['sally', 'sara'],
            'karen': ['kari', 'karen'],
            'nancy': ['nan', 'nancy'],
            'lisa': ['lisa', 'liz'],
            'helen': ['helen', 'helena'],
            'sandra': ['sandy', 'sandra'],
            'donna': ['donna', 'don'],
            'carol': ['carol', 'caroline'],
            'ruth': ['ruth', 'ruthie'],
            'sharon': ['sharon', 'shari'],
            'michelle': ['michelle', 'mickey'],
            'laura': ['laura', 'laurie'],
            'emily': ['emily', 'em'],
            'kimberly': ['kim', 'kimberly'],
            'deborah': ['deb', 'debbie'],
            'dorothy': ['dot', 'dotty', 'dottie'],
            'linda': ['linda', 'lin'],
            'barbara': ['barb', 'barbara'],
            'ashley': ['ash', 'ashley'],
            'amanda': ['mandy', 'amanda'],
            'stephanie': ['steph', 'stephanie'],
            'nicole': ['nikki', 'nicole'],
            'emma': ['emma', 'em'],
            'samantha': ['sam', 'samantha'],
            'katherine': ['kate', 'kathy', 'katie', 'kat'],
            'christine': ['chris', 'christine'],
            'debra': ['deb', 'debbie'],
            'rachel': ['rach', 'rachel'],
            'carolyn': ['carol', 'carolyn'],
            'janet': ['jan', 'janet'],
            'virginia': ['ginny', 'virginia'],
            'maria': ['maria', 'marie'],
            'heather': ['heather', 'heath'],
            'diane': ['diane', 'diana'],
            'julie': ['julie', 'jules'],
            'joyce': ['joyce', 'joy'],
            'victoria': ['vicky', 'victoria'],
            'kelly': ['kelly', 'kel'],
            'christina': ['tina', 'christina'],
            'joan': ['joan', 'jo'],
            'evelyn': ['eve', 'evelyn'],
            'lauren': ['lauren', 'laurie'],
            'judith': ['judy', 'judith'],
            'megan': ['meg', 'megan'],
            'cheryl': ['cheryl', 'cher'],
            'andrea': ['andy', 'andrea'],
            'hannah': ['hannah', 'hanna'],
            'jacqueline': ['jackie', 'jacqueline'],
            'martha': ['martha', 'marty'],
            'gloria': ['gloria', 'glory'],
            'ann': ['ann', 'annie'],
            'brenda': ['brenda', 'bren'],
            'pamela': ['pam', 'pamela'],
            'nicole': ['nikki', 'nicole'],
            'emma': ['emma', 'em'],
            'samantha': ['sam', 'samantha'],
            'katherine': ['kate', 'kathy', 'katie', 'kat'],
            'christine': ['chris', 'christine'],
            'debra': ['deb', 'debbie'],
            'rachel': ['rach', 'rachel'],
            'carolyn': ['carol', 'carolyn'],
            'janet': ['jan', 'janet'],
            'virginia': ['ginny', 'virginia'],
            'maria': ['maria', 'marie'],
            'heather': ['heather', 'heath'],
            'diane': ['diane', 'diana'],
            'julie': ['julie', 'jules'],
            'joyce': ['joyce', 'joy'],
            'victoria': ['vicky', 'victoria'],
            'kelly': ['kelly', 'kel'],
            'christina': ['tina', 'christina'],
            'joan': ['joan', 'jo'],
            'evelyn': ['eve', 'evelyn'],
            'lauren': ['lauren', 'laurie'],
            'judith': ['judy', 'judith'],
            'megan': ['meg', 'megan'],
            'cheryl': ['cheryl', 'cher'],
            'andrea': ['andy', 'andrea'],
            'hannah': ['hannah', 'hanna'],
            'jacqueline': ['jackie', 'jacqueline'],
            'martha': ['martha', 'marty'],
            'gloria': ['gloria', 'glory'],
            'ann': ['ann', 'annie'],
            'brenda': ['brenda', 'bren'],
            'pamela': ['pam', 'pamela']
        }
        
        # Check if names are nicknames of each other
        words1 = name1.lower().split()
        words2 = name2.lower().split()
        
        for word1 in words1:
            for word2 in words2:
                # Check if either word is a nickname of the other
                if word1 in nicknames and word2 in nicknames[word1]:
                    return True
                if word2 in nicknames and word1 in nicknames[word2]:
                    return True
        
        # Check for common name variations (e.g., "John" vs "Johnny")
        common_variations = {
            'john': ['johnny', 'jon', 'jonathan'],
            'joseph': ['joe', 'joey'],
            'thomas': ['tom', 'tommy'],
            'charles': ['charlie', 'chuck'],
            'christopher': ['chris', 'topher'],
            'anthony': ['tony', 'ant'],
            'donald': ['don', 'donny'],
            'steven': ['steve', 'stevie'],
            'paul': ['paulie'],
            'mark': ['marky'],
            'kenneth': ['ken', 'kenny'],
            'george': ['georgie'],
            'timothy': ['tim', 'timmy'],
            'ronald': ['ron', 'ronnie'],
            'jason': ['jay'],
            'edward': ['ed', 'eddie', 'ted'],
            'jeffrey': ['jeff'],
            'ryan': ['ry'],
            'jacob': ['jake'],
            'gary': ['gary'],
            'nicholas': ['nick', 'nickie'],
            'eric': ['eric'],
            'jonathan': ['jon', 'jonny'],
            'stephen': ['steve', 'stevie'],
            'larry': ['larry'],
            'justin': ['justin'],
            'scott': ['scotty'],
            'brandon': ['brandon'],
            'benjamin': ['ben', 'benny'],
            'samuel': ['sam', 'sammy'],
            'frank': ['frankie'],
            'gregory': ['greg'],
            'raymond': ['ray'],
            'alexander': ['alex', 'al'],
            'patrick': ['pat', 'patty'],
            'jack': ['jackie'],
            'dennis': ['denny'],
            'jerry': ['jerry'],
            'tyler': ['ty'],
            'aaron': ['aaron'],
            'jose': ['jose'],
            'adam': ['adam'],
            'nathan': ['nate'],
            'henry': ['hank'],
            'douglas': ['doug'],
            'zachary': ['zach', 'zack'],
            'peter': ['pete'],
            'kyle': ['kyle'],
            'walter': ['walt'],
            'ethan': ['ethan'],
            'jeremy': ['jeremy'],
            'harold': ['harry', 'hal'],
            'seth': ['seth'],
            'christian': ['chris'],
            'andrew': ['andy', 'drew'],
            'sean': ['shawn'],
            'nathaniel': ['nate', 'nathan'],
            'terry': ['terry'],
            'max': ['max'],
            'oscar': ['oscar'],
            'keith': ['keith'],
            'tyler': ['ty'],
            'aaron': ['aaron'],
            'jose': ['jose'],
            'adam': ['adam'],
            'nathan': ['nate'],
            'henry': ['hank'],
            'douglas': ['doug'],
            'zachary': ['zach', 'zack'],
            'peter': ['pete'],
            'kyle': ['kyle'],
            'walter': ['walt'],
            'ethan': ['ethan'],
            'jeremy': ['jeremy'],
            'harold': ['harry', 'hal'],
            'seth': ['seth'],
            'christian': ['chris'],
            'andrew': ['andy', 'drew'],
            'sean': ['shawn'],
            'nathaniel': ['nate', 'nathan'],
            'terry': ['terry'],
            'max': ['max'],
            'oscar': ['oscar'],
            'keith': ['keith']
        }
        
        for word1 in words1:
            for word2 in words2:
                if word1 in common_variations and word2 in common_variations[word1]:
                    return True
                if word2 in common_variations and word1 in common_variations[word2]:
                    return True
        
        return False
    
    def _check_partial_address_match(self, addr1: str, addr2: str) -> bool:
        """Check for partial address matches (e.g., same street but different apartment)."""
        words1 = addr1.split()
        words2 = addr2.split()
        
        # If addresses are very different in length, they're probably not a match
        if abs(len(words1) - len(words2)) > 3:
            return False
        
        # Check if they share the same street number and street name
        # Look for numbers at the beginning
        number1 = None
        number2 = None
        
        for word in words1:
            if word.isdigit():
                number1 = word
                break
        
        for word in words2:
            if word.isdigit():
                number2 = word
                break
        
        # If both have the same street number, check street name similarity
        if number1 and number2 and number1 == number2:
            # Remove the number and compare the rest
            addr1_without_number = ' '.join([w for w in words1 if w != number1])
            addr2_without_number = ' '.join([w for w in words2 if w != number2])
            
            # Calculate similarity without the number
            word_similarity = self._word_similarity(addr1_without_number, addr2_without_number)
            return word_similarity >= 0.7  # 70% threshold for partial address match
        
        return False
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format."""
        try:
            # Handle common date formats
            import re
            from datetime import datetime
            
            # Remove extra spaces and common separators
            date_str = re.sub(r'[^\w\s-]', ' ', date_str).strip()
            
            # Try different date formats
            formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%d-%m-%Y',
                '%m-%d-%Y',
                '%d %m %Y',
                '%m %d %Y',
                '%Y/%m/%d',
                '%Y/%d/%m'
            ]
            
            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return original
            return date_str
            
        except Exception:
            return date_str
    
    def _clean_address(self, address: str) -> str:
        """Clean address string for comparison."""
        import re
        
        # Remove common punctuation and extra spaces
        cleaned = re.sub(r'[^\w\s]', ' ', address)
        cleaned = ' '.join(cleaned.split())
        
        # Remove common words that don't affect matching
        common_words = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln']
        words = cleaned.split()
        filtered_words = [word for word in words if word.lower() not in common_words]
        
        return ' '.join(filtered_words)

# Create global instance
document_processor = DocumentProcessor() 
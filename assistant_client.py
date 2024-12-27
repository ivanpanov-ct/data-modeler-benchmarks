from data_utils import persist_assistant_output
import google.oauth2.id_token
import google.auth.transport.requests
import requests
import json
import time
import base64
import os

LLM_SERVICE_URL='https://llm-service-211345793691.europe-west4.run.app'
BUCKET_NAME='ctp-vertex-sandbox-bucket'
PROJECT_ID='ctp-vertex-sandbox'
LOCATION='europe-west2' #does FE really need to know all this data? should they not be part of LLM service config?
FOLDER_NAME_TUTORIALS = 'modeling_product_tutorial_summary' #does FE really need to know all this data? should they not be part of LLM service config?
QUEUE_ID = "product-data-modeling-queue" #does FE really need to know all this data? should they not be part of LLM service config?
PROMPTS = json.loads('{"prompt": "live-prompt.json", "prompt_feedback": "live-prompt-feedback.json", "prompt_feedback_with_sample_data": "live-prompt-feedback-with-sample-data.json"}') #does FE really need to know all this data? should they not be part of LLM service config?
MODEL_NAME = "gemini-1.5-pro-001"
LARGE_FILES_CONFIG = json.loads('{"use_flash": true, "flash_model_name": "gemini-1.5-flash-002", "chunking_overlap": 100}')
SERVICE_ACCOUNT_EMAIL = "sa-llm-service@ctp-vertex-sandbox.iam.gserviceaccount.com"
USE_SAMPLE_FOR_FEEDBACK = False
GENERATION_CONFIG = json.loads('{"max_output_tokens": 8192, "temperature": 0, "top_p": 0.9}')

# TODO run -> evaluation_run or evaluation; run vs conversation into -> docs
def run_assistant_requests(run_data):
    """Feed every piece of test data to the assistant and persist the assistant output"""

    # TODO run requests in parallel
    for conversation_data in run_data["conversations"]:
        input_files = conversation_data["input_files"]
        parameters = conversation_data["parameters"]
        data_model, comment = send_request_to_assistant(input_files, parameters)
        persist_assistant_output(conversation_data, data_model, comment)
        pass

def send_request_to_assistant(input_files, parameters):
    print (f"sending request to assistant {input_files}, {parameters}")

    auth_headers = get_llm_service_auth_headers()
    #request_data = dummy_request 
    
    request_data = json.dumps(build_llm_map_request(input_files, parameters))

    with open('dummy-req.txt', "w") as file:
        # Write the string to the file
        file.write(dummy_request)

    with open('real-req.txt', "w") as file:
        # Write the string to the file
        file.write(request_data)

    response = requests.post(LLM_SERVICE_URL + "/map", data=request_data, headers=auth_headers)
    response.raise_for_status()

    job_id = response.json()["job_id"]

    return get_result_of_a_job(job_id, auth_headers)

def get_result_of_a_job(job_id, auth_headers):
    WAITING_TIME = 10
    status = None
    result = None
    while True:
        status_response = requests.get(LLM_SERVICE_URL + f"/status/{job_id}?bucket_name=" + BUCKET_NAME, headers=auth_headers)
        print('polling')
        status_response.raise_for_status()
        status_data = status_response.json()
        status = status_data["status"]
        #status = status_response.json()["status"]
        if status == "completed":
            break
        elif status == "failed":
            error_message = status_data["error"]
            #st.error("Job failed. Please check the backend logs for details.")
            break
        time.sleep(WAITING_TIME) 

    # Retrieve results
    if status == "completed":
        try:
            results_response = requests.get(LLM_SERVICE_URL + f"/results/{job_id}?bucket_name=" + BUCKET_NAME, headers=auth_headers)
            results_response.raise_for_status()
            if results_response == "failed":
                raise Exception("Job failed. Please check the backend logs for details.")
            else:
                results = results_response.json()
                comment = results.get("markdown")
                comment = comment.replace("```markdown", "").replace("```", "") 
                data_model_json = results.get("json_content")
                csv_content = results.get("csv_content")
        except Exception as e:
            Exception(f"An unexpected error occurred: {e}") 
    
    return data_model_json, comment

def get_llm_service_auth_headers():
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, LLM_SERVICE_URL)
    return {'Authorization': f'Bearer {id_token}'}


def build_llm_map_request(input_files, parameters):
    sample_data = get_sample_data(input_files)
    granularity_level = 2 #FIXME
    industry_type = [] #FIXME
    request_data = {
        "data": sample_data,
        "granularity": granularity_level,
        "questions": {
            "prodFams": parameters['prodFams'],
            "attrPerProdFam": parameters['attrPerProdFam'],
            "mandatoryAttrs": parameters['mandatoryAttrs'],
            "searchableAttrs": parameters['searchableAttrs'],
            "localizedAttrs": parameters['localizedAttrs'],
            "predefinedValsAttrs": parameters['predefinedValsAttrs'],
        },
        "industry_type": industry_type,
        "llm_service_url": LLM_SERVICE_URL,
        "bucket_name": BUCKET_NAME,
        "project_id": PROJECT_ID,
        "location": LOCATION, 
        "folder_name_tutorials": FOLDER_NAME_TUTORIALS,
        "queue_id": QUEUE_ID,
        "prompts": PROMPTS,
        "model_name": MODEL_NAME,
        "large_files_config": LARGE_FILES_CONFIG,
        "service_account_email": SERVICE_ACCOUNT_EMAIL,
        "use_sample_for_feedback": USE_SAMPLE_FOR_FEEDBACK,
        "generation_config": GENERATION_CONFIG,
    }
    
    return request_data

def get_sample_data(input_files):
    for input_file in input_files:
        with open(input_file, "rb") as file:
            bytes_data = file.read()
            file_name = os.path.basename(input_file)

            if file_name.endswith(".xlsx"):                                               
                encoded_bytes = base64.b64encode(bytes_data).decode('utf-8')
                sample_data = {"content": encoded_bytes, "name": file_name}          
            elif file_name.endswith(".txt"):  
                sample_data = {"content": bytes_data.decode(), "name": file_name}
            elif file_name.endswith(".pdf"):
                #save_pdf = save_pdf_to_gcs(uploaded_file, BUCKET_NAME, "product_data_modeling_requests/" + uploaded_file.name)
                #if not save_pdf:
                #    st.error("Error saving PDF file to GCS")
                #else:
                #    sample_data = {"content": "", "name": uploaded_file.name}   
                pass #FIXME
            else:                                                                       # For other file types (csv, json)
                sample_data = {"content": bytes_data.decode(), "name": file_name} 
        
    return sample_data


def parse_assistant_response(assistant_response):
    pass


def tmp():

    
    pass
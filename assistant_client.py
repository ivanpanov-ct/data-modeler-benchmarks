import httpx
import asyncio
from data_utils import persist_assistant_output
import google.oauth2.id_token
import google.auth.transport.requests
import json
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

def run_cases(run_data):
    cases = run_data["conversations"]
    loop = asyncio.new_event_loop()
    tasks  = [loop.create_task(run_case(case)) for case in cases]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

async def run_case(case):
    input_files = case["input_files"]
    parameters = case["parameters"]
    data_model, comment, error = await generate_data_model(input_files, parameters)
    persist_assistant_output(case, data_model, comment, error)   

async def generate_data_model(input_files, parameters):
    print (f"sending request to assistant {input_files}, {parameters}")

    auth_headers = get_llm_service_auth_headers()
    
    request_data = json.dumps(build_llm_map_request(input_files, parameters))

    async with httpx.AsyncClient() as client:
        response = await client.post(
            LLM_SERVICE_URL + "/map",
            data=request_data,
            headers=auth_headers
        )
        response.raise_for_status()
        job_id = response.json()["job_id"]

    return await get_job_result(job_id, auth_headers)

async def get_job_result(job_id, auth_headers):
    WAITING_TIME = 10

    comment = None 
    data_model_json = None 
    error = None
    
    status = None
    while True:
        async with httpx.AsyncClient() as client:
            status_url = f"{LLM_SERVICE_URL}/status/{job_id}?bucket_name={BUCKET_NAME}"
            print(f"Polling. Job id: {job_id}")
            response = await client.get(status_url, headers=auth_headers)
            response.raise_for_status()
            status_data = response.json()
            status = status_data["status"]

        if status == "completed":
            break
        elif status == "failed":
            error_message = status_data["error"]
            error = f'Job failed:{error_message}'
            print(error)
            break
        
        await asyncio.sleep(WAITING_TIME) 

    if status == "completed":
        try:
            async with httpx.AsyncClient() as client:
                results_url = f"{LLM_SERVICE_URL}/results/{job_id}?bucket_name={BUCKET_NAME}"
                response = await client.get(results_url, headers=auth_headers)
                response.raise_for_status()

                if response.text == "failed":
                    pass # TODO
                else:
                    results = response.json()
                    comment = results.get("markdown")
                    comment = comment.replace("```markdown", "").replace("```", "")
                    data_model_json = results.get("json_content", "")
            
        except Exception as e:
            error = f"An unexpected error occurred: {e}"
    
    return data_model_json, comment, error

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

from data_utils import persist_assistant_output

# TODO run -> evaluation_run or evaluation
def run_assistant_requests(run_data):
    """Feed every piece of test data to the assistant and persist the assistant output"""

    for conversation_data in run_data["conversations"]:
        input_files = conversation_data["input_files"]
        parameters = conversation_data["parameters"]
        data_model, comment = send_request_to_assistant(input_files, parameters)
        persist_assistant_output(conversation_data, data_model, comment)
        pass


def send_request_to_assistant(input_files, parameters):
    print (f"sending request to assistant {input_files}, {parameters}")

    assistant_response = None
    return None, None #TODO
    data_model, comment = parse_assistant_response(assistant_response)
    pass

def parse_assistant_response(assistant_response):
    pass
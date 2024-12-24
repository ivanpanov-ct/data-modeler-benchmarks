from data_utils import prepare_data_for_run
from assistant_client import run_assistant_requests
from results_evaluator import evalute_run_results

def run(mode="auto"):    
    print("Running tests")

    run_data = prepare_data_for_run() #FIXME
    run_assistant_requests(run_data)
    evalute_run_results(run_data, mode)
    
run()

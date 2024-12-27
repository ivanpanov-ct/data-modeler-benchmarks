# Usage
dme --auto - run evaluation fully automated (AI will match expected the real output with expected on)
dme --human - run human evaluation (every generated output will be shown to human along with the expected output. Human will give a score to generated output)
dme --hybrid - run human + AI evaluation (every generated output along with the expected output will be shown to AI. If it obviously matches, AI gives it a high score. Otherwise it will be given to a human for evaluation)

# Scoring
## Scoring of individual run evaluation
1 - the result is an absolute non-sense
2 - the result has a few parts that make sense, but is mostly wrong and is hardly helpful in practice
3 - the result has some correct parts, but also some significant mistakes. Might be partially helpful for some cases.
4 - the result is mostly correct, but there minor improvement possibilities
5 - the result totally matches the expectation

TODO precision and recall?

## Scoring of whole dataset evalutation
total score = average(results of individual run) #FIXME we need to come up with a better formula that reflects the actual business goals (is it more important to get certain percentage of ideal results? is it more important to get rid on non-sense? are mediocre results acceptable? etc.)

# Dataset structure
## Input
Every data point of an input dataset corresponds to a to a user interaction with the Data Modeler. It includes end-to-end interaction (includes data about all actions user did to get the final result).
It might be just one interaction (if user got expected result from the first shot) or also rounds of feedback conversation (if the user had to refine the initial result).

- Id 
- Products data - set of datasets containing the product data. Format 
- Input params
- Feedback messages (optional) -

## Ground truth (aka test dataset)
Ground truth dataset includes "correct" end-to-end interactions of user and system. Each data point contains a data point from input dataset + expected result.

Fields
- Id 
- Products data
- Input params
- Feedback messages (user)
- Feedback response 
- Results
TODO think about better format for results and feedback - should it be an integrated....?

## Evaluation datasets
Containts results of evaluation. 
Data point:
- Input Id
- Real result
- Expected result
- Score
- Evalutor comment
TODO should result include both feedback conversation and result?

TODO allow multiple valid variants of output?
TODO add wrights to mistakes?


## Datasets versioning
TODO

## Test data
- positive and negative examples 
- with and without feedback
- scaling edge cases (too many attributes, to many variants, to many products for model to grasp)


# Setup
## Activate virtual environment
(if you haven't create the environment yet) python3 -m venv dme-venv
source dme-venv/bin/activate

## Setup Google Cloud credentials
- create a key for LLM Service Account (https://console.cloud.google.com/iam-admin/serviceaccounts/details/113288978936219270482?hl=en&inv=1&invt=AblLNQ&project=ctp-vertex-sandbox)
- download this key and store in local holder
- set the following environment variable 'export GOOGLE_APPLICATION_CREDENTIALS="path-to-service-account-key/my-key.json"'

## Install dependencies
pip install -r requirements.txt
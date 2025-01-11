## Usage
python main.py

## Setup
### Activate virtual environment
(if you haven't create the environment yet) python -m venv dme-venv
source dme-venv/bin/activate

### Setup Google Cloud credentials
- create a key for LLM Service Account (https://console.cloud.google.com/iam-admin/serviceaccounts/details/113288978936219270482?hl=en&inv=1&invt=AblLNQ&project=ctp-vertex-sandbox)
- download this key and store in local holder
- set the following environment variable 'export GOOGLE_APPLICATION_CREDENTIALS="path-to-service-account-key/my-key.json"'

### Install dependencies
pip install -r requirements.txt

## Dataset structure
## Ground truth (aka test dataset)
Ground truth dataset contains data used to test different aspects of data modeller behaviour. The ground truth dataset is a collection of "cases". 

Each case contain:
- input data (what is given to the assistant for generating data model - sample data from catalog and input parameters)
- expected output data
- notes - any additional information to be noted about this case. not machine-readable, only for information purposes

Ground truth is an asset of the project and is versioned with it (treated as code)

## Run data
Run data is a collection of data from individual exections of benchmark. 

Data of a single execution contains a copy of the whole ground truth data. In addition to it, every case of ground-truth is amended by a generated-output and evaluation data (score, comment from evaluator)

Run data is treated as transient (is not versioned together with the code)

## Cases design 
Assumptions:
- we focus on optimizing first output (i.e. optimizing quality of feedback conversation is out of scope for now)
- we focus on optimizing JSON output (i.e. markdown text is out of scope for now)

TODO scaling edge cases (too many attributes, to many variants, to many products for model to grasp)
TODO positive and negative examples
TODO cases with multiple valid outputs
TODO test granularity 

## Scoring
### Scoring of individual run evaluation
1. the result is an absolute non-sense
2. the result has a few parts that make sense, but is mostly wrong and is hardly helpful in practice
3. the result has some correct parts, but also some significant mistakes. Might be partially helpful for some cases.
4. the result is mostly correct, but there minor improvement possibilities
5. the result totally matches the expectation

### Scoring of whole dataset evalutation
total score = average(results of individual run) #FIXME we need to come up with a better formula that reflects the actual business goals (is it more important to get certain percentage of ideal results? is it more important to get rid on non-sense? are mediocre results acceptable? etc.)

## (draft) Planned Usage 
benchmark --auto - run benchmark fully automated (AI will compare the expected outputs with the real ones and give a score)
benchmark --human - run benchmark with human evaluation (a human will compare expected outputs with the real ones and give a score)
benchmark --hybrid - run human + AI evaluation (AI tries compare the expected outputs with the real ones. For easy cases it give a score, for less obvious ones the evaluation will is handed over to a human)
benchmark --score - 


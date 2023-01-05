import re 
import os 
import pandas as pd
from datasets import load_dataset
from joblib import dump

def reg_func(regex):
    # compile our regex
    pattern = re.compile(regex)
    dataset = load_dataset("GroNLP/ik-nlp-22_slp")
    # https://www.dataquest.io/blog/regular-expressions-data-scientists/
    df = dataset['train'].to_pandas()
    # create a new column in our dataframe for the matches 
    df['matches'] = False 
    # iterate over the rows in our dataframe for the regex matches 
    for index, row in df.iterrows():
        if pattern.search(row['text']) is not None:
            # set value of the matchest column to true 
            df.loc[index, 'matches'] = True
    return df

# now convert the function to dump file 
dump(reg_func, "regex_dump.joblib")

if __name__ == "__main__":
    reg_func("[0-9]+")
    print("done")


"""
import re 
from kserve import InferenceService
service = InferenceService()

# Define the inference function
def regex_inference(string: str, regex: str) -> bool:
    #Inference function that checks if a string matches a given regex pattern.
    pattern = re.compile(regex)
    return bool(pattern.match(string))

# Register the inference function with the InferenceService instance
service.register_inference_function(regex_inference)

# Start the inference service
service.start()

# Start the service
service.start()

# Create a client for the service
client = kserse.Client('regex_service')

# Call the service's function
result = client.regex_inference('[0-9]+', 'My favorite number is 7')

"""
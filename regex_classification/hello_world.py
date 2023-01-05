import pickle 

def hello_world(message):
    return "Hello" + message + "!"


with open("hello_world.pkl", "wb") as f:
        pickle.dump(hello_world, f)
# https://stackoverflow.com/questions/60863928/how-can-i-python-function-export-and-recall-pickle-joblib-dump
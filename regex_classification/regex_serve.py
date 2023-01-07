import kserve 
from typing import Dict 
import pickle
from regex_func import regex_func

class regex_func(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()
        self.model = None
        self.ready = False

    def load(self):
        # Load your model here
        self.ready = True
        self.model = pickle.load(open("regex_dump.pkl", 'rb')) 


    def predict(self, request: Dict) -> Dict:
        print('regex function called', request)
        regex = request["regex"]
        string = request["string"]
        result = regex_func(regex, string) # something is off here 
        return {"predictions": result}


if __name__ == "__main__":
    model = regex_func("regex-model")
    model.load()
    kserve.ModelServer().start([model])

# http://incredible.ai/kubernetes/2022/01/01/KServe-Custom-Model/
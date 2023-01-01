import kserve 
from typing import Dict 
import joblib

class regex_func(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        # Load your model here
        self.ready = True
        self.model = joblib.load("regex_dump.joblib") # double check this

    def predict(self, request: Dict) -> Dict:
        print('regex function called', request)
        inputs = request["inputs"]
        result = regex_func(inputs)
        return {"predictions": result}


if __name__ == "__main__":
    model = regex_func("regex-world")
    model.load()
    #model.predict()
    kserve.KServe().start([model])

# http://incredible.ai/kubernetes/2022/01/01/KServe-Custom-Model/
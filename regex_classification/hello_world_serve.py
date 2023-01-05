import kserve 
from typing import Dict, list
import pickle

class hello_world(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        # Load your model here
        self.ready = True
        self.model = pickle.load("hello_world.pkl") # double check this


    def predict(self, request: Dict) -> Dict:
        print('predict function called', request)
        inputs = request["inputs"]
        result = hello_world(inputs)
        return {"message": result}

if __name__ == "__main__":
    model = hello_world("hello-world")
    model.load()
    #model.predict()
    kserve.KServe().start([model])


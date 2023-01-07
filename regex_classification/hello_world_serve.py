import kserve 
from typing import Dict
import pickle


class hello_world(kserve.Model):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.load()
        self.model = None
        self.ready = False

    def load(self):
        # Load your model here
        self.ready = True
        self.model = pickle.load(open("hello_world.pkl", 'rb')) 


    def predict(self, request: Dict) -> Dict:
        print('predict function called', request)
        inputs = request["inputs"]
        result = hello_world(inputs)
        return {"message": result}

if __name__ == "__main__":
    model = hello_world("hello-world")
    model.load()
    kserve.ModelServer().start([model]) 

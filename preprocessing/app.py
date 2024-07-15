from flask import Flask, jsonify, request
from package.circuit.circuit import Circuit
from package.simulation.simulation import Simulation
from package.simulation.graph import Graph

app = Flask(__name__)

# Create instances of your classes
my_class1 = Circuit()
my_class2 = Simulation()
my_class3 = Graph()

# Define your API routes
@app.route('/api/myclass1', methods=['POST'])
def post_myclass1():
    # Get data from the request and pass it to a method in MyClass1
    data = request.get_json()
    response = my_class1.some_method(data)
    return jsonify(response), my_class3

@app.route('/api/myclass2', methods=['POST'])
def post_myclass2():
    # Get data from the request and pass it to a method in MyClass2
    data = request.get_json()
    response = my_class2.another_method(data)
    return jsonify(response)

if __name__ == '__main__':
    app.run()
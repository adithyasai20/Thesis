"""
The circuit class gets a name, a dictionary of gate names and their corresponding gate objects,
a dictionary of voltage source names , and an end of sequence capacitance and sizing.
The user will provide a topologically sorted dictionary of gate names and their corresponding gate objects.
structure of the gates dictionary:
{
    "gate_name": {"type": str, "k": int, "input_components": [input_gate_names or input voltage_source_names : str]}
}
structure of the voltage sources dictionary:
{
    "voltage_source_name": {"ideal": bool, "k": int}
}
Structure of the eos_dict dictionary:
{
    "k": int,
    "input_gate": "gate_name",
    "capacitance": float
}
inverting: bool


The circuit class will generate a netlist for the circuit and write it to a file.
The circuit class will also generate a spice simulation for the circuit and write it to a file.
example:
circuit1 = Circuit("circuit1", 
                    {
                        "gate1": {"type":"2NOR", "k":2, "input_components":["v1", "v2"]},
                        "gate2": {"type":"1NOT", "k":10, "input_components":["gate1"]}
                    },
                    {
                        "v1": { "ideal": False, "k": 1},
                        "v2": { "ideal": False, "k": 1}
                    },
                    {
                        "k": 1,
                        "input_gate": "gate1",
                        "capacitance": 9
                    }, 
                    inverting=True
                    )

"""

import numpy as np

from .voltagesource import VoltageSource
from .gate import Gate
from .eos import EndOfSequence


class Circuit:
    """
    Represents a circuit.

    Args:
        name (str): The name of the circuit.
        gate_dict (dict): A dictionary containing gate configurations.
        voltage_dict (dict): A dictionary containing voltage source configurations.
        eos_dict (dict): A dictionary containing end-of-sequence configuration.
        inverting (bool, optional): Specifies whether the circuit is inverting or not. Defaults to False.
    """
    GATE_CHOICES = ["2NAND", "1NOT", "2NOR", "2AND", "2OR"]

    def __init__(self, name:str, gate_dict:dict, voltage_dict:dict, eos_dict:dict, inverting = False):
        self.name = name
        self.gates = {}
        self._voltage_sources = {}
        self._eos = None
        self.netlist = ""
        self.voltage_dict = {key + name: value for key, value in voltage_dict.items()}
        self.gate_dict = {key + name: value for key, value in gate_dict.items()}
        self._inverting = inverting

        for _, value in gate_dict.items():
            value['input_components'] = [item + name for item in value['input_components']]
        
        self.eos_dict = eos_dict
        
        self.eos_dict["input_gate"] = eos_dict["input_gate"] + name
        
        self.__generate_voltage_sources(self.voltage_dict)
        self.__generate_gates(self.gate_dict)
        self.__generate_eos(self.eos_dict)
        self.__generate_netlist()

    def _get_gate_number(self, gate_name:str):
        """
        Returns the gate number of the given gate name.

        Args:
            gate_name (str): The name of the gate.

        Returns:
            int: The gate number of the given gate name.
        """
        if gate_name.endswith(self.name):
            gate_name_minus_circuit_name = gate_name[:len(gate_name)-len(self.name)]
        else:
            raise ValueError("The given gate name does not belong to this circuit.")
        
        if gate_name_minus_circuit_name.startswith("gate"):
            return int(gate_name_minus_circuit_name[4:])-1
        else:
            return -1
        
    def make_feature_matrix(self):
        """
        Returns the feature matrix of the circuit.

        each node has 3 types of features : node specific features(`F`) - [type of node]
                                            common features(`C`) - [overall input cap, overall output cap, t_delay]
                                            sizing of node(`K`) - [sizing of the node(k)]
        We will make a feature matrix of the circuit with only `F`, `K`, overall input cap and overall output cap features.
        You have to perform the preprocessing before performing graph representation learning, so add the t_delay feature 
        after preprocessing.

        Returns:
            numpy.ndarray: The feature matrix of the circuit.
        """
        number_of_gates = len(self.gates)
        number_of_features = 5
        feature_matrix = np.zeros((number_of_gates, number_of_features))
        for gate in self.gates.values():
            gate_number = self._get_gate_number(gate.name)
            type_of_gate = self.GATE_CHOICES.index(gate.type)
            overall_input_cap = self.gates[list(self.gates.keys())[0]].k
            overall_output_cap = self._eos.k
            sizing_of_gate = self.gates[gate.name].k
            feature_matrix[gate_number] = [gate_number, type_of_gate, overall_input_cap, overall_output_cap, sizing_of_gate]
        return feature_matrix
    
    def make_adjacency_list(self):
        """
        Returns the adjacency list of the circuit.

        Returns:
            list: The adjacency list of the circuit.
        """
        adjacency_list = set()
        for gate in self.gates.values():
            gate_number = self._get_gate_number(gate.name)
            for input_gate in gate.input_gates:
                input_gate_number = self._get_gate_number(input_gate.name)
                if input_gate_number != -1 and gate_number != -1:
                    adjacency_list.add((input_gate_number, gate_number))
        adjacency_list = list(adjacency_list)
        adjacency_list = sorted(adjacency_list, key=lambda x: x[0])

        return adjacency_list

    def make_adjacency_matrix(self):
        """
        Returns the adjacency matrix of the circuit.

        Returns:
            numpy.ndarray: The adjacency matrix of the circuit.
        """
        num_gates = len(self.gates)
        adjacency_matrix = np.zeros((num_gates, num_gates))
        for gate in self.gates.values():
            gate_number = self._get_gate_number(gate.name)  # 0 indexed gate numbering
            for input_gate in gate.input_gates:
                input_gate_number = self._get_gate_number(input_gate.name) # 0 indexed gate numbering
                if input_gate_number != -1 and gate_number != -1 and adjacency_matrix[gate_number][input_gate_number] == 0:
                    adjacency_matrix[input_gate_number][gate_number] = 1
                    adjacency_matrix[gate_number][input_gate_number] = -1

        return adjacency_matrix
    
    def __generate_voltage_sources(self, voltage_dict):
        """
        Generates voltage sources based on the given voltage dictionary.

        Args:
            voltage_dict (dict): A dictionary containing voltage source configurations.
        """
        for name, params in voltage_dict.items():
            params['name'] = name
            self._voltage_sources[name] = VoltageSource(params)
    
    def __generate_gates(self, gate_dict):
        """
        Generates gates based on the given gate dictionary.

        Args:
            gate_dict (dict): A dictionary containing gate configurations.
        """
        for name, params in gate_dict.items():
            input_components = []
            for input_name in params['input_components']:
                if input_name in self.gates:
                    input_components.append(self.gates[input_name])
                elif input_name in self._voltage_sources:
                    input_components.append(self._voltage_sources[input_name])
            gate_config = {"name":name, "type":params['type'], "k":params['k'], "input_components":input_components}
            self.gates[name] = Gate(gate_config)
    
    def __generate_eos(self, eos_dict):
        """
        Generates the end-of-sequence gate based on the given end-of-sequence dictionary.

        Args:
            eos_dict (dict): A dictionary containing end-of-sequence configuration.
        """
        eos_dict["name"] = self.name
        eos_dict["input_gate"] = self.gates[eos_dict["input_gate"]]
        self._eos = EndOfSequence(eos_dict)

    def return_netlist(self):
        """
        Returns the netlist of the circuit.

        Returns:
            tuple: A tuple containing the netlist and the simulation statement.
        """
        netlist = ""
        for voltage_source in self._voltage_sources.values():
            netlist += voltage_source.netlist
        for gate in self.gates.values():
            netlist += gate.netlist
        netlist += str(self._eos)

        if self._inverting:
            simulation_statement = f".MEASURE TRAN tdlay{self.name} TRIG V({self._voltage_sources[list(self._voltage_sources.keys())[0]].output_node_name})"+\
        f" VAL = 0.35 TD = 0n RISE = 1 TARG V({self._eos.input_gate.output_node_name}) VAL = 0.35  FALL = 1\n"
        else:
            simulation_statement = f".MEASURE TRAN tdlay{self.name} TRIG V({self._voltage_sources[list(self._voltage_sources.keys())[0]].output_node_name})"+\
        f" VAL = 0.35 TD = 0n RISE = 1 TARG V({self._eos.input_gate.output_node_name}) VAL = 0.35  RISE = 1\n"

        
        return netlist, simulation_statement


    def __generate_netlist(self):
        """
        Generates the netlist of the circuit.

        Returns:
            str: The generated netlist.
        """
        self.netlist = f"/////////////////////3 STAGE NAND/////////////////////////////\n"+\
                ".inc \"/home/lalithsai20/EMDproject/7nm_TT_160803.pm\"\n\n"
        self.netlist += self.return_netlist()[0]
        self.netlist += "\nVdd vdd 0 0.7\n"
        self.netlist += f"\n.option post\n"+\
                        ".tran 1p 2u\n"
        self.netlist += self.return_netlist()[1]
        self.netlist += ".end\n"
        return self.netlist
    
    def __repr__(self):
        return self.__generate_netlist()

    def save_circuit_to_file(self, file_path:str):
        """
        Saves the circuit netlist to a file.

        Args:
            file_path (str): The path of the file to save the netlist.
        """
        with open(file_path, "w") as file:
            file.write(self.netlist)



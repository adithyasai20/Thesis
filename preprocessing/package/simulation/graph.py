
import numpy as np
from ..circuit.circuit import Circuit
from ..circuit.gate import Gate

class Graph:
    GATE_CHOICES = ["2NAND", "1NOT", "2NOR", "2AND", "2OR"]
    INVERTING_GATES = ["1NOT", "2NAND", "2NOR"]
    NON_INVERTING_GATES = ["2AND", "2OR"]
    def __init__(self, name, max_num_of_gates = 20, max_sizing = 50, BETA = 2):
        self.name = name
        self.BETA = BETA
        self.max_num_of_gates = np.random.randint(10, max_num_of_gates)
        self.max_sizing = max_sizing
        self.circuit = self.__make_circuit()

    def idealized_weights(self, gate_list:list, input_cap:int, output_cap:int):
        """This function implements Linear delay model to calculate 
        the weights of gates for minimum propagation delay.
        The model is based on the following equation:
        f_opt = (G*H)^(1/n) 
        where G = product of g_coeffecients of all gates in the circuit
        H = output_cap/input_cap
        n = number of gates in the circuit
        gate_list : `list[str]` list of gates in the circuit
        input_cap : `int` input capacitance of the circuit's driver
        output_cap : `int` output capacitance of the circuit's load
        """
        g_coeffecients = {
            "2NAND": (self.BETA + 2)/(self.BETA + 1),
            "1NOT": (self.BETA + 1)/(self.BETA + 1),
            "2NOR": (2*self.BETA + 1)/(self.BETA + 1),
            "2AND": (self.BETA + 2)/(self.BETA + 1),
            "2OR": (2*self.BETA + 1)/(self.BETA + 1)

        }
        # Not used in this particular implementation but maybe used in future. idk
        # parasitic_delay_coeffecients = {
        #     "2NAND": (2*self.BETA + 2)/(self.BETA + 1),
        #     "1NOT": (self.BETA + 1)/(self.BETA + 1),
        #     "2NOR": (4*self.BETA + 1)/(self.BETA + 1),
        #     "2AND": (self.BETA + 1)/(self.BETA + 1),
        #     "2OR": (self.BETA + 1)/(self.BETA + 1)
        # }
        H, G= \
            output_cap/input_cap, \
            np.prod([g_coeffecients[gate_idx] for gate_idx in gate_list]) 
        
        f_opt = np.round(    (G*H) ** (1/len(gate_list))    )
        weights, capacitance_list = np.zeros(len(gate_list)), np.zeros(len(gate_list))
        for i in range(len(gate_list)):
            x = f_opt * input_cap / g_coeffecients[gate_list[i]] if i == 0 \
                else f_opt * capacitance_list[i-1] / g_coeffecients[gate_list[i]]
            capacitance_list[i] = x
            weights[i] = max(int(x / (   g_coeffecients[gate_list[i]] * (self.BETA + 1)   )) , 1)


        # if not hasattr(self, "gate_list"):
        #     raise AttributeError("Graph object has no attribute 'gate_list'. Run __make_circuit() first.")
        return weights
    


    def make_adjacency_list_and_feature_matrix(self):
        return np.array(self.circuit.make_adjacency_list()).T, self.circuit.make_feature_matrix()

    def make_graph_matrices(self):
        return self.circuit.make_adjacency_matrix(), self.circuit.make_feature_matrix()
    
    def save_adjacency_list_and_feature_matrix(self, file_path):
        adj_list, feature_matrix = self.make_adjacency_list_and_feature_matrix()
        np.savez(file_path, adj_list=adj_list, feature_matrix=feature_matrix)

    def save_graph_matrices(self, file_path):
        adj_matrix, feature_matrix = self.make_graph_matrices()
        np.savez(file_path, adj_matrix=adj_matrix, feature_matrix=feature_matrix)

    def __make_circuit(self):
        self.gate_list = list(np.random.choice(self.GATE_CHOICES, self.max_num_of_gates))
        self.gate_sizes = np.random.randint(1, self.max_sizing, self.max_num_of_gates)
        self.drivers = [f"v{i+1}" for i in range(int(self.gate_list[0][0]))]
        self.driver_sizes = np.random.randint(1, self.max_sizing, len(self.drivers))

        gate_dict, driver_dict, eos_dict = {}, {}, {}
        ideal_gate_dict, ideal_driver_dict, ideal_eos_dict = {}, {}, {}

        eos_dict["k"] = np.random.randint(1, self.max_sizing)
        eos_dict["input_gate"] = f"gate{len(self.gate_list)}"
        eos_dict["capacitance"] = 10

        ideal_eos_dict["k"] = eos_dict["k"]
        ideal_eos_dict["input_gate"] = f"gate{len(self.gate_list)}"
        ideal_eos_dict["capacitance"] = 10
        self.ideal_weights = self.idealized_weights(self.gate_list, self.driver_sizes[0], eos_dict["k"])



        for i in range(len(self.gate_list)):
            gate_dict[f"gate{i+1}"] = {"type":self.gate_list[i], "k":int(self.gate_sizes[i]), "input_components" : [f"gate{i}" for _ in range(int(self.gate_list[i][0]))] if i > 0 else self.drivers} 
            ideal_gate_dict[f"gate{i+1}"] = {"type":self.gate_list[i], "k":int(self.ideal_weights[i]), "input_components" : [f"gate{i}" for _ in range(int(self.gate_list[i][0]))] if i > 0 else self.drivers}

        for i in range(len(self.drivers)):
            driver_dict[f"v{i+1}"] = {"ideal":False, "k":int(self.driver_sizes[i])}
            ideal_driver_dict[f"v{i+1}"] = {"ideal":False, "k":int(self.driver_sizes[i])}
        
        # count number of invering gates in gate list



        self.num_inverting_gates = len([gate for gate in self.gate_list if gate in self.INVERTING_GATES])
        self.inverting = True if self.num_inverting_gates % 2  else False


        self.circuit = Circuit(self.name, gate_dict, driver_dict, eos_dict, self.inverting)
        self.idealized_circuit = Circuit(self.name, ideal_gate_dict, ideal_driver_dict, ideal_eos_dict, self.inverting)

        return self.circuit
    

    def __repr__(self):
        return f"{self.name}: {self.circuit}"

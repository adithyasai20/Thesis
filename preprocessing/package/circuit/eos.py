from .gate import Gate


class EndOfSequence:
    def __init__(self, config:dict = {}):
        """
        Initializes an EndOfSequence object with the given configuration.

        Args:
            config (dict): Configuration parameters for the EndOfSequence object.
                The dictionary should contain the following keys:
                - 'k' (int): The value of k.
                - 'name' (str): The name of the EndOfSequence object.
                - 'input_gate' (Gate): The input gate object.
                - 'capacitance' (float or int): The capacitance value.
        
        Raises:
            ValueError: If any of the required keys are missing or if the values have incorrect types.
        """
        self._validate_config(config)
        self.k = config['k']
        self.name = config['name']
        self.input_gate = config['input_gate']
        self.capacitance = config['capacitance']
        gate_config = {"name":f"{self.name}EOS", "type":"1NOT", "k":config['k'], "input_components":[config['input_gate']]}
        self.eos = Gate(gate_config)
        self.netlist = self.__generate_netlist()
    
    def __generate_netlist(self):
        """
        Generates the netlist for the EndOfSequence object.

        Returns:
            str: The generated netlist string.
        """
        return self.eos.netlist + f"C{self.name}eos {self.eos.output_node_name} 0 {self.capacitance}f\n"
    
    def __repr__(self):
        """
        Returns a string representation of the EndOfSequence object.

        Returns:
            str: The string representation of the object.
        """
        return self.__generate_netlist()
    
    def _validate_config(self, config):
        """
        Validates the configuration parameters for the EndOfSequence object.

        Args:
            config (dict): Configuration parameters for the EndOfSequence object.

        Raises:
            ValueError: If any of the required keys are missing or if the values have incorrect types.
        """
        required_keys = {
            'k': int,
            'input_gate': Gate,
            'capacitance': (float, int),
            'name': str
        }
        
        for key, expected_type in required_keys.items():
            if key not in config:
                raise ValueError(f"{key.replace('_', ' ').capitalize()} not provided")
            if not isinstance(config[key], expected_type):
                if isinstance(expected_type, tuple):
                    type_names = ' or '.join(t.__name__ for t in expected_type)
                    raise ValueError(f"{key.replace('_', ' ').capitalize()} must be {type_names}")
                else:
                    raise ValueError(f"{key.replace('_', ' ').capitalize()} must be {expected_type.__name__}")
        
        return True
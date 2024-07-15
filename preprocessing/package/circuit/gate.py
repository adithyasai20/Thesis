class Gate:
    """
    Represents a gate in a circuit.

    Attributes:
        VALID_TYPES (set): A set of valid gate types.
        type (str): The type of the gate.
        name (str): The name of the gate.
        output_node_name (str): The name of the output node of the gate.
        k (int): The sizing of the gate.
        input_gates (list): A list of input gates.
        output_nodes (list): A list of output nodes.
        netlist (str): The generated netlist for the gate.

    Methods:
        __init__(self, config: dict = {}): Initializes a Gate object with the given configuration.
        __generate_netlist(self): Generates the netlist for the gate based on its type.
        __repr__(self): Returns the generated netlist for the gate.
        _validate_config(self, config: dict): Validates the configuration of the gate.

    """

    VALID_TYPES = {"2AND", "2OR", "1NOT", "2NAND", "2NOR"}

    def __init__(self, config: dict = {}):
        """
        Initializes a Gate object with the given configuration.

        Args:
            config (dict): The configuration of the gate.

        Raises:
            ValueError: If the gate type, input components, name, or sizing is not provided or is invalid.
        """
        self._validate_config(config)
        if config['type'] not in self.VALID_TYPES:
            raise ValueError(f"Invalid gate type: {config['type']}. Valid types are: {', '.join(self.VALID_TYPES)}")
        if int(config['type'][0]) != len(config['input_components']):
            raise ValueError(f"Number of input components does not match gate type. {config['type']}, {len(config['input_components'])}")
        self.type = config['type']
        self.name = config['name']
        self.output_node_name = f"out_{config['name']}"
        self.k = config['k']
        self.input_gates = config['input_components']
        self.output_nodes = []
        self.netlist = self.__generate_netlist()

    def __generate_netlist(self):
        """
        Generates the netlist for the gate based on its type.

        Returns:
            str: The generated netlist for the gate.
        """
        if self.type == "2NAND":
            return f"M{self.name}m0 {self.output_node_name} {self.input_gates[0].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k * 3)}\n"+\
            f"M{self.name}m1 {self.output_node_name} {self.input_gates[1].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k * 3)}\n"+\
            f"M{self.name}m2 {self.output_node_name} {self.input_gates[0].output_node_name} {self.name}mid 0 nmos_lvt nfin = {int(self.k*4)}\n"+\
            f"M{self.name}m3 {self.name}mid {self.input_gates[1].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*4)}\n\n"
            
        elif self.type == "1NOT":
            return f"M{self.name}m0 {self.output_node_name} {self.input_gates[0].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k * 3)}\n"+\
            f"M{self.name}m1 {self.output_node_name} {self.input_gates[0].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*2)}\n\n"
        
        elif self.type == "2NOR":
            return f"M{self.name}m0 {self.output_node_name} {self.input_gates[0].output_node_name} {self.name}mid vdd pmos_lvt nfin = {int(self.k*6)}\n"+\
                f"M{self.name}m1 {self.name}mid {self.input_gates[1].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k*6)}\n"+\
                f"M{self.name}m2 {self.output_node_name} {self.input_gates[0].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*2)}\n"+\
                f"M{self.name}m3 {self.output_node_name} {self.input_gates[1].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*2)}\n\n"
        
        elif self.type == "2AND":
            return f"M{self.name}m0 {self.output_node_name}intermediate {self.input_gates[0].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k * 3)}\n"+\
                f"M{self.name}m1 {self.output_node_name}intermediate {self.input_gates[1].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k * 3)}\n"+\
                f"M{self.name}m2 {self.output_node_name}intermediate {self.input_gates[0].output_node_name} {self.name}mid 0 nmos_lvt nfin = {int(self.k*4)}\n"+\
                f"M{self.name}m3 {self.name}mid {self.input_gates[1].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*4)}\n"+\
                f"M{self.name}m4 {self.output_node_name} {self.output_node_name}intermediate 0 0 nmos_lvt nfin = {int(self.k*2)}\n"+\
                f"M{self.name}m5 {self.output_node_name} {self.output_node_name}intermediate vdd vdd pmos_lvt nfin = {int(self.k*3)}\n\n"
        
        elif self.type == "2OR":
            return f"M{self.name}m0 {self.output_node_name}intermediate {self.input_gates[0].output_node_name} {self.name}mid vdd pmos_lvt nfin = {int(self.k*6)}\n"+\
                f"M{self.name}m1 {self.name}mid {self.input_gates[1].output_node_name} vdd vdd pmos_lvt nfin = {int(self.k*6)}\n"+\
                f"M{self.name}m2 {self.output_node_name}intermediate {self.input_gates[0].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*2)}\n"+\
                f"M{self.name}m3 {self.output_node_name}intermediate {self.input_gates[1].output_node_name} 0 0 nmos_lvt nfin = {int(self.k*2)}\n"+\
                f"M{self.name}m4 {self.output_node_name} {self.output_node_name}intermediate 0 0 nmos_lvt nfin = {int(self.k*2)}\n"+\
                f"M{self.name}m5 {self.output_node_name} {self.output_node_name}intermediate vdd vdd pmos_lvt nfin = {int(self.k*3)}\n\n"
            
        

    def __repr__(self):
        """
        Returns the generated netlist for the gate.

        Returns:
            str: The generated netlist for the gate.
        """
        return self.__generate_netlist()

    def _validate_config(self, config: dict):
        """
        Validates the configuration of the gate.

        Args:
            config (dict): The configuration of the gate.

        Raises:
            ValueError: If the gate type, input components, name, or sizing is not provided or is invalid.

        Returns:
            bool: True if the configuration is valid.
        """
        if 'type' not in config:
            raise ValueError("Type of the gate not provided")
        if 'input_components' not in config:
            raise ValueError("Input components of the gate not provided")
        if 'name' not in config:
            raise ValueError("Name of the gate not provided")
        if 'k' not in config:
            raise ValueError("Sizing of the gate not provided")
        if 'type' in config and config['type'] not in self.VALID_TYPES:
            raise ValueError(f"Invalid gate type: {config['type']}. Valid types are: {', '.join(self.VALID_TYPES)}")
        if 'input_components' in config and not isinstance(config['input_components'], list):
            raise ValueError("Input components of the gate must be a list")
        if 'name' in config and not isinstance(config['name'], str):
            raise ValueError("Name of the gate must be a string")
        if 'k' in config and not isinstance(config['k'], int):
            raise ValueError("Sizing of the gate must be an integer")
        return True
from .gate import Gate
class VoltageSource:
    """
    Represents a voltage source in a circuit.

    Args:
        config (dict): A dictionary containing the configuration parameters for the voltage source.
            - 'name' (str): The name of the voltage source.
            - 'ideal' (bool): Indicates whether the voltage source is ideal or not.
            - 'k' (int, optional): The sizing of the driver. Required if 'ideal' is False.

    Raises:
        ValueError: If any of the required configuration parameters are missing or have invalid types.

    Attributes:
        name (str): The name of the voltage source.
        input_config (dict): The input configuration parameters for the voltage source.
        output_node_name (str): The name of the output node.
        driver (Gate): The driver gate for the voltage source. Only present if 'ideal' is False.
        netlist (str): The netlist representation of the voltage source.

    Methods:
        __init__(self, config: dict): Initializes a new instance of the VoltageSource class.
        __generate_netlist(self): Generates the netlist representation of the voltage source.
        __repr__(self): Returns the netlist representation of the voltage source.
        _validate_config(self, config: dict): Validates the configuration parameters.

    """

    def __init__(self, config: dict):
        """
        Initializes a new instance of the VoltageSource class.

        Args:
            config (dict): A dictionary containing the configuration parameters for the voltage source.

        Raises:
            ValueError: If any of the required configuration parameters are missing or have invalid types.
        """
        self.name = config['name']
        if self._validate_config(config):
            self.input_config = config

        self.output_node_name = config['name']
        if not config['ideal']:
            gate_config = {"name": self.name + "driver", "type": "1NOT", "k": config['k'], "input_components": [self]}
            self.driver = Gate(gate_config)
            self.output_node_name = self.driver.output_node_name

        self.netlist = self.__generate_netlist()

    def __generate_netlist(self):
        """
        Generates the netlist representation of the voltage source.

        Returns:
            str: The netlist representation of the voltage source.
        """
        if self.output_node_name == self.name:
            return f"{self.name.upper()} {self.name} 0 pwl(0 0.7 0.9999us 0.7 1us 0 2us 0)\n\n"
        else:
            return f"{self.name.upper()} {self.name} 0 pwl(0 0.7 0.9999us 0.7 1us 0 2us 0)\n" + self.driver.netlist

    def __repr__(self):
        """
        Returns the netlist representation of the voltage source.

        Returns:
            str: The netlist representation of the voltage source.
        """
        return self.__generate_netlist()

    def _validate_config(self, config: dict):
        """
        Validates the configuration parameters.

        Args:
            config (dict): A dictionary containing the configuration parameters for the voltage source.

        Raises:
            ValueError: If any of the required configuration parameters are missing or have invalid types.

        Returns:
            bool: True if the configuration parameters are valid, False otherwise.
        """
        if 'name' not in config:
            raise ValueError("Name of the voltage source not provided")
        if 'ideal' not in config:
            raise ValueError("Ideal property of the voltage source not provided")
        if not config['ideal']:
            if 'k' not in config:
                raise ValueError("Sizing of the driver not provided")
        if 'ideal' in config and not isinstance(config['ideal'], bool):
            raise ValueError(f"Ideal property must be a boolean not {type(config['ideal'])}")
        if 'k' in config and not isinstance(config['k'], int):
            raise ValueError(f"Driver sizing must be an integer, not {type(config['k'])}")
        if 'name' in config and not isinstance(config['name'], str):
            raise ValueError(f"Name of the voltage source must be a string not {type(config['name'])}")

        return True

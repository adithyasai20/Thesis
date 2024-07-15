class Simulation:
    """
    A class representing a simulation.

    Attributes:
    - name (str): The name of the simulation.
    - circuits (list): A list of circuits to be simulated.
    - netlist (str): The generated netlist for the simulation.

    Methods:
    - __init__(name:str, circuits:list): Initializes a Simulation object.
    - __generate_netlist(circuits): Generates the netlist for the simulation.
    - __repr__(): Returns a string representation of the simulation.
    - save(file_path:str): Saves the netlist to a file.
    """

    def __init__(self, name:str, circuits:list):
        """
        Initializes a Simulation object.

        Parameters:
        - name (str): The name of the simulation.
        - circuits (list): A list of circuits to be simulated.
        """
        self.name = name
        self.netlist = self.__generate_netlist(circuits)
    
    

    
    def __generate_netlist(self, circuits):
        """
        Generates the netlist for the simulation.

        Parameters:
        - circuits (list): A list of circuits to be simulated.

        Returns:
        - netlist (str): The generated netlist for the simulation.
        """
        self.netlist = f"/////////////////////3 STAGE NAND/////////////////////////////\n"+\
                ".inc \"/home/lalithsai20/EMDproject/7nm_TT_160803.pm\"\n\n"
        for circuit in circuits:
            self.netlist += circuit.return_netlist()[0]
        self.netlist += "\nVdd vdd 0 0.7\n"
        self.netlist += f"\n.option post\n"+\
                        ".tran 1p 2u\n"
        for circuit in circuits:
            self.netlist += circuit.return_netlist()[1]
        self.netlist += ".end\n"

        return self.netlist
    
    def __repr__(self):
        """
        Returns a string representation of the simulation.

        Returns:
        - netlist (str): The generated netlist for the simulation.
        """
        return self.netlist
    
    def save(self, file_path:str):
        """
        Saves the netlist to a file.

        Parameters:
        - file_path (str): The path of the file to save the netlist to.
        """
        with open(file_path, "w") as file:
            file.write(self.netlist)
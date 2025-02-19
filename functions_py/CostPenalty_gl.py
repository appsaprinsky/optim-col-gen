class CostsPenalties:
    def __init__(self, file_path):
        self.file_path = file_path
        self.deadhead_cost = None
        self.flight_cost = None
        self.specific_flight_cost = None
        self._read_file()

    def _read_file(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split(',')
                if key == "Deadhead":
                    self.deadhead_cost = float(value)
                elif key == "FlightCost":
                    self.flight_cost = float(value)
                elif key == "SpecificFlightCost":
                    self.specific_flight_cost = float(value)

    def get_deadhead_cost(self):
        return self.deadhead_cost

    def get_flight_cost(self):
        return self.flight_cost

    def get_specific_flight_cost(self):
        return self.specific_flight_cost

    def __repr__(self):
        return (f"CostsPenalties(deadhead_cost={self.deadhead_cost}, "
                f"flight_cost={self.flight_cost}, "
                f"specific_flight_cost={self.specific_flight_cost})")
from datetime import datetime
class Flight:
    def __init__(self, departure_city, arrival_city, cost, flight_id, departure_time, arrival_time):
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.cost = cost
        self.flight_id = flight_id
        self.departure_time = datetime.strptime(departure_time, "%d-%m-%Y %H:%M:%S")
        self.arrival_time = datetime.strptime(arrival_time, "%d-%m-%Y %H:%M:%S")

    def __repr__(self):
        return f"{self.departure_city} -> {self.arrival_city} ({self.flight_id}, Cost: {self.cost}, Dep: {self.departure_time}, Arr: {self.arrival_time})"

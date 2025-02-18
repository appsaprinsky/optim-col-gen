from datetime import timedelta
class Trip:
    def __init__(self, legs, cost, base):
        self.legs = legs
        self.cost = cost
        self.base = base

    def __repr__(self):
        route = " -> ".join(f"{leg.departure_city} -> {leg.arrival_city} ({leg.flight_id})" for leg in self.legs)
        return f"Trip cost: {self.cost}\n{route}"

    def __eq__(self, other):
        # Compare trips based on their legs
        return isinstance(other, Trip) and self.legs == other.legs

    def can_add_flight(self, new_flight):
        if not self.legs:
            return True
        last_flight = self.legs[-1]
        # Ensure the new flight departs after the last flight arrives and there's at least 2 hours difference
        time_difference = (new_flight.departure_time - last_flight.arrival_time).total_seconds() / 3600
        return new_flight.departure_time >= last_flight.arrival_time and time_difference >= 2

    def total_duration(self):
        if not self.legs:
            return timedelta(0)
        return self.legs[-1].arrival_time - self.legs[0].departure_time
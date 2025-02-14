from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value, COIN_CMD

class Flight:
    def __init__(self, departure_city, arrival_city, cost, flight_id):
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.cost = cost
        self.flight_id = flight_id

class Trip:
    def __init__(self, legs, cost, base):
        self.legs = legs  # List of Flight objects
        self.cost = cost
        self.base = base

    def __repr__(self):
        route = " -> ".join(f"{leg.departure_city} -> {leg.arrival_city} ({leg.flight_id})" for leg in self.legs)
        return f"Trip cost: {self.cost}\n{route}"

    def __eq__(self, other):
        # Compare trips based on their legs
        return isinstance(other, Trip) and self.legs == other.legs

class RestrictedMasterProblem:
    def __init__(self):
        self.trips = []
        self.dual_values = {}

    def add_trip(self, trip):
        # Only add trips that start and end at the same base city
        if trip.legs[0].departure_city == trip.legs[-1].arrival_city:
            # Avoid adding duplicate trips
            if trip not in self.trips:
                self.trips.append(trip)

    def solve(self):
        # Create an LP problem
        prob = LpProblem("RestrictedMasterProblem", LpMinimize)

        # Decision variables: whether to use each trip
        trip_vars = {i: LpVariable(f"trip_{i}", 0, 1, cat="Binary") for i in range(len(self.trips))}

        # Objective function: minimize total cost
        prob += lpSum(trip_vars[i] * self.trips[i].cost for i in range(len(self.trips)))

        # Constraints: satisfy demand for each city
        # For simplicity, assume each city must be visited exactly once
        # (This is a placeholder; you need to define the exact constraints)
        for city in set(f.departure_city for f in airline_flights):
            prob += lpSum(trip_vars[i] for i, trip in enumerate(self.trips) if city in [leg.departure_city for leg in trip.legs]) >= 1

        # Solve the LP problem
        prob.solve(COIN_CMD(path="/opt/homebrew/bin/cbc"))

        # Retrieve dual values
        self.dual_values = {city: prob.constraints[f"constraint_{city}"].pi for city in set(f.departure_city for f in airline_flights)}

    def get_dual_values(self):
        return self.dual_values

class PricingProblem:
    def __init__(self, flights, dual_values, base):
        self.flights = flights
        self.dual_values = dual_values
        self.base = base

    def is_valid_extension(self, trip, new_leg):
        # Ensure the new leg is not already in the trip
        return new_leg not in trip.legs

    def calculate_reduced_cost(self, legs):
        # Reduced cost = total cost - sum of dual values for visited cities
        return sum(f.cost for f in legs) - sum(self.dual_values.get(f.departure_city, 0) for f in legs)

    def extend_trip(self, current_trip, best_trip, best_reduced_cost, depth=0, max_depth=5):
        if depth >= max_depth:
            return best_trip, best_reduced_cost

        # Check if the trip is complete (returns to the base)
        if current_trip.legs[-1].arrival_city == self.base:
            reduced_cost = self.calculate_reduced_cost(current_trip.legs)
            if reduced_cost < best_reduced_cost:
                return current_trip, reduced_cost

        # Explore all possible extensions
        for next_flight in self.flights:
            if current_trip.legs[-1].arrival_city == next_flight.departure_city:
                if self.is_valid_extension(current_trip, next_flight):
                    extended_trip = Trip(
                        current_trip.legs + [next_flight],
                        current_trip.cost + next_flight.cost,
                        self.base,
                    )
                    best_trip, best_reduced_cost = self.extend_trip(
                        extended_trip, best_trip, best_reduced_cost, depth + 1, max_depth
                    )

        return best_trip, best_reduced_cost

    def solve(self):
        best_trip = None
        best_reduced_cost = float("inf")

        for start_flight in self.flights:
            if start_flight.departure_city == self.base:
                current_trip = Trip([start_flight], start_flight.cost, self.base)
                best_trip, best_reduced_cost = self.extend_trip(
                    current_trip, best_trip, best_reduced_cost
                )

        print(f"Best reduced cost for base {self.base}: {best_reduced_cost}")
        if best_trip:
            print(f"Best trip found: {[(leg.departure_city, leg.arrival_city, leg.flight_id) for leg in best_trip.legs]}")
        return best_trip

# Sample Flights
airline_flights = [
    Flight("A", "B", 100, "FL1"),
    Flight("B", "C", 150, "FL2"),
    Flight("C", "A", 200, "FL3"),
    Flight("A", "C", 180, "FL4"),
    Flight("C", "F", 150, "FL5"),
    Flight("F", "G", 200, "FL6"),
    Flight("G", "A", 180, "FL7"),
    Flight("C", "A", 50, "FL8"),
]

def main():
    rmp = RestrictedMasterProblem()
    max_iterations = 10
    tolerance = 1e-6
    iteration = 0

    while iteration < max_iterations:
        rmp.solve()
        dual_values = rmp.get_dual_values()

        for base in set(f.departure_city for f in airline_flights):
            pp = PricingProblem(airline_flights, dual_values, base)
            new_trip = pp.solve()

            if new_trip and len(new_trip.legs) > 1:
                reduced_cost = pp.calculate_reduced_cost(new_trip.legs)
                if reduced_cost < -tolerance:
                    rmp.add_trip(new_trip)

        iteration += 1

    print("Optimal trips found!")
    for trip in rmp.trips:
        print(trip)

if __name__ == "__main__":
    main()
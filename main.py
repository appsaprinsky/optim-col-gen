from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value, COIN_CMD

class Flight:
    def __init__(self, departure_city, arrival_city, cost, flight_id):
        self.departure_city = departure_city
        self.arrival_city = arrival_city
        self.cost = cost
        self.flight_id = flight_id

    def __repr__(self):
        return f"{self.departure_city} -> {self.arrival_city} ({self.flight_id}, Cost: {self.cost})"

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
        self.city_constraints = {}  # Store city constraints for easy access

    def add_trip(self, trip):
        if trip.legs[0].departure_city == trip.legs[-1].arrival_city and trip not in self.trips:
            self.trips.append(trip)

    def solve(self):
        prob = LpProblem("RestrictedMasterProblem", LpMinimize)
        trip_vars = {i: LpVariable(f"trip_{i}", 0, 1, cat="Binary") for i in range(len(self.trips))}
        prob += lpSum(trip_vars[i] * self.trips[i].cost for i in range(len(self.trips)))

        self.city_constraints = {}  # Clear existing constraints

        for city in set(f.departure_city for f in airline_flights):
            constraint_name = f"constraint_{city}"
            # Create the constraint expression
            constraint_expression = lpSum(trip_vars[i] for i, trip in enumerate(self.trips) if any(leg.departure_city == city for leg in trip.legs)) >= 1
            # Add the constraint to the problem with a name
            prob.addConstraint(constraint_expression, constraint_name)
            self.city_constraints[city] = prob.constraints[constraint_name]  # Access using name

        prob.solve(COIN_CMD(path="/opt/homebrew/bin/cbc"))

        if prob.status == 1:  # Optimal
            self.dual_values = {city: self.city_constraints[city].pi for city in set(f.departure_city for f in airline_flights)}
        else:
            print(f"RMP Infeasible or other issue: Status = {prob.status}")
            self.dual_values = {}

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

    def calculate_reduced_cost(self, legs, existing_trip_cost=0):
        # Reduced cost = total cost - sum of dual values for visited cities - existing_trip_cost
        return sum(f.cost for f in legs) - sum(self.dual_values.get(f.departure_city, 0) for f in legs) - existing_trip_cost

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
    Flight("D", "C", 150, "FL2"),
    Flight("B", "C", 150, "FL9"),
    Flight("C", "A", 200, "FL3"),
    Flight("C", "A", 50, "FL9"),
    Flight("A", "C", 180, "FL4"),
    Flight("C", "F", 150, "FL5"),
    Flight("F", "G", 200, "FL6"),
    Flight("G", "A", 180, "FL7"),
    Flight("C", "A", 50, "FL8"),
]

def main():
    rmp = RestrictedMasterProblem()
    global_solution_trip = []
    # Add an initial feasible trip to start the process.  Crucially important!
    for i in range(len(airline_flights)):
        loop_flight = airline_flights[i]
        loop_flight_dh = Flight(loop_flight.arrival_city, loop_flight.departure_city, 1000, loop_flight.flight_id+'_DH')
        initial_trip = Trip([loop_flight, loop_flight_dh ], loop_flight.cost +loop_flight_dh.cost, 'T_' +str(i))
        rmp.add_trip(initial_trip)
        global_solution_trip.append(initial_trip)


    max_iterations = 100
    tolerance = 1e-6
    iteration = 0

    while iteration < max_iterations:
        rmp.solve()
        dual_values = rmp.get_dual_values()
        print(f'Dual Values: {dual_values}')

        if not dual_values:  # Check if dual values are available (RMP might be infeasible)
            print("No dual values available. Stopping.")
            break

        for base in set(f.departure_city for f in airline_flights):
            pp = PricingProblem(airline_flights, dual_values, base)
            new_trip = pp.solve()

            if new_trip and len(new_trip.legs) > 1:
                print(f'New Trip: {new_trip.legs}')

                # search for trips that are affected
                flights_in_the_new_trip = [legg.flight_id for legg in new_trip.legs]
                #  Next steps:
                # Finding trips that will be affected by a new solution
                # identify what flights will be uncovered (ignoring DH)
                # generate them solutions with Deadhead
                # calculate the cost of new trips  - cost of old trips and assign them value of ==as existing trp cost
                # Delete the old trips and add new trips in the solutions of global solution and restricted master problem
                affected_trips_in_OG = []
                reduced_cost = pp.calculate_reduced_cost(new_trip.legs, existing_trip_cost=new_trip.cost)
                print(reduced_cost)
                print(-tolerance)
                if reduced_cost < -tolerance:
                    rmp.add_trip(new_trip)

        iteration += 1

    print("Optimal trips found!")
    for trip in rmp.trips:
        print(trip)


if __name__ == "__main__":
    main()
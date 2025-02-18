from pulp import LpProblem, LpVariable, LpMinimize, lpSum, COIN_CMD


class RestrictedMasterProblem:
    def __init__(self):
        self.trips = []
        self.dual_values = {}
        self.city_constraints = {}

    def add_trip(self, trip):
        if trip.legs[0].departure_city == trip.legs[-1].arrival_city and trip not in self.trips:
            self.trips.append(trip)

    def remove_trip(self, trip):
        if trip in self.trips:
            self.trips.remove(trip)

    def solve(self, airline_flights):
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

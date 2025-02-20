from datetime import timedelta
from functions_py.LegalityChecker_gl import *
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, COIN_CMD
from datetime import timedelta

class RestrictedMasterProblem:
    def __init__(self):
        self.trips = []
        self.dual_values = {}
        self.city_constraints = {}

    def add_trip(self, trip):
        self.trips.append(trip)

    def remove_trip(self, trip):
        if trip in self.trips:
            self.trips.remove(trip)

    def solve(self, airline_flights):
        prob = LpProblem("RestrictedMasterProblem", LpMinimize)

        # Decision variables for each trip
        # trip_vars = {i: LpVariable(f"trip_{i}", lowBound=0, upBound=1, cat="Integer") 
        #              for i in range(len(self.trips))}
        trip_vars = {i: LpVariable(f"trip_{i}", lowBound=0, upBound=1, cat="Continuous") 
                for i in range(len(self.trips))}

        # Objective Function: Minimize cost
        prob += lpSum(trip_vars[i] * self.trips[i].cost for i in range(len(self.trips))), "Total_Cost"

        self.city_constraints = {}

        # ✅ Fix: Ensure the base trip constraint is correctly defined
        prob += lpSum(trip_vars[i] for i, trip in enumerate(self.trips) 
                      if trip.legs[0].departure_city == trip.legs[-1].arrival_city) >= 1, "Base_Trip_Constraint"

        # ✅ Fix: Connection time constraints
        min_connection_seconds = timedelta(hours=2).total_seconds()
        for i, trip in enumerate(self.trips):
            for j in range(len(trip.legs) - 1):
                current_flight = trip.legs[j]
                next_flight = trip.legs[j + 1]
                connection_time_seconds = (next_flight.departure_time - current_flight.arrival_time).total_seconds()
                if connection_time_seconds < min_connection_seconds:
                    prob += trip_vars[i] == 0, f"Min_Connection_{i}_{j}"

        # ✅ Fix: Maximum duration constraint
        max_duration_seconds = timedelta(days=6).total_seconds()
        for i, trip in enumerate(self.trips):
            trip_duration_seconds = (trip.legs[-1].arrival_time - trip.legs[0].departure_time).total_seconds()
            if trip_duration_seconds > max_duration_seconds:
                prob += trip_vars[i] == 0, f"Max_Duration_{i}"

        # ✅ Fix: Ensure no duplicate flights within a trip
        for i, trip in enumerate(self.trips):
            flight_ids = [flight.flight_id for flight in trip.legs]
            if len(flight_ids) != len(set(flight_ids)):  # Duplicate flights exist
                prob += trip_vars[i] == 0, f"Unique_Flights_{i}"

        # ✅ Fix: City constraints (Ensuring at least one trip departs from each city)
        for city in set(f.departure_city for f in airline_flights):
            constraint_name = f"constraint_{city}"
            prob += lpSum(trip_vars[i] for i, trip in enumerate(self.trips) 
                          if any(leg.departure_city == city for leg in trip.legs)) >= 1, constraint_name
            self.city_constraints[city] = prob.constraints[constraint_name]


        for i in range(len(self.trips)):
            trip = self.trips[i]
            for j in range(len(trip.legs) - 1):
                current_flight = trip.legs[j]
                next_flight = trip.legs[j + 1]
                min_connection_seconds = timedelta(hours=2).total_seconds()
                connection_time_seconds = (next_flight.departure_time - current_flight.arrival_time).total_seconds()

                # If connection time is too short, force trip to be 0
                if connection_time_seconds < min_connection_seconds:
                    prob += trip_vars[i] == 0, f"Min_Connection_{i}_{j}"


        # ✅ Debugging Prints Before Solving
        print("🚀 Constraints before solving:")
        for name, constraint in prob.constraints.items():
            print(f"{name}: LHS = {constraint.value()}  RHS = {constraint.constant}")

        print("🚀 Decision Variables:")
        print(prob.variables()) 

        for name, constraint in prob.constraints.items():
            print(f"{name}: {constraint}")       

        # Solve the problem using COIN-OR CBC solver
        prob.solve(COIN_CMD(path="/opt/homebrew/bin/cbc", msg=1))

# 🚀 Print constraints *after* solving to get proper LHS values  
        print("\n🚀 Constraints after solving:")
        for name, constraint in prob.constraints.items():
            print(f"{name}: LHS = {constraint.value()}  RHS = {constraint.constant}")

        print("\n🚀 Dual Values:")
        self.dual_values = {city: self.city_constraints[city].pi for city in self.city_constraints}
        print(self.dual_values)

        # ✅ Fix: Get Dual Values Correctly
        if prob.status == 1:  # Optimal
            self.dual_values = {city: self.city_constraints[city].pi for city in self.city_constraints}
        else:
            print(f"⚠️ RMP Infeasible or other issue: Status = {prob.status}")
            self.dual_values = {}

    def get_dual_values(self):
        return self.dual_values

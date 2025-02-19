from datetime import timedelta
from functions_py.Trip_gl import *
class PricingProblem:
    def __init__(self, flights, dual_values, base):
        self.flights = flights
        self.dual_values = dual_values
        self.base = base

    def is_valid_extension(self, trip, new_leg):
        # Ensure the new leg is not already in the trip and respects time constraints
        return new_leg not in trip.legs and trip.can_add_flight(new_leg)

    def calculate_reduced_cost(self, legs):
        # Reduced cost = total cost - sum of dual values for visited cities
        return sum(f.cost for f in legs) - sum(self.dual_values.get(f.departure_city, 0) for f in legs)

    def calculate_reduced_cost_EXTERNAL(self, legs, existing_trip_cost):
        # Reduced cost = total cost - sum of dual values for visited cities - existing_trip_cost
        return existing_trip_cost - sum(self.dual_values.get(f.departure_city, 0) for f in legs)

    def generate_all_trips(self, current_trip, all_trips, max_depth=10):
        # Base case: if the trip returns to the base and is within 6 days, add it to the list
        if current_trip.legs[-1].arrival_city == self.base:
            if current_trip.total_duration() <= timedelta(days=6):
                all_trips.append(current_trip)
            return

        # Base case: if max depth is reached, stop exploring
        if len(current_trip.legs) >= max_depth:
            return

        # Explore all possible extensions
        for next_flight in self.flights:
            if current_trip.legs[-1].arrival_city == next_flight.departure_city:
                if self.is_valid_extension(current_trip, next_flight):
                    extended_trip = Trip(
                        current_trip.legs + [next_flight],
                        current_trip.cost + next_flight.cost,
                        self.base,
                    )
                    self.generate_all_trips(extended_trip, all_trips, max_depth)

    def solve(self):
        all_trips = []  # Store all legal trips
        best_trip = None
        best_reduced_cost = float("inf")

        # Start with all flights departing from the base
        start_flights = [f for f in self.flights if f.departure_city == self.base]
        for start_flight in start_flights:
            current_trip = Trip([start_flight], start_flight.cost, self.base)
            self.generate_all_trips(current_trip, all_trips)

        print(all_trips)
        # Evaluate all generated trips and select the best one
        for trip in all_trips:
            reduced_cost = self.calculate_reduced_cost(trip.legs)
            if reduced_cost < best_reduced_cost:
                best_trip = trip
                best_reduced_cost = reduced_cost

        print(f"Best reduced cost for base {self.base}: {best_reduced_cost}")
        if best_trip:
            print(f"Best trip found: {[(leg.departure_city, leg.arrival_city, leg.flight_id) for leg in best_trip.legs]}")
        return best_trip
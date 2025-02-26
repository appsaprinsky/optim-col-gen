from functions_py.Flight_gl import Flight
from datetime import timedelta
from functions_py.Trip_gl import *

class PricingProblemDH:
    def __init__(self, airline_flights, airline_flights_copy, dual_values, base, costs_penalties, legality_checker):
        self.airline_flights = airline_flights  # Flights yet to cover
        self.airline_flights_copy = airline_flights_copy  # All flights (for deadheads)
        self.dual_values = dual_values
        self.base = base
        self.costs_penalties = costs_penalties
        self.legality_checker = legality_checker

    def is_valid_extension(self, trip, new_leg, is_deadhead=False):
        """
        Check if a new leg can be added to the trip.
        Deadheads bypass time constraints but cannot be duplicates.
        """
        if is_deadhead:
            return new_leg not in trip.legs  # Deadheads can be added regardless of time constraints
        else:
            return new_leg not in trip.legs and trip.can_add_flight(new_leg)

    def calculate_reduced_cost(self, legs):
        """
        Calculate the reduced cost of a trip.
        Includes a fixed cost for deadhead flights and subtracts the cost of uncovered flights.
        """
        total_cost = sum(
            self.costs_penalties.get_flight_cost() if not f.flight_id.endswith('_DH')
            else self.costs_penalties.get_deadhead_cost()
            for f in legs
        )
        # Subtract the cost of uncovered flights
        uncovered_cost = sum(
            self.costs_penalties.get_uncovered_deadhead_cost()
            for f in self.airline_flights
            if f not in legs
        )
        return total_cost - uncovered_cost - sum(self.dual_values.get(f.departure_city, 0) for f in legs)

    def generate_all_trips(self, current_trip, all_trips, max_depth=10):
        """
        Recursively generate all valid trips starting from the current trip.
        Deadheads are added only when no regular flights are available.
        """
        # Base case: if the trip returns to the base and is within 7 days, add it to the list
        if current_trip.legs[-1].arrival_city == self.base:
            if current_trip.total_duration() <= timedelta(days=7):
                all_trips.append(current_trip)
            return

        # Base case: if max depth is reached, stop exploring
        if len(current_trip.legs) >= max_depth:
            return

        # Find the next possible flights
        next_flights = [
            f for f in self.airline_flights
            if current_trip.legs[-1].arrival_city == f.departure_city
        ]
        deadhead_flights = [
                f for f in self.airline_flights_copy
                if current_trip.legs[-1].arrival_city == f.departure_city
                and f not in current_trip.legs
                and self.legality_checker.is_flight_sequence_valid(current_trip.legs + [f])
            ]

        # Try to extend the trip with regular flights
        for next_flight in next_flights:
            if self.is_valid_extension(current_trip, next_flight):
                extended_trip = Trip(
                    current_trip.legs + [next_flight],
                    current_trip.cost + self.costs_penalties.get_flight_cost(),
                    self.base,
                )
                self.generate_all_trips(extended_trip, all_trips, max_depth)
        if not current_trip.legs[-1].flight_id.endswith('_DH'):
            for next_flight in deadhead_flights:
                if self.is_valid_extension(current_trip, next_flight, is_deadhead=True):
                    # Mark the flight as a deadhead
                    dh_flight = Flight(
                        next_flight.departure_city,
                        next_flight.arrival_city,
                        self.costs_penalties.get_deadhead_cost(),
                        next_flight.flight_id + '_DH',  # Append _DH to flight_id
                        next_flight.departure_time.strftime("%d-%m-%Y %H:%M:%S"),
                        next_flight.arrival_time.strftime("%d-%m-%Y %H:%M:%S")
                    )
                    extended_trip = Trip(
                        current_trip.legs + [dh_flight],
                        current_trip.cost + self.costs_penalties.get_deadhead_cost(),
                        self.base,
                    )
                    self.generate_all_trips(extended_trip, all_trips, max_depth)
        # If no regular flights are available, try adding a deadhead
        # if not next_flights:
        #     print('TRYING DEADHEAD!!!!!!!!!!!!!!!!!!!!!')
        #     deadhead_flights = [
        #         f for f in self.airline_flights_copy
        #         if current_trip.legs[-1].arrival_city == f.departure_city
        #         and f not in current_trip.legs
        #         and self.legality_checker.is_flight_sequence_valid(current_trip.legs + [f])
        #     ]
        #     print('TRYING DEADHEAD {deadhead_flights}')
        #     for next_flight in deadhead_flights:
        #         if self.is_valid_extension(current_trip, next_flight, is_deadhead=True):
        #             # Mark the flight as a deadhead
        #             dh_flight = Flight(
        #                 next_flight.departure_city,
        #                 next_flight.arrival_city,
        #                 self.costs_penalties.get_deadhead_cost(),
        #                 next_flight.flight_id + '_DH',  # Append _DH to flight_id
        #                 next_flight.departure_time,
        #                 next_flight.arrival_time
        #             )
        #             extended_trip = Trip(
        #                 current_trip.legs + [dh_flight],
        #                 current_trip.cost + self.costs_penalties.get_deadhead_cost(),
        #                 self.base,
        #             )
        #             self.generate_all_trips(extended_trip, all_trips, max_depth)

    def solve(self):
        """
        Solve the pricing problem by generating valid trips and selecting the one with the lowest reduced cost.
        """
        all_trips = []  # Store all legal trips
        best_trip = None
        best_reduced_cost = float("inf")

        # Start with all flights departing from the base
        start_flights = [f for f in self.airline_flights if f.departure_city == self.base]
        print(f"Start Flights generated: {start_flights}")
        for start_flight in start_flights:
            current_trip = Trip([start_flight], self.costs_penalties.get_flight_cost(), self.base)
            self.generate_all_trips(current_trip, all_trips)
        print(f"Total trips generated: {all_trips}")
        print(f"Total trips generated: {len(all_trips)}")
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
from datetime import timedelta

class IsLegal:
    def __init__(self, base, min_connection_time=timedelta(hours=2), max_trip_duration=timedelta(days=6)):
        self.base = base
        self.min_connection_time = min_connection_time
        self.max_trip_duration = max_trip_duration

    def is_flight_sequence_valid(self, flights):
        """
        Check if a sequence of flights is valid in terms of time constraints.
        """
        for i in range(len(flights) - 1):
            current_flight = flights[i]
            next_flight = flights[i + 1]

            # Check if the next flight departs after the current flight arrives
            if next_flight.departure_time < current_flight.arrival_time:
                return False

            # Check if the time difference between flights is at least min_connection_time
            time_difference = next_flight.departure_time - current_flight.arrival_time
            if time_difference < self.min_connection_time:
                return False

        return True

    def is_trip_duration_valid(self, flights):
        """
        Check if the total duration of a trip is within the allowed limit.
        """
        if not flights:
            return False

        trip_duration = flights[-1].arrival_time - flights[0].departure_time
        return trip_duration <= self.max_trip_duration

    def is_trip_base_valid(self, flights):
        """
        Check if the trip starts and ends at the base city.
        """
        if not flights:
            return False

        starts_at_base = flights[0].departure_city == self.base
        ends_at_base = flights[-1].arrival_city == self.base
        return starts_at_base and ends_at_base

    def are_flights_unique(self, flights):
        """
        Check if all flights in the trip are unique.
        """
        flight_ids = [flight.flight_id for flight in flights]
        return len(flight_ids) == len(set(flight_ids))

    def is_trip_legal(self, trip):
        """
        Check if a trip is legal based on all constraints.
        """
        flights = trip.legs

        # Check all constraints
        return (
            self.is_flight_sequence_valid(flights)
            and self.is_trip_duration_valid(flights)
            and self.is_trip_base_valid(flights)
            and self.are_flights_unique(flights)
        )

    def is_flight_legal(self, flight):
        """
        Check if a single flight is legal (e.g., not a duplicate or invalid).
        """
        # Add any specific flight-level checks here if needed
        return True
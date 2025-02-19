from pulp import LpProblem, LpVariable, LpMinimize, lpSum, COIN_CMD
from datetime import timedelta
from functions_py.Flight_gl import *
from functions_py.Trip_gl import *
from functions_py.schedule_reader import *
import random
from functions_py.RestrictedMasterProblem_gl import *
from functions_py.PricingProblem_gl import *
from functions_py.CostPenalty_gl import *
from functions_py.LegalityChecker_gl import *

airline_flights = read_flights_from_file('input_py/sam_py.txt')

def process_trips(global_solution_trip, flights_in_the_new_trip):
    valid_trips = []
    for trip_coll in global_solution_trip:
        if any(legg.flight_id in flights_in_the_new_trip for legg in trip_coll.legs):
            valid_trips.append(trip_coll)
            flight_ids = [legg.flight_id for legg in trip_coll.legs]
    return valid_trips

def basic_trip_solution_with_DH(LIST_airline_flights):
    LIST_output_trips = []
    for i in range(len(LIST_airline_flights)):
        loop_flight = LIST_airline_flights[i]
        dh_departure_time = loop_flight.arrival_time + timedelta(hours=5)
        flight_duration = loop_flight.arrival_time - loop_flight.departure_time
        dh_arrival_time = dh_departure_time + flight_duration
        loop_flight_dh = Flight(
            loop_flight.arrival_city, 
            loop_flight.departure_city, 
            10000, 
            loop_flight.flight_id + '_DH',
            dh_departure_time.strftime("%d-%m-%Y %H:%M:%S"),
            dh_arrival_time.strftime("%d-%m-%Y %H:%M:%S")
        )
        initial_trip = Trip(
            [loop_flight, loop_flight_dh], 
            loop_flight.cost + loop_flight_dh.cost, 
            'T_' + str(i)
        )
        LIST_output_trips.append(initial_trip)
    
    return LIST_output_trips

def find_flights_by_id(flights, flight_id):
    flight_out = None
    for flight in flights: 
        if flight.flight_id == flight_id:
            flight_out = flight
    return flight_out

def calculate_total_cost_of_flights(flights):
    if not flights:
        return 0
    if not all(isinstance(flight, Flight) for flight in flights): # Check if all elements are Flight objects
        return "Error: All items in the list must be Flight objects."
    return sum(flight.cost for flight in flights)

def calculate_total_trip_cost(trips):
    if not trips:
        return 0
    if not all(isinstance(trip, Trip) for trip in trips):
        return "Error: All items in the list must be Trip objects."
    return sum(trip.cost for trip in trips)

def main():
    pc = CostsPenalties('input_py/cost_penalties.txt')
    rmp = RestrictedMasterProblem()
    global_solution_trip = []
    # initial feasible trip
    for i in range(len(airline_flights)):
        loop_flight = airline_flights[i]
        dh_departure_time = loop_flight.arrival_time + timedelta(hours=5)
        flight_duration = loop_flight.arrival_time - loop_flight.departure_time
        dh_arrival_time = dh_departure_time + flight_duration
        loop_flight_dh = Flight(loop_flight.arrival_city, loop_flight.departure_city, pc.get_deadhead_cost(), loop_flight.flight_id+'_DH', dh_departure_time.strftime("%d-%m-%Y %H:%M:%S"), dh_arrival_time.strftime("%d-%m-%Y %H:%M:%S"))
        initial_trip = Trip([loop_flight, loop_flight_dh], loop_flight.cost + loop_flight_dh.cost, 'T_' + str(i))
        lc = IsLegal(loop_flight.departure_city)
        lc.is_trip_legal(initial_trip)
        rmp.add_trip(initial_trip)
        global_solution_trip.append(initial_trip)

    max_iterations = 10
    tolerance = 1e-6
    iteration = 0

    while iteration < max_iterations:
        rmp.solve(airline_flights)
        dual_values = rmp.get_dual_values()
        print(f'Dual Values: {dual_values}')

        if not dual_values:
            print("No dual values available. Stopping.")
            break

        for base in set(f.departure_city for f in airline_flights):
            pp = PricingProblem(airline_flights, dual_values, base)
            new_trip = pp.solve()

            if new_trip and len(new_trip.legs) > 1:
                print(f'New Trip: {new_trip.legs}')
                flights_in_the_new_trip = [legg.flight_id for legg in new_trip.legs]                
                affected_trips_in_OG = process_trips(global_solution_trip, flights_in_the_new_trip)
                list_of_uncovered_trips = []
                for tripp in affected_trips_in_OG:
                    for legg in tripp.legs:
                        if (legg.flight_id not in flights_in_the_new_trip) and (legg.flight_id[-2:] != 'DH'):
                            list_of_uncovered_trips.append(find_flights_by_id(airline_flights, legg.flight_id))
                
                rest_of_trips_solution = basic_trip_solution_with_DH(list_of_uncovered_trips)
                existing_trip_cost= calculate_total_trip_cost(rest_of_trips_solution) + calculate_total_trip_cost([new_trip]) - calculate_total_trip_cost(affected_trips_in_OG)
                reduced_cost = pp.calculate_reduced_cost_EXTERNAL(new_trip.legs, existing_trip_cost)
                print(reduced_cost)
                print(-tolerance)
                if reduced_cost < -tolerance:
                    rmp.add_trip(new_trip)
                    global_solution_trip.append(new_trip)
                    for tripp in affected_trips_in_OG:
                        global_solution_trip.remove(tripp)
                        rmp.remove_trip(tripp)

        iteration += 1
        dual_values = rmp.get_dual_values()
        print(f'Iteration {iteration} completed.')
        print('-----------------------------------')
        print(f'Dual Values: {dual_values}')

    print("Optimal trips found!")
    for trip in global_solution_trip:
        print(trip)

if __name__ == "__main__":
    main()
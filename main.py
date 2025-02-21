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


    
# def generate_all_trips_Initial_Solution(current_trip, all_trips, flights, base, max_depth=10):
#     def is_valid_extension(trip, new_leg):
#         # Ensure the new leg is not already in the trip and respects time constraints
#         return new_leg not in trip.legs and trip.can_add_flight(new_leg)
#     if current_trip.legs[-1].arrival_city == base:
#         if current_trip.total_duration() <= timedelta(days=6):
#             all_trips.append(current_trip)
#         return
#     # Base case: if max depth is reached, stop exploring
#     if len(current_trip.legs) >= max_depth:
#         return
#     # Explore all possible extensions
#     for next_flight in flights:
#         if current_trip.legs[-1].arrival_city == next_flight.departure_city:
#             if is_valid_extension(current_trip, next_flight):
#                 extended_trip = Trip(
#                     current_trip.legs + [next_flight],
#                     current_trip.cost + next_flight.cost,
#                     base,
#                 )
#                 generate_all_trips_Initial_Solution(extended_trip, all_trips, flights, max_depth)


def calculate_total_trip_cost(trips):
    if not trips:
        return 0
    if not all(isinstance(trip, Trip) for trip in trips):
        return "Error: All items in the list must be Trip objects."
    return sum(trip.cost for trip in trips)



def generate_initial_solution(airline_flights, pc, rmp, global_solution_trip):
    assigned_flights = set()
    trips = []
    
    for i in range(len(airline_flights)):
        if airline_flights[i] in assigned_flights:
            continue
        
        loop_flight = airline_flights[i]
        trip_flights = [loop_flight]
        assigned_flights.add(loop_flight)
        
        # Try to extend the trip with connecting flights
        for j in range(len(airline_flights)):
            if i == j or airline_flights[j] in assigned_flights:
                continue
            
            candidate_flight = airline_flights[j]
            
            # Check if the flights can be linked directly
            if loop_flight.arrival_city == candidate_flight.departure_city \
                    and loop_flight.arrival_time <= candidate_flight.departure_time:
                trip_flights.append(candidate_flight)
                assigned_flights.add(candidate_flight)
                loop_flight = candidate_flight
                
        # If no connection is found and DH is required
        if len(trip_flights) == 1:
            dh_departure_time = loop_flight.arrival_time + timedelta(hours=5)
            flight_duration = loop_flight.arrival_time - loop_flight.departure_time
            dh_arrival_time = dh_departure_time + flight_duration
            loop_flight_dh = Flight(
                loop_flight.arrival_city, loop_flight.departure_city, 
                pc.get_deadhead_cost(), loop_flight.flight_id+'_DH', 
                dh_departure_time.strftime("%d-%m-%Y %H:%M:%S"),
                dh_arrival_time.strftime("%d-%m-%Y %H:%M:%S")
            )
            trip_flights.append(loop_flight_dh)
        
        trip_cost = sum(f.cost for f in trip_flights)
        initial_trip = Trip(trip_flights, trip_cost, 'T_' + str(i))
        
        # lc = is_legal_func(loop_flight.departure_city)
        # lc.is_trip_legal(initial_trip)
        rmp.add_trip(initial_trip)
        global_solution_trip.append(initial_trip)
        
    return trips


def main():
    pc = CostsPenalties('input_py/cost_penalties.txt')
    airline_flights = read_flights_from_file('input_py/sam_py.txt', cost_class=pc)
    rmp = RestrictedMasterProblem()
    global_solution_trip = []
    # initial feasible trip

    # flights_to_cover = airline_flights.copy()
    # flights_impossible_to_cover = []

    # while len(flights_to_cover)!=0:
    #     flight_curr = flights_to_cover[0]
    #     trip_curr = Trip([flight_curr], flight_curr.cost, 'U_')
    #     generate_all_trips_Initial_Solution(current_trip, all_trips, flights_to_cover, flight_curr.base, max_depth=10)
        


    # for i in range(len(airline_flights)):
    #     loop_flight = airline_flights[i]
    #     dh_departure_time = loop_flight.arrival_time + timedelta(hours=5)
    #     flight_duration = loop_flight.arrival_time - loop_flight.departure_time
    #     dh_arrival_time = dh_departure_time + flight_duration
    #     loop_flight_dh = Flight(loop_flight.arrival_city, loop_flight.departure_city, pc.get_deadhead_cost(), loop_flight.flight_id+'_DH', dh_departure_time.strftime("%d-%m-%Y %H:%M:%S"), dh_arrival_time.strftime("%d-%m-%Y %H:%M:%S"))
    #     initial_trip = Trip([loop_flight, loop_flight_dh], loop_flight.cost + loop_flight_dh.cost, 'T_' + str(i))
    #     lc = IsLegal(loop_flight.departure_city)
    #     lc.is_trip_legal(initial_trip)
    #     rmp.add_trip(initial_trip)
    #     global_solution_trip.append(initial_trip)

# trying to avoid all the DH flights
    # trips_with_DH_to_clean = []
    # for trip in global_solution_trip:
    #     if any(leg.flight_id[-2:] == 'DH' for leg in trip.legs):
    #         trips_with_DH_to_clean.append(trip) 



    generate_initial_solution(airline_flights, pc, rmp, global_solution_trip)

    max_iterations = 20
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
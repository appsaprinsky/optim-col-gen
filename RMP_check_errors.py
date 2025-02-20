from functions_py.Flight_gl import *
from functions_py.Trip_gl import *
from functions_py.RestrictedMasterProblem_gl import *

rmp = RestrictedMasterProblem()

# Create example flights
flights = [
    Flight("A", "B", 100, "F1", "01-01-2023 08:00:00", "01-01-2023 10:00:00"),
    Flight("B", "C", 100, "F2", "01-01-2023 12:00:00", "01-01-2023 14:00:00"),
    Flight("C", "A", 100, "F3", "01-01-2023 16:00:00", "01-01-2023 18:00:00"),
    Flight("A", "D", 100, "F4", "02-01-2023 08:00:00", "02-01-2023 10:00:00"),
    Flight("D", "G", 100, "F5", "02-01-2023 12:00:00", "02-01-2023 14:00:00"),
    Flight("G", "A", 100, "F6", "02-01-2023 16:00:00", "02-01-2023 18:00:00"),
    Flight("A", "F", 100, "F7", "03-01-2023 08:00:00", "03-01-2023 10:00:00"),
    Flight("F", "A", 100, "F8", "03-01-2023 12:00:00", "03-01-2023 14:00:00"),
]

# Create trips
trip1 = Trip([flights[0], flights[1], flights[2]], 100 + 120 + 150, 'A')
trip2 = Trip([flights[3], flights[4], flights[5]], 100 + 120 + 150, 'A')
trip3 = Trip([flights[6], flights[7]], 100 + 120, 'A')

# Add trips to RMP
rmp.add_trip(trip1)
rmp.add_trip(trip2)
rmp.add_trip(trip3)

# Solve RMP
rmp.solve(flights)

# Print dual values
print(f"Dual Values: {rmp.get_dual_values()}")
import numpy as np
from scipy.optimize import linprog

# Example: Small flight network for crew pairing
costs = [10, 15, 20]  # Example pairing costs for initial columns
initial_pairings = np.array([
    [1, 0, 1],  # Pairing 1 covers flight 1 and 3
    [1, 1, 0],  # Pairing 2 covers flight 1 and 2
    [0, 1, 1]   # Pairing 3 covers flight 2 and 3
])
demands = [1, 1, 1]  # Require all flights to be covered at least once

# Restricted Master Problem setup
def solve_rmp(costs, initial_pairings, demands):
    num_pairings = initial_pairings.shape[1]
    result = linprog(c=costs, A_eq=initial_pairings, b_eq=demands,
                      bounds=[(0, None)] * num_pairings, method='highs')
    if result.success:
        print("RMP solution:")
        print("Pairing values:", result.x)
        print("Optimal cost:", result.fun)
        return result.x, result.fun
    else:
        print("RMP failed.")
        return None, None

# Pricing Problem setup
def solve_pricing_problem(dual_values):
    # Minimize reduced cost: c_j - dual * A_j
    # Example: New column covers flight 1 and 2 with a cost of 12
    new_cost = 12
    new_column = [1, 1, 0]
    reduced_cost = new_cost - np.dot(dual_values, new_column)
    print("Pricing problem reduced cost:", reduced_cost)

    if reduced_cost < -1e-6:
        print("Adding new column with cost:", new_cost)
        return new_cost, new_column
    return None, None

# Main Column Generation Loop
def column_generation():
    pairings = initial_pairings.copy()
    costs_list = costs.copy()

    while True:
        solution, optimal_cost = solve_rmp(costs_list, pairings, demands)
        if solution is None:
            break

        # Dual values from the RMP (placeholders for illustration)
        dual_values = [0.5, 0.3, 0.2]  # Example of obtained dual values

        # Solve the pricing problem
        new_cost, new_column = solve_pricing_problem(dual_values)
        if new_cost is None:
            print("No column with negative reduced cost. Optimal solution found.")
            break

        # Add new column and its cost to the master problem
        pairings = np.column_stack((pairings, new_column))
        costs_list.append(new_cost)
        print("Updated pairings:", pairings)

if __name__ == "__main__":
    column_generation()

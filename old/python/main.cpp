// g++ -std=c++11 main.cpp -o main 
// ./main


#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>

using namespace std;

// Solve Restricted Master Problem
vector<double> solveRMP(const vector<double>& costs, const vector<vector<int>>& pairings, const vector<int>& demands) {
    size_t num_pairings = costs.size();
    size_t num_flights = demands.size();
    
    vector<double> solution(num_pairings, 0.0);
    vector<bool> flight_covered(num_flights, false);
    double optimal_cost = 0.0;

    for (size_t i = 0; i < num_pairings; ++i) {
        bool covers_new_flight = false;
        for (size_t j = 0; j < num_flights; ++j) {
            if (pairings[i][j] == 1 && !flight_covered[j]) {
                covers_new_flight = true;
            }
        }
        if (covers_new_flight) {
            solution[i] = 1.0;
            optimal_cost += costs[i];
            for (size_t j = 0; j < num_flights; ++j) {
                if (pairings[i][j] == 1) flight_covered[j] = true;
            }
        }
    }

    cout << "RMP solution:\nPairing values: ";
    for (double val : solution) cout << val << " ";
    cout << "\nOptimal cost: " << optimal_cost << endl;

    return solution;
}

// Solve Pricing Problem
pair<double, vector<int>> solvePricingProblem(const vector<double>& dual_values) {
    vector<int> new_column(3);  // Allocate fixed size
    new_column[0] = 1;
    new_column[1] = 1;
    new_column[2] = 0;

    double new_cost = 12;
    double reduced_cost = new_cost;

    for (size_t i = 0; i < dual_values.size(); ++i) {
        reduced_cost -= dual_values[i] * new_column[i];
    }

    cout << "Pricing problem reduced cost: " << reduced_cost << endl;

    if (reduced_cost < -1e-6) {
        cout << "Adding new column with cost: " << new_cost << endl;
        return make_pair(new_cost, new_column);
    }
    return make_pair(numeric_limits<double>::infinity(), vector<int>());
}

// Main Column Generation function
void columnGeneration() {
    vector<vector<int>> pairings = {
        {1, 0, 1},
        {1, 1, 0},
        {0, 1, 1}
    };
    vector<double> costs = {10, 15, 20};
    vector<int> demands = {1, 1, 1};

    while (true) {
        vector<double> solution = solveRMP(costs, pairings, demands);

        vector<double> dual_values = {0.5, 0.3, 0.2};

        pair<double, vector<int>> pricing_solution = solvePricingProblem(dual_values);
        double new_cost = pricing_solution.first;
        vector<int> new_column = pricing_solution.second;

        if (new_cost == numeric_limits<double>::infinity()) {
            cout << "No column with negative reduced cost. Optimal solution found." << endl;
            break;
        }

        pairings.push_back(new_column);
        costs.push_back(new_cost);

        cout << "Updated pairings:\n";
        for (const auto& row : pairings) {
            for (int val : row) cout << val << " ";
            cout << endl;
        }
    }
}

int main() {
    columnGeneration();
    return 0;
}

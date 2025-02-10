// g++ -std=c++11 main_bigger.cpp -o main_bigger 
// ./main_bigger


#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <ctime>
#include <cstdlib>
#include <iomanip>

using namespace std;

// Solve Restricted Master Problem (RMP)
vector<double> solveRMP(const vector<double>& costs, const vector<vector<int>>& pairings, const vector<int>& demands, vector<int>& selectedPairings) {
    size_t num_pairings = costs.size();
    size_t num_flights = demands.size();
    
    vector<double> solution(num_pairings, 0.0);
    vector<bool> flight_covered(num_flights, false);
    double optimal_cost = 0.0;

    selectedPairings.clear();

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
            selectedPairings.push_back(i);
            for (size_t j = 0; j < num_flights; ++j) {
                if (pairings[i][j] == 1) flight_covered[j] = true;
            }
        }
    }

    cout << "RMP solution found with cost: " << fixed << setprecision(2) << optimal_cost << endl;
    return solution;
}

// Solve Pricing Problem
pair<double, vector<int>> solvePricingProblem(const vector<double>& dual_values, int num_flights) {
    vector<int> new_column(num_flights);
    
    // Generate a random new pairing
    double new_cost = rand() % 30 + 10;  // Random cost between 10 and 40

    for (int i = 0; i < num_flights; ++i) {
        new_column[i] = rand() % 2;  // Random 0 or 1 assignment
    }

    double reduced_cost = new_cost;
    for (size_t i = 0; i < dual_values.size(); ++i) {
        reduced_cost -= dual_values[i] * new_column[i];
    }

    if (reduced_cost < -1e-6) {
        return make_pair(new_cost, new_column);
    }
    return make_pair(numeric_limits<double>::infinity(), vector<int>());
}

// Generate random pairings and costs for a bigger problem
void generateProblem(vector<vector<int>>& pairings, vector<double>& costs, vector<int>& demands, int num_pairings, int num_flights) {
    srand(time(0));
    pairings.clear();
    costs.clear();
    demands.assign(num_flights, 1);  // All flights need coverage

    for (int i = 0; i < num_pairings; ++i) {
        vector<int> pairing(num_flights);
        for (int j = 0; j < num_flights; ++j) {
            pairing[j] = rand() % 2;  // Random 0 or 1
        }
        pairings.push_back(pairing);
        costs.push_back(rand() % 50 + 10);  // Random cost between 10 and 60
    }
}

// Main Column Generation function
void columnGeneration(int num_pairings, int num_flights) {
    vector<vector<int>> pairings;
    vector<double> costs;
    vector<int> demands;

    generateProblem(pairings, costs, demands, num_pairings, num_flights);

    cout << "\n--- Initial Problem ---\n";
    cout << "Pairings (rows) with flight coverage:\n";
    for (const auto& row : pairings) {
        for (int val : row) cout << val << " ";
        cout << endl;
    }
    cout << "Costs for pairings:\n";
    for (double cost : costs) cout << cost << " ";
    cout << endl;

    vector<int> selectedPairings;
    while (true) {
        vector<double> solution = solveRMP(costs, pairings, demands, selectedPairings);

        // Dummy dual values for demonstration
        vector<double> dual_values(num_flights, 0.5);

        pair<double, vector<int>> pricing_solution = solvePricingProblem(dual_values, num_flights);
        double new_cost = pricing_solution.first;
        vector<int> new_column = pricing_solution.second;

        if (new_cost == numeric_limits<double>::infinity()) {
            cout << "\nNo column with negative reduced cost. Optimal solution found.\n";
            break;
        }

        pairings.push_back(new_column);
        costs.push_back(new_cost);

        cout << "\nAdding new column with cost: " << new_cost << endl;
        for (int val : new_column) cout << val << " ";
        cout << endl;
    }

    // Print the final solution
    cout << "\n--- Final Solution ---\n";
    cout << "Selected Pairings (by index): ";
    for (int idx : selectedPairings) cout << idx << " ";
    cout << "\nTotal Cost: ";
    double totalCost = 0;
    for (int idx : selectedPairings) totalCost += costs[idx];
    cout << totalCost << endl;

    cout << "\nSelected Pairings Coverage:\n";
    for (int idx : selectedPairings) {
        for (int val : pairings[idx]) cout << val << " ";
        cout << "(Cost: " << costs[idx] << ")" << endl;
    }
}

int main() {
    int num_pairings = 10;  // Increase for a bigger problem
    int num_flights = 5;

    columnGeneration(num_pairings, num_flights);
    return 0;
}

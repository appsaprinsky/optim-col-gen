
// g++ -std=c++11 main_v1.cpp -o main
// ./main
#include <iostream>
#include <vector>
#include <limits>
#include <algorithm>
#include <unordered_set>
using namespace std;

// Flight structure to store the origin and destination cities
struct Flight {
    char origin;
    char destination;
    double cost;
};

const int MAX_DUTY_HOURS = 60;
const int FLIGHT_DURATION = 13;

// Solve the Restricted Master Problem (RMP) using a simple greedy approach
vector<int> solveRMP(const vector<vector<int>>& pairings, const vector<int>& demands, vector<vector<int>>& selectedPairings) {
    int numFlights = demands.size();
    vector<int> solution(numFlights, 0);

    for (const auto& pairing : pairings) {
        bool valid = true;

        // Ensure demand is satisfied
        for (int i = 0; i < numFlights; ++i) {
            if (pairing[i] > demands[i]) {
                valid = false;
                break;
            }
        }
        if (valid) {
            selectedPairings.push_back(pairing);
            for (int i = 0; i < numFlights; ++i) {
                solution[i] += pairing[i];
            }
        }
    }
    return solution;
}

// Pricing problem: find a new column with negative reduced cost
pair<double, vector<int>> solvePricingProblem(const vector<double>& dualValues, const vector<Flight>& flights) {
    int numFlights = flights.size();
    double bestCost = numeric_limits<double>::infinity();
    vector<int> bestPairing(numFlights, 0);

    for (int i = 0; i < numFlights; ++i) {
        vector<int> candidatePairing(numFlights, 0);
        double cost = flights[i].cost - dualValues[i];
        char currentCity = flights[i].destination;
        char startCity = flights[i].origin;
        candidatePairing[i] = 1;
        int dutyHours = FLIGHT_DURATION;
        bool validPairing = true;

        for (int j = (i + 1) % numFlights; dutyHours <= MAX_DUTY_HOURS; j = (j + 1) % numFlights) {
            if (flights[j].origin == currentCity && candidatePairing[j] == 0) {
                candidatePairing[j] = 1;
                cost += flights[j].cost - dualValues[j];
                currentCity = flights[j].destination;
                dutyHours += FLIGHT_DURATION;
            } else {
                continue;
            }

            if (currentCity == startCity) break;
            if (j == i) {
                validPairing = false;
                break;
            }
        }

        if (validPairing && currentCity == startCity && dutyHours <= MAX_DUTY_HOURS && cost < bestCost) {
            bestCost = cost;
            bestPairing = candidatePairing;
        }
    }

    if (bestCost == numeric_limits<double>::infinity()) {
        return {numeric_limits<double>::infinity(), {}};
    }
    return {bestCost, bestPairing};
}

int main() {
    vector<Flight> flights = {
        {'A', 'B', 10}, {'B', 'C', 15}, {'C', 'E', 20},
        {'E', 'C', 25}, {'C', 'B', 5}, {'B', 'A', 10},
        {'E', 'C', 25}, {'C', 'B', 5}, {'G', 'A', 10}
    };
    int numFlights = flights.size();

    vector<int> demands(numFlights, 1);
    vector<vector<int>> pairings;
    vector<vector<int>> selectedPairings;

    pairings.push_back(vector<int>(numFlights, 1));

    int maxIterations = 50;
    int iterationCount = 0;

    while (iterationCount < maxIterations) {
        vector<int> solution = solveRMP(pairings, demands, selectedPairings);

        vector<double> dualValues(numFlights, 0.5);

        auto [newCost, newPairing] = solvePricingProblem(dualValues, flights);
        if (newCost == numeric_limits<double>::infinity()) {
            break;
        }

        bool duplicatePairing = false;
        for (const auto& existingPairing : pairings) {
            if (existingPairing == newPairing) {
                duplicatePairing = true;
                break;
            }
        }

        if (!duplicatePairing) {
            pairings.push_back(newPairing);
        }

        iterationCount++;
    }

    if (iterationCount == maxIterations) {
        cout << "\nWarning: Column generation stopped after reaching max iterations.\n";
    }

    cout << "\nSelected trips in correct order:\n";
    unordered_set<int> coveredFlights;
    for (const auto& pairing : selectedPairings) {
        double totalCost = 0;
        char startCity = 'X';
        char lastCity = 'X';
        int dutyHours = 0;
        bool validSequence = true;

        for (int i = 0; i < numFlights; ++i) {
            if (pairing[i] == 1) {
                coveredFlights.insert(i);
                if (startCity == 'X') {
                    startCity = flights[i].origin;
                    lastCity = flights[i].destination;
                } else if (flights[i].origin != lastCity) {
                    validSequence = false;
                    break;
                }
                lastCity = flights[i].destination;
                cout << flights[i].origin << " -> " << flights[i].destination << " (Cost: " << flights[i].cost << ")\n";
                totalCost += flights[i].cost;
                dutyHours += FLIGHT_DURATION;
            }
        }

        if (startCity != 'X' && validSequence && dutyHours <= MAX_DUTY_HOURS) {
            cout << "Total cost: " << totalCost << "\n";
        }
    }

    cout << "\nUncovered flights:\n";
    for (int i = 0; i < numFlights; ++i) {
        if (coveredFlights.find(i) == coveredFlights.end()) {
            cout << "Flight from " << flights[i].origin << " to " << flights[i].destination << " is uncovered.\n";
        }
    }

    return 0;
}

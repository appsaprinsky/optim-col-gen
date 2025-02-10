
// g++ -std=c++11 main_bigger_constraints.cpp -o main_bigger_constraints 
// ./main_bigger_constraints

#include <iostream>
#include <vector>
#include <algorithm>
#include <limits>
#include <ctime>
#include <cstdlib>
#include <iomanip>
#include <map>

using namespace std;

struct Flight {
    int id;
    string origin;
    string destination;
    double duration;  // in hours
};

struct Pairing {
    vector<int> flight_ids;
    double cost;
    double duty_time;
    string base_city;  // Added to track the base city
};

// Sample flight schedule
vector<Flight> generateFlightSchedule() {
    return {
        {0, "A", "B", 1.5},
        {1, "B", "C", 2.0},
        {2, "C", "A", 1.0},
        {3, "A", "C", 2.5},
        {4, "C", "B", 1.5},
        {5, "B", "A", 2.0}
    };
}

// Generate initial pairings with the start/end constraint
void generateInitialPairings(vector<Pairing>& pairings, const vector<Flight>& flights) {
    int num_flights = flights.size();
    srand(time(0));

    for (int i = 0; i < 10; ++i) {
        Pairing p;
        double total_duty = 0;
        int num_legs = rand() % num_flights + 1;

        bool valid_pairing = false;
        while (!valid_pairing) {
            p.flight_ids.clear();
            total_duty = 0;
            valid_pairing = true;

            for (int j = 0; j < num_legs; ++j) {
                int flight_id = rand() % num_flights;
                if (p.flight_ids.empty()) {
                    p.base_city = flights[flight_id].origin;  // Initialize base city
                }

                p.flight_ids.push_back(flight_id);
                total_duty += flights[flight_id].duration;
            }

            // Validate start/end in the same city
            string first_city = flights[p.flight_ids.front()].origin;
            string last_city = flights[p.flight_ids.back()].destination;

            if (first_city != last_city || total_duty > 8.0) {  // Respect duty period
                valid_pairing = false;
            }
        }

        p.duty_time = total_duty;
        p.cost = total_duty * 50;
        pairings.push_back(p);
    }
}

vector<double> solveRMP(const vector<Pairing>& pairings, const vector<int>& demands, vector<int>& selectedPairings) {
    size_t num_pairings = pairings.size();
    size_t num_flights = demands.size();

    vector<double> solution(num_pairings, 0.0);
    vector<bool> flight_covered(num_flights, false);
    double optimal_cost = 0.0;

    selectedPairings.clear();

    for (size_t i = 0; i < num_pairings; ++i) {
        bool covers_new_flight = false;

        for (int flight_id : pairings[i].flight_ids) {
            if (!flight_covered[flight_id]) {
                covers_new_flight = true;
            }
        }

        if (covers_new_flight) {
            solution[i] = 1.0;
            optimal_cost += pairings[i].cost;
            selectedPairings.push_back(i);

            for (int flight_id : pairings[i].flight_ids) {
                flight_covered[flight_id] = true;
            }
        }
    }

    cout << "RMP solution found with cost: " << fixed << setprecision(2) << optimal_cost << endl;
    return solution;
}

pair<double, Pairing> solvePricingProblem(const vector<double>& dual_values, const vector<Flight>& flights) {
    Pairing new_pairing;
    double new_cost = rand() % 30 + 10;
    double reduced_cost = new_cost;

    for (const auto& flight : flights) {
        new_pairing.flight_ids.push_back(flight.id);
        reduced_cost -= dual_values[flight.id];
    }

    if (reduced_cost < -1e-6) {
        new_pairing.cost = new_cost;
        return make_pair(new_cost, new_pairing);
    }
    return make_pair(numeric_limits<double>::infinity(), Pairing());
}

void columnGeneration(int num_flights) {
    vector<Flight> flights = generateFlightSchedule();
    vector<Pairing> pairings;
    generateInitialPairings(pairings, flights);

    vector<int> demands(num_flights, 1);  // All flights must be covered
    vector<int> selectedPairings;

    cout << "\nEntering While Loop\n";
    while (true) {
        vector<double> solution = solveRMP(pairings, demands, selectedPairings);

        vector<double> dual_values(num_flights, 0.5);  // Dummy dual values
        cout << "\nEntering PP \n";

        auto [new_cost, new_pairing] = solvePricingProblem(dual_values, flights);
        if (new_cost == numeric_limits<double>::infinity()) {
            cout << "\nNo column with negative reduced cost. Optimal solution found.\n";
            break;
        }

        pairings.push_back(new_pairing);
        cout << "\nAdding new column with cost: " << new_cost << endl;
    }

    // Print the final solution
    cout << "\n--- Final Solution ---\n";
    cout << "Selected Pairings (by index): ";
    double totalCost = 0;
    for (int idx : selectedPairings) {
        totalCost += pairings[idx].cost;
        cout << idx << " ";
    }
    cout << "\nTotal Cost: " << totalCost << endl;

    cout << "\nSelected Pairings Coverage:\n";
    for (int idx : selectedPairings) {
        for (int flight_id : pairings[idx].flight_ids) {
            cout << flights[flight_id].origin << "->" << flights[flight_id].destination << " ";
        }
        cout << "(Cost: " << pairings[idx].cost << ")" << endl;
    }
}

int main() {
    int num_flights = 6;
    cout << "\n Start \n";
    columnGeneration(num_flights);
    return 0;
}

#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <coin/ClpSimplex.hpp>
#include <fstream>
using namespace std;
#include "flight_loader.h"


// Define a structure for a trip
struct Trip {
    std::vector<FlightLeg> legs;
    double cost; // Total cost of the trip
};

// Restricted Master Problem (RMP)
class RestrictedMasterProblem {
    private:
        std::vector<Trip> trips; // Current set of trips (columns)
        std::vector<double> dualValues; // Dual values from the RMP
    
    public:
        void solve() {
            ClpSimplex model;
    
            // Set up the problem
            int numCols = trips.size(); // Number of variables (one per trip)
            int numRows = 2; // Number of constraints (one per city)
    
            // Column bounds (all variables >= 0)
            std::vector<double> colLower(numCols, 0.0);
            std::vector<double> colUpper(numCols, COIN_DBL_MAX);
    
            // Objective coefficients (minimize total cost)
            std::vector<double> objCoeffs;
            for (const auto& trip : trips) {
                objCoeffs.push_back(trip.cost);
            }
    
            // Row bounds (demand constraints)
            std::vector<double> rowLower = {5.0, 7.0}; // Example demands
            std::vector<double> rowUpper = {COIN_DBL_MAX, COIN_DBL_MAX};
    
            // Define the constraint matrix
            // For simplicity, assume each trip contributes to both constraints
            std::vector<CoinBigIndex> start(numCols + 1); // Start of each column
            std::vector<int> index; // Row indices of non-zero elements
            std::vector<double> value; // Values of non-zero elements
    
            int nonZeroCount = 0;
            for (int col = 0; col < numCols; ++col) {
                start[col] = nonZeroCount;
                index.push_back(0); // Trip contributes to the first constraint
                value.push_back(1.0); // Coefficient for the first constraint
                nonZeroCount++;
    
                index.push_back(1); // Trip contributes to the second constraint
                value.push_back(1.0); // Coefficient for the second constraint
                nonZeroCount++;
            }
            start[numCols] = nonZeroCount; // End marker
    
            // Load the problem into the model
            model.loadProblem(
                numCols, numRows,
                start.data(), index.data(), value.data(),
                colLower.data(), colUpper.data(),
                objCoeffs.data(), rowLower.data(), rowUpper.data()
            );
    
            // Solve the LP problem
            model.primal();
    
            // Retrieve dual values
            dualValues.resize(model.numberRows());
            for (int i = 0; i < model.numberRows(); ++i) {
                dualValues[i] = model.dualRowSolution()[i];
            }
        }
    
        const std::vector<double>& getDualValues() const {
            return dualValues;
        }
    
        void addTrip(const Trip& trip) {
            trips.push_back(trip);
        }
    
        const std::vector<Trip>& getTrips() const {
            return trips;
        }
    };

// Pricing Problem (PP)
class PricingProblem {
private:
    std::vector<FlightLeg> flights; // List of all flights
    std::vector<double> dualValues; // Dual values from the RMP

public:
    PricingProblem(const std::vector<FlightLeg>& flights, const std::vector<double>& dualValues)
        : flights(flights), dualValues(dualValues) {}

    Trip solve() {
        Trip bestTrip;
        double bestReducedCost = 0.0;

        // Heuristic: Find the trip with the most negative reduced cost // For simplicity, we'll use a greedy approach
        for (const auto& flight1 : flights) {
            for (const auto& flight2 : flights) {
                if (flight1.arrivalCity == flight2.departureCity) {
                    for (const auto& flight3 : flights) {
                        if (flight2.arrivalCity == flight3.departureCity && flight3.arrivalCity == flight1.departureCity) {
                            // Check if the trip is valid (e.g., respects duty time constraints)
                            double reducedCost = calculateReducedCost({flight1, flight2, flight3});
                            if (reducedCost < bestReducedCost) {
                                bestReducedCost = reducedCost;
                                bestTrip = {{flight1, flight2, flight3}, flight1.cost + flight2.cost + flight3.cost};
                            }
                        }
                    }
                }
            }
        }

        return bestTrip;
    }

private:
    double calculateReducedCost(const std::vector<FlightLeg>& legs) const {
        double cost = 0.0;
        for (const auto& leg : legs) {
            cost += leg.cost;
        }
        // Subtract dual values (this is a placeholder; you need to define the exact formula)
        for (size_t i = 0; i < dualValues.size(); ++i) {
            cost -= dualValues[i]; // Example reduction
        }
        return cost;
    }
};

// // load flights (sam.txt)
// std::vector<FlightLeg> loadFlights(const std::string& filename) {
//     std::vector<FlightLeg> flights = loadFlights(filename);
//     printFlights(flights);
//     return flights;
// }

int main() {
    // Load flight data from sam.txt    
    std::vector<FlightLeg> flights = loadFlights("../sam.txt");
    printFlights(flights);

    // Initialize the RMP with a small set of feasible trips
    RestrictedMasterProblem rmp;
    // Add initial trips to rmp (this is a placeholder; implement logic to generate initial trips)
    rmp.addTrip({{flights[0], flights[1], flights[2]}, flights[0].cost + flights[1].cost + flights[2].cost});

    // Column Generation Loop
    while (true) {
        // Solve the RMP
        rmp.solve();

        // Get dual values from the RMP
        const auto& dualValues = rmp.getDualValues();

        // Solve the Pricing Problem
        PricingProblem pp(flights, dualValues);
        Trip newTrip = pp.solve();

        // Check if the new trip has a negative reduced cost
        if (newTrip.cost < 0) {
            rmp.addTrip(newTrip);
        } else {
            break; // No more improving columns
        }
    }

    // Output the final solution
    std::cout << "Optimal trips found!" << std::endl;
    for (const auto& trip : rmp.getTrips()) {
        std::cout << "Trip cost: " << trip.cost << std::endl;
        for (const auto& leg : trip.legs) {
            std::cout << leg.departureCity << " -> " << leg.arrivalCity << " (" << leg.flightNumber << ")" << std::endl;
        }
    }

    return 0;
}


// int main() {
//     RestrictedMasterProblem rmp;

//     // Add some trips (example data)
//     rmp.addTrip({{}, 10.0}); // Trip with cost 10
//     rmp.addTrip({{}, 15.0}); // Trip with cost 15

//     // Solve the RMP
//     rmp.solve();

//     // Print dual values
//     const auto& dualValues = rmp.getDualValues();
//     for (double value : dualValues) {
//         std::cout << "Dual value: " << value << std::endl;
//     }

//     return 0;
// }
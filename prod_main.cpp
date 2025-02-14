#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <coin/ClpSimplex.hpp>
#include <fstream>
using namespace std;
#include "flight_loader.h"


struct Trip {
    std::vector<FlightLeg> legs;
    double cost;
    std::string base;
};

class RestrictedMasterProblem {
    private:
        std::vector<Trip> trips;
        std::vector<double> dualValues;
        std::vector<FlightLeg> flights;
    
    public:
        RestrictedMasterProblem(const std::vector<FlightLeg>& flights) : flights(flights) {}
    
        void solve() {
            ClpSimplex model;
            int numCols = trips.size(); // Number of variables (one per trip)
            int numRows = flights.size(); // Number of constraints (one per flight leg)
            std::vector<double> colLower(numCols, 0.0);
            std::vector<double> colUpper(numCols, COIN_DBL_MAX); 
            // Objective coefficients (minimize total cost)
            std::vector<double> objCoeffs;
            for (const auto& trip : trips) {
                objCoeffs.push_back(trip.cost);
            }
    
            // Row bounds (each flight leg must be covered exactly once)
            std::vector<double> rowLower(numRows, 1.0);
            std::vector<double> rowUpper(numRows, 1.0);
            // Define the constraint matrix
            std::vector<CoinBigIndex> start(numCols + 1); // Start of each column
            std::vector<int> index; // Row indices of non-zero elements
            std::vector<double> value; // Values of non-zero elements
    
            int nonZeroCount = 0;
            for (int col = 0; col < numCols; ++col) {
                start[col] = nonZeroCount;
                for (size_t row = 0; row < flights.size(); ++row) {
                    if (std::find(trips[col].legs.begin(), trips[col].legs.end(), flights[row]) != trips[col].legs.end()) {
                        index.push_back(row);
                        value.push_back(1.0);
                        nonZeroCount++;
                    }
                }
            }
            start[numCols] = nonZeroCount; // End marker
    
            // Load the problem into the model
            model.loadProblem(
                numCols, numRows,
                start.data(), index.data(), value.data(),
                colLower.data(), colUpper.data(),
                objCoeffs.data(), rowLower.data(), rowUpper.data()
            );
            model.primal();
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
        std::string base; // Base city for the trip
    
    public:
        PricingProblem(const std::vector<FlightLeg>& flights, const std::vector<double>& dualValues, const std::string& base)
            : flights(flights), dualValues(dualValues), base(base) {}
    
        Trip solve() {
            Trip bestTrip;
            double bestReducedCost = 0.0;
    
            // Iterate over all flights that start at the base
            for (const auto& startFlight : flights) {
                if (startFlight.departureCity == base) {
                    // Initialize a trip starting with this flight
                    Trip currentTrip;
                    currentTrip.legs.push_back(startFlight);
                    currentTrip.cost = startFlight.cost;
                    currentTrip.base = base;
    
                    // Recursively extend the trip
                    extendTrip(currentTrip, bestTrip, bestReducedCost);
                }
            }
    
            return bestTrip;
        }
    
        double calculateReducedCost(const std::vector<FlightLeg>& legs) const {
            double cost = 0.0;
            for (const auto& leg : legs) {
                cost += leg.cost;
            }
    
            // Subtract dual values based on how the trip contributes to the constraints
            // For example, if the RMP has constraints for each flight leg, count how many legs are covered
            for (size_t i = 0; i < dualValues.size(); ++i) {
                cost -= dualValues[i]; // Adjust this logic based on your actual constraints
            }
    
            return cost;
        }
    
    private:
        void extendTrip(Trip& currentTrip, Trip& bestTrip, double& bestReducedCost) {
            // Check if the current trip is valid (ends at the base)
            if (currentTrip.legs.back().arrivalCity == base) {
                double reducedCost = calculateReducedCost(currentTrip.legs);
                if (reducedCost < bestReducedCost) {
                    bestReducedCost = reducedCost;
                    bestTrip = currentTrip;
                }
            }
    
            // Try to extend the trip by adding more legs
            for (const auto& nextFlight : flights) {
                if (currentTrip.legs.back().arrivalCity == nextFlight.departureCity) {
                    // Check if adding this flight would exceed constraints (e.g., duty time)
                    if (isValidExtension(currentTrip, nextFlight)) {
                        Trip extendedTrip = currentTrip;
                        extendedTrip.legs.push_back(nextFlight);
                        extendedTrip.cost += nextFlight.cost;
    
                        // Recursively extend the trip
                        extendTrip(extendedTrip, bestTrip, bestReducedCost);
                    }
                }
            }
        }
    
        bool isValidExtension(const Trip& trip, const FlightLeg& nextFlight) {
            // Add logic to check constraints (e.g., duty time, layover time)
            // For now, assume all extensions are valid
            return true;
        }
    };



    int main() {
        std::vector<FlightLeg> flights = loadFlights("../sam.txt");
        printFlights(flights);
    
        RestrictedMasterProblem rmp(flights);
    
        // Add initial trips to the RMP (e.g., single-leg trips)
        for (const auto& flight : flights) {
            rmp.addTrip({{flight}, flight.cost, flight.departureCity});
        }
    
        // Column Generation Loop
        const double tolerance = 1e-6;
        int maxIterations = 100;
        int iteration = 0;
    
        while (iteration < maxIterations) {
            rmp.solve();
            const auto& dualValues = rmp.getDualValues();
    
            // Solve the Pricing Problem for each base
            for (const auto& base : {"A", "B", "C"}) { // Adjust based on your bases
                PricingProblem pp(flights, dualValues, base);
                Trip newTrip = pp.solve();
    
                // Calculate reduced cost for the new trip
                double reducedCost = pp.calculateReducedCost(newTrip.legs);
                if (reducedCost < -tolerance) {
                    rmp.addTrip(newTrip);
                }
            }
    
            iteration++;
        }
    
        std::cout << "Optimal trips found!" << std::endl;
        for (const auto& trip : rmp.getTrips()) {
            std::cout << "Trip cost: " << trip.cost << std::endl;
            for (const auto& leg : trip.legs) {
                std::cout << leg.departureCity << " -> " << leg.arrivalCity << " (" << leg.flightNumber << ")" << std::endl;
            }
        }
    
        return 0;
    }
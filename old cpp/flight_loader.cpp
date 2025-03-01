// flight_loader.cpp
#include "flight_loader.h"
#include <fstream>
#include <sstream>

std::vector<FlightLeg> loadFlights(const std::string& filename) {
    std::vector<FlightLeg> flights;
    std::ifstream file(filename);
    
    if (!file) {
        std::cerr << "Error: Unable to open file " << filename << std::endl;
        return flights;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        FlightLeg flight;
        std::string costStr;
        
        std::getline(ss, flight.flightNumber, ',');
        std::getline(ss, flight.departureCity, ',');
        std::getline(ss, flight.arrivalCity, ',');
        std::getline(ss, flight.departureTime, ',');
        std::getline(ss, flight.departureDate, ',');
        std::getline(ss, flight.arrivalTime, ',');
        std::getline(ss, flight.arrivalDate, ',');
        std::getline(ss, costStr, ',');
        
        try {
            flight.cost = std::stod(costStr);
        } catch (const std::exception& e) {
            std::cerr << "Error parsing cost: " << costStr << "\n";
            continue;
        }
        
        flights.push_back(flight);
    }
    
    return flights;
}

void printFlights(const std::vector<FlightLeg>& flights) {
    for (const auto& flight : flights) {
        std::cout << "Flight Number: " << flight.flightNumber
                  << " | From: " << flight.departureCity
                  << " to " << flight.arrivalCity
                  << " | Departure: " << flight.departureDate << " " << flight.departureTime
                  << " | Arrival: " << flight.arrivalDate << " " << flight.arrivalTime
                  << " | Cost: " << flight.cost << "\n";
    }
}

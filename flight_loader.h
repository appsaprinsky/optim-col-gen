#ifndef FLIGHT_LOADER_H
#define FLIGHT_LOADER_H

#include <iostream>
#include <vector>

struct FlightLeg {
    std::string flightNumber;
    std::string departureCity;
    std::string arrivalCity;
    std::string departureTime;
    std::string departureDate;
    std::string arrivalTime;
    std::string arrivalDate;
    double cost;
};

std::vector<FlightLeg> loadFlights(const std::string& filename);
void printFlights(const std::vector<FlightLeg>& flights);

#endif // FLIGHT_LOADER_H

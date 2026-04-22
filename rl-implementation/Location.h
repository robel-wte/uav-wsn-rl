#ifndef __UAVWSN_LOCATION_H
#define __UAVWSN_LOCATION_H

#include <cmath>

struct Location {
    double x;
    double y;
    double z;
    
    Location(double _x = 0, double _y = 0, double _z = 0) : x(_x), y(_y), z(_z) {}
    
    double distanceTo(const Location& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        double dz = z - other.z;
        return sqrt(dx*dx + dy*dy + dz*dz);
    }
};

#endif

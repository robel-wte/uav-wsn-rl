#include "UAVNode.h"
#include "SensorNode.h"
#include "MetricsCollector.h"
#include <cmath>
#include <algorithm>

Define_Module(UAVNode);

// Routing-specific constants (First-Order Radio Model)
static const double TX_POWER_DBM = 0.0;        // 0 dBm transmit power (1 mW)
static const double NOISE_FLOOR_DBM = -95.0;   // Typical noise floor
static const double PATH_LOSS_EXPONENT = 2.0;  // Free space (first-order radio)
static const double REFERENCE_DISTANCE = 1.0;  // 1 meter reference
static const double ENERGY_THRESHOLD_LOW = 0.05;  // 5% energy - high failure risk
static const double DISTANCE_RELIABILITY_FACTOR = 0.9;  // 90% of max range for reliability

void UAVNode::initialize()
{
    // Read parameters
    uavHeight = par("uavHeight").doubleValue();
    searchSpeed = par("searchSpeed").doubleValue();
    commRadius = par("commRadius").doubleValue();
    dataRate = par("dataRate").doubleValue();
    handshakeDelay = par("handshakeDelay").doubleValue();
    roundDuration = par("roundDuration").doubleValue();
    collectionWindow = par("collectionWindow").doubleValue();
    discoveryInterval = par("discoveryInterval").doubleValue();
    
    // Network geometry
    double areaX = getParentModule()->par("areaX").doubleValue();
    double areaY = getParentModule()->par("areaY").doubleValue();
    networkCenter = Location(areaX / 2, areaY / 2, uavHeight);
    
    // Base station location
    cModule *bs = getParentModule()->getSubmodule("bs");
    if (bs) {
        double bsX = bs->par("xPos").doubleValue();
        double bsY = bs->par("yPos").doubleValue();
        baseStationPos = Location(bsX, bsY, 0);
    } else {
        baseStationPos = Location(-100, -100, 0);
    }
    currentPos = Location(baseStationPos.x, baseStationPos.y, uavHeight);
    
    // Initialize state
    currentMode = WAIT_ROUND_START;
    inContactWindow = false;
    currentCHIndex = 0;
    totalCHsVisited = 0;
    totalDataCollected = 0;
    totalFlightDistance = 0;
    simulationStartTime = simTime();
    currentRound = 0;
    
    // Set work area boundaries [0, areaX] x [0, areaY]
    areaMinX = 0;
    areaMinY = 0;
    areaMaxX = areaX;
    areaMaxY = areaY;
    roundEndTime = simTime();
    roundStartTime = simTime();
    nextRoundStartTime = simTime();
    
    // Metrics
    metrics = MetricsCollector::getInstance();
    lastThroughputUpdate = simTime();
    intervalDataCollected = 0;
    
    // Configure timing parameters in MetricsCollector
    if (metrics) {
        metrics->setRoundDuration(roundDuration);
        metrics->setCollectionWindow(collectionWindow);
        EV << "UAV configured MetricsCollector: roundDuration=" << roundDuration 
           << "s, collectionWindow=" << collectionWindow << "s" << endl;
    }

    if (metrics) {
        metrics->recordUAVPosition(currentPos.x, currentPos.y, currentPos.z, simTime(), "START_AT_BASE");
    }
    
    // Initialize messages
    modeTimer = new cMessage("modeTimer");
    beaconMsg = new cMessage("beacon");
    contactTimer = new cMessage("contactTimer");
    
    // Initialize RL parameters
    alpha = 0.1;
    gamma = 0.9;
    epsilon = 0.1;
    
    // Initialize last states
    lastUAVState = {0,0,0,0};
    lastUAVAction = SELECT_CH;
    lastUAVReward = 0.0;
    
    // GLOBAL SYNC: Align first round start with sensors at t=0
    // UAV starts flying immediately at t=0, arrives at network at t=35s
    nextRoundStartTime = simTime();
    scheduleAt(nextRoundStartTime, modeTimer);
    
    EV << "UAV initialized at (" << baseStationPos.x << "," << baseStationPos.y 
       << ") Random Waypoint in [" << areaMinX << "," << areaMaxX << "] x [" 
       << areaMinY << "," << areaMaxY << "]" << endl;
}

void UAVNode::handleMessage(cMessage *msg)
{
    if (!strcmp(msg->getName(), "modeTimer")) {
        switch (currentMode) {
            case WAIT_ROUND_START: {
                startRound();
                currentMode = ENTER_NETWORK;
                // Calculate flight time to network center (BS to network center ~351m at 10m/s = 35s)
                double flightTime = 35.0;  // Matches global sync design
                scheduleAt(simTime() + flightTime, msg);
                return;
            }
                
            case ENTER_NETWORK:
                enterNetwork();
                return;
                
            case RANDOM_WAYPOINT:
                arriveAtWaypoint();
                return;
                
            case IN_CONTACT:
                // Handled by contactTimer
                break;
                
            case LEAVE_NETWORK:
                // Arrived at base station
                currentPos = baseStationPos;
                if (metrics) {
                    metrics->recordUAVPosition(baseStationPos.x, baseStationPos.y, baseStationPos.z, simTime(), "BASE");
                }
                currentMode = RETURN_HOME;
                // Process data forwarding immediately (no additional flight needed)
                // Fall through to RETURN_HOME processing
                scheduleAt(simTime(), msg);
                return;
                
            case RETURN_HOME:
                // Forward all collected data to Base Station before waiting
                if (!collectedData.empty()) {
                    int totalDataSize = 0;
                    std::string allPacketIDs = "";
                    
                    // Aggregate all buffered data from this round
                    for (const auto& buffer : collectedData) {
                        totalDataSize += buffer.totalDataSize;
                        for (int pid : buffer.packetIDs) {
                            if (!allPacketIDs.empty()) allPacketIDs += ",";
                            allPacketIDs += std::to_string(pid);
                        }
                    }
                    
                    // Send aggregated data to Base Station
                    cModule *bs = getParentModule()->getSubmodule("bs");
                    if (bs) {
                        cMessage *dataMsg = new cMessage("UAV_DATA");
                        dataMsg->addPar("dataSize") = totalDataSize;
                        dataMsg->addPar("packetIDs") = allPacketIDs.c_str();
                        dataMsg->addPar("round") = currentRound;
                        dataMsg->addPar("numBatches") = (int)collectedData.size();
                        
                        sendDirect(dataMsg, bs, "directIn");
                        
                        EV << "UAV forwarded " << totalDataSize << " bits (" 
                           << collectedData.size() << " batches, round " << currentRound 
                           << ") to Base Station" << endl;
                    }
                    
                    // Clear buffer for next round
                    collectedData.clear();
                }
                
                currentMode = WAIT_ROUND_START;
                {
                    // Wait until the next aligned round boundary before starting again
                    simtime_t nextStart = std::max(nextRoundStartTime, simTime());
                    scheduleAt(nextStart, msg);
                }
                return;
        }
    }
    else if (!strcmp(msg->getName(), "beacon")) {
        if (currentMode == RANDOM_WAYPOINT || currentMode == IN_CONTACT) {
            sendBeacon();
            scheduleAt(simTime() + discoveryInterval, msg);
        }
        return;
    }
    else if (!strcmp(msg->getName(), "contactTimer")) {
        // Contact completed - check if collection window expired
        currentMode = RANDOM_WAYPOINT;
        
        // CRITICAL FIX: Check if collection window has expired before contacting more CHs
        if (simTime() >= roundEndTime) {
            EV << "UAV collection window expired at t=" << simTime() 
               << " (roundEndTime=" << roundEndTime << ") - leaving network" << endl;
            
            currentMode = LEAVE_NETWORK;
            if (modeTimer->isScheduled()) {
                cancelEvent(modeTimer);
            }
            // Fly back to base station (35s flight time)
            scheduleAt(simTime() + 35.0, modeTimer);
            return;
        }
        
        // Collection window still open - check if more CHs at this waypoint
        contactAllCHsInRange();
        
        // If no more CHs were contacted, move to next waypoint
        if (currentMode == RANDOM_WAYPOINT) {
            executeRandomWaypoint();
        }
        return;
    }
    else if (!strcmp(msg->getName(), "CH_RESPONSE")) {
        int chID = msg->par("chID");
        double chX = msg->par("locationX");
        double chY = msg->par("locationY");
        int dataSize = msg->par("dataSize");
        
        handleCHResponse(chID, Location(chX, chY, 0), dataSize);
        delete msg;
        return;
    }
    else if (!strcmp(msg->getName(), "AGGREGATED_DATA")) {
        // Data received from CH/independent node
        int chID = msg->par("chID");
        int dataSize = msg->par("dataSize");
        
        // Parse packet IDs for delay tracking
        std::string packetIDsStr = msg->par("packetIDs").stringValue();
        std::vector<int> packetIDs;
        
        // Parse comma-separated packet IDs
        if (!packetIDsStr.empty()) {
            size_t start = 0;
            size_t end = packetIDsStr.find(',');
            
            while (end != std::string::npos) {
                std::string idStr = packetIDsStr.substr(start, end - start);
                if (!idStr.empty()) {
                    packetIDs.push_back(std::stoi(idStr));
                }
                start = end + 1;
                end = packetIDsStr.find(',', start);
            }
            
            // Get last ID
            std::string lastId = packetIDsStr.substr(start);
            if (!lastId.empty()) {
                packetIDs.push_back(std::stoi(lastId));
            }
        }
        
        // BUFFER the data for forwarding to BaseStation (don't record reception yet)
        BufferedData buffer;
        buffer.packetIDs = packetIDs;
        buffer.totalDataSize = dataSize;
        buffer.sourceNodeId = chID;
        collectedData.push_back(buffer);
        
        EV << "UAV buffered " << dataSize << " bits (" << packetIDs.size() 
           << " packets) from node " << chID << " - will forward to BaseStation" << endl;
        
        delete msg;
        return;
    }
}

void UAVNode::startRound()
{
    currentRound++;
    discoveredCHs.clear();
    visitedSet.clear();
    currentCHIndex = 0;
    roundStartTime = simTime();
    
    // GLOBAL SYNC: Use MetricsCollector for precise timing
    // Phase 1 (0-8s): Sensors cluster
    // Phase 2 (0-35s): UAV flies to network (parallel with Phase 1)
    // Phase 3 (35-65s): UAV collects data (starts AFTER clustering completes at t=8s)
    // Phase 4 (65-100s): UAV returns to BS
    
    contactWindowStart = metrics->getUAVCollectionWindowStart(currentRound);
    simtime_t collectionWindowEnd = metrics->getUAVCollectionWindowEnd(currentRound);
    roundEndTime = collectionWindowEnd;
    nextRoundStartTime = metrics->getRoundStartTime(currentRound + 1);
    
    EV << "UAV starting round " << currentRound << " at t=" << simTime() 
       << " (collection window: " << contactWindowStart << "-" << collectionWindowEnd 
       << "), roundEndTime=" << roundEndTime << ", nextRoundStartTime=" << nextRoundStartTime << endl;
    
    // RL Phase 8: UAV Scheduling
    performUAVRLScheduling();
}

void UAVNode::enterNetwork()
{
    // Calculate target position in network center
    // Network is 500×500m at (0,0) to (500,500), center is (250,250)
    double targetX = (areaMinX + areaMaxX) / 2.0;
    double targetY = (areaMinY + areaMaxY) / 2.0;
    
    // Update position to network center (entry point after 35s flight)
    currentPos = Location(targetX, targetY, uavHeight);
    if (metrics) {
        metrics->recordUAVPosition(currentPos.x, currentPos.y, currentPos.z, simTime(), "ENTER");
    }
    
    // Start beaconing immediately
    sendBeacon();
    scheduleAt(simTime() + discoveryInterval, beaconMsg);
    
    EV << "UAV entered network at (" << targetX << "," << targetY << ") at t=" << simTime() << endl;
    
    // Start pure Random Waypoint Model
    currentMode = RANDOM_WAYPOINT;
    executeRandomWaypoint();
}

void UAVNode::generateRandomWaypoint()
{
    double x = uniform(areaMinX, areaMaxX);
    double y = uniform(areaMinY, areaMaxY);
    currentWaypoint = Location(x, y, uavHeight);
    
    EV << "UAV generated waypoint at (" << x << "," << y << ")" << endl;
}

void UAVNode::executeRandomWaypoint()
{
    // PURE RANDOM WAYPOINT MODEL: Generate random destination and fly there
    // Position updates AFTER flight time elapses (scheduled arrival)
    
    // Generate random waypoint
    generateRandomWaypoint();
    
    // Calculate actual distance and flight time
    double dist = currentPos.distanceTo(currentWaypoint);
    double flyTime = dist / searchSpeed;
    
    // Check if enough time remains for this flight
    if (simTime() + flyTime > roundEndTime) {
        EV << "UAV insufficient time for next waypoint (need " << flyTime 
           << "s, have " << (roundEndTime - simTime()) << "s) - leaving network" << endl;
        
        // OPTIMIZATION: Calculate adaptive priorities before leaving
        if (!discoveredCHs.empty()) {
            calculateAdaptivePriorities();
            sortCHsByPriority();
        }
        
        currentMode = LEAVE_NETWORK;
        if (modeTimer->isScheduled()) {
            cancelEvent(modeTimer);
        }
        // Fly back to base station (35s flight time)
        scheduleAt(simTime() + 35.0, modeTimer);
        return;
    }
    
    // Schedule arrival at waypoint (KEY: CONSUME TIME)
    currentMode = RANDOM_WAYPOINT;
    if (modeTimer->isScheduled()) {
        cancelEvent(modeTimer);
    }
    scheduleAt(simTime() + flyTime, modeTimer);
    
    EV << "UAV flying to waypoint (" << currentWaypoint.x << "," << currentWaypoint.y 
       << "), dist=" << dist << "m, arrival in " << flyTime << "s" << endl;
}

void UAVNode::arriveAtWaypoint()
{
    // NOW update position (after time consumed in flight)
    currentPos = currentWaypoint;
    
    // Record arrival at waypoint
    if (metrics) {
        metrics->recordUAVPosition(currentPos.x, currentPos.y, currentPos.z, simTime(), "WAYPOINT");
    }
    
    EV << "UAV arrived at waypoint (" << currentPos.x << "," << currentPos.y << ") at t=" << simTime() << endl;
    
    // PURE RWP: Hover at waypoint and collect from ALL CHs/unclustered nodes in range
    // This is the key difference - we don't move until ALL in-range nodes are contacted
    contactAllCHsInRange();
    
    // If no CH was contacted, move to next waypoint immediately
    // If CHs were contacted, the last contact will schedule next waypoint via contactTimer
    if (currentMode == RANDOM_WAYPOINT) {
        // No CH found nearby, continue to next waypoint
        executeRandomWaypoint();
    }
}

void UAVNode::sendBeacon()
{
    int numNodes = getParentModule()->par("numNodes");
    for (int i = 0; i < numNodes; i++) {
        cModule *node = getParentModule()->getSubmodule("node", i);
        if (node) {
            cMessage *beacon = new cMessage("DISCOVERY_BEACON");
            beacon->addPar("uavX") = currentPos.x;
            beacon->addPar("uavY") = currentPos.y;
            beacon->addPar("uavZ") = currentPos.z;
            
            sendDirect(beacon, node, "directIn");
        }
    }
    
    EV << "UAV broadcast beacon from (" << currentPos.x << "," << currentPos.y << ")" << endl;
}

void UAVNode::handleCHResponse(int chId, Location chLoc, int dataSize)
{
    if (visitedSet.find(chId) != visitedSet.end()) {
        return;
    }
    
    // Only record CHs where aggregation is complete and has data
    int chDataSize = dataSize;
    bool aggComplete = false;
    cModule *chNode = getParentModule()->getSubmodule("node", chId);
    if (chNode) {
        auto *sensor = check_and_cast<SensorNode*>(chNode);
        chDataSize = sensor->getAggregatedDataSize();
        aggComplete = sensor->isAggregationComplete();
    }
    
    if (chDataSize <= 0 || !aggComplete) {
        EV << "UAV discovered CH " << chId << " but aggregation incomplete or no data; skipping" << endl;
        return;
    }
    
    EV << "UAV discovered CH " << chId << " with " << chDataSize << " bits (aggregation complete)" << endl;
    
    DiscoveredCH discovered;
    discovered.id = chId;
    discovered.location = chLoc;
    discovered.dataSize = chDataSize;
    
    discoveredCHs.push_back(discovered);
    
    // Don't interrupt waypoint flight - wait until UAV arrives at waypoint
    // Then it will check for nearby CHs and contact them
    // This ensures proper network exploration via Random Waypoint Model
    EV << "CH " << chId << " discovered and added to list (will contact after arriving at waypoint)" << endl;
}

void UAVNode::contactNearestCH()
{
    // Greedy algorithm: select nearest unvisited CH within communication range
    DiscoveredCH* nearestCH = nullptr;
    double minDistance = commRadius + 1.0;  // Start beyond comm radius
    
    for (auto& ch : discoveredCHs) {
        // Skip already visited CHs
        if (visitedSet.find(ch.id) != visitedSet.end()) {
            continue;
        }
        
        double dist = currentPos.distanceTo(ch.location);
        
        // Only consider CHs within communication range
        if (dist <= commRadius && dist < minDistance) {
            minDistance = dist;
            nearestCH = &ch;
        }
    }
    
    // Contact the nearest CH if found
    if (nearestCH != nullptr) {
        EV << "Greedy selection: contacting nearest CH " << nearestCH->id 
           << " at distance " << minDistance << "m" << endl;
        contactCH(*nearestCH);
    }
}

void UAVNode::contactAllCHsInRange()
{
    // PURE RWP: Contact ALL CHs/unclustered nodes within range at current waypoint
    // This ensures proper hovering behavior - UAV stays at waypoint until all nodes serviced
    
    // Find all unvisited CHs within communication range
    std::vector<DiscoveredCH*> nearbyUnvisitedCHs;
    
    for (auto& ch : discoveredCHs) {
        // Skip already visited CHs
        if (visitedSet.find(ch.id) != visitedSet.end()) {
            continue;
        }
        
        double dist = currentPos.distanceTo(ch.location);
        
        // Add all CHs within communication range
        if (dist <= commRadius) {
            nearbyUnvisitedCHs.push_back(&ch);
        }
    }
    
    if (!nearbyUnvisitedCHs.empty()) {
        EV << "UAV at waypoint: found " << nearbyUnvisitedCHs.size() 
           << " unvisited CHs/nodes in range (" << commRadius << "m)" << endl;
        
        // Contact the first one - after T_c, contactTimer will trigger and check for more
        contactCH(*nearbyUnvisitedCHs[0]);
    }
}

void UAVNode::contactCH(const DiscoveredCH& ch)
{
    EV << "UAV contacting CH " << ch.id << " at (" << ch.location.x << "," << ch.location.y << ")" << endl;

    // Get CH node and current state
    cModule *chNode = getParentModule()->getSubmodule("node", ch.id);
    if (!chNode) {
        EV << "CH " << ch.id << " node not found" << endl;
        return;
    }
    
    auto *sensor = check_and_cast<SensorNode*>(chNode);
    int currentDataSize = sensor->getAggregatedDataSize();
    double nodeEnergy = sensor->getEnergy();
    
    if (currentDataSize <= 0) {
        EV << "CH " << ch.id << " has no data; skipping" << endl;
        return;
    }
    
    // Calculate actual distance
    double distance = currentPos.distanceTo(ch.location);
    
    // Calculate actual T_c (contact time window) for this specific CH
    double T_c = calculateActualContactTime_Tc(ch.location);
    if (T_c <= 0) {
        EV << "CH " << ch.id << " - no contact window (T_c=0), skipping" << endl;
        visitedSet.insert(ch.id);
        return;
    }
    
    // Calculate transfer time required
    double transferTime = calculateTransferTime(currentDataSize);
    
    // Check if transfer time exceeds T_c (contact window constraint)
    if (transferTime > T_c) {
        EV << "CH " << ch.id << " - insufficient T_c: need " << transferTime << "s but T_c=" << T_c << "s, FAILED" << endl;
        metrics->recordContactEnd(ch.id, simTime() + T_c, false);  // Contact failed
        visitedSet.insert(ch.id);
        return;
    }
    
    // Evaluate channel quality (SNR-based PER, distance, energy)
    bool channelOK = evaluateChannelQuality(distance, nodeEnergy, currentDataSize);
    if (!channelOK) {
        EV << "CH " << ch.id << " - channel quality insufficient, FAILED" << endl;
        metrics->recordContactEnd(ch.id, simTime() + T_c, false);  // Contact failed
        visitedSet.insert(ch.id);
        return;
    }
    
    // All checks passed - successful contact
    currentPos = ch.location;
    if (metrics) {
        std::string event = "CH_" + std::to_string(ch.id);
        metrics->recordUAVPosition(ch.location.x, ch.location.y, ch.location.z, simTime(), event.c_str());
    }
    
    currentMode = IN_CONTACT;
    inContactWindow = true;
    
    // Record contact start
    metrics->recordContactStart(ch.id, simTime());
    
    // Collect data
    cMessage *collectMsg = new cMessage("UAV_COLLECT");
    sendDirect(collectMsg, chNode, "directIn");
    
    visitedSet.insert(ch.id);
    totalCHsVisited++;
    totalDataCollected += currentDataSize;
    
    // Record contact end with T_c duration (not just transfer time)
    metrics->recordContactEnd(ch.id, simTime() + T_c, true);  // SUCCESS - use T_c
    
    EV << "UAV collected " << currentDataSize << " bits from CH " << ch.id 
       << ", transferTime=" << transferTime << "s, T_c=" << T_c << "s, SNR-OK" << endl;
    
    // Hover for T_c duration (actual contact window, not just transfer time)
    if (contactTimer->isScheduled()) {
        cancelEvent(contactTimer);
    }
    scheduleAt(simTime() + T_c, contactTimer);
}

void UAVNode::leaveNetwork()
{
    currentMode = LEAVE_NETWORK;
    
    // Calculate actual flight time back to base station
    double dist = currentPos.distanceTo(baseStationPos);
    double flyTime = dist / searchSpeed;
    
    if (modeTimer->isScheduled()) {
        cancelEvent(modeTimer);
    }
    scheduleAt(simTime() + flyTime, modeTimer);
    
    EV << "UAV leaving network, flying to base station, dist=" << dist 
       << "m, arrival in " << flyTime << "s" << endl;
}

bool UAVNode::assessLinkQuality(const Location& chLoc, int dataSize, bool& needsHover)
{
    double Tc = calculateContactTime(chLoc);
    double Treq = calculateTransferTime(dataSize);
    
    needsHover = (Treq > Tc);
    
    return Treq <= (Tc + 10.0);  // Allow 10s buffer
}

double UAVNode::calculateContactTime(const Location& chLoc)
{
    double dx = chLoc.x - currentPos.x;
    double dy = chLoc.y - currentPos.y;
    double horizontalDist = sqrt(dx*dx + dy*dy);
    
    double rmax = sqrt(commRadius * commRadius - uavHeight * uavHeight);
    
    if (horizontalDist > rmax) {
        return 0;
    }
    
    double b = horizontalDist;
    double Tc = (2 * sqrt(rmax * rmax - b * b)) / searchSpeed;
    
    return Tc;
}

double UAVNode::calculateTransferTime(int dataSize)
{
    double transferTime = (double)dataSize / dataRate;
    return transferTime + handshakeDelay;
}

void UAVNode::flyTo(const Location& target)
{
    // Calculate distance for statistics (position updated later upon arrival)
    double dx = target.x - currentPos.x;
    double dy = target.y - currentPos.y;
    double distance = sqrt(dx*dx + dy*dy);
    
    // Don't update position instantly - this violates pure RWP
    // Position will be updated when arrival timer fires
    totalFlightDistance += distance;
    
    EV << "UAV flying to (" << target.x << "," << target.y << ") distance=" << distance << "m" << endl;
}

void UAVNode::finish()
{
    EV << "=== UAV Mission Statistics ===" << endl;
    EV << "Total CHs Visited: " << totalCHsVisited << endl;
    EV << "Total Data Collected: " << totalDataCollected << " bits" << endl;
    EV << "Total Flight Distance: " << totalFlightDistance << " m" << endl;
    
    if (modeTimer) {
        if (modeTimer->isScheduled()) {
            cancelEvent(modeTimer);
        }
        delete modeTimer;
        modeTimer = nullptr;
    }
    if (beaconMsg) {
        if (beaconMsg->isScheduled()) {
            cancelEvent(beaconMsg);
        }
        delete beaconMsg;
        beaconMsg = nullptr;
    }
    if (contactTimer) {
        if (contactTimer->isScheduled()) {
            cancelEvent(contactTimer);
        }
        delete contactTimer;
        contactTimer = nullptr;
    }
}

// Duplicate UAVNode destructor removed (see above for correct implementation)

void UAVNode::calculateAdaptivePriorities()
{
    // Calculate contact time T_c for each discovered CH
    // T_c = 2*sqrt(rmax^2 - b^2) / v
    // where rmax = sqrt(commRadius^2 - uavHeight^2), b = 2D distance to CH
    
    double rmax = sqrt(commRadius * commRadius - uavHeight * uavHeight);
    
    for (auto& ch : discoveredCHs) {
        // Calculate 2D distance (ignore z/height difference)
        double dx = currentPos.x - ch.location.x;
        double dy = currentPos.y - ch.location.y;
        double b = sqrt(dx * dx + dy * dy);
        
        if (b < rmax) {
            // CH is reachable - calculate contact time
            ch.contactTime = (2 * sqrt(rmax * rmax - b * b)) / searchSpeed;
            
            // Priority = (dataSize/1000) * contactTime
            // Prioritize CHs with high data and good contact time
            if (ch.contactTime > 0.5) {  // Minimum viable contact time
                ch.priority = (ch.dataSize / 1000.0) * ch.contactTime;
            } else {
                ch.priority = 0.0;  // Too brief, skip
            }
        } else {
            // CH is too far - no contact possible
            ch.contactTime = 0.0;
            ch.priority = 0.0;
        }
    }
}

void UAVNode::sortCHsByPriority()
{
    // Sort CHs by priority in descending order (highest priority first)
    std::sort(discoveredCHs.begin(), discoveredCHs.end(),
              [](const DiscoveredCH& a, const DiscoveredCH& b) {
                  return a.priority > b.priority;
              });
}

// Routing-Specific Communication Model Implementation

double UAVNode::calculateSNR(double distance, double nodeEnergy)
{
    // First-order radio model: path loss with distance
    // SNR = P_tx - PathLoss - NoiseFloor
    // PathLoss = 10 * n * log10(d/d0) where n=2 for free space
    
    static const double TX_POWER_DBM = 0.0;        // 0 dBm transmit power (1 mW)
    static const double NOISE_FLOOR_DBM = -95.0;   // Typical noise floor
    static const double PATH_LOSS_EXPONENT = 2.0;  // Free space (first-order radio)
    static const double REFERENCE_DISTANCE = 1.0;  // 1 meter reference
    static const double ENERGY_THRESHOLD_LOW = 0.05;  // 5% energy threshold
    
    if (distance < REFERENCE_DISTANCE) {
        distance = REFERENCE_DISTANCE;  // Prevent log(0)
    }
    
    double pathLoss = 10.0 * PATH_LOSS_EXPONENT * log10(distance / REFERENCE_DISTANCE);
    double receivedPower = TX_POWER_DBM - pathLoss;
    double snr = receivedPower - NOISE_FLOOR_DBM;
    
    // Energy degradation affects transmission quality
    if (nodeEnergy < ENERGY_THRESHOLD_LOW) {
        double energyPenalty = 3.0 * (1.0 - nodeEnergy / ENERGY_THRESHOLD_LOW);  // Up to 3dB loss
        snr -= energyPenalty;
    }
    
    return snr;  // SNR in dB
}

double UAVNode::calculatePacketErrorRate(double snr)
{
    // Packet Error Rate based on SNR (first-order radio model)
    // TUNED for 75-90% PDR target:
    // SNR < 5 dB: ~15-25% PER
    // SNR 5-10 dB: ~5-15% PER
    // SNR 10-15 dB: ~1-5% PER
    // SNR > 15 dB: <1% PER
    
    if (snr < 0) {
        return 0.35;  // 35% PER for negative SNR (reduced from 70%)
    } else if (snr < 5) {
        return 0.25 - 0.02 * snr;  // Linear from 25% to 15% (reduced from 60-40%)
    } else if (snr < 10) {
        return 0.15 - 0.01 * snr;  // Linear from 15% to 5% (reduced from 40-10%)
    } else if (snr < 15) {
        return 0.05 * exp(-0.15 * (snr - 10));  // Exponential decay from 5%
    } else if (snr < 20) {
        return 0.01 * exp(-0.20 * (snr - 15));  // <1% PER
    } else {
        return 0.002;  // Minimum 0.2% error rate
    }
}

bool UAVNode::evaluateDistanceBasedFailure(double distance)
{
    // Distance-based failure: probabilistic near edge of range
    
    static const double DISTANCE_RELIABILITY_FACTOR = 0.95;  // Increased from 0.9 to 0.95
    double reliableDistance = commRadius * DISTANCE_RELIABILITY_FACTOR;
    
    if (distance > commRadius) {
        return true;  // Beyond range
    }
    
    if (distance <= reliableDistance) {
        return false;  // Reliable within 95%
    }
    
    // Between 95-100%: linear failure probability 0-20% (reduced from 25%)
    double ratio = (distance - reliableDistance) / (commRadius - reliableDistance);
    double failureProb = 0.20 * ratio;
    
    return (uniform(0, 1) < failureProb);
}

bool UAVNode::evaluateEnergyBasedFailure(double nodeEnergy)
{
    // Energy-based transmission failure
    
    static const double ENERGY_THRESHOLD_LOW = 0.05;  // 5% threshold
    
    if (nodeEnergy > ENERGY_THRESHOLD_LOW) {
        return false;  // Sufficient energy
    }
    
    if (nodeEnergy <= 0.0) {
        return true;  // Node dead
    }
    
    // Probabilistic failure for low energy
    double failureProb = 0.30 * (1.0 - nodeEnergy / ENERGY_THRESHOLD_LOW);
    
    return (uniform(0, 1) < failureProb);
}

double UAVNode::calculateActualContactTime_Tc(const Location& chLoc)
{
    // Calculate actual T_c for this specific CH
    // T_c = 2 * sqrt(rmax^2 - b^2) / v
    
    double effectiveRadius = sqrt(commRadius * commRadius - uavHeight * uavHeight);
    
    // Perpendicular distance (offset b)
    double horizDist = sqrt(pow(currentPos.x - chLoc.x, 2) + pow(currentPos.y - chLoc.y, 2));
    double offset_b = horizDist;
    
    if (offset_b >= effectiveRadius) {
        return 0.0;  // No contact window
    }
    
    double contactWindow = 2.0 * sqrt(effectiveRadius * effectiveRadius - offset_b * offset_b) / searchSpeed;
    
    return contactWindow;
}

bool UAVNode::evaluateChannelQuality(double distance, double nodeEnergy, int dataSize)
{
    // Comprehensive channel quality assessment for routing
    
    // 1. Distance check
    if (evaluateDistanceBasedFailure(distance)) {
        EV << "Channel failed: distance-based (" << distance << "m)" << endl;
        return false;
    }
    
    // 2. Energy check
    if (evaluateEnergyBasedFailure(nodeEnergy)) {
        EV << "Channel failed: energy-based (" << nodeEnergy << "J)" << endl;
        return false;
    }
    
    // 3. SNR-based PER
    double snr = calculateSNR(distance, nodeEnergy);
    double per = calculatePacketErrorRate(snr);
    
    // Check aggregate success probability
    int numPackets = std::max(1, dataSize / 2000);
    double successProb = pow(1.0 - per, numPackets);
    
    if (successProb < 0.7) {  // Less than 70% chance (increased from 60%)
        EV << "Channel failed: low success probability=" << successProb << " (SNR=" << snr << "dB)" << endl;
        return false;
    }
    
    // Random PER sampling (reduced for more reliable communication)
    if (uniform(0, 1) < per * 0.2) {  // Use 20% of PER (reduced from 50%)
        EV << "Channel failed: random PER (SNR=" << snr << "dB, PER=" << per << ")" << endl;
        return false;
    }
    
    EV << "Channel OK: SNR=" << snr << "dB, PER=" << per << ", dist=" << distance << "m" << endl;
    return true;
}

UAVNode::~UAVNode()
{
    if (modeTimer) {
        if (modeTimer->isScheduled()) {
            cancelEvent(modeTimer);
        }
        delete modeTimer;
        modeTimer = nullptr;
    }
    if (beaconMsg) {
        if (beaconMsg->isScheduled()) {
            cancelEvent(beaconMsg);
        }
        delete beaconMsg;
        beaconMsg = nullptr;
    }
    if (contactTimer) {
        if (contactTimer->isScheduled()) {
            cancelEvent(contactTimer);
        }
        delete contactTimer;
        contactTimer = nullptr;
    }
}

// RL Implementation for UAV Agent

UAVNode::UAVState UAVNode::observeUAVState() {
    UAVState state;
    
    // Average CH metrics (simplified)
    if (discoveredCHs.empty()) {
        state = {0,0,0,0};
        return state;
    }
    
    double avgQueue = 0, avgAge = 0, avgEnergy = 0, avgDist = 0;
    for (auto& ch : discoveredCHs) {
        avgQueue += ch.dataSize; // Approximate
        avgDist += currentPos.distanceTo(ch.location);
    }
    avgQueue /= discoveredCHs.size();
    avgDist /= discoveredCHs.size();
    
    // Discretize
    state.chQueue = avgQueue < 1000 ? 0 : 1; // LOW/HIGH
    state.chAge = 0; // Not tracked
    state.chEnergy = 0; // Not tracked
    state.chDistance = avgDist < commRadius ? 0 : 1; // NEAR/FAR
    
    return state;
}

UAVNode::UAVAction UAVNode::selectUAVAction(UAVState state) {
    auto stateKey = std::make_tuple(state.chQueue, state.chAge, state.chEnergy, state.chDistance);
    
    // Epsilon-greedy
    if (uniform(0,1) < epsilon) {
        return static_cast<UAVAction>(intrand(2));
    }
    
    // Greedy
    double maxQ = -1e9;
    UAVAction bestAction = SELECT_CH;
    for (int a = 0; a < 2; a++) {
        UAVAction action = static_cast<UAVAction>(a);
        double q = qTableUAV[stateKey][action];
        if (q > maxQ) {
            maxQ = q;
            bestAction = action;
        }
    }
    return bestAction;
}

double UAVNode::computeUAVReward(UAVAction action) {
    double reward = 0.0;
    
    if (action == SELECT_CH) {
        reward += totalDataCollected * 0.001; // Reward for data collected
    }
    
    // Penalty for flight distance
    reward -= totalFlightDistance * 0.0001;
    
    return reward;
}

void UAVNode::updateUAVQTable(UAVState state, UAVAction action, double reward, UAVState nextState) {
    auto stateKey = std::make_tuple(state.chQueue, state.chAge, state.chEnergy, state.chDistance);
    auto nextStateKey = std::make_tuple(nextState.chQueue, nextState.chAge, nextState.chEnergy, nextState.chDistance);
    
    double maxNextQ = -1e9;
    for (int a = 0; a < 2; a++) {
        maxNextQ = std::max(maxNextQ, qTableUAV[nextStateKey][static_cast<UAVAction>(a)]);
    }
    
    qTableUAV[stateKey][action] += alpha * (reward + gamma * maxNextQ - qTableUAV[stateKey][action]);
}

void UAVNode::performUAVRLScheduling() {
    UAVState currentState = observeUAVState();
    UAVAction action = selectUAVAction(currentState);
    
    // Execute action
    if (action == SELECT_CH && !discoveredCHs.empty()) {
        // Select top CHs based on priority
        calculateAdaptivePriorities();
        sortCHsByPriority();
        // Contact top CHs
        contactAllCHsInRange();
    }
    
    // Store for update
    lastUAVState = currentState;
    lastUAVAction = action;
}

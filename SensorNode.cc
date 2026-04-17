#include "SensorNode.h"
#include "MetricsCollector.h"
#include <omnetpp.h>
#include <cmath>
#include <algorithm>
#include <fstream>

Define_Module(SensorNode);

SensorNode::~SensorNode() = default;

void SensorNode::initialize()
{
    // Read parameters
    initialEnergy = par("initialEnergy").doubleValue();
    chProbability = par("chProbability").doubleValue();
    controlPacketSize = par("controlPacketSize").doubleValue();
    dataPacketSize = par("dataPacketSize").doubleValue();
    eElec = par("eElec").doubleValue();
    eFreeSpace = par("eFreeSpace").doubleValue();
    eMultiPath = par("eMultiPath").doubleValue();
    commRadius = par("commRadius").doubleValue();
    idleListeningPower = par("idleListeningPower").doubleValue();
    chDutyCycle = par("chDutyCycle").doubleValue();
    memberDutyCycle = par("memberDutyCycle").doubleValue();
    isolatedDutyCycle = par("isolatedDutyCycle").doubleValue();
    eDA = 5e-9;  // Data aggregation energy per bit
    
    // Read timing parameters (must be consistent across all nodes)
    neighborDiscoveryDelay = par("neighborDiscoveryDelay").doubleValue();
    clusteringPhaseDelay = par("clusteringPhaseDelay").doubleValue();
    joinAttemptDelay = par("joinAttemptDelay").doubleValue();
    unclusteredTimeout = par("unclusteredTimeout").doubleValue();
    roundDuration = par("roundDuration").doubleValue();
    maxBufferSize = par("maxBufferSize").intValue();
    
    // Initialize state
    roundNum = 0;
    roundStartTime = 0;
    nextRoundStartTime = 0;
    status = MEMBER_NODE;
    energy = initialEnergy;
    chTarget = -1;
    isDead = false;
    aggregatedDataSize = 0;
    aggregationComplete = false;
    tdmaSlotDuration = 10;
    isInSleepMode = true;  // Start in sleep until a CH ADV is heard
    wakeUpMsg = nullptr;
    
    controlPacketsSent = 0;
    dataPacketsSent = 0;
    totalEnergyConsumed = 0;
    firstNodeDeathTime = -1;
    lastNodeDeathTime = -1;
    joinScheduled = false;
    lastEpoch = -1;
    
    // Get metrics collector instance
    metrics = MetricsCollector::getInstance();
    
    // Initialize metrics collector if this is node 0
    if (getIndex() == 0) {
        int numNodes = getParentModule()->par("numNodes");
        metrics->initialize(numNodes, simTime());
        metrics->setRoundDuration(roundDuration);
    }
    // Keep metrics in sync with configured round duration even for non-coordinator nodes
    metrics->setRoundDuration(roundDuration);
    
    // Random location
    double areaX = getParentModule()->par("areaX").doubleValue();
    double areaY = getParentModule()->par("areaY").doubleValue();
    myLocation = Location(uniform(0, areaX), uniform(0, areaY), 0);

    // Persist one-shot topology snapshot for plotting
    if (getIndex() == 0) {
        std::ofstream topoInit("results/topology.csv", std::ios::trunc);
        topoInit << "NodeID,X,Y\n";
    }
    {
        std::ofstream topo("results/topology.csv", std::ios::app);
        topo << getIndex() << "," << myLocation.x << "," << myLocation.y << "\n";
    }
    
    startRoundMsg = new cMessage("startRound");
    // GLOBAL SYNC: Schedule first round start at t=0 for ALL nodes
    scheduleAt(simTime(), startRoundMsg);
    
    sleepMsg = nullptr;
    tdmaSlotMsg = nullptr;
    dataCollectionMsg = nullptr;
}

void SensorNode::startNewRound()
{
    if (isDead) return;

    const bool drivesMetrics = metrics && metrics->claimCoordinator(getIndex());
    
    // End previous round metrics
    if (roundNum > 0 && drivesMetrics) {
        metrics->endCurrentRound();
    }
    
    roundNum++;
    roundStartTime = simTime();
    nextRoundStartTime = metrics->getRoundStartTime(roundNum + 1);  // Use global sync

    // Continue until Last Node Death (LND) - no hard round limit with random waypoint UAV
    
    // Clean up old CH rounds from tracking set (Algorithm 1: G set maintenance)
    int period = (int)(1.0 / chProbability);

        // Reset eligibility set at epoch boundaries (every 1/P rounds)
        int currentEpoch = (roundNum - 1) / period;
        if (currentEpoch != lastEpoch) {
            recentCHRounds.clear();
            lastEpoch = currentEpoch;
            EV << "Node " << getIndex() << " epoch reset at round " << roundNum
               << " (epoch " << currentEpoch << ")" << endl;
        }
    auto it = recentCHRounds.begin();
    while (it != recentCHRounds.end()) {
        if (roundNum - *it >= period) {
            it = recentCHRounds.erase(it);  // Node is eligible again
        } else {
            ++it;
        }
    }
    
    // Start new round metrics
    if (drivesMetrics) {
        metrics->startNewRound(roundNum);
    }

    // Schedule the next round boundary using configured roundDuration
    if (startRoundMsg && startRoundMsg->isScheduled()) {
        cancelEvent(startRoundMsg);
    }
    scheduleAt(nextRoundStartTime, startRoundMsg);

    // Duty-cycle based idle energy: CH active, members low duty, isolated mostly sleeping
    const double roundDurationSeconds = roundDuration;
    double dutyCycle = isolatedDutyCycle;  // default sleep

    if (status == CLUSTER_HEAD) {
        dutyCycle = chDutyCycle;
        isInSleepMode = false;
    } else if (!isInSleepMode && chTarget >= 0) {
        dutyCycle = memberDutyCycle;
    } else {
        isInSleepMode = true;
        dutyCycle = isolatedDutyCycle;
    }

    consumeIdleEnergy(idleListeningPower * roundDurationSeconds * dutyCycle);
    if (isDead) return;
    
    status = MEMBER_NODE;
    neighborMap.clear();
    joinedMembers.clear();
    aggregationComplete = false;
    chTarget = -1;
    joinScheduled = false;
    
    // Discard packets older than 3 rounds (not collected by UAV)
    discardExpiredPackets();

    EV << "Node " << getIndex() << " starting round " << roundNum << " energy=" << energy << "J";
    if (aggregatedDataSize > 0) {
        EV << " (buffered data: " << aggregatedDataSize << " bits with " << aggregatedPacketIDs.size() << " packets)";
    }
    EV << endl;
    
    // Update node energy in metrics
    metrics->updateNodeEnergy(getIndex(), energy);
    
    electClusterHead();
}

double SensorNode::calculateThreshold()
{
    // LEACH protocol fairness: Ensure all nodes become CH at least once per epoch
    // Epoch = 1/P rounds (for P=0.1, epoch = 10 rounds)
    // Every 10 rounds, approximately P*N nodes should have been elected as CH
    
    int period = (int)(1.0 / chProbability);
    
    // Determine which epoch we're in
    int currentEpoch = (roundNum - 1) / period;
    int epochStartRound = currentEpoch * period + 1;
    
    // Check if node has been elected in THIS EPOCH
    bool wasElectedThisEpoch = false;
    for (int r : recentCHRounds) {
        if (r >= epochStartRound) {  // Check if round is in current epoch
            wasElectedThisEpoch = true;
            break;
        }
    }
    
    if (wasElectedThisEpoch) {
        // Already elected once in this epoch - cannot be CH again this epoch
        // This ensures fairness: each node gets at most one CH slot per epoch
        return 0.0;
    }
    
    // Node is in G (eligible for this epoch)
    // Use Energy-Weighted LEACH threshold:
    // T_i = (P * (E_i / E_avg)) / (1 - P * (r mod (1/P)))

    int cyclePosition = (roundNum - 1) % period;  // Position within epoch (0 to period-1)
    double denominator = 1.0 - chProbability * cyclePosition;
    if (denominator <= 0.0) {
        // Late in epoch: guarantee election
        return 1.0;
    }

    // Get average energy of alive nodes from metrics
    double avgEnergy = metrics ? metrics->calculateAverageResidualEnergy() : initialEnergy;
    if (avgEnergy <= 0.0) avgEnergy = initialEnergy; // Fallback to initialEnergy if needed

    double threshold = 0.0;
    if (avgEnergy > 0.0) {
        threshold = (chProbability * (energy / avgEnergy)) / denominator;
    }

    // Clamp to valid probability range [0, 1]
    return std::min(1.0, std::max(0.0, threshold));
}

void SensorNode::electClusterHead()
{
    // LEACH protocol: Use probability-based election with per-round threshold
    // that increases as epoch progresses, guaranteeing all nodes become CH at least once per epoch
    
    double threshold = calculateThreshold();
    
    // Random draw against threshold to determine if this node becomes CH
    double randValue = uniform(0, 1);
    bool electCH = (randValue < threshold);

    if (electCH) {
        status = CLUSTER_HEAD;
        recentCHRounds.insert(roundNum);
        joinedMembers.clear();
        receivedMemberSet.clear();  // Clear received members for new round
        
        EV << "Node " << getIndex() << " elected CLUSTER HEAD at t=" << simTime() 
           << " (threshold=" << threshold << ", rand=" << randValue << ")" << endl;
        sendAdvMsg();
        // Beacon phase: send out CH beacons to help members discover neighbors
        scheduleAt(simTime() + neighborDiscoveryDelay, new cMessage("neighborDiscovery"));
        // TDMA scheduling: delay to collect all join requests
        // Members receive ADV at ~0s, schedule sendJoin at 0.05-0.2s
        // This allows a full window for joins to arrive before TDMA
        scheduleAt(simTime() + clusteringPhaseDelay, new cMessage("createTDMA"));
    } else {
        status = MEMBER_NODE;
        EV << "Node " << getIndex() << " is MEMBER NODE at t=" << simTime() 
           << " (threshold=" << threshold << ", rand=" << randValue << ")" << endl;
        
        // Schedule attempt to join a cluster. If no CH responds, node becomes independent data source
        // and sends directly to UAV (avoiding clustering protocol entirely)
        scheduleAt(simTime() + joinAttemptDelay, new cMessage("checkClusterMembership"));
        
        // Schedule timeout - if no TDMA received by then, send data independently
        if (!sleepMsg || !sleepMsg->isScheduled()) {
            if (sleepMsg) {
                cancelAndDelete(sleepMsg);
                sleepMsg = nullptr;
            }
            sleepMsg = new cMessage("wakeUp");
            scheduleAt(simTime() + unclusteredTimeout, sleepMsg);  // timeout for cluster phase
            EV << "Member node " << getIndex() << " will retry as independent node at t=" 
               << (simTime() + unclusteredTimeout) << " if not clustered" << endl;
        }
    }
}

void SensorNode::sendAdvMsg()
{
    int numNodes = getParentModule()->par("numNodes");
    int nodesSent = 0;
    for (int i = 0; i < numNodes; i++) {
        if (i != getIndex()) {
            cModule *targetNode = getParentModule()->getSubmodule("node", i);
            if (targetNode) {
                SensorNode *target = check_and_cast<SensorNode*>(targetNode);
                double dist = myLocation.distanceTo(target->myLocation);
                
                // CRITICAL FIX: Only broadcast within communication radius
                // This reduces energy cost by ~10x compared to broadcasting to all nodes
                if (dist <= commRadius) {
                    cMessage *msg = new cMessage("ADV_MSG");
                    msg->addPar("senderID") = getIndex();
                    msg->addPar("locationX") = myLocation.x;
                    msg->addPar("locationY") = myLocation.y;
                    msg->addPar("round") = roundNum;
                    
                    sendDirect(msg, targetNode, "directIn");
                    consumeTxEnergy(controlPacketSize, dist);
                    controlPacketsSent++;
                    nodesSent++;
                    metrics->recordControlPacket();  // Metric: control overhead
                }
            }
        }
    }
    EV << "CH " << getIndex() << " sent ADV to " << nodesSent << " nodes within " << commRadius << "m range" << endl;
}

void SensorNode::sendJoinReq(int chId)
{
    cModule *targetNode = getParentModule()->getSubmodule("node", chId);
    if (targetNode) {
        cMessage *msg = new cMessage("JOIN_REQ");
        msg->addPar("senderID") = getIndex();
        msg->addPar("locationX") = myLocation.x;
        msg->addPar("locationY") = myLocation.y;
        msg->addPar("round") = roundNum;
        
        SensorNode *target = check_and_cast<SensorNode*>(targetNode);
        double dist = myLocation.distanceTo(target->myLocation);
        
        sendDirect(msg, targetNode, "directIn");
        consumeTxEnergy(controlPacketSize, dist);
        controlPacketsSent++;
        metrics->recordControlPacket();  // Metric: control overhead
    }
}

void SensorNode::processAdvMsg(int senderId, Location senderLoc, double rssi)
{
    double dist = myLocation.distanceTo(senderLoc);
    if (dist > commRadius) {
        return;
    }

    if (isInSleepMode) {
        isInSleepMode = false;
        EV << "Node " << getIndex() << " woke from sleep due to ADV from CH " << senderId << endl;
    }

    if (status == MEMBER_NODE && chTarget == -1) {
        chTarget = senderId;
        neighborMap[senderId] = NeighborInfo{senderId, senderLoc, 0, rssi};
        sendJoinReq(chTarget);
        joinScheduled = true;
    } else if (status == MEMBER_NODE) {
        if (rssi > neighborMap[chTarget].rssi) {
            chTarget = senderId;
        }
        neighborMap[senderId] = NeighborInfo{senderId, senderLoc, 0, rssi};
        if (!joinScheduled) {
            sendJoinReq(chTarget);
            joinScheduled = true;
        }
    }
}

void SensorNode::processJoinReq(int senderId, double senderX, double senderY)
{
    if (status == CLUSTER_HEAD) {
        // CRITICAL FIX: Check for duplicates FIRST to prevent same node joining twice in same round
        auto it = std::find(joinedMembers.begin(), joinedMembers.end(), senderId);
        if (it != joinedMembers.end()) {
            EV << "CH " << getIndex() << " ignoring DUPLICATE JOIN from node " << senderId << endl;
            return;
        }

        // Then check global uniqueness: reject if member already attached to another CH this round
        bool accepted = metrics ? metrics->registerClusterMember(roundNum, senderId, getIndex()) : true;
        if (!accepted) {
            EV << "CH " << getIndex() << " rejecting JOIN from node " << senderId
               << " because it is already assigned to another CH this round" << endl;
            return;
        }

        // Record member distance to CH for clustering metric
        Location senderLoc(senderX, senderY, 0);
        double dist = myLocation.distanceTo(senderLoc);
        if (metrics) {
            metrics->recordMemberDistance(roundNum, dist);
        }

        joinedMembers.push_back(senderId);
        EV << "CH " << getIndex() << " accepted JOIN from node " << senderId << " (now has " << joinedMembers.size() << " members)" << endl;
    }
}

void SensorNode::createTDMASchedule()
{
    if (status == CLUSTER_HEAD) {
        tdmaSchedule.clear();
        simtime_t currentTime = simTime();
        
        for (size_t i = 0; i < joinedMembers.size(); i++) {
            simtime_t slotTime = currentTime + (i * tdmaSlotDuration / 1000.0);
            tdmaSchedule[joinedMembers[i]] = slotTime;
        }
        
        sendTDMASchedule();
        
        // Record cluster formation for metrics
        metrics->recordClusterFormation(getIndex(), joinedMembers.size(), roundNum);
        EV << "CH " << getIndex() << " formed cluster with " << joinedMembers.size() << " members in round " << roundNum << endl;
        
        if (!joinedMembers.empty()) {
            simtime_t collectionTime = currentTime + (joinedMembers.size() * tdmaSlotDuration / 1000.0) + 0.1;
            dataCollectionMsg = new cMessage("collectData");
            scheduleAt(collectionTime, dataCollectionMsg);
            
            // FIX: Set aggregationDeadline to allow full TDMA + aggregation before UAV arrives
            // Timeline: TDMA completes at collectionTime, +3s for aggregation, +5s safety margin
            aggregationDeadline = collectionTime + 8.0;  // 8s after TDMA ends = ~10-11s into 45s round
            EV << "CH " << getIndex() << " set aggregationDeadline to " << aggregationDeadline 
               << " (TDMA ends at " << collectionTime << ")" << endl;
        } else {
            // BUGFIX: CH with no members must also sleep
            sleepTillNextRound();
        }
    }
}

void SensorNode::sendTDMASchedule()
{
    for (int memberId : joinedMembers) {
        cModule *targetNode = getParentModule()->getSubmodule("node", memberId);
        if (targetNode) {
            cMessage *msg = new cMessage("TDMA_SCHEDULE");
            msg->addPar("chID") = getIndex();
            msg->addPar("slotTime") = tdmaSchedule[memberId].dbl();
            msg->addPar("round") = roundNum;
            
            SensorNode *target = check_and_cast<SensorNode*>(targetNode);
            double dist = myLocation.distanceTo(target->myLocation);
            
            sendDirect(msg, targetNode, "directIn");
            consumeTxEnergy(controlPacketSize, dist);
            controlPacketsSent++;
        }
    }
}

void SensorNode::sendDataPacket(int chId)
{
    cModule *targetNode = getParentModule()->getSubmodule("node", chId);
    if (targetNode && !isDead) {
        // Metric: Generate packet with timestamp
        int packetId = metrics->generatePacket(getIndex(), simTime(), dataPacketSize);
        packetGenRounds[packetId] = roundNum;  // Track generation round
        
        cMessage *msg = new cMessage("DATA_PKT");
        msg->addPar("senderID") = getIndex();
        msg->addPar("dataSize") = (int)dataPacketSize;
        msg->addPar("timestamp") = simTime().dbl();
        msg->addPar("packetID") = packetId;  // Track packet for delay
        
        SensorNode *target = check_and_cast<SensorNode*>(targetNode);
        double dist = myLocation.distanceTo(target->myLocation);
        
        sendDirect(msg, targetNode, "directIn");
        consumeTxEnergy(dataPacketSize, dist);
        dataPacketsSent++;
        metrics->recordDataPacket();  // Metric: data packet sent
        
        sleepTillNextRound();
    }
}

void SensorNode::collectDataFromMembers()
{
    if (status == CLUSTER_HEAD) {
          // LEACH Aggregation Model:
          // - Multiple member packets are fused into ONE aggregated packet
          // - Aggregated data size remains fixed at dataPacketSize regardless of member count
          // - This models data fusion/compression at the CH (e.g., averaging, MIN/MAX aggregation)
          // - Individual member packet IDs are tracked for delay metrics
          // - Packet loss is modeled statistically to represent wireless channel errors
          
          // Model realistic packet collection with losses
          // TDMA-scheduled members: some packets don't arrive (5-10% loss typical)
          double packetLossRate = 0.05;  // 5% packet loss in clustering phase
          
          // Generate own data packet
          int ownPacketId = metrics->generatePacket(getIndex(), simTime(), dataPacketSize);
          aggregatedPacketIDs.push_back(ownPacketId);
          packetGenRounds[ownPacketId] = roundNum;  // Track generation round for expiration
        
          // Aggregate member data with realistic losses
          int membersReached = joinedMembers.size();
          for (int mid : joinedMembers) {
              // Each member has independent probability of successful transmission
              if (uniform(0, 1) > packetLossRate) {
                  // Member packet successfully transmitted and aggregated
              } else {
                  // Member packet lost (collision, fading, or timeout)
                  membersReached--;
              }
          }
          
          // Aggregate all member data into a single compressed packet (LEACH-style)
          double aggregatedBits = dataPacketSize;  // single fused packet regardless of member count
          aggregatedDataSize += aggregatedBits;

          // Charge data aggregation energy for all inputs (members + CH)
          double bitsToAggregate = dataPacketSize * (joinedMembers.size() + 1);
          consumeAggregationEnergy(bitsToAggregate);
          
          EV << "CH " << getIndex() << " aggregated " << aggregatedBits << " bits from " 
              << joinedMembers.size() << " members + self"
              << " (total buffered: " << aggregatedDataSize << " bits, packets: " << aggregatedPacketIDs.size() << ")" << endl;
        
          // Record aggregation result for metrics
          if (metrics) {
              bool deadlineMet = simTime() <= aggregationDeadline;
              // Use actual received members (tracked in receivedMemberSet)
              int actualReceivedMembers = (int)receivedMemberSet.size();
              int expectedMembers = (int)joinedMembers.size();
              
              metrics->recordAggregationResult(
                  roundNum,
                  getIndex(),
                  expectedMembers,      // expected members (excluding CH itself)
                  actualReceivedMembers, // actual members that sent data
                  deadlineMet
              );
              
              EV << "CH " << getIndex() << " round " << roundNum << ": expected=" << expectedMembers 
                 << " received=" << actualReceivedMembers << " deadline_met=" << deadlineMet << endl;
          }
          aggregationComplete = true;
        // Schedule automatic sleep if UAV doesn't collect within timeout
        // Cancel any existing sleep message first
        if (sleepMsg && sleepMsg->isScheduled()) {
            cancelEvent(sleepMsg);
        } else if (!sleepMsg) {
            sleepMsg = new cMessage("wakeUp");
        }
        scheduleAt(simTime() + 20.0, sleepMsg);  // 20s timeout for UAV visit (within 45s round, allows UAV collection window of 15s)
        EV << "CH " << getIndex() << " will auto-sleep at " << (simTime() + 20.0) << endl;
    }
}

void SensorNode::aggregateData()
{
    collectDataFromMembers();
}

void SensorNode::interCHNeighborDiscovery()
{
    if (status == CLUSTER_HEAD) {
        sendBeacon();
        EV << "CH " << getIndex() << " performing inter-CH neighbor discovery" << endl;
    }
}

void SensorNode::processCHBeacon(int chId, Location chLoc)
{
    // Process beacon from another CH (already handled in handleMessage CH_BEACON)
    // This is a placeholder for any additional processing needed
    EV << "CH " << getIndex() << " processed beacon from CH " << chId << endl;
}

void SensorNode::sendBeacon()
{
    int numNodes = getParentModule()->par("numNodes");
    for (int i = 0; i < numNodes; i++) {
        if (i != getIndex()) {
            cModule *targetNode = getParentModule()->getSubmodule("node", i);
            if (targetNode) {
                SensorNode *target = check_and_cast<SensorNode*>(targetNode);
                double dist = myLocation.distanceTo(target->myLocation);
                
                if (dist <= commRadius) {
                    cMessage *msg = new cMessage("CH_BEACON");
                    msg->addPar("senderID") = getIndex();
                    msg->addPar("locationX") = myLocation.x;
                    msg->addPar("locationY") = myLocation.y;
                    msg->addPar("dataSize") = aggregatedDataSize;
                    msg->addPar("isCH") = (status == CLUSTER_HEAD ? 1 : 0);
                    msg->addPar("aggComplete") = (aggregationComplete ? 1 : 0);
                    
                    sendDirect(msg, targetNode, "directIn");
                    consumeTxEnergy(controlPacketSize, dist);
                    controlPacketsSent++;
                    metrics->recordControlPacket();  // Metric: control overhead
                }
            }
        }
    }
}

void SensorNode::sendAggregatedData()
{
    // NOTE: This function is intentionally empty.
    // Data transmission to UAV is handled via direct message passing in handleMessage()
    // when UAV sends UAV_COLLECT message (see lines 945-965).
    // Kept as placeholder for potential future routing implementations.
}

void SensorNode::sleepTillNextRound()
{
    simtime_t wakeTime = nextRoundStartTime > simTime() ? nextRoundStartTime : simTime() + 0.01;

    if (!sleepMsg || !sleepMsg->isScheduled()) {
        if (sleepMsg) {
            cancelAndDelete(sleepMsg);
            sleepMsg = nullptr;
        }
        sleepMsg = new cMessage("wakeUp");
        scheduleAt(wakeTime, sleepMsg);
        EV << "Node " << getIndex() << " sleeping till next round (wakeup at " 
           << wakeTime << ")" << endl;
    }
}

double SensorNode::consumeTxEnergy(double bits, double distance)
{
    // First-Order Radio Model transmit energy with free-space / multipath switch
    double d0 = sqrt(eFreeSpace / eMultiPath);
    double amp = (distance > d0) ? eMultiPath : eFreeSpace;
    double txEnergy = (eElec * bits) + (amp * bits * distance * distance);
    energy -= txEnergy;
    totalEnergyConsumed += txEnergy;

    metrics->recordEnergyConsumption(getIndex(), txEnergy);
    metrics->updateNodeEnergy(getIndex(), energy);

    checkAlive();
    return txEnergy;
}

double SensorNode::consumeRxEnergy(double bits)
{
    double rxEnergy = eElec * bits;
    energy -= rxEnergy;
    totalEnergyConsumed += rxEnergy;

    metrics->recordEnergyConsumption(getIndex(), rxEnergy);
    metrics->updateNodeEnergy(getIndex(), energy);

    checkAlive();
    return rxEnergy;
}

double SensorNode::consumeAggregationEnergy(double bits)
{
    double aggEnergy = eDA * bits;
    energy -= aggEnergy;
    totalEnergyConsumed += aggEnergy;

    metrics->recordEnergyConsumption(getIndex(), aggEnergy);
    metrics->updateNodeEnergy(getIndex(), energy);

    checkAlive();
    return aggEnergy;
}

double SensorNode::consumeIdleEnergy(double energyAmount)
{
    if (energyAmount <= 0) {
        return 0.0;
    }

    energy -= energyAmount;
    totalEnergyConsumed += energyAmount;

    metrics->recordEnergyConsumption(getIndex(), energyAmount);
    metrics->updateNodeEnergy(getIndex(), energy);

    checkAlive();
    return energyAmount;
}

double SensorNode::calculateRSSI(double distance)
{
    if (distance == 0) distance = 0.01;
    return 1.0 / (distance * distance);
}

bool SensorNode::checkAlive()
{
    if (energy <= 0 && !isDead) {
        isDead = true;
        energy = 0;
        EV << "Node " << getIndex() << " DIED at round " << roundNum << " time " << simTime() << endl;
        
        // Metric: Record node death for FND/LND tracking
        metrics->recordNodeDeath(getIndex(), roundNum);
        
        if (firstNodeDeathTime < 0) {
            firstNodeDeathTime = simTime();
        }
        lastNodeDeathTime = simTime();
        return false;
    }
    return !isDead;
}

void SensorNode::handleMessage(cMessage *msg)
{
    if (isDead) {
        delete msg;
        return;
    }
    
    if (msg == startRoundMsg) {
        startNewRound();
    } else if (!strcmp(msg->getName(), "neighborDiscovery")) {
        interCHNeighborDiscovery();
        delete msg;
    } else if (!strcmp(msg->getName(), "createTDMA")) {
        createTDMASchedule();
        delete msg;
    } else if (!strcmp(msg->getName(), "collectData")) {
        if (msg == dataCollectionMsg) {
            dataCollectionMsg = nullptr;
        }
        collectDataFromMembers();
        delete msg;
    } else if (!strcmp(msg->getName(), "wakeUp")) {
        sleepMsg = nullptr;
        
        // Node wakes up and starts next round
        // If node was a member but never received TDMA, it acts as independent and sends data now
        if (status == MEMBER_NODE && chTarget >= 0 && aggregatedDataSize == 0) {
            // Joined a cluster but never sent data via TDMA - send independently as fallback
            int packetId = metrics->generatePacket(getIndex(), simTime(), dataPacketSize);
            aggregatedPacketIDs.push_back(packetId);
            packetGenRounds[packetId] = roundNum;  // Track generation round
            aggregatedDataSize += dataPacketSize;
            consumeTxEnergy(dataPacketSize, 50.0);  // Approximate energy for sending
            EV << "Node " << getIndex() << " timeout: joined CH but no TDMA received, sending independent packet " << packetId << endl;
        }
        
        if (startRoundMsg && !startRoundMsg->isScheduled()) {
            scheduleAt(nextRoundStartTime, startRoundMsg);
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "ADV_MSG")) {
        int msgRound = msg->hasPar("round") ? (int)msg->par("round") : -1;
        // Allow modest round skew so drifting timers don't break clustering
        if (msgRound != -1 && msgRound < roundNum - 2) {
            delete msg;
            return;
        }
        int senderId = msg->par("senderID");
        Location senderLoc(msg->par("locationX"), msg->par("locationY"), 0);
        double dist = myLocation.distanceTo(senderLoc);
        double rssi = calculateRSSI(dist);
        processAdvMsg(senderId, senderLoc, rssi);
        
        // FIX: Only schedule sendJoin once per round
        if (status == MEMBER_NODE && chTarget >= 0 && !joinScheduled) {
            scheduleAt(simTime() + uniform(0.05, 0.2), new cMessage("sendJoin"));  // Increased jitter window
            joinScheduled = true;
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "sendJoin")) {
        if (chTarget >= 0) {
            sendJoinReq(chTarget);
        } else {
            // FIX: No CH in range - node remains unclustered (normal LEACH behavior)
            EV << "Node " << getIndex() << " has no CH in range - will be unclustered this round" << endl;
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "checkClusterMembership")) {
        // Node that did not join a cluster: enter passive listening for UAV
        if (status == MEMBER_NODE && chTarget == -1) {
            // Node is unclustered - generate data and enter passive listening
            
            // Generate data packet (like clustered members do)
            int packetId = metrics->generatePacket(getIndex(), simTime(), dataPacketSize);
            packetGenRounds[packetId] = roundNum;
            aggregatedPacketIDs.push_back(packetId);
            aggregatedDataSize += dataPacketSize;
            
            EV << "Unclustered node " << getIndex() << " generated packet " << packetId 
               << ", entering passive listening for UAV" << endl;
            
            // Enter passive listening mode - wait for UAV discovery beacon
            // Node will respond to DISCOVERY_BEACON just like CHs do
            isInSleepMode = false;  // Active listening for UAV
            
            // Schedule sleep until UAV collection window starts (t=35s from round start)
            simtime_t collectionWindowStart = metrics->getUAVCollectionWindowStart(roundNum);
            if (collectionWindowStart > simTime()) {
                // Wake up just before UAV enters network
                if (!sleepMsg || !sleepMsg->isScheduled()) {
                    if (sleepMsg) {
                        cancelAndDelete(sleepMsg);
                    }
                    sleepMsg = new cMessage("wakeUp");
                    scheduleAt(collectionWindowStart - 0.5, sleepMsg);
                    EV << "Unclustered node " << getIndex() << " will wake at t=" 
                       << (collectionWindowStart - 0.5) << " for UAV collection window" << endl;
                }
            }
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "JOIN_REQ")) {
        int msgRound = msg->hasPar("round") ? (int)msg->par("round") : -1;
        // Accept joins unless they are clearly stale; future-round joins are still valid
        if (msgRound != -1 && msgRound < roundNum - 2) {
            delete msg;
            return;
        }
        int senderId = msg->par("senderID");
        double sx = msg->par("locationX");
        double sy = msg->par("locationY");
        processJoinReq(senderId, sx, sy);
        delete msg;
    } else if (!strcmp(msg->getName(), "TDMA_SCHEDULE")) {
        int msgRound = msg->hasPar("round") ? (int)msg->par("round") : -1;
        if (msgRound != -1 && std::abs(msgRound - roundNum) > 1) {
            delete msg;
            return;
        }
        int chID = msg->par("chID");
        simtime_t slotTime = msg->par("slotTime").doubleValue();
        // Guard against TDMA messages that arrive after their intended slot time
        simtime_t safeSlotTime = slotTime < simTime() ? simTime() + 0.0001 : slotTime;
        cMessage *dataMsg = new cMessage("sendData");
        dataMsg->addPar("chID") = chID;
        if (msgRound != -1) dataMsg->addPar("round") = msgRound;
        scheduleAt(safeSlotTime, dataMsg);
        
        // Cancel the fallback sleep/independent transmission since we got TDMA
        if (sleepMsg && sleepMsg->isScheduled()) {
            cancelEvent(sleepMsg);
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "sendData")) {
        int msgRound = msg->hasPar("round") ? (int)msg->par("round") : -1;
        if (msgRound != -1 && msgRound != roundNum) {
            delete msg;
            return;
        }
        int chID = msg->par("chID");
        sendDataPacket(chID);
        delete msg;
    } else if (!strcmp(msg->getName(), "DATA_PKT")) {
        if (status == CLUSTER_HEAD) {
            // Track which member sent data and the packet ID for aggregation
            int senderID = msg->par("senderID");
            if (msg->hasPar("packetID")) {
                int packetId = msg->par("packetID");
                aggregatedPacketIDs.push_back(packetId);

                // Track generation round for expiration: derive from generation timestamp
                double genTs = msg->hasPar("timestamp") ? msg->par("timestamp").doubleValue() : simTime().dbl();
                int genRound = (int)(genTs / roundDuration) + 1;
                packetGenRounds[packetId] = genRound;
                
                // Track this member as having successfully sent data
                receivedMemberSet.insert(senderID);
            }
            EV << "CH " << getIndex() << " received data packet from member " << senderID << endl;
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "CH_BEACON")) {
        int senderId = msg->par("senderID");
        int isCH = msg->par("isCH");
        
        if (status == CLUSTER_HEAD && isCH == 1 && senderId != getIndex()) {
            Location chLoc(msg->par("locationX"), msg->par("locationY"), 0);
            int dataSize = msg->par("dataSize");
            double rssi = calculateRSSI(myLocation.distanceTo(chLoc));
            neighborMap[senderId] = NeighborInfo{senderId, chLoc, dataSize, rssi};
            
            EV << "CH " << getIndex() << " discovered neighbor CH " << senderId << endl;
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "DISCOVERY_BEACON")) {
        // Respond to UAV discovery if node has buffered data OR is an unclustered node that just generated packets
        // This ensures unclustered nodes participate in data collection
        // Range filtering will be done by UAV when it arrives at waypoint
        bool hasData = (aggregatedDataSize > 0) || (!aggregatedPacketIDs.empty());
        
        if (hasData) {
            cMessage *response = new cMessage("CH_RESPONSE");
            response->addPar("chID") = getIndex();
            response->addPar("locationX") = myLocation.x;
            response->addPar("locationY") = myLocation.y;
            response->addPar("dataSize") = (aggregatedDataSize > 0 ? aggregatedDataSize : (int)(aggregatedPacketIDs.size() * dataPacketSize));
            response->addPar("aggComplete") = 1;  // Mark as ready for collection
            
            cModule *uav = getParentModule()->getSubmodule("uav");
            if (uav) {
                sendDirect(response, uav, "directIn");
                std::string nodeType = (status == CLUSTER_HEAD) ? "CH" : "Independent/Unclustered";
                EV << nodeType << " node " << getIndex() << " responded to UAV discovery beacon" << endl;
            }
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "UAV_COLLECT")) {
        // Both CHs and independent nodes transfer buffered data to UAV
        // Update aggregatedDataSize if it's zero but we have packets (unclustered node case)
        if (aggregatedDataSize == 0 && !aggregatedPacketIDs.empty()) {
            aggregatedDataSize = aggregatedPacketIDs.size() * dataPacketSize;
        }
        
        if (aggregatedDataSize > 0) {
            std::string nodeType = (status == CLUSTER_HEAD) ? "CH" : "Independent";
            EV << nodeType << " node " << getIndex() << " transferring " << aggregatedDataSize << " bits to UAV" << endl;
            
            cMessage *dataMsg = new cMessage("AGGREGATED_DATA");
            dataMsg->addPar("chID") = getIndex();
            dataMsg->addPar("dataSize") = aggregatedDataSize;
            dataMsg->addPar("memberCount") = (int)joinedMembers.size();
            
            // Include packet IDs for delay tracking (build comma-separated string)
            std::string packetIDsStr = "";
            for (size_t i = 0; i < aggregatedPacketIDs.size(); i++) {
                packetIDsStr += std::to_string(aggregatedPacketIDs[i]);
                if (i < aggregatedPacketIDs.size() - 1) {
                    packetIDsStr += ",";  // Only add comma between elements, not at end
                }
            }
            dataMsg->addPar("packetIDs") = packetIDsStr.c_str();
            
            cModule *uav = getParentModule()->getSubmodule("uav");
            if (uav) sendDirect(dataMsg, uav, "directIn");
            
            // FIX: Calculate proper 3D distance to UAV (at height 30m)
            // UAV horizontal distance varies, but typical range is 50-100m
            // Use estimated distance based on UAV coverage radius
            double uavHeight = 30.0;  // UAV flies at 30m altitude
            double horizontalDist = 100.0;  // Assume avg horizontal distance
            double dist3D = sqrt(horizontalDist * horizontalDist + uavHeight * uavHeight);  // ~104.4m
            consumeTxEnergy(aggregatedDataSize, dist3D);
            
            aggregatedDataSize = 0;
            aggregatedPacketIDs.clear();
        }
        delete msg;
    } else if (!strcmp(msg->getName(), "UAV_SLEEP")) {
        if (status == CLUSTER_HEAD || aggregatedDataSize > 0) {
            std::string nodeType = (status == CLUSTER_HEAD) ? "CH" : "Independent";
            EV << nodeType << " node " << getIndex() << " entering sleep mode by UAV command" << endl;
            // Cancel any pending automatic sleep
            if (sleepMsg && sleepMsg->isScheduled()) {
                cancelEvent(sleepMsg);
            }
            sleepTillNextRound();
        }
        delete msg;
    } else {
        delete msg;
    }
}

void SensorNode::finish()
{
    auto safeCancelAndDelete = [this](cMessage *&msg) {
        if (!msg) return;

        // If this is a self-message we own, attempt to cancel and delete it safely.
        if (msg->isSelfMessage()) {
            // Ensure the self-message is actually scheduled for THIS module.
            // If it's scheduled for another module, deleting it here causes double-free.
            cModule *arrival = msg->getArrivalModule();
            if (arrival != this) {
                EV << "Warning: self-message '" << msg->getName() << "' is owned by another module ("
                   << (arrival ? arrival->getFullPath().c_str() : "<null>")
                   << "); not cancelling/deleting it here." << endl;
                msg = nullptr;
                return;
            }

            if (msg->isScheduled()) {
                cancelEvent(msg);
            }
            // Do not delete messages here: ownership may be shared or managed
            // by the simulation kernel or other modules. Null our pointer to
            // avoid further access; the message will be cleaned up by OMNeT++
            // at simulation shutdown or by its rightful owner.
            msg = nullptr;
            return;
        }

        // Non-self messages may be owned/managed elsewhere. Do NOT delete them
        // here to avoid double-free; just clear our pointer and warn if it was
        // still scheduled (indicates an unexpected ownership situation).
        if (msg->isScheduled()) {
            EV << "Warning: non-self message '" << msg->getName() << "' is still scheduled in finish(); leaving it to its owner" << endl;
        } else {
            EV << "Warning: not deleting non-self message '" << msg->getName() << "' in finish()" << endl;
        }
        msg = nullptr;
    };
    
    safeCancelAndDelete(startRoundMsg);
    safeCancelAndDelete(sleepMsg);
    safeCancelAndDelete(tdmaSlotMsg);
    safeCancelAndDelete(dataCollectionMsg);
    
    recordScalar("finalEnergy", energy);
    recordScalar("energyConsumed", totalEnergyConsumed);
    recordScalar("isDead", isDead ? 1 : 0);
    recordScalar("controlPacketsSent", controlPacketsSent);
    recordScalar("dataPacketsSent", dataPacketsSent);
    recordScalar("roundsCompleted", roundNum);
    
    if (isDead) {
        recordScalar("timeOfDeath", lastNodeDeathTime);
    }
}

void SensorNode::discardExpiredPackets()
{
    // STRICT 5-ROUND TIMEOUT: Prevent buffer overflow and ensure data freshness
    // Requirement: Packets must not wait more than 5 rounds for delivery
    // Rationale: With 100s rounds, 5 rounds = 500s maximum acceptable delay
    const int maxPacketAge = 5;  // FIXED: 5 rounds maximum (no adaptive logic)
    
    if (aggregatedPacketIDs.empty()) {
        return;
    }
    
    std::vector<int> validPacketIDs;
    int discardedCount = 0;
    int discardedBits = 0;
    
    for (int pid : aggregatedPacketIDs) {
        auto it = packetGenRounds.find(pid);
        if (it != packetGenRounds.end()) {
            int packetAge = roundNum - it->second;
            if (packetAge <= maxPacketAge) {
                // Keep packet - still fresh
                validPacketIDs.push_back(pid);
            } else {
                // Discard expired packet
                discardedCount++;
                discardedBits += dataPacketSize;
                packetGenRounds.erase(it);
                
                // Record as expired/lost in metrics
                if (metrics) {
                    metrics->recordExpiredPacket(pid, roundNum, it->second);
                }
            }
        } else {
            // No generation round tracked - keep for safety
            validPacketIDs.push_back(pid);
        }
    }
    
    if (discardedCount > 0) {
        aggregatedPacketIDs = validPacketIDs;
        aggregatedDataSize -= discardedBits;
        if (aggregatedDataSize < 0) aggregatedDataSize = 0;
        
        EV << "Node " << getIndex() << " discarded " << discardedCount 
           << " expired packets (age > " << maxPacketAge 
           << " rounds), freed " << discardedBits << " bits" << endl;
    }
}

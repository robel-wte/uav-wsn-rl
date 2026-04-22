#include "MetricsCollector.h"
#include <iomanip>
#include <algorithm>

MetricsCollector* MetricsCollector::instance = nullptr;

MetricsCollector::MetricsCollector()
{
    nextPacketId = 0;
    currentRound = 0;
    totalNodes = 0;
    aliveNodes = 0;
    coordinatorId = -1;
    fndRound = -1;
    lndRound = -1;
    fndRecorded = false;
    lndRecorded = false;
    configuredRoundDuration = 200.0;  // FIXED: Synced with omnetpp.ini 200s rounds
    fndCandidateRound = -1;
    
    // Global timing parameters for 200s rounds with Pure Random Waypoint Model
    // CORRECTED FORMULA for square area: E[L] = a × (2 + sqrt(2) + 5×ln(1+sqrt(2))) / 15 ≈ 0.521×a
    // For 500×500m area: E[L] ≈ 0.521 × 500 = 260.5m expected flight distance
    // Flight time per waypoint: E[L] / speed = 260.5m / 10m/s = 26.05s
    // Effective comm radius: 190m (projected from 192m nominal at 30m height)
    // Pause time when CH nearby: E[T_c] ≈ 9s (avg contact time, max 18s)
    // Total expected time per waypoint: 26.05s + 9s = 35.05s
    // Expected waypoints: 130s / 35.05s = 3.71 waypoints per round
    clusteringPhaseDuration = 8.0;         // 0-8s: Clustering phase  
    uavFlightToNetworkTime = 35.0;         // 0-35s: UAV flight to network (parallel with clustering)
    uavCollectionWindowDuration = 130.0;   // 35-165s: UAV collection (~3.71 waypoints per round)
    uavReturnToBaseTime = 35.0;            // 165-200s: UAV return to BS (no overshoot - exact fit)
    uavBaseTransferTime = 1.0;             // Base station data transfer time
    
    roundEnergyConsumption = 0;
    roundControlPackets = 0;
    roundDataPackets = 0;
    roundPacketsGenerated = 0;
    roundPacketsReceived = 0;
    roundBitsReceived = 0;
    
    totalPacketsGenerated = 0;
    totalPacketsReceived = 0;
    totalEnergyConsumed = 0;
    totalThroughput = 0;
}

MetricsCollector* MetricsCollector::getInstance()
{
    if (instance == nullptr) {
        instance = new MetricsCollector();
    }
    return instance;
}

void MetricsCollector::setRoundDuration(double seconds)
{
    if (seconds > 0) {
        configuredRoundDuration = seconds;
    }
}

void MetricsCollector::setCollectionWindow(double seconds)
{
    if (seconds > 0) {
        uavCollectionWindowDuration = seconds;
        std::cout << "MetricsCollector::setCollectionWindow(" << seconds 
                  << ") - uavCollectionWindowDuration now = " << uavCollectionWindowDuration << std::endl;
    }
}

bool MetricsCollector::claimCoordinator(int nodeId)
{
    bool coordinatorDead = false;
    if (coordinatorId >= 0 && coordinatorId < (int)nodeEnergies.size()) {
        coordinatorDead = nodeEnergies[coordinatorId] <= 0;
    }

    if (coordinatorId == -1 || coordinatorDead) {
        coordinatorId = nodeId;
        return true;
    }
    return coordinatorId == nodeId;
}

void MetricsCollector::initialize(int numNodes, simtime_t startTime)
{
    totalNodes = numNodes;
    aliveNodes = numNodes;
    simulationStartTime = startTime;
    nodeEnergies.resize(numNodes, 0);
    fndCandidateRound = -1;
    totalExpiredPackets = 0;
    
    // Get output directory from OMNeT++
    cConfigurationEx *config = cSimulation::getActiveEnvir()->getConfigEx();
    cConfigOption *outputDirOption = cConfigOption::find("outputdir");
    if (outputDirOption) {
        outputDir = config->getAsPath(outputDirOption);
    }
    if (outputDir.empty()) {
        outputDir = "results";
    }
    
    // Prevent deeply nested output directories that could fill the drive
    size_t slashCount = 0;
    size_t pos = 0;
    while ((pos = outputDir.find('/', pos)) != std::string::npos) {
        slashCount++;
        pos++;
    }
    if (slashCount > 1) {
        // More than one level deep, flatten to results/lastDir
        size_t lastSlash = outputDir.find_last_of('/');
        std::string lastDir = (lastSlash != std::string::npos) ? outputDir.substr(lastSlash + 1) : outputDir;
        outputDir = "results/" + lastDir;
    }
    
    // Always create the output directory
    system(("mkdir -p " + outputDir).c_str());
    
    // Open CSV files with headers
    stabilityFile.open(outputDir + "/stability.csv");
    stabilityFile << "Round,Time,AliveNodes,DeadNodes\n";
    
    energyFile.open(outputDir + "/energy.csv");
    energyFile << "Round,EnergyConsumed,AvgResidualEnergy,TotalNetworkEnergy\n";
    
    pdrFile.open(outputDir + "/pdr.csv");
    pdrFile << "Round,PacketsGenerated,PacketsReceived,PDR\n";
    
    throughputFile.open(outputDir + "/throughput.csv");
    throughputFile << "Time,Throughput_bps,Throughput_kbps\n";
    
    delayFile.open(outputDir + "/delay.csv");
    delayFile << "PacketID,SourceNode,GenerationTime,ReceptionTime,Delay_s\n";
    
    contactFile.open(outputDir + "/contact.csv");
    contactFile << "Instance,CHID,StartTime,Duration_s,Successful\n";
    
    overheadFile.open(outputDir + "/overhead.csv");
    overheadFile << "Round,ControlPackets,DataPackets,ControlRatio,OverheadRatio\n";
    
    networkFile.open(outputDir + "/network.csv");
    networkFile << "Round,Time,TotalEnergy,AliveNodes,DeadNodes,AvgEnergy\n";
    
    clusteringFile.open(outputDir + "/clustering.csv");
    
        uavTrajectoryFile.open(outputDir + "/uav_trajectory.csv");
        uavTrajectoryFile << "Time,X,Y,Z,Event\n";
    clusteringFile << "Round,ClusterID,MemberCount,ExpectedMembers,ReceivedMembers,AggregationCompletion,AvgMembersPerCluster,TotalClusters,UnclusteredNodes,AvgDistToCH,DeadlineHit\n";
}

void MetricsCollector::finalize()
{
    // End the current round if it hasn't been ended yet
    if (currentRound > 0) {
        endCurrentRound();
    }

    // Always recalculate LND from actual final state (override any premature recording)
    // LND is the last round where the network was operational
    int finalAliveCount = 0;
    for (double e : nodeEnergies) {
        if (e > 0) finalAliveCount++;
    }
    if (!fndRecorded && fndCandidateRound >= 0) {
        fndRound = fndCandidateRound;
        fndRecorded = true;
    }
    // If all nodes are now dead, LND is the current round (last operational round)
    if (finalAliveCount == 0 && currentRound > 0) {
        lndRound = currentRound;
        lndRecorded = true;
    }

    // Close all open files first before rewriting
    if (stabilityFile.is_open()) stabilityFile.close();
    if (energyFile.is_open()) energyFile.close();
    if (pdrFile.is_open()) pdrFile.close();
    if (throughputFile.is_open()) throughputFile.close();
    if (delayFile.is_open()) delayFile.close();
    if (contactFile.is_open()) contactFile.close();
    if (overheadFile.is_open()) overheadFile.close();
    if (networkFile.is_open()) networkFile.close();
    if (clusteringFile.is_open()) clusteringFile.close();
    if (uavTrajectoryFile.is_open()) uavTrajectoryFile.close();

    // Rewrite PDR file with final per-round delivery (accounts for late arrivals)
    {
        std::ofstream pdrOut(outputDir + "/pdr.csv");
        pdrOut << "Round,PacketsGenerated,PacketsReceived,PDR\n";
        for (int r = 1; r <= currentRound; ++r) {
            int genCount = roundGeneratedMap[r];
            int recvCount = roundReceivedMap[r];
            if (recvCount > genCount) recvCount = genCount;  // clamp to avoid PDR > 1.0
            double pdr = genCount > 0 ? static_cast<double>(recvCount) / genCount : 0.0;
            pdrOut << r << "," << genCount << "," << recvCount << "," << pdr << "\n";
        }
        pdrOut.close();
    }
    
    // Write summary file
    // First, ensure stability metrics are up to date
    int finalAlive = 0;
    for (double e : nodeEnergies) {
        if (e > 0) finalAlive++;
    }
    aliveNodes = finalAlive;
    if (aliveNodes < totalNodes && !fndRecorded) {
        fndRound = fndCandidateRound >= 0 ? fndCandidateRound : currentRound;
        fndRecorded = true;
    }
    if (aliveNodes == 0 && !lndRecorded) {
        lndRound = currentRound;
        lndRecorded = true;
    }

    std::ofstream summaryFile(outputDir + "/summary.txt");
    summaryFile << "=== Simulation Summary ===\n";
    summaryFile << "Total Nodes: " << totalNodes << "\n";
    summaryFile << "FND (First Node Death): Round " << (fndRecorded ? std::to_string(fndRound) : "-1") << "\n";
    summaryFile << "LND (Last Node Death): Round " << (lndRecorded ? std::to_string(lndRound) : "-1") << "\n";
    summaryFile << "Total Packets Generated: " << totalPacketsGenerated << "\n";
    summaryFile << "Total Packets Received: " << totalPacketsReceived << "\n";
    summaryFile << "Overall PDR: " << calculatePDR() << "\n";
    summaryFile << "Average End-to-End Delay: " << calculateAverageDelay() << " s\n";
    summaryFile << "Total Energy Consumed: " << totalEnergyConsumed << " J\n";
    summaryFile << "Total Contact Events: " << contactEvents.size() << "\n";
    summaryFile.close();
}

void MetricsCollector::startNewRound(int roundNum)
{
    currentRound = roundNum;
    roundEnergyConsumption = 0;
    roundControlPackets = 0;
    roundDataPackets = 0;
    roundPacketsGenerated = 0;
    roundPacketsReceived = 0;
    roundBitsReceived = 0;
    roundDelays.clear();
    roundClusters.clear();  // Clear clustering data for new round

    // Snapshot alive node count at the start of the round for consistent clustering math
    aliveNodesAtRoundStart[roundNum] = aliveNodes;

    // Reset per-round member assignments to avoid cross-round contamination
    memberAssignmentsByRound[roundNum].clear();
    memberDistanceSumByRound[roundNum] = 0.0;
    memberDistanceCountByRound[roundNum] = 0;
}

void MetricsCollector::endCurrentRound()
{
    // Recompute aliveNodes from residual energies to avoid stale counters
    int recomputedAlive = 0;
    for (double e : nodeEnergies) {
        if (e > 0) {
            recomputedAlive++;
        }
    }
    aliveNodes = recomputedAlive;
    if (aliveNodes < totalNodes && !fndRecorded) {
        fndRound = (fndCandidateRound >= 0) ? fndCandidateRound : currentRound;
        fndRecorded = true;
    }
    if (aliveNodes == 0 && !lndRecorded) {
        lndRound = currentRound;
        lndRecorded = true;
    }

    // Calculate average residual energy
    double avgResidual = calculateAverageResidualEnergy();
    double totalEnergy = getTotalNetworkEnergy();
    
    const double roundDurationSeconds = (configuredRoundDuration > 0) ? configuredRoundDuration : 150.0;
    double timeStamp = roundDurationSeconds * currentRound;

    // Write stability data with deterministic round-aligned timestamps
    writeStabilityData(currentRound, timeStamp, aliveNodes);
    
    // Write energy data
    writeEnergyData(currentRound, roundEnergyConsumption, avgResidual, totalEnergy);
    
    // Write overhead data
    double overheadRatio = (roundControlPackets + roundDataPackets) > 0 ?
                           (double)roundControlPackets / (roundControlPackets + roundDataPackets) : 0.0;
    writeOverheadData(currentRound, roundControlPackets, roundDataPackets, overheadRatio);
    
    // Calculate and write throughput based on configured round duration
    // (avoids spurious spikes when the simulator stops mid-round)
    if (roundDurationSeconds > 0) {
        double throughput = roundBitsReceived / roundDurationSeconds;
        writeThroughputData(timeStamp, throughput);
    }
    
    // Write clustering data
    writeClusteringData(currentRound);
    
    // Write network data
    writeNetworkData(currentRound, timeStamp, totalEnergy, aliveNodes, totalNodes - aliveNodes);
    
    // Write PDR using generation vs reception counts credited to generation round
    int genCount = roundGeneratedMap[currentRound];
    int recvCount = roundReceivedMap[currentRound];
    double pdr = (genCount > 0) ? (double)recvCount / genCount : 0.0;
    writePDRData(currentRound, pdr);
}

int MetricsCollector::generatePacket(int sourceNode, simtime_t genTime, int dataSize)
{
    int packetId = nextPacketId++;
    PacketInfo info;
    info.genTime = genTime;
    info.recvTime = -1;
    info.sourceNode = sourceNode;
    info.dataSize = dataSize;
    info.genRound = currentRound;  // Track which round this packet was generated in
    packetTracker[packetId] = info;
    
    roundPacketsGenerated++;
    totalPacketsGenerated++;
    roundGeneratedMap[currentRound]++;  // Track per round
    
    return packetId;
}

void MetricsCollector::recordPacketReception(int packetId, simtime_t recvTime)
{
    if (packetTracker.find(packetId) != packetTracker.end()) {
        packetTracker[packetId].recvTime = recvTime;
        double delay = (recvTime - packetTracker[packetId].genTime).dbl();
        
        // Count all received packets for PDR (no window restriction)
        // This allows realistic PDR measurement even with large delays
        int genRound = packetTracker[packetId].genRound;
        roundReceivedMap[genRound]++;
        totalPacketsReceived++;

        // Throughput is measured at reception time (current round)
        roundPacketsReceived++;
        roundBitsReceived += packetTracker[packetId].dataSize;
        
        // Record delay for every delivered packet (even if received in a later round)
        roundDelays.push_back(delay);
        allDelays.push_back(delay);
        writeDelayData(packetId, delay);
    }
}

void MetricsCollector::recordExpiredPacket(int packetId, int currentRound, int genRound)
{
    // Mark packet as expired/lost - do not count as received
    // These packets timed out waiting for UAV collection
    totalExpiredPackets++;
    
    // Could write to a separate expired packets CSV if needed
    // For now, just track the count
}

void MetricsCollector::recordEnergyConsumption(int nodeId, double energyConsumed)
{
    roundEnergyConsumption += energyConsumed;
    totalEnergyConsumed += energyConsumed;
}

void MetricsCollector::updateNodeEnergy(int nodeId, double residualEnergy)
{
    if (nodeId >= 0 && nodeId < nodeEnergies.size()) {
        nodeEnergies[nodeId] = residualEnergy;
    }
}

void MetricsCollector::recordControlPacket()
{
    roundControlPackets++;
}

void MetricsCollector::recordDataPacket()
{
    roundDataPackets++;
}

void MetricsCollector::recordNodeDeath(int nodeId, int roundNum)
{
    aliveNodes--;

    if (nodeId == coordinatorId) {
        coordinatorId = -1;  // Force reassignment to an alive node
    }

    // Track first observed death, but validate at round end for consistency
    if (fndCandidateRound < 0) {
        fndCandidateRound = roundNum;
    }
}

void MetricsCollector::recordContactStart(int chId, simtime_t startTime)
{
    ContactEvent event;
    event.chId = chId;
    event.startTime = startTime;
    event.duration = -1;
    event.successful = false;
    contactEvents.push_back(event);
}

void MetricsCollector::recordContactEnd(int chId, simtime_t endTime, bool successful)
{
    // Find the most recent contact event for this CH
    for (auto it = contactEvents.rbegin(); it != contactEvents.rend(); ++it) {
        if (it->chId == chId && it->duration.dbl() < 0) {
            it->duration = endTime - it->startTime;
            it->successful = successful;
            
            // Track UAV visit for adaptive packet expiration
            if (successful) {
                nodeUAVVisitCount[chId]++;
            }
            
            // Write to file
            writeContactData(contactEvents.size(), it->duration, successful ? 1.0 : 0.0);
            break;
        }
    }
}

void MetricsCollector::recordThroughput(double bitsReceived, simtime_t interval)
{
    double throughput = bitsReceived / interval.dbl();
    totalThroughput += throughput;
    writeThroughputData(simTime(), throughput);
}

void MetricsCollector::writeStabilityData(int roundNum, double timeStamp, int aliveNodes)
{
    if (stabilityFile.is_open()) {
        stabilityFile << roundNum << ","
                     << timeStamp << ","
                     << aliveNodes << ","
                     << (totalNodes - aliveNodes) << "\n";
        stabilityFile.flush();
    }
}

void MetricsCollector::writeEnergyData(int roundNum, double energyConsumed, 
                                       double avgResidualEnergy, double totalNetworkEnergy)
{
    if (energyFile.is_open()) {
        energyFile << roundNum << ","
                  << energyConsumed << ","
                  << avgResidualEnergy << ","
                  << totalNetworkEnergy << "\n";
        energyFile.flush();
    }
}

void MetricsCollector::writePDRData(int roundNum, double pdr)
{
    if (pdrFile.is_open()) {
        int genCount = roundGeneratedMap[roundNum];
        int recvCount = roundReceivedMap[roundNum];
        if (recvCount > genCount) recvCount = genCount;  // clamp to avoid PDR > 1.0
        pdrFile << roundNum << ","
               << genCount << ","
               << recvCount << ","
               << pdr << "\n";
        pdrFile.flush();
    }
}

void MetricsCollector::writeThroughputData(simtime_t time, double throughput)
{
    if (throughputFile.is_open()) {
        throughputFile << time.dbl() << ","
                      << throughput << ","
                      << (throughput / 1000.0) << "\n";
        throughputFile.flush();
    }
}

void MetricsCollector::writeDelayData(int packetId, double delay)
{
    if (delayFile.is_open() && packetTracker.find(packetId) != packetTracker.end()) {
        PacketInfo& info = packetTracker[packetId];
        delayFile << packetId << ","
                 << info.sourceNode << ","
                 << info.genTime.dbl() << ","
                 << info.recvTime.dbl() << ","
                 << delay << "\n";
        delayFile.flush();
    }
}

void MetricsCollector::writeContactData(int instance, simtime_t duration, double probability)
{
    if (contactFile.is_open() && !contactEvents.empty()) {
        ContactEvent& event = contactEvents.back();
        contactFile << instance << ","
                   << event.chId << ","
                   << event.startTime.dbl() << ","
                   << duration.dbl() << ","
                   << (event.successful ? "Yes" : "No") << "\n";
        contactFile.flush();
    }
}

void MetricsCollector::writeOverheadData(int roundNum, int controlPkts, 
                                         int dataPkts, double ratio)
{
    if (overheadFile.is_open()) {
        int total = controlPkts + dataPkts;
        double controlRatio = total > 0 ? (double)controlPkts / total : 0.0;
        overheadFile << roundNum << ","
                    << controlPkts << ","
                    << dataPkts << ","
                    << controlRatio << ","
                    << ratio << "\n";
        overheadFile.flush();
    }
}

void MetricsCollector::writeNetworkData(int roundNum, double timeStamp, double totalEnergy, 
                                        int alive, int dead)
{
    if (networkFile.is_open()) {
        double avgEnergy = alive > 0 ? totalEnergy / alive : 0.0;
        networkFile << roundNum << ","
                   << timeStamp << ","
                   << totalEnergy << ","
                   << alive << ","
                   << dead << ","
                   << avgEnergy << "\n";
        networkFile.flush();
    }
}

double MetricsCollector::calculateAverageDelay()
{
    if (allDelays.empty()) return 0.0;
    
    double sum = 0;
    for (double delay : allDelays) {
        sum += delay;
    }
    return sum / allDelays.size();
}

double MetricsCollector::calculatePDR()
{
    if (totalPacketsGenerated == 0) return 0.0;
    return (double)totalPacketsReceived / totalPacketsGenerated;
}

double MetricsCollector::calculateAverageResidualEnergy()
{
    if (aliveNodes == 0) return 0.0;
    
    double sum = 0;
    int count = 0;
    for (double energy : nodeEnergies) {
        if (energy > 0) {
            sum += energy;
            count++;
        }
    }
    return count > 0 ? sum / count : 0.0;
}

double MetricsCollector::getTotalNetworkEnergy()
{
    double total = 0;
    for (double energy : nodeEnergies) {
        if (energy > 0) {
            total += energy;
        }
    }
    return total;
}

void MetricsCollector::recordClusterFormation(int chId, int memberCount, int roundNum)
{
    // Buffer cluster data by round number to handle async recording
    auto& clusters = clustersByRound[roundNum];
    
    // Check if this CH has already been recorded in this round
    for (const auto& cluster : clusters) {
        if (cluster.chId == chId) {
            return;  // Already recorded
        }
    }
    
    ClusterInfo cluster;
    cluster.chId = chId;
    cluster.memberCount = memberCount;
    cluster.expectedMembers = memberCount;
    cluster.receivedMembers = 0;
    cluster.deadlineHit = false;
    clusters.push_back(cluster);
}

void MetricsCollector::recordAggregationResult(int roundNum, int chId, int expectedMembers, int receivedMembers, bool deadlineMet)
{
    auto& clusters = clustersByRound[roundNum];

    // Find existing cluster entry
    for (auto& cluster : clusters) {
        if (cluster.chId == chId) {
            cluster.memberCount = expectedMembers;
            cluster.expectedMembers = expectedMembers;
            cluster.receivedMembers = receivedMembers;
            cluster.deadlineHit = !deadlineMet;  // Swap logic: deadlineHit = 1 if deadline was NOT met
            return;
        }
    }

    // If not found, create a new entry so metrics remain consistent
    ClusterInfo cluster;
    cluster.chId = chId;
    cluster.memberCount = expectedMembers;
    cluster.expectedMembers = expectedMembers;
    cluster.receivedMembers = receivedMembers;
    cluster.deadlineHit = !deadlineMet;  // Swap logic: deadlineHit = 1 if deadline was NOT met
    clusters.push_back(cluster);
}

bool MetricsCollector::registerClusterMember(int roundNum, int memberId, int chId)
{
    auto& assignments = memberAssignmentsByRound[roundNum];

    // Reject if this member is already tied to another CH in the same round
    if (assignments.find(memberId) != assignments.end()) {
        return false;
    }

    assignments[memberId] = chId;
    return true;
}

void MetricsCollector::recordMemberDistance(int roundNum, double distance)
{
    memberDistanceSumByRound[roundNum] += distance;
    memberDistanceCountByRound[roundNum] += 1;
}

void MetricsCollector::recordUAVPosition(double x, double y, double z, simtime_t time, const char* event)
{
    if (uavTrajectoryFile.is_open()) {
        uavTrajectoryFile << time.dbl() << ","
                         << x << ","
                         << y << ","
                         << z << ","
                         << event << "\n";
        uavTrajectoryFile.flush();
    }
}

void MetricsCollector::writeClusteringData(int roundNum)
{
    // Get clusters for this specific round from the buffer
    auto it = clustersByRound.find(roundNum);
    if (it == clustersByRound.end() || it->second.empty()) {
        // No clusters formed this round - all nodes are unclustered
        double avgDist = 0.0;
        if (memberDistanceCountByRound[roundNum] > 0) {
            avgDist = memberDistanceSumByRound[roundNum] / memberDistanceCountByRound[roundNum];
        }
        int aliveForRound = aliveNodesAtRoundStart.count(roundNum) ? aliveNodesAtRoundStart[roundNum] : aliveNodes;
        clusteringFile << roundNum << ",N/A,0,0,0,0,0,0," << aliveForRound << "," << avgDist << ",0\n";
        clusteringFile.flush();
        return;
    }
    
    const auto& clusters = it->second;

    // Prefer deduplicated member assignments if available; fallback to recorded counts
    const auto assignmentsIt = memberAssignmentsByRound.find(roundNum);
    std::unordered_map<int, int> derivedCounts;
    int totalMembers = 0;

    // Use deduplicated assignments only when we actually recorded any; otherwise
    // fall back to the CH-reported member counts to avoid zeroing totals.
    if (assignmentsIt != memberAssignmentsByRound.end() && !assignmentsIt->second.empty()) {
        for (const auto& entry : assignmentsIt->second) {
            derivedCounts[entry.second]++;  // entry.second is chId
        }
        totalMembers = static_cast<int>(assignmentsIt->second.size());
    } else {
        for (const auto& cluster : clusters) {
            derivedCounts[cluster.chId] = cluster.memberCount;
            totalMembers += cluster.memberCount;
        }
    }

    // Unclustered nodes = alive - (CHs + members). Each CH counts as assigned.
    int aliveForRound = aliveNodesAtRoundStart.count(roundNum) ? aliveNodesAtRoundStart[roundNum] : aliveNodes;
    int assigned = static_cast<int>(clusters.size()) + totalMembers;
    int unclusteredNodes = aliveForRound - assigned;
    if (unclusteredNodes < 0) unclusteredNodes = 0;

    double avgMembersPerCluster = clusters.empty() ? 0.0 : (double)totalMembers / clusters.size();

    double avgDist = 0.0;
    if (memberDistanceCountByRound[roundNum] > 0) {
        avgDist = memberDistanceSumByRound[roundNum] / memberDistanceCountByRound[roundNum];
    }

    // Write one row per cluster using derived counts when available
    for (auto& cluster : clusters) {
        int expectedMembers = derivedCounts.count(cluster.chId) ? derivedCounts[cluster.chId] : cluster.memberCount;
        int receivedMembers = cluster.receivedMembers;
        if (expectedMembers == 0 && receivedMembers == 0) {
            // Zero-member CHs are treated as complete
            receivedMembers = 0;
        }

        double completion = expectedMembers > 0 ? std::min(receivedMembers, expectedMembers) / static_cast<double>(expectedMembers) : 1.0;
        int deadlineFlag = cluster.deadlineHit ? 1 : 0;

        clusteringFile << roundNum << ","
                      << cluster.chId << ","
                      << expectedMembers << ","
                      << expectedMembers << ","
                      << receivedMembers << ","
                      << completion << ","
                      << avgMembersPerCluster << ","
                      << clusters.size() << ","
                      << unclusteredNodes << ","
                      << avgDist << ","
                      << deadlineFlag << "\n";
    }

    clusteringFile.flush();

    // Clean up old round data to prevent memory leaks
    clustersByRound.erase(it);
    memberAssignmentsByRound.erase(roundNum);
    memberDistanceSumByRound.erase(roundNum);
    memberDistanceCountByRound.erase(roundNum);
    aliveNodesAtRoundStart.erase(roundNum);
}

// Global synchronization functions for precise timing coordination
simtime_t MetricsCollector::getRoundStartTime(int roundNum) const
{
    // Round starts at t = roundNum * roundDuration
    // Round 1 starts at t=0, Round 2 at t=100, etc.
    return simulationStartTime + (roundNum - 1) * configuredRoundDuration;
}

simtime_t MetricsCollector::getClusteringPhaseEnd() const
{
    // Clustering phase ends at t = roundStart + 8s
    return getRoundStartTime(currentRound) + clusteringPhaseDuration;
}

simtime_t MetricsCollector::getUAVCollectionWindowStart(int roundNum) const
{
    // UAV collection window starts at t = roundStart + 35s
    return getRoundStartTime(roundNum) + uavFlightToNetworkTime;
}

simtime_t MetricsCollector::getUAVCollectionWindowEnd(int roundNum) const
{
    // UAV collection window ends at t = roundStart + flightTime + collectionWindow
    return getRoundStartTime(roundNum) + uavFlightToNetworkTime + uavCollectionWindowDuration;
}

int MetricsCollector::getNodeUAVVisits(int nodeId) const
{
    auto it = nodeUAVVisitCount.find(nodeId);
    if (it != nodeUAVVisitCount.end()) {
        return it->second;
    }
    return 0;
}


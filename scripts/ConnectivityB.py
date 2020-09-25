# Project: LandAdvisor-ITCP
# Credits: Islands Trust, John Gallo, Randal Greene
# Copyright 2012 Islands Trust
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Import system modules...
import sys, os, math, arcpy
from arcpy.sa import *

# Path to custom toolbox...
scriptDir = os.path.dirname(sys.argv[0])
toolboxpath = scriptDir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
arcpy.AddToolbox(toolboxpath)

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script arguments...
protectedAreaPairsFeatureClass = sys.argv[1]
studyAreaRasterMask = sys.argv[2]
percentageCorridorValuesToKeep = sys.argv[3]
numPercentageCorridorValuesToKeep = float(percentageCorridorValuesToKeep)
permeabilityWeight = sys.argv[4]
corridorEnvelopeWeight = sys.argv[5]
lcpLengthWeight = sys.argv[6]
connectivityOutputRaster = sys.argv[7]
deleteTemps = sys.argv[8]

# # Settings and script arguments - hard-code for testing...
# arcpy.env.overwriteOutput = True
# arcpy.env.workspace = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output"
# arcpy.env.scratchWorkspace = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\scratch"
# arcpy.env.extent = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# arcpy.env.snapRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# arcpy.env.cellSize = 25
# arcpy.env.mask = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# protectedAreaPairsFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\" +\
#                                  "IslandsOutput.gdb\\ProtectedAreaPairs"
# studyAreaRasterMask = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# percentageCorridorValuesToKeep = "4"
# numPercentageCorridorValuesToKeep = float(percentageCorridorValuesToKeep)
# permeabilityWeight = "0.6"
# corridorEnvelopeWeight = "0.2"
# lcpLengthWeight = "0.2"
# connectivityOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\connectivity"
# deleteTemps = "true"

# Process each pair of Protected Areas - first pass
arcpy.AddMessage("Started Processing Pairs of Protected Areas (pass 1) at: " + time.ctime())
impZonalStatsTempTable = "%scratchWorkspace%\\Scratch.gdb\\impzonsttbl"
stdZonalStatsTempTable = "%scratchWorkspace%\\Scratch.gdb\\stdzonsttbl"
# Determine overall min and max for use in second pass
minOverallLCPLength = 999999999999.0
maxOverallLCPLength = 0.0
minOverallImpermeability = 999999999999.0
maxOverallImpermeability = 0.0
# Remember PA pairs for use in second pass
pairList = []
with arcpy.da.SearchCursor(protectedAreaPairsFeatureClass, ["TARGET_FID", "JOIN_FID"]) as protectedAreaPairs:
    for protectedAreaPair in protectedAreaPairs:
        paIDA = str(protectedAreaPair[0])
        protectedAreaTempRasterA = "%scratchWorkspace%\\parst" + paIDA + ".tif"
        costDistanceTempRasterA = "%scratchWorkspace%\\cdrst" + paIDA + ".tif"
        paIDB = str(protectedAreaPair[1])
        costDistanceTempRasterB = "%scratchWorkspace%\\cdrst" + paIDB + ".tif"
        backlinkTempRasterB = "%scratchWorkspace%\\blrst" + paIDB + ".tif"
        corridorTempRaster = "%scratchWorkspace%\\" + "cor" + paIDA + "-" + paIDB + ".tif"
        # Calc Least Cost Path (LCP)
        lcpTempRaster = CostPath(protectedAreaTempRasterA, costDistanceTempRasterB, backlinkTempRasterB, "BEST_SINGLE",
                                 "VALUE")
        lcpTempRaster.save("%scratchWorkspace%\\lcptmprst.tif")
        lcpTempRaster = "%scratchWorkspace%\\lcptmprst.tif"
        # Estimate LCP Length as LCP Cell Count (potential to improve this) and Compare to Overall
        # Also get Path Cost
        lcpLength = 1.0
        pathCost = 1.0
        with arcpy.da.SearchCursor(lcpTempRaster, ["COUNT", "PATHCOST"]) as lcpTable:
            for lcpRow in lcpTable:
                if lcpRow[0] > lcpLength:
                    lcpLength = lcpRow[0]
                if lcpRow[1] > pathCost:
                    pathCost = lcpRow[1]
        del lcpTable, lcpRow
        if lcpLength < minOverallLCPLength:
            minOverallLCPLength = lcpLength
        if lcpLength > maxOverallLCPLength:
            maxOverallLCPLength = lcpLength
        # Calc Standardized Corridor as Corridor divided by Path Cost
        stdTempRaster = Raster(corridorTempRaster) / pathCost
        # Create Corridor Envelope by eliminating higher values from Standardized Corridor using
        # percentageCorridorValuesToKeep
        stdZonalStatsTempTable = ZonalStatisticsAsTable(studyAreaRasterMask, "Value", stdTempRaster, "DATA")
        with arcpy.da.SearchCursor(stdZonalStatsTempTable, ["MIN", "MAX"]) as stdZonalStatsRows:
            for stdZonalStatsRow in stdZonalStatsRows:
                # only one row; don't really need for loop
                cutoff = stdZonalStatsRow[0] + ((stdZonalStatsRow[1] - stdZonalStatsRow[0]) *
                                                (numPercentageCorridorValuesToKeep / 100))
                envTempRaster = Con(stdTempRaster, stdTempRaster, "", "VALUE < " + str(cutoff))
                envTempRaster.save("%scratchWorkspace%\\" + "env" + paIDA + "-" + paIDB + ".tif")
        del stdZonalStatsRows, stdZonalStatsRow
        # Extract Corridor cells only within Corridor Envelope
        creTempRaster = ExtractByMask(Raster(corridorTempRaster), envTempRaster)
        # Calc Impermeability as Extracted Corridor divided by LCP Length
        impTempRaster = creTempRaster / lcpLength
        impTempRaster.save("%scratchWorkspace%\\" + "imp" + paIDA + "-" + paIDB + ".tif")
        # Get Min and Max Impermeability and Compare to Overall
        ZonalStatisticsAsTable(studyAreaRasterMask, "Value", impTempRaster, impZonalStatsTempTable, "DATA")
        with arcpy.da.SearchCursor(impZonalStatsTempTable, ["MIN", "MAX"]) as impZonalStatsRows:
            for impZonalStatsRow in impZonalStatsRows:
                # only one row; don't really need for loop
                if impZonalStatsRow[0] < minOverallImpermeability:
                    minOverallImpermeability = impZonalStatsRow[0]
                if impZonalStatsRow[1] > maxOverallImpermeability:
                    maxOverallImpermeability = impZonalStatsRow[1]
        del impZonalStatsRows, impZonalStatsRow
        # Remember Corridor's Protected Area Pair with LCP Length
        pairList.append([paIDA, paIDB, lcpLength])
        if deleteTemps == "true":
            arcpy.Delete_management(stdZonalStatsTempTable)
            arcpy.Delete_management(impZonalStatsTempTable)
del protectedAreaPairs, protectedAreaPair
arcpy.AddMessage("Finished Processing Pairs of Protected Areas (pass 1) at: " + time.ctime())

# Process each pair of Protected Areas - second pass
arcpy.AddMessage("Started Processing Pairs of Protected Areas (pass 2) at: " + time.ctime())
# Avoid divide by 0!
impermeabilityDifference = maxOverallImpermeability - minOverallImpermeability
if impermeabilityDifference < 1:
    impermeabilityDifference = 1
lengthDifference = maxOverallLCPLength - minOverallLCPLength
if lengthDifference < 1:
    lengthDifference = 1
pairConnectivityRasterList = []
for pair in pairList:
    paIDA = pair[0]
    paIDB = pair[1]
    lcpLength = pair[2]
    # Invert/Normalize Impermeability based on overall min and max (A - permeability from the wildlife perspective is
    # desirable); cCould develop a new Generic tool or modify existing "Max Score Inverted Normalization from Raster"
    # tool to take an external parm for Max
    impTempRaster = "%scratchWorkspace%\\" + "imp" + paIDA + "-" + paIDB + ".tif"
    prxTempRaster = (maxOverallImpermeability - Raster(impTempRaster)) / impermeabilityDifference
    prmTempRaster = "%scratchWorkspace%\\" + "prm" + paIDA + "-" + paIDB + ".tif"
    arcpy.SetNoDataTo0_laitcp(prxTempRaster, prmTempRaster)
    # Invert/Normalize Corridor Envelope (B - crucial corridors between core areas need to be considered, even if they
    # have low permeability)
    envTempRaster = "%scratchWorkspace%\\" + "env" + paIDA + "-" + paIDB + ".tif"
    nenTempRaster = "%scratchWorkspace%\\" + "nen" + paIDA + "-" + paIDB + ".tif"
    arcpy.MaxScoreInvertedNormalizationFromRaster_laitcp(envTempRaster, studyAreaRasterMask, nenTempRaster)
    # Invert/Normalize LCP Length based on overall min and max (C - shorter corridors are better than longer corridors
    # of the same permeability); then make a constant raster covering Envelope from Normalized LCP Length
    nrmLCPLength = float(maxOverallLCPLength - lcpLength) / float(lengthDifference)
    nleTempRaster = Raster(envTempRaster) - Raster(envTempRaster) + nrmLCPLength
    nllTempRaster = "%scratchWorkspace%\\" + "nll" + paIDA + "-" + paIDB + ".tif"
    arcpy.SetNoDataTo0_laitcp(nleTempRaster, nllTempRaster)
    # Calc Pair Connectivity as Weighted Sum of A, B, C
    pcnTempRaster = (Raster(prmTempRaster) * float(permeabilityWeight)) +\
                    (Raster(nenTempRaster) * float(corridorEnvelopeWeight)) +\
                    (Raster(nllTempRaster) * float(lcpLengthWeight))
    pcnTempRaster.save("%scratchWorkspace%\\" + "pcn" + paIDA + "-" + paIDB + ".tif")
    # Add to raster list for use in next step
    pcnTempRaster = "%scratchWorkspace%\\" + "pcn" + paIDA + "-" + paIDB + ".tif"
    pairConnectivityRasterList.append(pcnTempRaster)
    if deleteTemps == "true":
        arcpy.Delete_management(impTempRaster)
        arcpy.Delete_management(prmTempRaster)
        arcpy.Delete_management(envTempRaster)
        arcpy.Delete_management(nenTempRaster)
        arcpy.Delete_management(nllTempRaster)
arcpy.AddMessage("Finished Processing Pairs of Protected Areas (pass 2) at: " + time.ctime())

# Calc Overall Connectivity as Max of all Pair Connectivity rasters
arcpy.AddMessage("Started Calculating Overall Connectivity at: " + time.ctime())
rasterCount = len(pairConnectivityRasterList)
if rasterCount > 0:
    # Split processing into chunks to overcome 1000 raster limit for cell stats
    chunkSize = 100.0
    iterations = int(math.ceil(rasterCount / chunkSize))
    for iteration in range(iterations):
        partialList = []
        for pairIndex in range(iteration * int(chunkSize), (iteration + 1) * int(chunkSize)):
            if pairIndex == rasterCount:
                break
            partialList.append(pairConnectivityRasterList[pairIndex])
        if iteration > 0:
            # Include result of previous iteration in this iteration
            partialList.append("%scratchWorkspace%\\pairtmprst" + str(iteration - 1) + ".tif")
        pairTempRaster = CellStatistics(partialList, "MAXIMUM")
        pairTempRaster.save("%scratchWorkspace%\\pairtmprst" + str(iteration) + ".tif")
        if deleteTemps == "true":
            arcpy.Delete_management("%scratchWorkspace%\\pairtmprst" + str(iteration - 1) + ".tif")
        connTempRaster1 = pairTempRaster
    # Because corridor rasters only kept highest X percent of values, renormalize using non-0 min and max values
    connTempRaster2 = SetNull(connTempRaster1, connTempRaster1, "VALUE = 0")
    connTempRaster3 = "%scratchWorkspace%\\contmprst3.tif"
    arcpy.ScoreRangeNormalizationFromRaster_laitcp(connTempRaster2, studyAreaRasterMask, connTempRaster3)
    arcpy.SetNoDataTo0_laitcp(connTempRaster3, connectivityOutputRaster)
    if deleteTemps == "true":
        arcpy.Delete_management(connTempRaster3)
else:
    constantRaster = CreateConstantRaster(1, "INTEGER")
    constantRaster.save(connectivityOutputRaster)
arcpy.AddMessage("Finished Calculating Overall Connectivity at: " + time.ctime())
    
# Cleanup
if deleteTemps == "true":
    arcpy.AddMessage("Started Cleanup at: " + time.ctime())
    for pair in pairList:
        paIDA = pair[0]
        paIDB = pair[1]
        pcnTempRaster = "%scratchWorkspace%\\" + "pcn" + paIDA + "-" + paIDB + ".tif"
        arcpy.Delete_management(pcnTempRaster)
        corTempRaster = "%scratchWorkspace%\\" + "cor" + paIDA + "-" + paIDB + ".tif"
        arcpy.Delete_management(corTempRaster)
    protectedAreasTempRaster = "%scratchWorkspace%\\parst.tif"
    with arcpy.da.SearchCursor(protectedAreasTempRaster, ["Value"]) as protectedAreas:
        for protectedArea in protectedAreas:
            paID = str(protectedArea[0])
            protectedAreaTempRaster = "%scratchWorkspace%\\parst" + paID + ".tif"
            arcpy.Delete_management(protectedAreaTempRaster)
            costDistanceTempRaster = "%scratchWorkspace%\\cdrst" + paID + ".tif"
            arcpy.Delete_management(costDistanceTempRaster)
            backlinkTempRaster = "%scratchWorkspace%\\blrst" + paID + ".tif"
            arcpy.Delete_management(backlinkTempRaster)
    del protectedAreas, protectedArea
    arcpy.Delete_management(protectedAreasTempRaster)
    arcpy.AddMessage("Finished Cleanup at: " + time.ctime())

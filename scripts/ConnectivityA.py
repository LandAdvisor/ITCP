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
import sys, os, arcpy
from arcpy.sa import *

# Path to custom toolbox...
scriptDir = os.path.dirname(sys.argv[0])
toolboxpath = scriptDir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
arcpy.AddToolbox(toolboxpath)

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script arguments...
compositionRaster = sys.argv[1]
roadsFeatureClass = sys.argv[2]
roadThreatMultiplier = sys.argv[3]
streamsFeatureClass = sys.argv[4]
streamBenefitFactor = sys.argv[5]
protectedAreasFeatureClass = sys.argv[6]
studyAreaRasterMask = sys.argv[7]
smallestProtectedArea = sys.argv[8]
maxProtectedAreaSeparation = sys.argv[9]
protectedAreaPairsOutputFeatureClass = sys.argv[10]
deleteTemps = sys.argv[11]

# Generate Cost Surface from Composition, Road Threat, and Stream Benefit
arcpy.AddMessage("Started Generating Cost Surface at: " + time.ctime())
# Invert Composition
costTempRaster1 = 1.0 - Raster(compositionRaster)
# Convert Roads Threat to Raster
roadsThreatTempRaster1 = "%scratchWorkspace%\\rdtht1.tif"
arcpy.FeatureToRaster_conversion(roadsFeatureClass, "ROADS_THT", roadsThreatTempRaster1)
roadsThreatTempRaster2 = "%scratchWorkspace%\\rdtht2.tif"
arcpy.SetNoDataTo0_laitcp(roadsThreatTempRaster1, roadsThreatTempRaster2)
# Convert Streams to Raster, inverting benefit to get cost
arcpy.AddField_management(streamsFeatureClass, "Cost", "FLOAT")
streamCost = 1 / float(streamBenefitFactor)
arcpy.CalculateField_management(streamsFeatureClass, "Cost", str(streamCost), "PYTHON_9.3", "")
streamsTempRaster1 = "%scratchWorkspace%\\strms1.tif"
arcpy.FeatureToRaster_conversion(streamsFeatureClass, "Cost", streamsTempRaster1)
streamsTempRaster2 = "%scratchWorkspace%\\strms2.tif"
arcpy.SetNoDataToValue_laitcp(streamsTempRaster1, streamsTempRaster2, "1")
# Add Roads and Streams to Cost Surface, assigning Roads a very high cost
costTempRaster2 = Raster(streamsTempRaster2) * (costTempRaster1 + (float(roadThreatMultiplier) *
                                                                   Raster(roadsThreatTempRaster2)))
costTempRaster2.save("%scratchWorkspace%\\costrst.tif")
arcpy.AddMessage("Finished Generating Cost Surface at: " + time.ctime())
if deleteTemps == "true":
    arcpy.Delete_management(roadsThreatTempRaster1)
    arcpy.Delete_management(roadsThreatTempRaster2)

# Exclude small Protected Areas
arcpy.AddMessage("Started Excluding Protected Areas at: " + time.ctime())
largeProtectedAreasTempFeatureClass = "%scratchWorkspace%\\Scratch.gdb\\lgpas"
arcpy.Select_analysis(protectedAreasFeatureClass, largeProtectedAreasTempFeatureClass,
                      "Shape_Area > " + smallestProtectedArea)
arcpy.AddMessage("Finished Excluding Protected Areas at: " + time.ctime())

# Convert Protected Areas to Raster
arcpy.AddMessage("Started Converting Protected Areas at: " + time.ctime())
protectedAreasTempRaster = "%scratchWorkspace%\\parst.tif"
#arcpy.FeatureToRaster_conversion(largeProtectedAreasTempFeatureClass, "ObjectID_1", protectedAreasTempRaster)
arcpy.FeatureToRaster_conversion(largeProtectedAreasTempFeatureClass, "ObjectID", protectedAreasTempRaster)
arcpy.AddMessage("Finished Converting Protected Areas at: " + time.ctime())

# Process each Protected Area
arcpy.AddMessage("Started Processing Protected Areas at: " + time.ctime())
with arcpy.da.SearchCursor(protectedAreasTempRaster, ["VALUE"]) as protectedAreas:
    for protectedArea in protectedAreas:
        # Generate separate raster
        paID = str(protectedArea[0])
        protectedAreaTempRaster = ExtractByAttributes(Raster(protectedAreasTempRaster), '"VALUE" = ' + paID)
        protectedAreaTempRaster.save("%scratchWorkspace%\\parst" + paID + ".tif")
        # Calc Cost Distance with Backlinks
        backlinkTempRaster = "%scratchWorkspace%\\blrst" + paID + ".tif"
        costDistanceTempRaster = CostDistance(protectedAreaTempRaster, costTempRaster2, "", backlinkTempRaster)
        costDistanceTempRaster.save("%scratchWorkspace%\\cdrst" + paID + ".tif")
del protectedAreas, protectedArea

arcpy.AddMessage("Finished Processing Protected Areas at: " + time.ctime())

# Determine the Distance between each pair of Protected Areas, limiting pairs to those at least as close as the
# maxProtectedAreaSeparation
arcpy.AddMessage("Started Processing Protected Area Pair Distance at: " + time.ctime())
arcpy.SpatialJoin_analysis(largeProtectedAreasTempFeatureClass, largeProtectedAreasTempFeatureClass,
                           protectedAreaPairsOutputFeatureClass, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "INTERSECT",
                           maxProtectedAreaSeparation)
arcpy.AddMessage("Finished Processing Protected Area Pair Distance at: " + time.ctime())
if deleteTemps == "true":
    arcpy.Delete_management(largeProtectedAreasTempFeatureClass)

# Process each pair of Protected Areas, deleting self pairs, duplicates, and those that have no corridor
arcpy.AddMessage("Started Processing Pairs of Protected Areas at: " + time.ctime())
corrZonalStatsTempTable = "%scratchWorkspace%\\Scratch.gdb\\corzonsttbl"
with arcpy.da.UpdateCursor(protectedAreaPairsOutputFeatureClass, ["TARGET_FID", "JOIN_FID"]) as protectedAreaPairs:
    for protectedAreaPair in protectedAreaPairs:
        # Can't make a corridor to yourself; only need to process corridors in one direction
        if protectedAreaPair[0] < protectedAreaPair[1]:
            paIDA = str(protectedAreaPair[0])
            costDistanceTempRasterA = "%scratchWorkspace%\\cdrst" + paIDA + ".tif"
            paIDB = str(protectedAreaPair[1])
            costDistanceTempRasterB = "%scratchWorkspace%\\cdrst" + paIDB + ".tif"
            # Calc Corridor
            corridorTempRaster = Corridor(costDistanceTempRasterA, costDistanceTempRasterB)
            corridorTempRaster.save("%scratchWorkspace%\\" + "cor" + paIDA + "-" + paIDB + ".tif")
            # Determine if there are any non-NoData cells in the corridor;
            # this method is not particularly intuitive, but it performs well
            corrZonalStatsTempTable = ZonalStatisticsAsTable(studyAreaRasterMask, "Value", corridorTempRaster, "DATA")
            # zonalStatsTempTable will contain 0 rows if there are only NoData cells (no corridor) and 1 row if there
            # any non-NoData cells (is a corridor)
            rowCount = 0
            with arcpy.da.SearchCursor(corrZonalStatsTempTable, ["OID@"]) as corrZonalStatsRows:
                for corrZonalStatsRow in corrZonalStatsRows:
                    rowCount = 1
                if rowCount == 0:
                    protectedAreaPairs.deleteRow()
        else:
            protectedAreaPairs.deleteRow()
del protectedAreaPairs, protectedAreaPair
arcpy.AddMessage("Finished Processing Pairs of Protected Areas at: " + time.ctime())

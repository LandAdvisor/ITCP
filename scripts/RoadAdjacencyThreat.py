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

# Path to custom toolbox...
scriptdir = os.path.dirname(sys.argv[0])
toolboxpath = scriptdir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
arcpy.AddToolbox(toolboxpath)

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script Arguments...
RoadsFeatureClass = sys.argv[1]
PropertiesFeatureClass = sys.argv[2]
AdjacencyTolerance = sys.argv[3]
RoadAdjacencyThreatOutputRaster = sys.argv[4]
RasterMaskSingleValue = sys.argv[5]

# Add field to Properties to hold road adjacency threat and default to 0
arcpy.DeleteField_management(PropertiesFeatureClass, "ROAD_ADJ_THT")
arcpy.AddField_management(PropertiesFeatureClass, "ROAD_ADJ_THT", "float")
arcpy.CalculateField_management(PropertiesFeatureClass, "ROAD_ADJ_THT", "0.0", "PYTHON_9.3", "")

# Populate list of unique road threat values from table and sort it ascending
arcpy.AddMessage("Populating list of unique Road Threat values...")
RoadThreatList = []
with arcpy.da.SearchCursor(RoadsFeatureClass, ["ROADS_THT"]) as RoadCursor:
    for RoadRow in RoadCursor:
        RoadThreatValue = RoadRow[0]
        if RoadThreatValue is not None:
            if RoadThreatValue not in RoadThreatList:
                RoadThreatList.append(RoadThreatValue)
del RoadCursor, RoadRow
RoadThreatList.sort()

# MakeFeatureLayers to facilitate selects...
arcpy.MakeFeatureLayer_management(RoadsFeatureClass, "RoadsLYR")
arcpy.MakeFeatureLayer_management(PropertiesFeatureClass, "PropertiesLYR")

# Loop through list of road threat values, selecting properties adjacent to roads and assigning the threat of those
# roads to the properties; because it is done in ascending order by road threat value, the highest road threat of all
# roads adjacent to a property will be assigned
expression = ""
count = 0
for RoadThreat in RoadThreatList:
    arcpy.AddMessage("Processing Road Threat value " + str(RoadThreat))
    
    # Select unique road class threat value...
    WhereClause = " \"ROADS_THT\" > " + str(RoadThreat - 0.000001) + " AND \"ROADS_THT\" < " + str(RoadThreat +
                                                                                                   0.000001)
    arcpy.SelectLayerByAttribute_management("RoadsLYR", "NEW_SELECTION", WhereClause)

    # Select parcel polygons adjacent to road threat line features ...
    arcpy.SelectLayerByLocation_management("PropertiesLYR", "WITHIN_A_DISTANCE", "RoadsLYR", AdjacencyTolerance +
                                                                                             " Meters", "NEW_SELECTION")

    # CalculateField to hold the current road threat value
    arcpy.CalculateField_management("PropertiesLYR", "ROAD_ADJ_THT", "\"" + str(RoadThreat) + "\"", "PYTHON_9.3", "")
    
# Convert road adjacency threat to raster
arcpy.AddMessage("Converting Road Adjacency Threat to raster and reclassifying NoData to 0")
TempRaster = "%scratchWorkspace%\\temprpt.tif"
arcpy.FeatureToRaster_conversion(PropertiesFeatureClass, "ROAD_ADJ_THT", TempRaster)

# Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
arcpy.SetNoDataTo0_laitcp(TempRaster, RoadAdjacencyThreatOutputRaster)

# Delete temp datasets
arcpy.Delete_management(TempRaster)

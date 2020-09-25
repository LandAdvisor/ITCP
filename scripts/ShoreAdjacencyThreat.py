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
ShorelineUnitsFeatureClass = sys.argv[1]
PropertiesFeatureClass = sys.argv[2]
ShoreUnitThreatTable = sys.argv[3]
AdjacencyTolerance = sys.argv[4]
ShoreAdjacencyThreatOutputRaster = sys.argv[5]
RasterMaskSingleValue = sys.argv[6]

# Add field for relative shore threat
arcpy.DeleteField_management(ShorelineUnitsFeatureClass, "SHORE_THT")
arcpy.AddField_management(ShorelineUnitsFeatureClass, "SHORE_THT", "float")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(ShorelineUnitsFeatureClass, "ShoreLYR")

# MakeTableView to facilitate joining
arcpy.MakeTableView_management(ShoreUnitThreatTable, "ShoreUnitThreatTableView")

# Join on REP_TYPE and assign threat value to the SHORE_THT field...
arcpy.AddMessage("Assigning Shore Unit Threat to Shoreline Units Feature Class...")
arcpy.AddJoin_management("ShoreLYR", "REP_TYPE", "ShoreUnitThreatTableView", "REP_TYPE", "KEEP_ALL")
arcpy.CalculateField_management("ShoreLYR", "SHORE_THT", "!ShoreUnitThreat$.THREAT!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("ShoreLYR", "ShoreUnitThreat$")

# Add field to Properties to hold shore adjacency threat and default to 0
arcpy.DeleteField_management(PropertiesFeatureClass, "SHORE_ADJ_THT")
arcpy.AddField_management(PropertiesFeatureClass, "SHORE_ADJ_THT", "float")
arcpy.CalculateField_management(PropertiesFeatureClass, "SHORE_ADJ_THT", "0.0", "PYTHON_9.3", "")

# Populate list of unique shore unit threat values from table and sort it ascending
arcpy.AddMessage("Populating list of unique Shore Unit Threat values...")
ShoreUnitThreatList = []
with arcpy.da.SearchCursor(ShorelineUnitsFeatureClass, ["SHORE_THT"]) as ShoreUnitCursor:
    for ShoreUnitRow in ShoreUnitCursor:
        ShoreUnitThreatValue = ShoreUnitRow[0]
        if ShoreUnitThreatValue is not None:
            if ShoreUnitThreatValue not in ShoreUnitThreatList:
                ShoreUnitThreatList.append(ShoreUnitThreatValue)
del ShoreUnitCursor, ShoreUnitRow
ShoreUnitThreatList.sort()

# Loop through list of shore unit threat values, selecting properties adjacent to shorelines and assigning the threat of those shorelines to the properties
# Because it is done in ascending order by shoreline threat value, the highest shore threat of all shores adjacent to a property will be assigned
expression = ""
count = 0
for ShoreUnitThreat in ShoreUnitThreatList:
    arcpy.AddMessage("Processing Shore Unit Threat value " + str(ShoreUnitThreat))
    
    # Select unique shore unit class threat value...
    WhereClause = " \"SHORE_THT\" > " + str(ShoreUnitThreat - 0.000001) + " AND \"SHORE_THT\" < " + str(ShoreUnitThreat + 0.000001) 
    arcpy.SelectLayerByAttribute_management("ShoreLYR", "NEW_SELECTION", WhereClause)

    # MakeFeatureLayer to facilitate select
    arcpy.MakeFeatureLayer_management(PropertiesFeatureClass, "PropertiesLYR")

    # Select parcel polygons adjacent to shore threat line features ...
    arcpy.SelectLayerByLocation_management("PropertiesLYR", "WITHIN_A_DISTANCE", "ShoreLYR", AdjacencyTolerance + " Meters", "NEW_SELECTION")

    # CalculateField to hold the current shore threat value
    arcpy.CalculateField_management("PropertiesLYR", "SHORE_ADJ_THT", "\"" + str(ShoreUnitThreat) + "\"", "PYTHON_9.3",
                                    "")
    
# Convert shore unit adjacency threat to raster
arcpy.AddMessage("Converting Shore Unit Adjacency Threat to raster and reclassifying NoData to 0")
TempRaster = "%scratchWorkspace%\\tempsat.tif"
arcpy.FeatureToRaster_conversion(PropertiesFeatureClass, "SHORE_ADJ_THT", TempRaster)

# Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
arcpy.SetNoDataTo0_laitcp(TempRaster, ShoreAdjacencyThreatOutputRaster)

# Delete temp datasets
arcpy.Delete_management(TempRaster)

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
scriptdir = os.path.dirname(sys.argv[0])
toolboxpath = scriptdir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
arcpy.AddToolbox(toolboxpath)

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Script Arguments...
ProtectedAreas = sys.argv[1]
ProtectedAreasAdjacencyImportanceRaster = sys.argv[2]
PropertiesRaster = sys.argv[3]
RasterMaskSingleValue = sys.argv[4]
AdjacentOutputRaster = sys.argv[5]

# Populate list of unique AdjImp values from ProtectedAreas polygons...
AdjImpList = []
with arcpy.da.SearchCursor(ProtectedAreas, ["AdjImp"]) as AdjImpCursor:
    for AdjImpRow in AdjImpCursor:
        AdjImpValue = AdjImpRow[0]
        if AdjImpValue is not None:
            if AdjImpValue not in AdjImpList:
                AdjImpList.append(AdjImpValue)
del AdjImpCursor, AdjImpRow

# For each of the unique AdjImp values extract adjacent properties...
count = 0
rasterList = []
for AdjImp in AdjImpList:
    count = count + 1
    # Get just those ProtectedAreas with the AdjImp Value...
    # kludge to work around precision issue and the v10 quirk which requires special handling for 1
    cond = ""
    if AdjImp == 1:
        cond = "Value = 1"
    else:
        cond = "Value > " + str(AdjImp - 0.000001) + " And Value < " + str(AdjImp + 0.000001)
    TempARaster = Con(ProtectedAreasAdjacencyImportanceRaster, "1", "", cond)
    #TempARaster.save("%scratchWorkspace%\\TempARaster.tif")
    # Identify adjacent properties...
    arcpy.IdentifyAdjacentProperties_laitcp(TempARaster, PropertiesRaster, "%scratchWorkspace%\\AdjImpTmpX" +
                                                                           str(count) + ".tif")
    TempBRaster = Raster("%scratchWorkspace%\\AdjImpTmpX" + str(count) + ".tif") * AdjImp
    #TempBRaster.save("%scratchWorkspace%\\TempbRaster" + str(count) + ".tif")
    rasterList.append(TempBRaster)

# Execute Map Algebra to get max of AdjImp for properties with multiple adjacent protected areas, and normalize
Temp1Raster = CellStatistics(rasterList, "MAXIMUM", "DATA")
#Temp1Raster.save("%scratchWorkspace%\\Temp1Raster.tif")
arcpy.MaxScoreNormalizationFromRaster_laitcp(Temp1Raster, RasterMaskSingleValue, AdjacentOutputRaster)

# Delete temp datasets...
count = 0
for AdjImp in AdjImpList:
    count = count + 1
    arcpy.Delete_management("%scratchWorkspace%\\AdjImpTmpX" + str(count) + ".tif")
arcpy.Delete_management(Temp1Raster)

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
import sys, string, os, arcgisscripting

# Create the Geoprocessor object...
gp = arcgisscripting.create()

# Path to custom toolbox...
scriptdir = os.path.dirname(sys.argv[0])
toolboxpath = scriptdir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
gp.AddToolbox(toolboxpath)

# Check out any necessary licenses
gp.CheckOutExtension("spatial")

# Script Arguments...
ProtectedAreas = sys.argv[1]
ProtectedAreasAdjacencyImportanceRaster = sys.argv[2]
PropertiesRaster = sys.argv[3]
RasterMaskSingleValue = sys.argv[4]
AdjacentOutputRaster = sys.argv[5]

# Populate list of unique AdjImp values from ProtectedAreas polygons...
AdjImpList = list()
AdjImpCursor = gp.searchCursor(ProtectedAreas)
AdjImpRow = AdjImpCursor.Next()
while AdjImpRow is not None:
    AdjImpValue = AdjImpRow.GetValue("AdjImp")
    if AdjImpValue is not None:
        if AdjImpValue not in AdjImpList:
            AdjImpList.append(AdjImpValue)
    AdjImpRow = AdjImpCursor.Next()
del AdjImpCursor, AdjImpRow

# For each of the unique AdjImp values extract adjacent properties...
count = 0
expression = ""
for AdjImp in AdjImpList:
    count = count + 1
    # Get just those ProtectedAreas with the AdjImp Value...
    # kludge to work around precision issue and the v10 quirk which requires special handling for 1
    cond = ""
    if AdjImp == 1:
        cond = "Value = 1"
    else:
        cond = "Value > " + str(AdjImp - 0.000001) + " And Value < " + str(AdjImp + 0.000001)
    gp.Con_sa(ProtectedAreasAdjacencyImportanceRaster, "1", "%scratchWorkspace%\\AdjImpTmp" + str(count), "", cond)
    # Identify adjacent properties...
    gp.toolbox = toolboxpath;
    gp.IdentifyAdjacentProperties("%scratchWorkspace%\\AdjImpTmp" + str(count), PropertiesRaster, "%scratchWorkspace%\\AdjImpTmpX" + str(count))
    # Build into Map Algebra expression...
    if len(expression) == 0:
        expression = "max("
    else:
        expression = expression + ", "
    expression = expression + "(%scratchWorkspace%\\AdjImpTmpX" + str(count) + " * " + str(AdjImp) + ")"
expression = expression + ")"

# Execute Map Algebra to total AdjImp for properties with multiple adjacent protected areas, and normalize
Temp1Raster = "%scratchWorkspace%\\TempRst221"
gp.SingleOutputMapAlgebra_sa(expression, Temp1Raster)
Temp2Raster = "%scratchWorkspace%\\TempRst222"
gp.toolbox = toolboxpath;
gp.MaxScoreNormalizationFromRaster(Temp1Raster, RasterMaskSingleValue, AdjacentOutputRaster)
#reclassify is now included in normalization tools
##gp.NormalizeLinearFromRaster(Temp1Raster, RasterMaskSingleValue, Temp2Raster)
##
### Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
##gp.Reclassify_sa(Temp2Raster, "Value", "NoData 0", AdjacentOutputRaster, "DATA")

# Delete temp datasets...
count = 0
for AdjImp in AdjImpList:
    count = count + 1
    gp.Delete_management("%scratchWorkspace%\\AdjImpTmp" + str(count))
    gp.Delete_management("%scratchWorkspace%\\AdjImpTmpX" + str(count))
gp.Delete_management(Temp1Raster)
##gp.Delete_management(Temp2Raster)

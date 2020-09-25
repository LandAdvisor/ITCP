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
ZoningFeatureClass = sys.argv[1]
PropertiesFeatureClass = sys.argv[2]
MinLotSizeTable = sys.argv[3]
SubPotThreatOutputRaster = sys.argv[4]

#  Intersect Zoning and Property Boundaries
arcpy.AddMessage("Intersecting property boundaries and zoning...")
TempCadZoneInt = "%scratchWorkspace%\Scratch.gdb\TempCadZoneInt"
arcpy.Intersect_analysis(PropertiesFeatureClass +  " #; " + ZoningFeatureClass + " #", TempCadZoneInt, "ALL", "",
                         "INPUT")

#  Add field for subdivision potential, minimum lot size and island zone
arcpy.AddField_management(TempCadZoneInt, "ISL_ZONE", "text")
arcpy.AddField_management(TempCadZoneInt, "MIN_LOT", "float")
arcpy.AddField_management(TempCadZoneInt, "SUB_POT", "float")

#  Calculate join field based on the zoning area and zone code
arcpy.CalculateField_management(TempCadZoneInt, "ISL_ZONE", "!ZONING_AREA! + !ZONE_CODE!", "PYTHON_9.3", "")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TempCadZoneInt, "CAD_ZONE_INT_LYR")

# Join on ISLAND_ZONE to determine a minimum lot size to assign to the SUB_POT field...
arcpy.AddJoin_management("CAD_ZONE_INT_LYR", "ISL_ZONE", MinLotSizeTable, "ISLAND_ZONE", "KEEP_ALL")
arcpy.CalculateField_management("CAD_ZONE_INT_LYR", "MIN_LOT", "!MinimumLotSizes$.MIN_LOT_SIZE!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("CAD_ZONE_INT_LYR", "MinimumLotSizes$")

# For each record calculate subdivision potential
arcpy.AddMessage("Calculating subdivision potential threat...")
with arcpy.da.UpdateCursor(TempCadZoneInt, ["MIN_LOT", "SHAPE@AREA", "SUB_POT"]) as OutputCursor:
    for OutputRow in OutputCursor:
        MinLot = OutputRow[0]
        ShapeArea = OutputRow[1]
        if MinLot is not None:
            if MinLot > 0:
                if ((ShapeArea * 0.0001) / MinLot) < 2:
                    OutputRow[2] = 0
                else:
                    OutputRow[2] = ((ShapeArea * 0.0001) / MinLot) - 1
        OutputCursor.updateRow(OutputRow)
del OutputCursor, OutputRow
            
# Create normalized subdivision potential raster...
arcpy.AddMessage("Normalizing output subdivision potential threat raster dataset...")
arcpy.MaxScoreNormalizationFromPolygon_laitcp(TempCadZoneInt, "SUB_POT", SubPotThreatOutputRaster)

# Delete temps
arcpy.Delete_management(TempCadZoneInt)

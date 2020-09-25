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
import sys
from arcpy.sa import *

# Function that returns the currently threatened percent for the habitat/landscape class
# This is a spatial calculation using the following algorithm:
# SumAcrossAllCells(PercentCover * Threat) / SumAcrossAllCells(PercentCover)
def PercentThreatened(ThreatRaster, MapClass, RasterMaskSingleValue):
    NumTable = "%scratchWorkspace%\\numtblht"
    DenTable = "%scratchWorkspace%\\dentblht"
    # Create raster to calculate numerator from...
    MapClassRaster = Raster("%workspace%\\" + MapClass + ".tif")
    ThreatRaster = Raster(ThreatRaster)
    TempRaster =  MapClassRaster * ThreatRaster
    # Calculate numerator...
    ZonalStatisticsAsTable(RasterMaskSingleValue, "Value", TempRaster, NumTable)
    with arcpy.da.SearchCursor(NumTable, ["SUM"]) as NumTableCursor:
        for NumTableRow in NumTableCursor:
            Numerator = NumTableRow[0]
    del NumTableCursor, NumTableRow
    # Calculate denominator
    ZonalStatisticsAsTable(RasterMaskSingleValue, "Value", "%workspace%\\" + MapClass + ".tif", DenTable)
    with arcpy.da.SearchCursor(DenTable, ["SUM"]) as DenTableCursor:
        for DenTableRow in DenTableCursor:
            Denominator = DenTableRow[0]
    del DenTableCursor, DenTableRow
    if Denominator == 0:
        Denominator = 1
    # Delete temp datasets...
    arcpy.Delete_management(TempRaster)
    arcpy.Delete_management(NumTable)
    arcpy.Delete_management(DenTable)
    # Return...
    return Numerator / Denominator

# Main script
# Script arguments...
ThreatRaster = sys.argv[1]
MapClassesTable = sys.argv[2]
RasterMaskSingleValue = sys.argv[3]
OutputRaster = sys.argv[4]

# Populate list of unique MapClasses from table...
MapClassList = []
with arcpy.da.SearchCursor(MapClassesTable, ["MapClass"]) as MapClassCursor:
    for MapClassRow in MapClassCursor:
        MapClassValue = MapClassRow[0]
        if MapClassValue is not None:
            if MapClassValue not in MapClassList:
                MapClassList.append(MapClassValue)
del MapClassCursor, MapClassRow

# Iterate MapClasses, building map algebra expression to perform weighted sum of habitat layers using this algorithm:
# % cover of habitat A (0-1) in that cell * relative threat to habitat A
# plus
# % cover of habitat B (0-1) in that cell * relative threat to habitat B
# plus
# ...
RasterList = []
for MapClass in MapClassList:
    # check for raster for this MapClass...
    if arcpy.Exists("%workspace%\\" + MapClass + ".tif"):
        # Calculate relative Marginal Value of protecting the next unit of this habitat...
        PercThreat = PercentThreatened(ThreatRaster, MapClass, RasterMaskSingleValue)
        # Calc intermediate and add to list of rasters...
        MapClassRaster = Raster("%workspace%\\" + MapClass + ".tif")
        InterRaster = MapClassRaster * PercThreat
        RasterList.append(InterRaster)

# Execute map algebra to combine layers...
CellStatsRaster = CellStatistics(RasterList, "SUM", "NODATA")
CellStatsRaster.save(OutputRaster)

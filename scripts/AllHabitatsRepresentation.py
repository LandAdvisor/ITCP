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
import sys, arcpy
from arcpy.sa import *

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Function that returns the currently protected percent for the habitat/landscape class
# This is a spatial calculation using the following algorithm:
# SumAcrossAllCells(PercentCover * ProtectedAreaQualityIndex) / SumAcrossAllCells(PercentCover)
def PercentProtected(ProtectedAreaImportanceRaster, NaturalnessRaster, MapClass, RasterMaskSingleValue):
    NumTable = "%scratchWorkspace%\\numtbl20211"
    DenTable = "%scratchWorkspace%\\dentbl20211"
    # Create raster to calculate numerator from...
    MapClassRaster = Raster("%workspace%\\" + MapClass + ".tif")
    ProtectedAreaImportanceRaster = Raster(ProtectedAreaImportanceRaster)
    NaturalnessRaster = Raster(NaturalnessRaster)
    TempRaster =  MapClassRaster * ProtectedAreaImportanceRaster * NaturalnessRaster
    # Calculate numerator...
    ZonalStatisticsAsTable(RasterMaskSingleValue, "Value", TempRaster, NumTable)
    with arcpy.da.SearchCursor(NumTable, "SUM") as NumTableCursor:
        for NumTableRow in NumTableCursor:
            Numerator = NumTableRow[0]
    del NumTableCursor, NumTableRow
    # Calculate denominator
    ZonalStatisticsAsTable(RasterMaskSingleValue, "Value", "%workspace%\\" + MapClass + ".tif", DenTable)
    with arcpy.da.SearchCursor(DenTable, "SUM") as DenTableCursor:
        for DenTableRow in DenTableCursor:
            Denominator = DenTableRow[0]
    del DenTableCursor, DenTableRow
    if Denominator == 0:
        Denominator = 1
    # Delete temp datasets...
    arcpy.Delete_management(NumTable)
    arcpy.Delete_management(DenTable)
    # Return...
    return Numerator / Denominator

# Functions used by MarginalValue
def a(r, s):
    return (1 - s) * (1 - r) + s

def i(r, t, q, f, a):
    return a - t * math.tan(3.14 / 2 - math.atan((1 - q + f - r) / a))

def v(a, i):
    return i + ((a - i) * 0)

# Function that returns the relative Marginal Value of protecting the next unit of a habitat/landscape class
# This is called w in "Calibrating the Continuous Benefit Functions-Habitats.xlsx" and in the ModelBuilder tool 4002-estimated-habitat-value
def MarginalValue(p, r, t, q, o, s, f, u):
    a1 = a(r, s)
    i1 = i(r, t, q, f, a1)
    v1 = v(a1, i1)
    if t < q:
        if p < q:
            return a1
        else:
            return u * v1 - (p - q) * math.tan(3.14 / 2 - math.atan((1 - q + f - r) / (v1 * u)))
    else:
        if p < q:
            return a1
        else:
            if p < t:
                return a1 - (p - q) * math.tan (3.14 / 2 - math.atan((t - q) / (a1 - v1)))
            else:
                return v1 * (1 - u) - (p - t) * math.tan(3.14 / 2 - math.atan((1 - t + f - r) / (v1 * (1 - u))))

# Main script
# Script arguments...
ProtectedAreaImportanceRaster = sys.argv[1]
NaturalnessRaster = sys.argv[2]
MapClassesTable = sys.argv[3]
RasterMaskSingleValue = sys.argv[4]
r = sys.argv[5]
t = sys.argv[6]
q = sys.argv[7]
o = sys.argv[8]
s = sys.argv[9]
f = sys.argv[10]
u = sys.argv[11]
OutputRaster = sys.argv[12]

# Populate list of unique MapClasses from table...
MapClassList = list()
with arcpy.da.SearchCursor(MapClassesTable, ["MapClass"]) as MapClassCursor:
    for MapClassRow in MapClassCursor:
        MapClassValue = MapClassRow[0]
        if MapClassValue is not None:
            if MapClassValue not in MapClassList:
                MapClassList.append(MapClassValue)
del MapClassCursor, MapClassRow

# Iterate MapClasses, building map algebra expression to perform weighted sum of habitat layers using this algorithm:
# % cover of habitat A (0-1) in that cell * relative value of protecting next unit of habitat A
# plus
# % cover of habitat B (0-1) in that cell * relative value of protecting next unit of habitat B
# plus
# ...
RasterList = []
for MapClass in MapClassList:
    # check for raster for this MapClass...
    if arcpy.Exists("%workspace%\\" + MapClass + ".tif"):
        # Calculate relative Marginal Value of protecting the next unit of this habitat...
        MargVal = MarginalValue(PercentProtected(ProtectedAreaImportanceRaster, NaturalnessRaster, MapClass,
                                                 RasterMaskSingleValue),
                                float(r), float(t), float(q), float(o), float(s), float(f), float(u))
        # Calculate intermediate raster and add to raster list
        MapClassRaster = Raster("%workspace%\\" + MapClass + ".tif")
        InterRaster = MapClassRaster * MargVal
        RasterList.append(InterRaster)

# Sum intermediate rasters...
CellStatsTempRaster = CellStatistics(RasterList, "SUM", "NODATA")
CellStatsTempRaster.save(OutputRaster)

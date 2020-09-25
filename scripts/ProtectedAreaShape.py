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

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script arguments...
ProtectedAreas = sys.argv[1]
RasterMaskSingleValue = sys.argv[2]
ProtectedAreaSizeNewMin = sys.argv[3]
ProtectedAreaSizeOutputRaster = sys.argv[4]
ProtectedAreaSizeWeight = sys.argv[5]
ProtectedAreaRatioOutputRaster = sys.argv[6]
ProtectedAreaRatioWeight = sys.argv[7]
ProtectedAreaShapeOutputRaster = sys.argv[8]

# Create normalized size raster...
arcpy.ScoreRangeNormalizationFromPolygon_laitcp(ProtectedAreas, "SHAPE_Area", ProtectedAreaSizeNewMin, 1,
                                                ProtectedAreaSizeOutputRaster)

# Add and calculate field for ratio...
arcpy.AddField_management(ProtectedAreas, "SIZE_RATIO", "FLOAT")
arcpy.CalculateField_management(ProtectedAreas, "SIZE_RATIO", "!SHAPE_Area! / !SHAPE_Length!", "PYTHON_9.3", "")

# Create normalized ratio raster...
arcpy.MaxScoreNormalizationFromPolygon_laitcp(ProtectedAreas, "SIZE_RATIO", ProtectedAreaRatioOutputRaster)

# Create normalized shape raster as weighted sum...
ws = WeightedSum(WSTable([[ProtectedAreaSizeOutputRaster, "Value", float(ProtectedAreaSizeWeight)],
                          [ProtectedAreaRatioOutputRaster, "Value", float(ProtectedAreaRatioWeight)]]))
ws.save("%scratchWorkspace%\\wstemp.tif")
ws = "%scratchWorkspace%\\wstemp.tif"
arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, ProtectedAreaShapeOutputRaster)

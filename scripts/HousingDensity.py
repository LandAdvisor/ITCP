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

# Import system modules
import sys, os, arcpy
from arcpy.sa import *

# Path to custom toolbox...
scriptdir = os.path.dirname(sys.argv[0])
toolboxpath = scriptdir + "\\..\\toolbox\\LandAdvisor-ITCP.tbx"
arcpy.AddToolbox(toolboxpath)

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Script arguments...
PropertiesFeatureClass = sys.argv[1]
HousingDensityOutputRaster = sys.argv[2]
RasterMaskSingleValue = sys.argv[3]
TempPropertiesWithImprovementsFeatureClass = "%scratchWorkspace%\\Scratch.gdb\\tempprimpfc"
TempCentroidFeatureClass = "%scratchWorkspace%\\Scratch.gdb\\tempcentfc"
#TempHousingDensityRaster = "%scratchWorkspace%\\temprsthd.tif"

#try:
# Convert polygons with improvements to points...
arcpy.Select_analysis(PropertiesFeatureClass, TempPropertiesWithImprovementsFeatureClass, "\"IMPROVVAL\" > 0")
arcpy.FeatureToPoint_management(TempPropertiesWithImprovementsFeatureClass, TempCentroidFeatureClass, "INSIDE")

# Calculate the point density of the improved properties...
#arcpy.PointDensity_sa(TempCentroidFeatureClass, "NONE", TempHousingDensityRaster, "25", "Circle 195 MAP", "HECTARES")
temp_hous_dens = PointDensity(TempCentroidFeatureClass, "NONE", "25", "Circle 195 MAP", "HECTARES")

# Normalize...
#arcpy.MaxScoreNormalizationFromRaster_laitcp(TempHousingDensityRaster, RasterMaskSingleValue, HousingDensityOutputRaster)
arcpy.MaxScoreNormalizationFromRaster_laitcp(temp_hous_dens, RasterMaskSingleValue, HousingDensityOutputRaster)
# except:
    # # Assume tool not licensed
    # arcpy.MaxScoreNormalizationFromRaster_laitcp(RasterMaskSingleValue, RasterMaskSingleValue, HousingDensityOutputRaster)

# Delete temp datasets...
arcpy.Delete_management(TempPropertiesWithImprovementsFeatureClass)
arcpy.Delete_management(TempCentroidFeatureClass)
#arcpy.Delete_management(TempHousingDensityRaster)

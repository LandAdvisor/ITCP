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
InputPolygonFeatureClass = sys.argv[1]
FieldToNormalize = sys.argv[2]
OutputRaster = sys.argv[3]
TempRaster = "%scratchWorkspace%\\temprst1014.tif"

# Add field to hold normalized value...
arcpy.AddField_management(InputPolygonFeatureClass, "norm", "float")

# Determine max in field...
Max = 0.0
with arcpy.da.SearchCursor(InputPolygonFeatureClass, [FieldToNormalize]) as FeatureClassCursor:
    for FeatureClassRow in FeatureClassCursor:
        FieldValue = FeatureClassRow[0]
        if FieldValue is not None:
            if FieldValue > Max:
                Max = FieldValue
del FeatureClassCursor, FeatureClassRow

# Calculate normalized value for each row...
arcpy.CalculateField_management(InputPolygonFeatureClass, "norm", "!" + str(FieldToNormalize) + "! / " + str(Max),
                                "PYTHON_9.3", "")

# Export to raster...
arcpy.FeatureToRaster_conversion(InputPolygonFeatureClass, "norm", TempRaster)

# Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)
arcpy.SetNoDataTo0_laitcp(TempRaster, OutputRaster)

# Delete temp raster...
arcpy.Delete_management(TempRaster)

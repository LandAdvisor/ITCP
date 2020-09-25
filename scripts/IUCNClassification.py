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
ProtectedAreasFeatureClass = sys.argv[1]
IUCNImportanceTable = sys.argv[2]
IUCNClassificationOutputRaster = sys.argv[3]

# Add and calculate field
arcpy.AddField_management(ProtectedAreasFeatureClass, "IUCN_IMP", "float")
arcpy.MakeFeatureLayer_management(ProtectedAreasFeatureClass, "PROTECTED_AREAS_LYR")
arcpy.AddJoin_management("PROTECTED_AREAS_LYR", "IUCN_DES", IUCNImportanceTable, "IUCNDesignation", "KEEP_ALL")
arcpy.CalculateField_management("PROTECTED_AREAS_LYR", "IUCN_IMP", "!IUCNImportance$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("PROTECTED_AREAS_LYR", "IUCNImportance$")

# Convert to rastert and set NoData to 0
TempRaster = "%scratchWorkspace%\\temprst0021.tif"
arcpy.FeatureToRaster_conversion(ProtectedAreasFeatureClass, "IUCN_IMP", TempRaster)
arcpy.SetNoDataTo0_laitcp(TempRaster, IUCNClassificationOutputRaster)

# Delete temp datasets...
arcpy.Delete_management(TempRaster)

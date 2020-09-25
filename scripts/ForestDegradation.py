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

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Script Arguments...
TEMFeatureClass = sys.argv[1]
ForestStandDegradationTable = sys.argv[2]
ForestDegradationOutputRaster = sys.argv[3]

#  Add required fields and indexes
arcpy.AddMessage("Adding required fields and indexes...")
# Delete fields if they previously existed
arcpy.DeleteField_management(TEMFeatureClass, "STRCT1")
arcpy.DeleteField_management(TEMFeatureClass, "STRCT2")
arcpy.DeleteField_management(TEMFeatureClass, "STRCT3")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec1")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec2")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec3")
arcpy.DeleteField_management(TEMFeatureClass, "TotalDist")

# Adding Structural Stage fields to create a common field type
arcpy.AddField_management(TEMFeatureClass, "STRCT1", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "STRCT2", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "STRCT3", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "DistDec1", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "DistDec2", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "DistDec3", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "TotalDist", "DOUBLE")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TEMFeatureClass, "TEM_SEM_LYR")

# Calculate structural stage attributes to double field
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "NEW_SELECTION",
                                        "\"STRCT_S1\" = 0 and \"DISTCLS_1\" = 'L' or \"STRCT_S1\" = 1 and \"DISTCLS_1\""
                                        "= 'L' or \"STRCT_S1\" = 2 and \"DISTCLS_1\" = 'L' or \"STRCT_S1\" = 3 and \""
                                        "DISTCLS_1\" = 'L' or \"STRCT_S1\" in (4,5,6,7)")
arcpy.CalculateField_management("TEM_SEM_LYR", "STRCT1", "!STRCT_S1!", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "NEW_SELECTION",
                                        "\"STRCT_S2\" = '0' and \"DISTCLS_2\" = 'L' or \"STRCT_S2\" = '1' and \"DISTCLS_2\""
                                        "= 'L' or \"STRCT_S2\" = '2' and \"DISTCLS_2\" = 'L' or \"STRCT_S2\" = '3' and \""
                                        "DISTCLS_2\" = 'L' or \"STRCT_S2\" in ('4','5','6','7')")
arcpy.CalculateField_management("TEM_SEM_LYR", "STRCT2", "!STRCT_S2!", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "NEW_SELECTION",
                                        "\"STRCT_S3\" = '0' and \"DISTCLS_3\" = 'L' or \"STRCT_S3\" = '1' and \"DISTCLS_3\""
                                        "= 'L' or \"STRCT_S3\" = '2' and \"DISTCLS_3\" = 'L' or \"STRCT_S3\" = '3' and \""
                                        "DISTCLS_3\" = 'L' or \"STRCT_S3\"  in ('4','5','6','7')")
arcpy.CalculateField_management("TEM_SEM_LYR", "STRCT3", "!STRCT_S3!", "PYTHON_9.3", "")

# For each record calculate Forest Stand Degradation
arcpy.AddMessage("Calculating forest stand degradation...")
arcpy.AddJoin_management("TEM_SEM_LYR", "STRCT1", ForestStandDegradationTable, "STRCT", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "DistDec1", "!StructuralStage$.DEGRADATION! * (!TEM_SEM.DEC1! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "StructuralStage$")
arcpy.AddJoin_management("TEM_SEM_LYR", "STRCT2", ForestStandDegradationTable, "STRCT", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "DistDec2", "!StructuralStage$.DEGRADATION! * (!TEM_SEM.DEC2! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "StructuralStage$")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "NEW_SELECTION", "DistDec2 IS Null")
arcpy.CalculateField_management("TEM_SEM_LYR", "DistDec2", "0", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "CLEAR_SELECTION", "")
arcpy.AddJoin_management("TEM_SEM_LYR", "STRCT3", ForestStandDegradationTable, "STRCT", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "DistDec3", "!StructuralStage$.DEGRADATION! * (!TEM_SEM.DEC3! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "StructuralStage$")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "NEW_SELECTION", "DistDec3 IS Null")
arcpy.CalculateField_management("TEM_SEM_LYR", "DistDec3", "0", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_SEM_LYR", "CLEAR_SELECTION", "")
arcpy.CalculateField_management("TEM_SEM_LYR", "TotalDist", "!DistDec1! + !DistDec2! + !DistDec3!", "PYTHON_9.3", "")

# Create normalized subdivision potential raster...
arcpy.AddMessage("Normalizing output Forest Stand Degradation raster dataset...")
arcpy.MaxScoreNormalizationFromPolygon_laitcp(TEMFeatureClass, "TotalDist", ForestDegradationOutputRaster)

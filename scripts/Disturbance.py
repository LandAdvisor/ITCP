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
TEMFeatureClass = sys.argv[1]
TEMDisturbanceTable = sys.argv[2]
ITEMFeatureClass = sys.argv[3]
ITEMDisturbanceTable = sys.argv[4]
DisturbanceOutputRaster = sys.argv[5]

# Temp rasters...
TempTEMDisturbanceRaster = "%scratchWorkspace%\\temptemnor.tif"
TempITEMDisturbanceRaster = "%scratchWorkspace%\\tempitemnor.tif"

#  Add required fields
arcpy.AddMessage("Adding required TEM fields and indexes...")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec1")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec2")
arcpy.DeleteField_management(TEMFeatureClass, "DistDec3")
arcpy.DeleteField_management(TEMFeatureClass, "TotalDist")
arcpy.AddField_management(TEMFeatureClass, "DistDec1", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "DistDec2", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "DistDec3", "DOUBLE")
arcpy.AddField_management(TEMFeatureClass, "TotalDist", "DOUBLE")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TEMFeatureClass, "TEM_LYR")

# For each record calculate TEM Disturbance
arcpy.AddMessage("Calculating TEM disturbance...")
arcpy.AddJoin_management("TEM_LYR", "SITEMC_S1", TEMDisturbanceTable, "DIST_CLASS", "KEEP_ALL")
arcpy.CalculateField_management("TEM_LYR", "DistDec1", "!TEMDisturbance$.DISTURBANCE! * (!TEM_SEM.DEC1! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_LYR", "TEMDisturbance$")
arcpy.AddJoin_management("TEM_LYR", "SITEMC_S2", TEMDisturbanceTable, "DIST_CLASS", "KEEP_ALL")
arcpy.CalculateField_management("TEM_LYR", "DistDec2", "!TEMDisturbance$.DISTURBANCE! * (!TEM_SEM.DEC2! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_LYR", "TEMDisturbance$")
arcpy.SelectLayerByAttribute_management("TEM_LYR", "NEW_SELECTION", "DistDec2 IS Null")
arcpy.CalculateField_management("TEM_LYR", "DistDec2", "0", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_LYR", "CLEAR_SELECTION", "")
arcpy.AddJoin_management("TEM_LYR", "SITEMC_S3", TEMDisturbanceTable, "DIST_CLASS", "KEEP_ALL")
arcpy.CalculateField_management("TEM_LYR", "DistDec3", "!TEMDisturbance$.DISTURBANCE! * (!TEM_SEM.DEC3! / 100)",
                                "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_LYR", "TEMDisturbance$")
arcpy.SelectLayerByAttribute_management("TEM_LYR", "NEW_SELECTION", "DistDec3 IS Null")
arcpy.CalculateField_management("TEM_LYR", "DistDec3", "0", "PYTHON_9.3", "")
arcpy.SelectLayerByAttribute_management("TEM_LYR", "CLEAR_SELECTION", "")
arcpy.CalculateField_management("TEM_LYR", "TotalDist", "!DistDec1! + !DistDec2! + !DistDec3!", "PYTHON_9.3", "")

# Create normalized subdivision potential raster...
arcpy.AddMessage("Normalizing temporary TEM disturbance raster dataset...")
arcpy.MaxScoreNormalizationFromPolygon_laitcp(TEMFeatureClass, "TotalDist", TempTEMDisturbanceRaster)

#  Add required fields
arcpy.AddMessage("Adding required ITEM fields and indexes...")
# Delete fields if the previously existed, otherwise AddIndex will fail...
arcpy.DeleteField_management(ITEMFeatureClass, "DIST_CLASS")
arcpy.DeleteField_management(ITEMFeatureClass, "DIST_IMP")
# Add fields for MapCode to MapClass reclassification...
arcpy.AddField_management(ITEMFeatureClass, "DIST_CLASS", "TEXT")
arcpy.AddField_management(ITEMFeatureClass, "DIST_IMP", "FLOAT")

# Calculate disturbance class from class and subclass fields...
arcpy.CalculateField_management(ITEMFeatureClass, "DIST_CLASS", "!CLASS! + !SUBCLASS!", "PYTHON_9.3", "")

# Index to speed joins...
arcpy.AddIndex_management(ITEMFeatureClass, "DIST_CLASS", "DC1Idx")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(ITEMFeatureClass, "ITEM_LYR")

# Calculate disturbance values...
arcpy.AddMessage("Calculating ITEM disturbance values...")
arcpy.AddJoin_management("ITEM_LYR", "DIST_CLASS", ITEMDisturbanceTable, "DIST_CLASS", "KEEP_ALL")
arcpy.CalculateField_management("ITEM_LYR", "DIST_IMP", "!ITEMDisturbance$.DISTURBANCE!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("ITEM_LYR", "ITEMDisturbance$")

# Create normalized ITEM Disturbance raster...
arcpy.AddMessage("Normalizing temporary ITEM disturbance raster dataset...")
arcpy.MaxScoreNormalizationFromPolygon_laitcp(ITEMFeatureClass, "DIST_IMP", TempITEMDisturbanceRaster)

# Combine into single disturbance raster...
arcpy.AddMessage("Calculating output disturbance raster...")
TempTEMDisturbanceRaster = Raster(TempTEMDisturbanceRaster)
TempITEMDisturbanceRaster = Raster(TempITEMDisturbanceRaster)
DisturbanceTempRaster = Con(TempTEMDisturbanceRaster == 0, TempITEMDisturbanceRaster, TempTEMDisturbanceRaster)
DisturbanceTempRaster.save(DisturbanceOutputRaster)

# Delete temps
arcpy.Delete_management(TempTEMDisturbanceRaster)
arcpy.Delete_management(TempITEMDisturbanceRaster)

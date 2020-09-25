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

# Script Arguments...
ZoneFeatureClass = sys.argv[1]
ZoneField = sys.argv[2]
ZoneRaster = sys.argv[3]
StatsRaster = sys.argv[4]
IncludeCount = sys.argv[5]
IncludeArea = sys.argv[6]
IncludeMin = sys.argv[7]
IncludeMax = sys.argv[8]
IncludeRange = sys.argv[9]
IncludeMean = sys.argv[10]
IncludeStd = sys.argv[11]
IncludeSum = sys.argv[12]
FieldPrefix = sys.argv[13]
StatsTable = "%scratchWorkspace%\\temptablegzs"

# Add a column/field for each statistic
if IncludeCount == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Count", "LONG")
if IncludeArea == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Area", "FLOAT")
if IncludeMin == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Min", "FLOAT")
if IncludeMax == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Max", "FLOAT")
if IncludeRange == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Range", "FLOAT")
if IncludeMean == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Mean", "FLOAT")
if IncludeStd == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Std", "FLOAT")
if IncludeSum == "true":
    arcpy.AddField_management(ZoneFeatureClass, FieldPrefix + "Sum", "FLOAT")

# Calculate zonal stats into new table
if ZoneRaster == "#":
    ZonalStatisticsAsTable(ZoneFeatureClass, ZoneField, StatsRaster, StatsTable)
else:
    ZonalStatisticsAsTable(ZoneRaster, "VALUE", StatsRaster, StatsTable)

# Make feature layer to facilitate joining
arcpy.MakeFeatureLayer_management(ZoneFeatureClass, "ZoneLayer")

# Make table view to facilitate joining
arcpy.MakeTableView_management(StatsTable, "StatsTableView")

# Join table back to feature class
if ZoneRaster == "#":
    arcpy.AddJoin_management("ZoneLayer", ZoneField, "StatsTableView", ZoneField, "KEEP_ALL")
else:
    arcpy.AddJoin_management("ZoneLayer", ZoneField, "StatsTableView", "VALUE", "KEEP_ALL")

# Calculate column/field for each statistic
if IncludeCount == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Count", "!temptablegzs:COUNT!", "PYTHON_9.3", "")
if IncludeArea == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Area", "!temptablegzs:AREA!", "PYTHON_9.3", "")
if IncludeMin == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Min", "!temptablegzs:MIN!", "PYTHON_9.3", "")
if IncludeMax == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Max", "!temptablegzs:MAX!", "PYTHON_9.3", "")
if IncludeRange == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Range", "!temptablegzs:RANGE!", "PYTHON_9.3", "")
if IncludeMean == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Mean", "!temptablegzs:MEAN!", "PYTHON_9.3", "")
if IncludeStd == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Std", "!temptablegzs:STD!", "PYTHON_9.3", "")
if IncludeSum == "true":
    arcpy.CalculateField_management("ZoneLayer", FieldPrefix + "Sum", "!temptablegzs:SUM!", "PYTHON_9.3", "")

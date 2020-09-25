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

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script Arguments...
RoadsFeatureClass = sys.argv[1]
RoadsThreatTable = sys.argv[2]

# Add field for relative road threat
lstFields = arcpy.ListFields(RoadsFeatureClass)
if "ROADS_THT" in lstFields:
  arcpy.DeleteField_management(RoadsFeatureClass, "ROADS_THT")
else:
  arcpy.AddField_management(RoadsFeatureClass, "ROADS_THT", "float")
arcpy.AddField_management(RoadsFeatureClass, "ROADS_THT", "float")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(RoadsFeatureClass, "RoadsLYR")

# MakeTableView to facilitate joining
arcpy.MakeTableView_management(RoadsThreatTable, "RoadsThreatTableView")

# Join on RD_CLASS and assign threat value to the ROADS_THT field...
arcpy.AddMessage("Assigning Roads Threat to Roads Feature Class...")
arcpy.AddJoin_management("RoadsLYR", "TRANSPORT_LINE_TYPE_DESCRIPTION", "RoadsThreatTableView", "RD_CLASS", "KEEP_ALL")
arcpy.CalculateField_management("RoadsLYR", "ROADS_THT", "!RoadsThreat$.THREAT!", "PYTHON_9.3", "")
# arcpy.SelectLayerByAttribute_management("RoadsLYR", "NEW_SELECTION", "RD_SURFACE = 'rough'")
# arcpy.CalculateField_management("RoadsLYR", "ROADS_THT", "0", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("RoadsLYR", "RoadsThreat$")

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
PropertiesFeatureClass = sys.argv[1]
PropertyValuesTable = sys.argv[2]
ActualValuesTable = sys.argv[3]

# Add fields for values...
arcpy.DeleteField_management(PropertiesFeatureClass, "LANDVAL")
arcpy.DeleteField_management(PropertiesFeatureClass, "IMPROVVAL")
arcpy.DeleteField_management(PropertiesFeatureClass, "TOTALVAL")
arcpy.DeleteField_management(PropertiesFeatureClass, "ACTUALVAL")
arcpy.AddField_management(PropertiesFeatureClass, "LANDVAL", "float")
arcpy.AddField_management(PropertiesFeatureClass, "IMPROVVAL", "float")
arcpy.AddField_management(PropertiesFeatureClass, "TOTALVAL", "float")
arcpy.AddField_management(PropertiesFeatureClass, "ACTUALVAL", "float")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(PropertiesFeatureClass, "PropLYR")

# MakeTableView to facilitate joining
arcpy.MakeTableView_management(PropertyValuesTable, "ValuesTableView")

# Join and assign values...
arcpy.AddMessage("Assigning Values to Properties Feature Class...")
arcpy.AddJoin_management("PropLYR", "PID", "ValuesTableView", "pid", "KEEP_ALL")
arcpy.CalculateField_management("PropLYR", "LANDVAL", "!PropValue$.LandValue!", "PYTHON_9.3", "")
arcpy.CalculateField_management("PropLYR", "IMPROVVAL", "!PropValue$.ImprovValue!", "PYTHON_9.3", "")
arcpy.CalculateField_management("PropLYR", "TOTALVAL", "!PropValue$.TotalValue!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("PropLYR", "PropValue$")

# MakeTableView to facilitate joining
arcpy.MakeTableView_management(ActualValuesTable, "ActualValuesTableView")

# Join and assign values...
arcpy.AddMessage("Assigning Actual Values to Properties Feature Class...")
arcpy.AddJoin_management("PropLYR", "PID", "ActualValuesTableView", "PID", "KEEP_ALL")
arcpy.CalculateField_management("PropLYR", "ACTUALVAL", "!ACTUAL_VALUE$.ACTUAL_VALUE!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("PropLYR", "ACTUAL_VALUE$")

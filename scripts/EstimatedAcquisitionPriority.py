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

# Script arguments...
ScenarioOutputFeatureClass = sys.argv[1]

# Calculate Estimated Acquisition Cost...
arcpy.AddField_management(ScenarioOutputFeatureClass, "ValuePerSqMetre", "FLOAT")
arcpy.CalculateField_management(ScenarioOutputFeatureClass, "ValuePerSqMetre", "dofunc(!ACTUALVAL!, !SHAPE_Area!)",
                                "PYTHON_9.3",
                                "def dofunc(tv, sa):\\n  if (tv > 0):\\n    return (tv / sa)\\n  else:\\n    return 0")
arcpy.AddField_management(ScenarioOutputFeatureClass, "RelPri", "FLOAT")
arcpy.CalculateField_management(ScenarioOutputFeatureClass, "RelPri", "dofunc(!BiodivImpMean!, !ACTUALVAL!,"
                                                                      "!SHAPE_Area!)", "PYTHON_9.3",
                                "def dofunc(bm, tv, sa):\\n  if (bm > 0 and tv > 0):\\n    return bm / (tv / sa)\\n  " +
                                "else:\\n    return 0")
# Normalize using field calculator...
arcpy.AddField_management(ScenarioOutputFeatureClass, "EstAcqPriority", "FLOAT")
TempStatsTblEAP = "%scratchWorkspace%\\TempStatsTblEAP"
arcpy.Statistics_analysis(ScenarioOutputFeatureClass, TempStatsTblEAP, "RelPri MAX")
with arcpy.da.SearchCursor(TempStatsTblEAP, ["MAX_RelPri"]) as rows:
    for row in rows:
        arcpy.CalculateField_management(ScenarioOutputFeatureClass, "EstAcqPriority", "!RelPri! / " +
                                                                                      str(row[0]), "PYTHON_9.3", "")
del rows, row
# Clean-up...
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "RelPri")
arcpy.Delete_management(TempStatsTblEAP)

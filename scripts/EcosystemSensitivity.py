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
TEM_SEM = sys.argv[1]
SensitiveEcosystems = sys.argv[2]
OutputRaster = sys.argv[3]

# Add fields for Sensitive Ecosystem Importance and overall ecosystem sensitivity...
arcpy.AddField_management(TEM_SEM, "SEM_IMP1", "FLOAT")
arcpy.AddField_management(TEM_SEM, "SEM_IMP2", "FLOAT")
arcpy.AddField_management(TEM_SEM, "SEM_IMP3", "FLOAT")
arcpy.AddField_management(TEM_SEM, "ECO_SEN", "FLOAT")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TEM_SEM, "TEM_SEM_LYR")

# Join on SEM_CLS_x to determine and assign SEM_IMPx field...
arcpy.AddJoin_management("TEM_SEM_LYR", "SEM_CLS_1", SensitiveEcosystems, "SEMCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "SEM_IMP1", "!SensitiveEcosystems$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "SensitiveEcosystems$")
arcpy.AddJoin_management("TEM_SEM_LYR", "SEM_CLS_2", SensitiveEcosystems, "SEMCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "SEM_IMP2", "!SensitiveEcosystems$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "SensitiveEcosystems$")
arcpy.AddJoin_management("TEM_SEM_LYR", "SEM_CLS_3", SensitiveEcosystems, "SEMCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "SEM_IMP3", "!SensitiveEcosystems$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "SensitiveEcosystems$")

# Calcuate overall ECO_SEN...
with arcpy.da.UpdateCursor(TEM_SEM,
                           ["DEC1", "DEC2", "DEC3", "SEM_IMP1", "SEM_IMP2", "SEM_IMP3", "ECO_SEN"]) as TEM_SEMCursor:
    for TEM_SEMRow in TEM_SEMCursor:
        # Local Vars...
        DEC1 = TEM_SEMRow[0]/100
        DEC2 = TEM_SEMRow[1]/100
        DEC3 = TEM_SEMRow[2]/100
        SEM_IMP1 = TEM_SEMRow[3]
        SEM_IMP2 = TEM_SEMRow[4]
        SEM_IMP3 = TEM_SEMRow[5]
        # Calc...
        EcoSen = 0.0
        if SEM_IMP1 is not None:
            EcoSen = EcoSen + (DEC1 * SEM_IMP1)
        if SEM_IMP2 is not None:
            EcoSen = EcoSen + (DEC2 * SEM_IMP2)
        if SEM_IMP3 is not None:
            EcoSen = EcoSen + (DEC3 * SEM_IMP3)
        TEM_SEMRow[6] = EcoSen
        # Update...
        TEM_SEMCursor.updateRow(TEM_SEMRow)
del TEM_SEMCursor, TEM_SEMRow

# Convert the polygon to raster based on the ECO_SEN field...
TempRaster = "%scratchWorkspace%\\temprst0040.tif"
arcpy.FeatureToRaster_conversion(TEM_SEM, "ECO_SEN", TempRaster)

# Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
arcpy.SetNoDataTo0_laitcp(TempRaster, OutputRaster)

# Delete temp datasets...
arcpy.Delete_management(TempRaster)

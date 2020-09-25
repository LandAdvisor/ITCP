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
AtRiskEcologicalCommunities = sys.argv[2]
OutputRaster = sys.argv[3]

# Delete fields if the previously existed, otherwise AddIndex will fail...
arcpy.DeleteField_management(TEM_SEM, "MC1")
arcpy.DeleteField_management(TEM_SEM, "MC2")
arcpy.DeleteField_management(TEM_SEM, "MC3")

# Add fields for MapCodes...
arcpy.AddField_management(TEM_SEM, "MC1", "TEXT")
arcpy.AddField_management(TEM_SEM, "MC2", "TEXT")
arcpy.AddField_management(TEM_SEM, "MC3", "TEXT")

# Calculate MCx fields from zone, subzone and map codes...
arcpy.CalculateField_management(TEM_SEM, "MC1", "!BGC_ZONE!.strip() + !BGC_SUBZON!.strip() + !BGC_VRT!.strip() + !SITEMC_S1!.strip()", "PYTHON_9.3", "")
arcpy.CalculateField_management(TEM_SEM, "MC2", "!BGC_ZONE!.strip() + !BGC_SUBZON!.strip() + !BGC_VRT!.strip() + !SITEMC_S2!.strip()", "PYTHON_9.3", "")
arcpy.CalculateField_management(TEM_SEM, "MC3", "!BGC_ZONE!.strip() + !BGC_SUBZON!.strip() + !BGC_VRT!.strip() + !SITEMC_S3!.strip()", "PYTHON_9.3", "")

### Index to speed joins...
##arcpy.AddIndex_management(TEM_SEM, "MC1", "MC1Idx")
##arcpy.AddIndex_management(TEM_SEM, "MC2", "MC2Idx")
##arcpy.AddIndex_management(TEM_SEM, "MC3", "MC3Idx")

# Add fields for AtRisk Importance...
arcpy.AddField_management(TEM_SEM, "ATRISK_IMP1", "FLOAT")
arcpy.AddField_management(TEM_SEM, "ATRISK_IMP2", "FLOAT")
arcpy.AddField_management(TEM_SEM, "ATRISK_IMP3", "FLOAT")
arcpy.AddField_management(TEM_SEM, "ATRISK_IMP", "FLOAT")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TEM_SEM, "TEM_SEM_LYR")

# Join on MCx to determine and assign ATRISK_IMPx field...
arcpy.AddJoin_management("TEM_SEM_LYR", "MC1", AtRiskEcologicalCommunities, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "ATRISK_IMP1", "!AtRiskEcologicalCommunities$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "AtRiskEcologicalCommunities$")
arcpy.AddJoin_management("TEM_SEM_LYR", "MC2", AtRiskEcologicalCommunities, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "ATRISK_IMP2", "!AtRiskEcologicalCommunities$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "AtRiskEcologicalCommunities$")
arcpy.AddJoin_management("TEM_SEM_LYR", "MC2", AtRiskEcologicalCommunities, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "ATRISK_IMP2", "!AtRiskEcologicalCommunities$.Importance!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "AtRiskEcologicalCommunities$")

# Calcuate overall ATRISK_IMP...
with arcpy.da.UpdateCursor(TEM_SEM, ["DEC1", "DEC2", "DEC3",
                                     "ATRISK_IMP1", "ATRISK_IMP2", "ATRISK_IMP3", "ATRISK_IMP"]) as TEM_SEMCursor:
    for TEM_SEMRow in TEM_SEMCursor:
        # Local Vars...
        DEC1 = TEM_SEMRow[0]/100
        DEC2 = TEM_SEMRow[1]/100
        DEC3 = TEM_SEMRow[2]/100
        ATRISK_IMP1 = TEM_SEMRow[3]
        ATRISK_IMP2 = TEM_SEMRow[4]
        ATRISK_IMP3 = TEM_SEMRow[5]
        # Calc...
        ATRISK_IMP = 0.0
        if ATRISK_IMP1 is not None:
            ATRISK_IMP = ATRISK_IMP + (DEC1 * ATRISK_IMP1)
        if ATRISK_IMP2 is not None:
            ATRISK_IMP = ATRISK_IMP + (DEC2 * ATRISK_IMP2)
        if ATRISK_IMP3 is not None:
            ATRISK_IMP = ATRISK_IMP + (DEC3 * ATRISK_IMP3)
        TEM_SEMRow[6] = ATRISK_IMP
        # Update
        TEM_SEMCursor.updateRow(TEM_SEMRow)
del TEM_SEMCursor, TEM_SEMRow

# Convert the polygon to raster based on the ECO_SEN field...
TempRaster = "%scratchWorkspace%\\temprst0050.tif"
arcpy.FeatureToRaster_conversion(TEM_SEM, "ATRISK_IMP", TempRaster)

# Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
arcpy.SetNoDataTo0_laitcp(TempRaster, OutputRaster)

# Delete temp datasets...
arcpy.Delete_management(TempRaster)

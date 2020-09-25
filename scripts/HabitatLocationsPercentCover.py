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
TEM_SEM = sys.argv[1]
MapClasses = sys.argv[2]

# Delete fields if they previously existed, otherwise AddIndex will fail...
arcpy.DeleteField_management(TEM_SEM, "MC1")
arcpy.DeleteField_management(TEM_SEM, "MC2")
arcpy.DeleteField_management(TEM_SEM, "MC3")
arcpy.DeleteField_management(TEM_SEM, "MCL1")
arcpy.DeleteField_management(TEM_SEM, "MCL2")
arcpy.DeleteField_management(TEM_SEM, "MCL3")

# Add fields for MapCode to MapClass reclassification...
arcpy.AddField_management(TEM_SEM, "MC1", "TEXT")
arcpy.AddField_management(TEM_SEM, "MC2", "TEXT")
arcpy.AddField_management(TEM_SEM, "MC3", "TEXT")
arcpy.AddField_management(TEM_SEM, "MCL1", "TEXT")
arcpy.AddField_management(TEM_SEM, "MCL2", "TEXT")
arcpy.AddField_management(TEM_SEM, "MCL3", "TEXT")

# Calculate MCx fields from zone, subzone and map codes...
arcpy.CalculateField_management(TEM_SEM, "MC1", "!BGC_ZONE! + !BGC_SUBZON! + !BGC_VRT! + !SITEMC_S1!", "PYTHON_9.3", "")
arcpy.CalculateField_management(TEM_SEM, "MC2", "!BGC_ZONE! + !BGC_SUBZON! + !BGC_VRT! + !SITEMC_S2!", "PYTHON_9.3", "")
arcpy.CalculateField_management(TEM_SEM, "MC3", "!BGC_ZONE! + !BGC_SUBZON! + !BGC_VRT! + !SITEMC_S3!", "PYTHON_9.3", "")

### Index to speed joins...
##arcpy.AddIndex_management(TEM_SEM, "MC1", "MC1Idx")
##arcpy.AddIndex_management(TEM_SEM, "MC2", "MC2Idx")
##arcpy.AddIndex_management(TEM_SEM, "MC3", "MC3Idx")

# MakeFeatureLayer to facilitate joining...
arcpy.MakeFeatureLayer_management(TEM_SEM, "TEM_SEM_LYR")

# Join on MCx to determine corresponding MapClass and assign to MCLx field...
arcpy.AddJoin_management("TEM_SEM_LYR", "MC1", MapClasses, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "MCL1", "!MapClasses$.MapClass!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "MapClasses$")
arcpy.AddJoin_management("TEM_SEM_LYR", "MC2", MapClasses, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "MCL2", "!MapClasses$.MapClass!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "MapClasses$")
arcpy.AddJoin_management("TEM_SEM_LYR", "MC3", MapClasses, "MapCode", "KEEP_ALL")
arcpy.CalculateField_management("TEM_SEM_LYR", "MCL3", "!MapClasses$.MapClass!", "PYTHON_9.3", "")
arcpy.RemoveJoin_management("TEM_SEM_LYR", "MapClasses$")

### Index to speed selects...
##arcpy.AddIndex_management(TEM_SEM, "MCL1", "MCL1Idx")
##arcpy.AddIndex_management(TEM_SEM, "MCL2", "MCL2Idx")
##arcpy.AddIndex_management(TEM_SEM, "MCL3", "MCL3Idx")

# Populate list of unique MapClasses from table...
MapClassList = list()
with arcpy.da.SearchCursor(MapClasses, ["MapClass"]) as MapClassCursor:
    for MapClassRow in MapClassCursor:
        MapClassValue = MapClassRow[0]
        if MapClassValue is not None:
            if MapClassValue not in MapClassList:
                MapClassList.append(MapClassValue)
del MapClassCursor, MapClassRow

# For each of the unique mapcodes create a polygon feature class and convert to raster...
for MapClass in MapClassList:
    # Clean up previous versions of the data...
    if arcpy.Exists("%workspace%\\" + MapClass + ".tif"):
        arcpy.Delete_management("%workspace%\\" + MapClass + ".tif")

    # Select to create the individual feature classes...
    SelectStatement = " \"MCL1\" = '" + MapClass + "' or \"MCL2\" = '" + MapClass + "' or \"MCL3\" = '" + MapClass + "'"
    TempFeatureClass = "%scratchWorkspace%\\Scratch.gdb\\" + MapClass
    ## If workspace is not a geodatabase, need extension to create shapefile...
    #Last4 = arcpy.env.scratchWorkspace[len(arcpy.env.scratchWorkspace) - 4:len(arcpy.env.scratchWorkspace)].lower()
    #if Last4 != ".mdb" and Last4 != ".gdb":
    #    TempFeatureClass = TempFeatureClass + ".shp"
    arcpy.Select_analysis(TEM_SEM, TempFeatureClass, SelectStatement)

    # Add field for percent cover
    arcpy.AddField_management(TempFeatureClass, "MCL_PERC", "FLOAT")

    # For each of the unique mapclasses calculate Decile value for each of the three possible ecosystem levels into the
    # newly created field...
    if int(arcpy.GetCount_management(TempFeatureClass).getOutput(0)) > 0:
        with arcpy.da.UpdateCursor(TempFeatureClass, ["MCL1", "MCL2", "MCL3", "DEC1", "DEC2","DEC3",
                                                      "MCL_PERC"]) as OutputCursor:
            for OutputRow in OutputCursor:
                # Accumulate the percentages across the 3 original values...
                perc = 0.0
                if OutputRow[0] == MapClass:
                    perc = perc + (OutputRow[3] / 100.0)
                if OutputRow[1] == MapClass:
                    perc = perc + (OutputRow[4] / 100.0)
                if OutputRow[2] == MapClass:
                    perc = perc + (OutputRow[5] / 100.0)
                OutputRow[6] = perc
                OutputCursor.updateRow(OutputRow)
        del OutputCursor, OutputRow

        # Convert the polygon to raster based on the MCL_PERC field...
        TempRaster = "%scratchWorkspace%\\temprst0030.tif"
        arcpy.FeatureToRaster_conversion(TempFeatureClass, "MCL_PERC", TempRaster)

        # Reclass NoData to 0 (if a Mask is set, this happens within Mask and all other values are set to NoData)...
        arcpy.SetNoDataTo0_laitcp(TempRaster, "%workspace%\\" + MapClass + ".tif")

        # Delete temp datasets...
        arcpy.Delete_management(TempFeatureClass)
        arcpy.Delete_management(TempRaster)

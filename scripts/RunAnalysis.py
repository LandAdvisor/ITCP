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

# Check out any necessary licenses...
arcpy.CheckOutExtension("spatial")

# Script arguments...
ProtectedAreasFeatureClass = sys.argv[1]
RasterMaskSingleValue = sys.argv[2]
ProtectedAreaSizeNewMin = sys.argv[3]
ProtectedAreaSizeOutputRaster = sys.argv[4]
ProtectedAreaSizeWeight = sys.argv[5]
ProtectedAreaRatioOutputRaster = sys.argv[6]
ProtectedAreaRatioWeight = sys.argv[7]
ProtectedAreaShapeOutputRaster = sys.argv[8]
ProtectedAreaShapeWeight = sys.argv[9]
IUCNImportanceTable = sys.argv[10]
IUCNClassificationOutputRaster = sys.argv[11]
IUCNClassificationWeight = sys.argv[12]
ProtectedAreaImportanceOutputRaster = sys.argv[13]
TEMFeatureClass = sys.argv[14]
ForestStandDegradationTable = sys.argv[15]
ForestDegradationOutputRaster = sys.argv[16]
ForestDegradationWeight = sys.argv[17]
TEMDisturbanceTable = sys.argv[18]
ITEMFeatureClass = sys.argv[19]
ITEMDisturbanceTable = sys.argv[20]
DisturbanceOutputRaster = sys.argv[21]
DisturbanceWeight = sys.argv[22]
RoadProximityRaster = sys.argv[23]
RoadProximityWeight = sys.argv[24]
HousingDensityOutputRaster = sys.argv[25]
HousingDensityWeight = sys.argv[26]
BrowsingRaster = sys.argv[27]
BrowsingWeight = sys.argv[28]
NaturalnessOutputRaster = sys.argv[29]
MapClassesTable = sys.argv[30]
r = sys.argv[31]
t = sys.argv[32]
q = sys.argv[33]
o = sys.argv[34]
s = sys.argv[35]
f = sys.argv[36]
u = sys.argv[37]
AllHabitatsRepresentationOutputRaster = sys.argv[38]
AllHabitatsRepresentationWeight = sys.argv[39]
ZoningFeatureClass = sys.argv[40]
PropertiesFeatureClass = sys.argv[41]
MinLotSizeTable = sys.argv[42]
SubPotThreatOutputRaster = sys.argv[43]
SubPotThreatWeight = sys.argv[44]
ShorelineUnitsFeatureClass = sys.argv[45]
ShoreUnitThreatTable = sys.argv[46]
ShoreAdjacencyTolerance = sys.argv[47]
ShoreAdjacencyThreatOutputRaster = sys.argv[48]
ShoreAdjacencyThreatWeight = sys.argv[49]
RoadsFeatureClass = sys.argv[50]
RoadAdjacencyTolerance = sys.argv[51]
RoadAdjacencyThreatOutputRaster = sys.argv[52]
RoadAdjacencyThreatWeight = sys.argv[53]
ThreatOutputRaster = sys.argv[54]
HabitatThreatOutputRaster = sys.argv[55]
HabitatThreatWeight = sys.argv[56]
HabitatConservationOutputRaster = sys.argv[57]
HabitatConservationWeight = sys.argv[58]
NaturalnessWeight = sys.argv[59]
ThreatWeight = sys.argv[60]
EcosystemSensitivityRaster = sys.argv[61]
EcosystemSensitivityWeight = sys.argv[62]
AtRiskEcologicalCommunitiesRaster = sys.argv[63]
AtRiskEcologicalCommunitiesWeight = sys.argv[64]
SpecialHabitatsOutputRaster = sys.argv[65]
SpecialHabitatsWeight = sys.argv[66]
CompositionOutputRaster = sys.argv[67]
CompositionWeight = sys.argv[68]
ProtectedAreaSizeImportanceTable = sys.argv[69]
ProtectedAreasAdjacencyImportanceOutputRaster = sys.argv[70]
PropertiesRaster = sys.argv[71]
RoadThreatMultiplier = sys.argv[72]
StreamsFeatureClass = sys.argv[73]
StreamBenefitFactor = sys.argv[74]
SmallestProtectedArea = sys.argv[75]
MaxProtectedAreaSeparation = sys.argv[76]
ProtectedAreaPairsOutputFeatureClass = sys.argv[77]
PercentageCorridorValuesToKeep = sys.argv[78]
PermeabilityWeight = sys.argv[79]
CorridorEnvelopeWeight = sys.argv[80]
LCPLengthWeight = sys.argv[81]
ConnectivityOutputRaster = sys.argv[82]
ConnectivityWeight = sys.argv[83]
ContiguityOutputRaster = sys.argv[84]
ContiguityWeight = sys.argv[85]
BiodiversityImportanceOutputRaster = sys.argv[86]
ScenarioOutputName = sys.argv[87]
AnalysisType = sys.argv[88]
GreedyTargetType = sys.argv[89]
GreedyBudgetTarget = sys.argv[90]
GreedyBudgetTargetNum = float(GreedyBudgetTarget)
GreedyAreaTarget = sys.argv[91]
GreedyAreaTargetNum = float(GreedyAreaTarget)
GreedyPropertyCountTarget = sys.argv[92]
GreedyPropertyCountTargetNum = int(GreedyPropertyCountTarget)
PropertiesPerGreedyIteration = sys.argv[93]
PropertiesPerGreedyIterationNum = int(PropertiesPerGreedyIteration)
ConnectivityRecalcInterval = sys.argv[94]
ConnectivityRecalcIntervalNum = int(ConnectivityRecalcInterval)
MinPropSizeBiodivBasedGreedy = sys.argv[95]

# # Settings and script arguments - hard-code for testing...
# arcpy.env.overwriteOutput = True
# arcpy.env.workspace = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output"
# arcpy.env.scratchWorkspace = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\scratch"
# arcpy.env.extent = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# arcpy.env.snapRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# arcpy.env.cellSize = 25
# arcpy.env.mask = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# ProtectedAreasFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\IslandsOutput.gdb\\" +\
#                              "ProtectedAreasDissolved"
# RasterMaskSingleValue = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\islandsmask1"
# ProtectedAreaSizeNewMin = "0.75"
# ProtectedAreaSizeOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\protareasize"
# ProtectedAreaSizeWeight = "0.8"
# ProtectedAreaRatioOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\protarearatio"
# ProtectedAreaRatioWeight = "0.2"
# ProtectedAreaShapeOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\protareashape"
# ProtectedAreaShapeWeight = "0.5"
# IUCNImportanceTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\" +\
#                       "IUCNImportance$"
# IUCNClassificationOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\iucnclass"
# IUCNClassificationWeight = "0.5"
# ProtectedAreaImportanceOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\protareaimp"
# TEMFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\TEM_SEM"
# ForestStandDegradationTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\" +\
#                               "StructuralStage$"
# ForestDegradationOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\forestdeg"
# ForestDegradationWeight = "0.23"
# TEMDisturbanceTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\" +\
#                       "TEMDisturbance$"
# ITEMFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\ITEM"
# ITEMDisturbanceTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\" +\
#                        "ITEMDisturbance$"
# DisturbanceOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\disturbance"
# DisturbanceWeight = "0.23"
# RoadProximityRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\roadprox"
# RoadProximityWeight = "0.23"
# HousingDensityOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\housdensity"
# HousingDensityWeight = "0.23"
# BrowsingRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\browsing"
# BrowsingWeight = "0.08"
# NaturalnessOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\naturalness"
# MapClassesTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\MapClasses$"
# r = "1"
# t = "0.4"
# q = "0.05"
# o = "-1"
# s = "1"
# f = "1"
# u = "0"
# AllHabitatsRepresentationOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\allhabsrepn"
# AllHabitatsRepresentationWeight = "0.75"
# ZoningFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\ZONING"
# PropertiesFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\CAD"
# MinLotSizeTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\MinimumLotSizes$"
# SubPotThreatOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\subpottht"
# SubPotThreatWeight = "0.34"
# ShorelineUnitsFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\" +\
#                              "SHORELINE_UNITS"
# ShoreUnitThreatTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsRCPTables.xls\\" +\
#                        "ShoreUnitThreat$"
# ShoreAdjacencyTolerance = "35"
# ShoreAdjacencyThreatOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\shoreadjtht"
# ShoreAdjacencyThreatWeight = "0.33"
# RoadsFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\TRANSIT_ROADS_MOT"
# RoadAdjacencyTolerance = "15"
# RoadAdjacencyThreatOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\roadadjtht"
# RoadAdjacencyThreatWeight = "0.33"
# ThreatOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\threat"
# HabitatThreatOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\habthreat"
# HabitatThreatWeight = "0.25"
# HabitatConservationOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\habitatcons"
# HabitatConservationWeight = "0.2"
# NaturalnessWeight = "0.2"
# ThreatWeight = "0.2"
# EcosystemSensitivityRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\ecosen"
# EcosystemSensitivityWeight = "0.5"
# AtRiskEcologicalCommunitiesRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\atrisk"
# AtRiskEcologicalCommunitiesWeight = "0.5"
# SpecialHabitatsOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\specialhab"
# SpecialHabitatsWeight = "0.4"
# CompositionOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\composition"
# CompositionWeight = "0.5"
# ProtectedAreaSizeImportanceTable = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\" +\
#                                    "IslandsRCPTables.xls\\ProtAReaSizeImportance$"
# ProtectedAreasAdjacencyImportanceOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\paadjimp"
# PropertiesRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\properties"
# RoadThreatMultiplier = "20"
# StreamsFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\inputs\\IslandsData.gdb\\WATER_COURSES"
# StreamBenefitFactor = "2"
# SmallestProtectedArea = "180000"
# MaxProtectedAreaSeparation = "26000"
# ProtectedAreaPairsOutputFeatureClass = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\" +\
#                                        "IslandsOutput.gdb\\ProtectedAreaPairs"
# PercentageCorridorValuesToKeep = "4"
# PermeabilityWeight = "0.6"
# CorridorEnvelopeWeight = "0.2"
# LCPLengthWeight = "0.2"
# ConnectivityOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\connectivity"
# ConnectivityWeight = "0.25"
# ContiguityOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\contiguity"
# ContiguityWeight = "0.25"
# BiodiversityImportanceOutputRaster = "C:\\GIS\\LandAdvisor\\LandAdvisor-ITCP-4.1.0-Sample\\output\\biodiversity"
# ScenarioOutputName = "ScnearioOutput1"
# AnalysisType = "Composition, Connectivity and Contiguity"
# GreedyTargetType = "Budget"
# GreedyBudgetTarget = "1000000"
# GreedyBudgetTargetNum = float(GreedyBudgetTarget)
# GreedyAreaTarget = "1000000"
# GreedyAreaTargetNum = float(GreedyAreaTarget)
# GreedyPropertyCountTarget = "3"
# GreedyPropertyCountTargetNum = int(GreedyPropertyCountTarget)
# PropertiesPerGreedyIteration = "1"
# PropertiesPerGreedyIterationNum = int(PropertiesPerGreedyIteration)
# ConnectivityRecalcInterval = "5"
# ConnectivityRecalcIntervalNum = int(ConnectivityRecalcInterval)
# MinPropSizeBiodivBasedGreedy = "100000"

# Output paths in geodatabase
if not arcpy.Exists("%workspace%\\IslandsOutput.gdb"):
    arcpy.CreateFileGDB_management("%workspace%", "IslandsOutput.gdb")
ParametersOutputTable = "%workspace%\\IslandsOutput.gdb\\" + ScenarioOutputName + "Parms"
ScenarioOutputFeatureClass = "%workspace%\\IslandsOutput.gdb\\" + ScenarioOutputName

# Record model parameters...
arcpy.AddMessage("Started Recording Model Parameters at: " + time.ctime())
if arcpy.Exists(ParametersOutputTable):
    arcpy.Delete_management(ParametersOutputTable)
arcpy.CreateTable_management("%workspace%\\IslandsOutput.gdb", ScenarioOutputName + "Parms")
arcpy.AddField_management(ParametersOutputTable, "Parameter", "TEXT")
arcpy.AddField_management(ParametersOutputTable, "ParmValue", "DOUBLE")
with arcpy.da.InsertCursor(ParametersOutputTable, ['Parameter', 'ParmValue']) as parms:
    parms.insertRow(("ScenarioName: " + ScenarioOutputName, None))
    parms.insertRow(("Protected Area Size Weight", ProtectedAreaSizeWeight))
    parms.insertRow(("Protected Area Ratio Weight", ProtectedAreaRatioWeight))
    parms.insertRow(("Protected Area Shape Weight", ProtectedAreaShapeWeight))
    parms.insertRow(("IUCN Classification Weight", IUCNClassificationWeight))
    parms.insertRow(("Forest Degradation Weight", ForestDegradationWeight))
    parms.insertRow(("Disturbance Weight", DisturbanceWeight))
    parms.insertRow(("Road Proximity Weight", RoadProximityWeight))
    parms.insertRow(("Housing Density Weight", HousingDensityWeight))
    parms.insertRow(("Browsing Weight", BrowsingWeight))
    parms.insertRow(("r", r))
    parms.insertRow(("t", t))
    parms.insertRow(("q", q))
    parms.insertRow(("o", o))
    parms.insertRow(("s", s))
    parms.insertRow(("f", f))
    parms.insertRow(("u", u))
    parms.insertRow(("All Habitats Representation Weight", AllHabitatsRepresentationWeight))
    parms.insertRow(("Subdivision Potential Threat Weight", SubPotThreatWeight))
    parms.insertRow(("Shore Adjacency Threat Weight", ShoreAdjacencyThreatWeight))
    parms.insertRow(("Road Adjacency Threat Weight", RoadAdjacencyThreatWeight))
    parms.insertRow(("Habitat Threat Weight", HabitatThreatWeight))
    parms.insertRow(("Naturalness Weight", NaturalnessWeight))
    parms.insertRow(("Threat Weight", ThreatWeight))
    parms.insertRow(("Ecosystem Sensitivity Weight", EcosystemSensitivityWeight))
    parms.insertRow(("At Risk Ecological Communities Weight", AtRiskEcologicalCommunitiesWeight))
    parms.insertRow(("Special Habitats Weight", SpecialHabitatsWeight))
    parms.insertRow(("Composition Weight", CompositionWeight))
    parms.insertRow(("Road Threat Multiplier", RoadThreatMultiplier))
    parms.insertRow(("Smallest Protected Area", SmallestProtectedArea))
    parms.insertRow(("Max Protected Area Separation", MaxProtectedAreaSeparation))
    parms.insertRow(("Percentage Corridor Values to Keep", PercentageCorridorValuesToKeep))
    parms.insertRow(("Permeability Weight", PermeabilityWeight))
    parms.insertRow(("Corridor Envelope Weight", CorridorEnvelopeWeight))
    parms.insertRow(("LCP Length Weight", LCPLengthWeight))
    parms.insertRow(("Connectivity Weight", ConnectivityWeight))
    parms.insertRow(("Contiguity Weight", ContiguityWeight))
    parms.insertRow(("Analysis Type: " + AnalysisType, None))
    if AnalysisType == "Greedy Heuristic":
        parms.insertRow(("Greedy Target Type: " + GreedyTargetType, None))
        parms.insertRow(("Greedy Budget Target", GreedyBudgetTarget))
        parms.insertRow(("Greedy Property Count Target", GreedyPropertyCountTarget))
        parms.insertRow(("Properties Per Greedy Iteration", PropertiesPerGreedyIteration))
        parms.insertRow(("Connectivity Recalc Interval", ConnectivityRecalcInterval))
del parms
arcpy.AddMessage("Finished Recording Model Parameters at: " + time.ctime())

# Make copy of Properties to store outputs and delete extraneous fields...
arcpy.AddMessage("Started Copying Properties Feature Class at: " + time.ctime())
if arcpy.Exists(ScenarioOutputFeatureClass):
    arcpy.Delete_management(ScenarioOutputFeatureClass)
arcpy.CopyFeatures_management(PropertiesFeatureClass, ScenarioOutputFeatureClass)
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ID")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "PCLLINKSID")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "DESCRIPT")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "LOCALAREA")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ACCURACY")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "METHOD")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "PIN")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "PCL")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "LOT")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "BLK")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "PLANDEFDOC")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "PRIMARY_")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "LAND_DIST")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "COMMENTS")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "FREEFORM")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "CROWNADMIN")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ICIS_ID")
# can't delete this field because it's based on a subtype...
#arcpy.DeleteField_management(ScenarioOutputFeatureClass, "STATUS")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ADMIN")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "CONTROL")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "EDITOR")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "SOURCE")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ADDDATE")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "MODDATE")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "SUBDATE")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ACRES")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "TEMP1")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "TEMP2")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "TEMP_1")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "TEMP_2")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ROAD_PROX_THT")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "SHORE_ADJ_THT")
arcpy.DeleteField_management(ScenarioOutputFeatureClass, "ROAD_ADJ_THT")
arcpy.AddField_management(ScenarioOutputFeatureClass, "RecAcqOrder", "LONG")
# Make a second copy of Propeties for use with Greedy Heuristic
if AnalysisType == "Greedy Heuristic":
    GreedyPropertiesFeatureClass = "%scratchWorkspace%\Scratch.gdb\TempProperties"
    arcpy.CopyFeatures_management(PropertiesFeatureClass, GreedyPropertiesFeatureClass)
arcpy.AddMessage("Finished Copying Properties Feature Class at: " + time.ctime())

# Reset Protected Areas From Previous Greedy Runs
with arcpy.da.UpdateCursor(ProtectedAreasFeatureClass, ['IUCN_DES'], "IUCN_DES = 'Acquisition Target'") as PACursor:
    for PARow in PACursor:
        PACursor.deleteRow()
del PACursor

# Greedy Heuristic Loop
Iterate = "true"
Iteration = 0
PropertiesAcquired = 0
TotalCost = 0.0
TotalArea = 0.0
while Iterate == "true":
    if AnalysisType == "Greedy Heuristic":
        Iteration = Iteration + 1
        arcpy.AddMessage("Started Iteration " + str(Iteration) + " at: " + time.ctime())

    # Run Protected Area Shape...
    arcpy.AddMessage("Started Protected Area Shape at: " + time.ctime())
    arcpy.ProtectedAreaShape_laitcp(ProtectedAreasFeatureClass, RasterMaskSingleValue, ProtectedAreaSizeNewMin,
                                    ProtectedAreaSizeOutputRaster, ProtectedAreaSizeWeight,
                                    ProtectedAreaRatioOutputRaster, ProtectedAreaRatioWeight,
                                    ProtectedAreaShapeOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ProtectedAreaSizeOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "ProtAreaSize")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ProtectedAreaRatioOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "ProtAreaRatio")
    arcpy.AddMessage("Finished Protected Area Shape at: " + time.ctime())

    # Run IUCN Classification...
    arcpy.AddMessage("Started IUCN Classification at: " + time.ctime())
    arcpy.IUCNClassification_laitcp(ProtectedAreasFeatureClass, IUCNImportanceTable, IUCNClassificationOutputRaster)
    arcpy.AddMessage("Finished IUCN Classification at: " + time.ctime())

    # Run Protected Area Importance Weighted Sum...
    arcpy.AddMessage("Started Protected Area Importance Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[ProtectedAreaShapeOutputRaster, "Value", float(ProtectedAreaShapeWeight)],
                              [IUCNClassificationOutputRaster, "Value", float(IUCNClassificationWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, ProtectedAreaImportanceOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ProtectedAreaShapeOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "ProtAreaShape")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    IUCNClassificationOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "IUCNClass")
    arcpy.AddMessage("Finished Protected Area Importance Weighted Sum at: " + time.ctime())

    # Run Forest Degradation...
    arcpy.AddMessage("Started Forest Degradation at: " + time.ctime())
    arcpy.ForestDegradation_laitcp(TEMFeatureClass, ForestStandDegradationTable, ForestDegradationOutputRaster)
    arcpy.AddMessage("Finished Forest Degradation at: " + time.ctime())

    # Run Disturbance...
    arcpy.AddMessage("Started Disturbance at: " + time.ctime())
    arcpy.Disturbance_laitcp(TEMFeatureClass, TEMDisturbanceTable, ITEMFeatureClass, ITEMDisturbanceTable,
                             DisturbanceOutputRaster)
    arcpy.AddMessage("Finished Disturbance at: " + time.ctime())

    # Run Housing Density...
    arcpy.AddMessage("Started Housing Density at: " + time.ctime())
    if AnalysisType == "Greedy Heuristic":
        arcpy.HousingDensity_laitcp(GreedyPropertiesFeatureClass, HousingDensityOutputRaster, RasterMaskSingleValue)
    else:
        arcpy.HousingDensity_laitcp(PropertiesFeatureClass, HousingDensityOutputRaster, RasterMaskSingleValue)
    arcpy.AddMessage("Finished Housing Density at: " + time.ctime())

    # Run Naturalness Weighted Sum...
    arcpy.AddMessage("Started Naturalness Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[ForestDegradationOutputRaster, "Value", float(ForestDegradationWeight)],
                              [DisturbanceOutputRaster, "Value", float(DisturbanceWeight)],
                              [RoadProximityRaster, "Value", float(RoadProximityWeight)],
                              [HousingDensityOutputRaster, "Value", float(HousingDensityWeight)],
                              [BrowsingRaster, "Value", float(BrowsingWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreInvertedNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, NaturalnessOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ForestDegradationOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "ForestDeg")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, DisturbanceOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "Disturbance")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, RoadProximityRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "RoadProx")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, HousingDensityOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "HousDensity")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, BrowsingRaster, "false",
                                    "false", "true", "true", "false", "true", "true", "false", "Browsing")
    arcpy.AddMessage("Finished Naturalness Weighted Sum at: " + time.ctime())

    # Run All Habitats Representation...
    arcpy.AddMessage("Started All Habitats Representation at: " + time.ctime())
    arcpy.AllHabitatsRepresentation_laitcp(ProtectedAreaImportanceOutputRaster, NaturalnessOutputRaster,
                                           MapClassesTable, RasterMaskSingleValue, r, t, q, o, s, f, u,
                                           AllHabitatsRepresentationOutputRaster)
    arcpy.AddMessage("Finished All Habitats Representation at: " + time.ctime())

    # Run Subdivision Potential Threat...
    arcpy.AddMessage("Started Subdivision Potential Threat at: " + time.ctime())
    if AnalysisType == "Greedy Heuristic":
        arcpy.SubdivisionPotentialThreat_laitcp(ZoningFeatureClass, GreedyPropertiesFeatureClass, MinLotSizeTable,
                                                SubPotThreatOutputRaster)
    else:
        arcpy.SubdivisionPotentialThreat_laitcp(ZoningFeatureClass, PropertiesFeatureClass, MinLotSizeTable,
                                                SubPotThreatOutputRaster)
    arcpy.AddMessage("Finished Subdivision Potential Threat at: " + time.ctime())

    # Run Shore Adjacency Threat...
    arcpy.AddMessage("Started Shore Adjacency Threat at: " + time.ctime())
    if AnalysisType == "Greedy Heuristic":
        arcpy.ShoreAdjacencyThreat_laitcp(ShorelineUnitsFeatureClass, GreedyPropertiesFeatureClass,
                                          ShoreUnitThreatTable, ShoreAdjacencyTolerance,
                                          ShoreAdjacencyThreatOutputRaster, RasterMaskSingleValue)
    else:
        arcpy.ShoreAdjacencyThreat_laitcp(ShorelineUnitsFeatureClass, PropertiesFeatureClass, ShoreUnitThreatTable,
                                          ShoreAdjacencyTolerance, ShoreAdjacencyThreatOutputRaster,
                                          RasterMaskSingleValue)
    arcpy.AddMessage("Finished Shore Adjacency Threat at: " + time.ctime())

    # Run Road Adjacency Threat...
    arcpy.AddMessage("Started Road Adjacency Threat at: " + time.ctime())
    if AnalysisType == "Greedy Heuristic":
        arcpy.RoadAdjacencyThreat_laitcp(RoadsFeatureClass, GreedyPropertiesFeatureClass, RoadAdjacencyTolerance,
                                         RoadAdjacencyThreatOutputRaster, RasterMaskSingleValue)
    else:
        arcpy.RoadAdjacencyThreat_laitcp(RoadsFeatureClass, PropertiesFeatureClass, RoadAdjacencyTolerance,
                                         RoadAdjacencyThreatOutputRaster, RasterMaskSingleValue)
    arcpy.AddMessage("Finished Road Adjacency Threat at: " + time.ctime())

    # Run Threat Weighted Sum...
    arcpy.AddMessage("Started Threat Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[SubPotThreatOutputRaster, "Value", float(SubPotThreatWeight)],
                              [ShoreAdjacencyThreatOutputRaster, "Value", float(ShoreAdjacencyThreatWeight)],
                              [RoadAdjacencyThreatOutputRaster, "Value", float(RoadAdjacencyThreatWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, ThreatOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, SubPotThreatOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "SubPotThreat")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ShoreAdjacencyThreatOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "ShoreAdjThreat")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    RoadAdjacencyThreatOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "RoadAdjThreat")
    arcpy.AddMessage("Finished Threat Weighted Sum at: " + time.ctime())

    # Run Habitat Threat...
    arcpy.AddMessage("Started Habitat Threat at: " + time.ctime())
    arcpy.HabitatThreat_laitcp(ThreatOutputRaster, MapClassesTable, RasterMaskSingleValue, HabitatThreatOutputRaster)
    arcpy.AddMessage("Finished Habitat Threat at: " + time.ctime())

    # Run Habitat Conservation Weighted Sum...
    arcpy.AddMessage("Started Habitat Conservation Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[HabitatThreatOutputRaster, "Value", float(HabitatThreatWeight)],
                              [AllHabitatsRepresentationOutputRaster, "Value", float(AllHabitatsRepresentationWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, HabitatConservationOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, HabitatThreatOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "HabitatThreat")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    AllHabitatsRepresentationOutputRaster, "false", "false", "true", "true", "false",
                                    "true", "true", "false", "AllHabsRepn")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    ProtectedAreaImportanceOutputRaster, "false", "false", "true", "true", "false",
                                    "true", "true", "false", "ProtAreaImp")
    arcpy.AddMessage("Finished Habitat Conservation Weighted Sum at: " + time.ctime())

    # Run Special Habitats Weighted Sum...
    arcpy.AddMessage("Started Special Habitats Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[EcosystemSensitivityRaster, "Value", float(EcosystemSensitivityWeight)],
                              [AtRiskEcologicalCommunitiesRaster, "Value", float(AtRiskEcologicalCommunitiesWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, SpecialHabitatsOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, EcosystemSensitivityRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "EcoSen")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    AtRiskEcologicalCommunitiesRaster, "false", "false", "true", "true", "false",
                                    "true", "true", "false", "AtRisk")
    arcpy.AddMessage("Finished Special Habitats Weighted Sum at: " + time.ctime())

    # Run Composition Weighted Sum...
    arcpy.AddMessage("Started Composition Weighted Sum at: " + time.ctime())
    ws = WeightedSum(WSTable([[HabitatConservationOutputRaster, "Value", float(HabitatConservationWeight)],
                              [ThreatOutputRaster, "Value", float(ThreatWeight)],
                              [NaturalnessOutputRaster, "Value", float(NaturalnessWeight)],
                              [SpecialHabitatsOutputRaster, "Value", float(SpecialHabitatsWeight)]]))
    ws.save("%scratchWorkspace%\\wstemp.tif")
    ws = "%scratchWorkspace%\\wstemp.tif"
    arcpy.MaxScoreNormalizationFromRaster_laitcp(ws, RasterMaskSingleValue, CompositionOutputRaster)
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                    HabitatConservationOutputRaster, "false", "false", "true", "true", "false", "true",
                                    "true", "false", "HabitatCons")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, ThreatOutputRaster, "false",
                                    "false", "true", "true", "false", "true", "true", "false", "Threat")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, NaturalnessOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "Naturalness")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, SpecialHabitatsOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "SpecialHab")
    arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, CompositionOutputRaster,
                                    "false", "false", "true", "true", "false", "true", "true", "false", "Composition")
    arcpy.AddMessage("Finished Composition Weighted Sum at: " + time.ctime())

    # Run Protected Area Size Class...
    if AnalysisType in ["Composition and Contiguity", "Composition, Connectivity and Contiguity", "Greedy Heuristic"]:
        arcpy.AddMessage("Started Protected Area Size Class at: " + time.ctime())
        arcpy.ProtectedAreaSizeClass_laitcp(ProtectedAreasFeatureClass, ProtectedAreaSizeImportanceTable)
        arcpy.AddMessage("Finished Protected Area Size Class at: " + time.ctime())

    # Run Protected Area Adjacency Importance...
    if AnalysisType in ["Composition and Contiguity", "Composition, Connectivity and Contiguity", "Greedy Heuristic"]:
        arcpy.AddMessage("Started Protected Area Adjacency Importance at: " + time.ctime())
        arcpy.ProtectedAreaAdjacencyImportance_laitcp(ProtectedAreasFeatureClass,
                                                      ProtectedAreasAdjacencyImportanceOutputRaster)
        arcpy.AddMessage("Finished Protected Area Adjacency Importance at: " + time.ctime())

    # Run Connectivity
    if AnalysisType in ["Composition and Connectivity", "Composition, Connectivity and Contiguity"] or\
            (AnalysisType == "Greedy Heuristic" and ((Iteration - 1) % ConnectivityRecalcIntervalNum == 0)):
        arcpy.AddMessage("Started Connectivity A at: " + time.ctime())
        arcpy.ConnectivityA_laitcp(CompositionOutputRaster, RoadsFeatureClass, RoadThreatMultiplier,
                                   StreamsFeatureClass, StreamBenefitFactor, ProtectedAreasFeatureClass,
                                   RasterMaskSingleValue, SmallestProtectedArea, MaxProtectedAreaSeparation,
                                   ProtectedAreaPairsOutputFeatureClass, "true")
        arcpy.AddMessage("Finished Connectivity A at: " + time.ctime())
        arcpy.AddMessage("Started Connectivity B at: " + time.ctime())
        arcpy.ConnectivityB_laitcp(ProtectedAreaPairsOutputFeatureClass, RasterMaskSingleValue,
                                   PercentageCorridorValuesToKeep, PermeabilityWeight, CorridorEnvelopeWeight,
                                   LCPLengthWeight, ConnectivityOutputRaster, "true")
        arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                        ConnectivityOutputRaster, "false", "false", "true", "true", "false", "true",
                                        "true", "false", "Connectivity")
        arcpy.AddMessage("Finished Connectivity B at: " + time.ctime())

    # Run Contiguity (Protected Areas Adjacency)...
    if AnalysisType in ["Composition and Contiguity", "Composition, Connectivity and Contiguity", "Greedy Heuristic"]:
        arcpy.AddMessage("Started Contiguity (Protected Area Adjacency) at: " + time.ctime())
        arcpy.Contiguity_laitcp(ProtectedAreasFeatureClass, ProtectedAreasAdjacencyImportanceOutputRaster,
                                PropertiesRaster, RasterMaskSingleValue, ContiguityOutputRaster)
        arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster, ContiguityOutputRaster,
                                        "false", "false", "true", "true", "false", "true", "true", "false",
                                        "Contiguity")
        arcpy.AddMessage("Finished Contiguity (Protected Area Adjacency) at: " + time.ctime())

    if AnalysisType == "Composition, Connectivity and Contiguity" or AnalysisType == "Greedy Heuristic":
        # Run Biodiversity Importance Weighted Sum...
        arcpy.AddMessage("Started Biodiversity Importance Weighted Sum at: " + time.ctime())
        BiodiversityImportanceTempRaster = WeightedSum(WSTable([[CompositionOutputRaster, "VALUE", CompositionWeight],
                                                                [ConnectivityOutputRaster, "VALUE", ConnectivityWeight],
                                                                [ContiguityOutputRaster, "VALUE", ContiguityWeight]]))
        BiodiversityImportanceTempRaster.save(BiodiversityImportanceOutputRaster)
        arcpy.GenerateZonalStats_laitcp(ScenarioOutputFeatureClass, "TempID", PropertiesRaster,
                                        BiodiversityImportanceOutputRaster, "false", "false", "true", "true", "false",
                                        "true", "true", "false", "BiodivImp")
        arcpy.AddMessage("Finished Biodiversity Importance Weighted Sum at: " + time.ctime())

        # Run Estimated Acquisition Priority...
        arcpy.AddMessage("Started Estimated Acquisition Priority at: " + time.ctime())
        arcpy.EstimatedAcquisitionPriority_laitcp(ScenarioOutputFeatureClass)
        arcpy.AddMessage("Finished Estimated Acquisition Priority at: " + time.ctime())

    # Process Greedy Heuristic Proposed Acquisitions
    if AnalysisType == "Greedy Heuristic":
        arcpy.AddMessage("Started Greedy Heuristic Selections at: " + time.ctime())
        # Select Top Properties From Scenario
        SortField = "EstAcqPriority D"
        if GreedyTargetType == "Biodiversity-based Area" or GreedyTargetType == "Biodiversity-based Property Count":
            SortField = "BiodivImpMean D"
        with arcpy.da.UpdateCursor(ScenarioOutputFeatureClass,
                                   ["RecAcqOrder", "EstAcqPriority", "ACTUALVAL", "SHAPE@AREA", "TempID"],
                                   "RecAcqOrder IS NULL AND Shape_Area >= " + MinPropSizeBiodivBasedGreedy,
                                   "", "", SortField) as ScenarioCursor:
            PropertyCount = 0
            # Iterate Properties
            for ScenarioRow in ScenarioCursor:
                # Check count
                if PropertyCount >= PropertiesPerGreedyIterationNum:
                    break
                # Exclude priority 0 when target type is not biodiversity-based
                if ((GreedyTargetType == "Budget" or GreedyTargetType == "Area" or GreedyTargetType == "Property Count")
                    and ScenarioRow[1] == 0):
                    Iterate = "false"
                    break
                # Accumulate Total Cost, Total Area and Property Count
                ActVal = ScenarioRow[2]
                if ActVal is not None:
                    TotalCost = TotalCost + ActVal
                TotalArea = TotalArea + ScenarioRow[3]
                PropertiesAcquired = PropertiesAcquired + 1
                # Flag in Scenario Output
                ScenarioRow[0] = PropertiesAcquired
                ScenarioCursor.updateRow(ScenarioRow)
                # Add to Protected Areas and Delete from Properties
                arcpy.MakeFeatureLayer_management(GreedyPropertiesFeatureClass, "GPROP_LYR")
                arcpy.SelectLayerByAttribute_management("GPROP_LYR", "NEW_SELECTION", "TempID = " + str(ScenarioRow[4]))
                arcpy.Append_management(["GPROP_LYR"], ProtectedAreasFeatureClass, "NO_TEST")
                arcpy.DeleteRows_management("GPROP_LYR")
                # Check Target
                if (GreedyTargetType == "Budget" and TotalCost >= GreedyBudgetTargetNum) or\
                        ((GreedyTargetType == "Area" or GreedyTargetType == "Biodiversity-based Area")
                         and TotalArea >= GreedyAreaTargetNum) or\
                        ((GreedyTargetType == "Property Count" or GreedyTargetType == "Biodiversity-based Property Count")
                         and PropertiesAcquired >= GreedyPropertyCountTargetNum):
                    Iterate = "false"
                    break
                PropertyCount = PropertyCount + 1
        del ScenarioCursor, ScenarioRow

        # Set IUCN_DES for added Protected Areas
        with arcpy.da.UpdateCursor(ProtectedAreasFeatureClass, ["IUCN_DES"], "IUCN_DES IS NULL") as PACursor:
            for PARow in PACursor:
                PARow[0] = "Acquisition Target"
                PACursor.updateRow(PARow)
        del PACursor, PARow

        arcpy.AddMessage("Finished Greedy Heuristic Selections at: " + time.ctime())
        arcpy.AddMessage("Finished Iteration " + str(Iteration) + " at: " + time.ctime())

    else:
        # stop iterating
        Iterate = "false"

# Clean-up and Report Greedy Stats
if AnalysisType == "Greedy Heuristic":
    arcpy.Delete_management(GreedyPropertiesFeatureClass)
    arcpy.AddMessage("Recommend acquiring " + str(PropertiesAcquired) + " properties totalling " +
                     str(TotalArea/10000) + " ha costing $" + str(TotalCost))

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

# Script arguments...
ProtectedAreasFeatureClass = sys.argv[1]
ProtectedAreasDissolvedOutputFeatureClass = sys.argv[2]
Passes = int(sys.argv[3])
AdjacencyDistance = int(sys.argv[4])
TempProtectedAreasSelect = "%scratchWorkspace%\\Scratch.gdb\\TempProtectedAreasSelect"
TempProtectedAreasDissolve = "%scratchWorkspace%\\Scratch.gdb\\TempProtectedAreasDissolve"

# Select land-based protected areas
arcpy.Select_analysis(ProtectedAreasFeatureClass, TempProtectedAreasSelect,
                      "IUCN_DES IN ('Science Nature Reserve', 'Wilderness Area', 'Park', 'Natural Monument', "
                      "'Habitat/Species Management Area', 'Managed Resource Protected Areas') AND TYPE_1 NOT IN "
                      "('Park Submerged Federal', 'Park Submerged Provincial', 'Rock Fish Conservation Area')")
# Dissolve adjacent protected areas
arcpy.Dissolve_management(TempProtectedAreasSelect, TempProtectedAreasDissolve + "1", "", "", "SINGLE_PART",
                          "DISSOLVE_LINES")
# Add dissolve id field
arcpy.AddField_management( TempProtectedAreasDissolve + "1", "DISSOLVE", "Integer")
# Repeat process until all adjacent polygons are merged into 1 protected area
for i in range(1, Passes):
    # Create Feature Layers
    arcpy.MakeFeatureLayer_management(TempProtectedAreasDissolve + str(i),'PROTECTED_AREAS_LAYER1')
    arcpy.MakeFeatureLayer_management(TempProtectedAreasDissolve + str(i),'PROTECTED_AREAS_LAYER2')
    # Create search cursor to loop through protected areas
    with arcpy.da.SearchCursor('PROTECTED_AREAS_LAYER1', ['SHAPE@', 'OID@']) as ProtectedAreaPolygons:
        # For each protected area select the intesecting projected areas within 30 meters
        for ProtectedAreaPolygon in ProtectedAreaPolygons:
            arcpy.SelectLayerByLocation_management('PROTECTED_AREAS_LAYER2', "WITHIN_A_DISTANCE",
                                                   ProtectedAreaPolygon[0], AdjacencyDistance)
            # Calculate DISSOLVE attribute to OBJECTID of protected area
            arcpy.CalculateField_management("PROTECTED_AREAS_LAYER2", "DISSOLVE",
                                            ProtectedAreaPolygon[1], "PYTHON_9.3")
    del ProtectedAreaPolygons, ProtectedAreaPolygon
    # Dissolve protected areas based on DISSOLVE attribute id
    arcpy.Dissolve_management(TempProtectedAreasDissolve + str(i), TempProtectedAreasDissolve + str(i + 1),
                              "DISSOLVE", "", "MULTI_PART", "DISSOLVE_LINES")

# Assign IUCN_DES to multipart polygons, using the IUCN class of the largest protected area
# Add IUCN_DES field...
arcpy.AddField_management( TempProtectedAreasDissolve + str(i), "IUCN_DES", "Text")
# Create Feature Layers
arcpy.MakeFeatureLayer_management(TempProtectedAreasDissolve + str(i),'PROTECTED_AREAS_DISSOLVE_LAYER')
arcpy.MakeFeatureLayer_management(ProtectedAreasFeatureClass,'PROTECTED_AREAS_LAYER')
# Create update cursor to update IUCN Class
with arcpy.da.UpdateCursor('PROTECTED_AREAS_DISSOLVE_LAYER', ['SHAPE@', 'IUCN_DES']) as ProtectedAreaPolygons:
    # For each protected area select the intesecting original source projected areas
    for ProtectedAreaPolygon in ProtectedAreaPolygons:
        arcpy.SelectLayerByLocation_management('PROTECTED_AREAS_LAYER', "INTERSECT", ProtectedAreaPolygon[0])
        # Create search cursor on Protect Areas Layer selection to loop through areas and record IUCN class of the
        # largest polygon
        with arcpy.da.SearchCursor('PROTECTED_AREAS_LAYER', ['SHAPE@AREA', 'IUCN_DES']) as rows:
            MaxArea = 0
            IUCN_Class = ""
            for row in rows:
                if row[0] > MaxArea:
                    MaxArea = row[0]
                    IUCN_Class = row[1]
            # Update IUCN Class
            ProtectedAreaPolygon[1] = IUCN_Class
            ProtectedAreaPolygons.updateRow(ProtectedAreaPolygon)
        del rows, row
del ProtectedAreaPolygons, ProtectedAreaPolygon

# Save the output of the final pass
arcpy.CopyFeatures_management(TempProtectedAreasDissolve + str(i), ProtectedAreasDissolvedOutputFeatureClass)

# Delete temp datasets...
arcpy.Delete_management(TempProtectedAreasSelect)
for i in range(1, Passes):
    if arcpy.Exists(TempProtectedAreasDissolve + str(i)):
        arcpy.Delete_management(TempProtectedAreasDissolve + str(i))

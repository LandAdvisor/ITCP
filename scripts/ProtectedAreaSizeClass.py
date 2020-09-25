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

# Script Arguments...
ProtectedAreas = sys.argv[1]
ProtectedAreaSizeImportanceTable = sys.argv[2]

# Add field for SizeClass and IUCN_IMP...
arcpy.AddField_management(ProtectedAreas, "SizeClass", "Float")

# Build field calculator expression for SizeClass...
expression = "getsizeclass(!shape.area!)"
codeblock = ""
with arcpy.da.SearchCursor(ProtectedAreaSizeImportanceTable, ["SizeStart", "SizeEnd", "Importance"]) as PASizeCursor:
    for PASizeRow in PASizeCursor:
        if len(codeblock) == 0:
            codeblock = "def getsizeclass(area):\n\
"
        codeblock = codeblock + "    if area >= " + str(PASizeRow[0]) + " and area <= " + str(PASizeRow[1]) + ":\n\
            return " + str(PASizeRow[2]) + "\n\
"
del PASizeCursor, PASizeRow

# Calculate SizeClass...
arcpy.CalculateField_management(ProtectedAreas, "SizeClass", expression, "PYTHON_9.3", codeblock)

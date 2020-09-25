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
roadsFeatureClass = sys.argv[1]
maxDistance = sys.argv[2]
distanceDecayPower = sys.argv[3]
roadProximityOutputRaster = sys.argv[4]

# Add and calculate integer field for relative road threat
lstFields = arcpy.ListFields(roadsFeatureClass)
if "THT_INT" in lstFields:
  arcpy.DeleteField_management(roadsFeatureClass, "THT_INT")
else:
  arcpy.AddField_management(roadsFeatureClass, "THT_INT", "short")
arcpy.CalculateField_management(roadsFeatureClass, "THT_INT", "!ROADS_THT! * 100", "PYTHON_9.3", "")

# Calculate Euclidean Allocation and Distance rasters
eucDistTempRaster = "%scratchWorkspace%\\eucdist.tif"
eucAlloTempRaster = EucAllocation(roadsFeatureClass, maxDistance, "", "", "THT_INT", eucDistTempRaster)

# Calculate proximity using distance decay power and threat-derived weight
eucDistTempRaster = Raster(eucDistTempRaster)
roadProximityTempRaster = pow((int(maxDistance) - eucDistTempRaster) / int(maxDistance), float(distanceDecayPower))\
                          * (eucAlloTempRaster / 100.0)
roadProximityTempRaster.save(roadProximityOutputRaster)

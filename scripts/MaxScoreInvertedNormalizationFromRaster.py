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

# Script Arguments...
InputRaster = sys.argv[1]
RasterMaskSingleValue = sys.argv[2]
OutputRaster = sys.argv[3]

# Calculation - (max - actual) / (max - min)
InputRaster = Raster(InputRaster)
RasterMaskSingleValue = Raster(RasterMaskSingleValue)
ResultRaster = (ZonalStatistics(RasterMaskSingleValue, "VALUE", InputRaster, "MAXIMUM") - InputRaster) /\
               (ZonalStatistics(RasterMaskSingleValue, "VALUE", InputRaster, "MAXIMUM") -
                ZonalStatistics(RasterMaskSingleValue, "VALUE", InputRaster, "MINIMUM"))
ResultRaster.save(OutputRaster)

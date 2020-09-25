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

This customization of the Landscape Decision Support Tools was undertaken by the Islands Trust Conservation Planning (ITCP) team - http://conceptioncoast01.managed.contegix.com/display/ITCP/Home.

The tools are the final versions used by the team for Phase III of the ITCP project, based on ArcGIS 10.

The data is a sample fabricated using 2 small ficticious islands off the west coast of Vancouver Island! It is based on the ITCP data model (i.e. all Inputs and Output layers are named and structured as per the real data), but the contents have been simplified to a small number of made-up features on the 2 fictitious islands.

Relative to the Little Karoo project (http://conceptioncoast01.managed.contegix.com/display/ORG/Downloads), this version of the tools:
1. Has substantial differences in the inputs and steps used to estimate priorities for biodiversity conservation (compare the hierarchy diagrams for the projects).
2. Is largely base on Python Script tools as opposed to Model Builder tools.
3. Implements recording of all parameters/inputs and the input/intermediate criteria scores that make up the overall biodiversity conservation score for each property (use identify on ScenarioOutputX and inspect the Polygon attributes).

The ITCP model has been pre-run (i.e. all outputs from the default scenario are distributed with the data). It is run from scratch as follows:
1. Run the "Create Raster Mask Single Value" tool to build islandsmask1, then set the following MXD environment settings to islandsmask1: Extent, Snap Raster, Mask.
2. Run the "Run Data Prep" tool to perform analysis preparations.
3. Run the "Run Analysis" tool to perform an analysis based on supplied parameters.

Depending on the changes between scenarios, generally only step 3 or steps 2 and 3 need to be re-run each time.

Please see the following documents in the LandAdvisor-ITCP-4.0.5-Sample folder for additional information:
- IslandsTrust-MultiCriteria-Summary-v2.pdf
- IslandsTrust-MultiCriteria-Hierarchy-v20.pdf
- Calibrating the Continuous Benefit Functions-Habitats-IslandsTrust-v3.xlsx
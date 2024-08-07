##!/usr/bin/python
# -*- coding: utf-8 -*-
import config
# The MIT License (MIT)

# This code is part of the CityGML2OBJs package

# Copyright (c) 2014
# Filip Biljecki
# Delft University of Technology
# fbiljecki@gmail.com

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import markup3dmodule
import polygon3dmodule
import componentseparationmodule as csm
from lxml import etree
import os
import argparse
import glob
import numpy as np
import itertools
import matplotlib.pyplot as plt
import CityGMLTranslation as cgt
from decimal import Decimal
from config import setVersion
import time

# -- ARGUMENTS
# -i -- input directory (it will read and convert ALL CityGML files in a directory)
# -o -- output directory (it will output the generated OBJs in that directory in the way that Delft.gml becomes Delft.obj)
# -- SETTINGS of the converter (can be combined):
# -s 0 (default) -- converts all geometries in one class in one file under the same object (plain OBJ file).
# -s 1 -- differentiate between semantics, output each semantic class as one file, e.g. Delft-WallSurface.obj. Please note that in this case the grouped "plain" OBJ is not generated.
# if no thematic boundaries are found, this option is ignored.
# -g 0 (default) -- keeps all objects in the same bin.
# -g 1 -- it creates one object for every building.
# -v 1 -- validation
# -p 1 -- skip triangulation and write polygons. Polys with interior not supported.
# -t 1 -- translation (reduction) of coordinates so the smallest vertex (one with the minimum coordinates) is at (0, 0)
# -a 1 or 2 or 3 -- this is a very custom setting for adding the texture based on attributes, here you can see the settings for my particular case of the solar radiation. By default it is off.

# -- Text to be printed at the beginning of each OBJ
header = """# Converted from CityGML to OBJ with CityGML2OBJs.
# Conversion tool developed by Filip Biljecki, TU Delft <fbiljecki@gmail.com>, see more at Github:
# https://github.com/tudelft3d/CityGML2OBJs
#
"""


def get_index(point, list_vertices, shift=0):
    """Index the vertices.
    The third option is for incorporating a local index (building-level) to the global one (dataset-level)."""
    global vertices
    """Unique identifier and indexer of vertices."""
    if point in list_vertices:
        return list_vertices.index(point) + 1 + shift, list_vertices
    else:
        list_vertices.append(point)
        return list_vertices.index(point) + 1 + shift, list_vertices


def write_vertices(list_vertices, cla):
    """Write the vertices in the OBJ format."""
    global vertices_output
    for each in list_vertices:
        vertices_output[cla].append("v" + " " + str(each[0]) + " " + str(each[1]) + " " + str(each[2]) + "\n")


def remove_reccuring(list_vertices):
    """Removes recurring vertices, which messes up the triangulation.
    Inspired by http://stackoverflow.com/a/1143432"""
    # last_point = list_vertices[-1]
    list_vertices_without_last = list_vertices[:-1]
    found = set()
    for item in list_vertices_without_last:
        if str(item) not in found:
            yield item
            found.add(str(item))


def poly_to_obj(poly, cl, material=None):
    """Main conversion function of one polygon to one or more faces in OBJ,
    in a specific semantic class. Supports assigning a material."""
    global local_vertices
    global vertices
    global face_output
    # -- Decompose the polygon into exterior and interior
    e, i = markup3dmodule.polydecomposer(poly)
    # -- Points forming the exterior LinearRing
    epoints = markup3dmodule.GMLpoints(e[0])
    # print(epoints)
    # -- Clean recurring points, except the last one
    last_ep = epoints[-1]
    epoints_clean = list(remove_reccuring(epoints))
    epoints_clean.append(last_ep)
    # print("epoints: ", epoints)
    # print("epoints_clean: ", epoints_clean)

    # -- LinearRing(s) forming the interior
    irings = []
    for iring in i:
        ipoints = markup3dmodule.GMLpoints(iring)
        # -- Clean them in the same manner as the exterior ring
        last_ip = ipoints[-1]
        ipoints_clean = list(remove_reccuring(ipoints))
        ipoints_clean.append(last_ip)
        irings.append(ipoints_clean)
        # print("irings: ", irings)
    # -- If the polygon validation option is enabled
    if VALIDATION:
        # -- Check the polygon
        valid = polygon3dmodule.isPolyValid(epoints_clean, True)
        if valid:
            for iring in irings:
                if not polygon3dmodule.isPolyValid(iring, False):
                    valid = False
        # -- If everything is valid send them to the Delaunay triangulation
        if valid:
            if SKIPTRI:
                # -- Triangulation is skipped, polygons are converted directly to faces
                # -- The last point is removed since it's equal to the first one
                t = [epoints_clean[:-1]]
            else:
                # -- Triangulate polys
                # t = polygon3dmodule.triangulation(epoints, irings)
                try:
                    t = polygon3dmodule.triangulation(epoints_clean, irings)
                except:
                    t = []
                    # t = polygon3dmodule.triangulation(epoints_clean, irings)

            # -- Process the triangles/polygons
            for tri in t:
                # -- Face marker
                f = "f "
                # -- For each point in the triangle/polygon (face) get the index "v" or add it to the index
                for ep in range(0, len(tri)):
                    v, local_vertices[cl] = get_index(tri[ep], local_vertices[cl], len(vertices[cl]))
                    f += str(v) + " "
                # -- Add the material if invoked
                if material:
                    face_output[cl].append("usemtl " + str(mtl(material, min_value, max_value, res)) + str("\n"))
                # -- Store all together
                face_output[cl].append(f + "\n")
        else:
            # Get the gml:id of the Polygon if it exists
            polyid = poly.xpath("@g:id", namespaces={'g': ns_gml})
            if polyid:
                polyid = polyid[0]
                print("\t\t!! Detected an invalid polygon (%s). Skipping..." % polyid)
            else:
                print("\t\t!! Detected an invalid polygon. Skipping...")

    else:
        # -- Do exactly the same, but without the validation
        try:
            if SKIPTRI:
                t = [epoints_clean[:-1]]
            else:
                t = polygon3dmodule.triangulation(epoints_clean, irings)


        except:

            t = []

        for tri in t:
            f = "f "
            for ep in range(0, len(tri)):
                v, local_vertices[cl] = get_index(tri[ep], local_vertices[cl], len(vertices[cl]))
                f += str(v) + " "

            if material:
                face_output[cl].append("usemtl " + str(mtl(material, min_value, max_value, res)) + str("\n"))
            face_output[cl].append(f + "\n")


# -- Parse command-line arguments
PARSER = argparse.ArgumentParser(description='Convert a CityGML to OBJ.')
PARSER.add_argument('-i', '--directory',
                    help='Directory containing CityGML file(s).', required=True)
PARSER.add_argument('-o', '--results',
                    help='Directory where the OBJ file(s) should be written.', required=True)
PARSER.add_argument('-s', '--semantics',
                    help='Write one OBJ (0) or multiple OBJ per semantic class (1). 0 is default.', required=False)
PARSER.add_argument('-g', '--grouping',
                    help='Writes all buildings in one group (0) or multiple groups (1). 0 is default.', required=False)
PARSER.add_argument('-a', '--attribute',
                    help='Creates a texture regarding the value of an attribute of the surface. No material is default.',
                    required=False)
PARSER.add_argument('-v', '--validation',
                    help='Validates polygons, and if they are not valid give a warning and skip them. No validation is default.',
                    required=False)
PARSER.add_argument('-t', '--translate',
                    help='Translates all vertices, so that the smallest vertex is at zero. No translation is default.',
                    required=False)
PARSER.add_argument('-p', '--polypreserve',
                    help='Skip the triangulation (preserve polygons). Triangulation is default.', required=False)

# Changes by Th_Fr: 2 New optional parameters added, see description for details!
PARSER.add_argument('-tC', '--translateCityGML',
                    help='Perform a Translation of the CityGML Dataset into a local CRS before further processing. No translation is default.',
                    required=False)

PARSER.add_argument('-tCw', '--translateCityGMLwrite',
                    help='Perform a Translation of the CityGML Dataset into a local CRS before further processing. The translation parameters are stored in a designated .txt file. No Translation is default ',
                    required=False)

PARSER.add_argument('-sepC', '--separateComponents',
                    help='Save each building component into an individual file with the filename serving as an identifier.',
                    required=False)

PARSER.add_argument('-appW', '--approximateWindows',
                    help='Approximate windows by their convex hulls to save some processing time.',
                    required=False)

PARSER.add_argument('-addBB', '--addBoundingBox',
                    help='Add small triangles defining the bounding box to each of the components.',
                    required=False)

PARSER.add_argument('-addBBJSON', '--addBoundingBoxJSON',
                    help='The bounding box of the building is additionally saved in a designated json-file',
                    required=False)

PARSER.add_argument('-tbw', '--translateBuildingWise', # todo: implementation yet to be completed
                    help='Translate into a local coordinate system building-wise.',
                    required=False)

# End of changes by Th_Fr

ARGS = vars(PARSER.parse_args())
DIRECTORY = os.path.join(ARGS['directory'], '')
RESULT = os.path.join(ARGS['results'], '')

SEMANTICS = ARGS['semantics']
if SEMANTICS == '1':
    SEMANTICS = True
elif SEMANTICS == '0':
    SEMANTICS = False
else:
    SEMANTICS = False

OBJECTS = ARGS['grouping']
if OBJECTS == '1':
    OBJECTS = True
elif OBJECTS == '0':
    OBJECTS = False
else:
    OBJECTS = False

ATTRIBUTE = ARGS['attribute']
if ATTRIBUTE == '1':
    ATTRIBUTE = 1
elif ATTRIBUTE == '2':
    ATTRIBUTE = 2
elif ATTRIBUTE == '3':
    ATTRIBUTE = 3
elif ATTRIBUTE == '0':
    ATTRIBUTE = False
else:
    ATTRIBUTE = False

VALIDATION = ARGS['validation']
if VALIDATION == '1':
    VALIDATION = True
elif VALIDATION == '0':
    VALIDATION = False
else:
    VALIDATION = False

TRANSLATE = ARGS['translate']
if TRANSLATE == '1':
    TRANSLATE = True
elif TRANSLATE == '0':
    TRANSLATE = False
else:
    TRANSLATE = False
if TRANSLATE:
    global smallest_point

SKIPTRI = ARGS['polypreserve']
if SKIPTRI == '1':
    SKIPTRI = True
elif SKIPTRI == '0':
    SKIPTRI = False
else:
    SKIPTRI = False

# Changes By Th_Fr:

TRANSLATECGML = ARGS['translateCityGML']
if TRANSLATECGML == '1':
    TRANSLATECGML = True
elif TRANSLATECGML == '0':
    TRANSLATECGML = False
else:
    TRANSLATECGML = False

TRANSLATECGMLW = ARGS['translateCityGMLwrite']
if TRANSLATECGMLW == '1':
    TRANSLATECGMLW = True
elif TRANSLATECGMLW == '0':
    TRANSLATECGMLW = False
else:
    TRANSLATECGMLW = False

SEPARATERCOMPONENTS = ARGS['separateComponents']
if SEPARATERCOMPONENTS == '1':
    SEPARATERCOMPONENTS = True
elif SEPARATERCOMPONENTS == '0':
    SEPARATERCOMPONENTS = False
else:
    SEPARATERCOMPONENTS = False

APPROXIMATEWINDOWS = ARGS['approximateWindows']
if APPROXIMATEWINDOWS == '1':
    APPROXIMATEWINDOWS = True
elif APPROXIMATEWINDOWS == '0':
    APPROXIMATEWINDOWS = False
else:
    APPROXIMATEWINDOWS = False

ADDBOUNDINGBOX = ARGS['addBoundingBox']
if ADDBOUNDINGBOX == '1':
    ADDBOUNDINGBOX = True
elif ADDBOUNDINGBOX == '0':
    ADDBOUNDINGBOX = False
else:
    ADDBOUNDINGBOX = False

ADDBOUNDINGBOXJSON = ARGS['addBoundingBoxJSON']
if ADDBOUNDINGBOXJSON == '1':
    ADDBOUNDINGBOXJSON = True
elif ADDBOUNDINGBOXJSON == '0':
    ADDBOUNDINGBOXJSON = False
else:
    ADDBOUNDINGBOXJSON = False

TRANSLATEBUILDINGS = ARGS['translateBuildingWise']  # todo: muss noch implementiert werden
if TRANSLATEBUILDINGS == '1':
    TRANSLATEBUILDINGS = True
elif TRANSLATEBUILDINGS == '0':
    TRANSLATEBUILDINGS = False
else:
    TRANSLATEBUILDINGS = False

# End of Changes by Th_Fr
# -----------------------------------------------------------------
# -- Attribute stuff

# -- Number of classes (colours)
res = 101
# -- Configuration
# -- Color the surfaces based on the normalised kWh/m^2 value <irradiation>. The plain OBJ will be coloured for the total irradiation.
if ATTRIBUTE == 1:
    min_value = 350.0  # 234.591880403
    max_value = 1300.0  # 1389.97943395
elif ATTRIBUTE == 2:
    min_value = 157.0136575
    max_value = 83371.4359245
elif ATTRIBUTE == 3:
    min_value = 24925.0
    max_value = 103454.0

# -- Statistic parameter
atts = []


# -- Colouring function
def mtl(att, min_value, max_value, res):
    """Finds the corresponding material."""
    ar = np.linspace(0, 1, res).tolist()
    # -- Get rid of floating point errors
    for i in range(0, len(ar)):
        ar[i] = round(ar[i], 4)
    # -- Normalise the attribute
    v = float(att - min_value) / (max_value - min_value)
    # -- Get the material
    assigned_material = min(ar, key=lambda x: abs(x - v))
    return str(assigned_material)


# -----------------------------------------------------------------
# Start time
start_time = time.time()
# -- Start of the program
print("CityGML2OBJ. Searching for CityGML files...")
global _VERSION
# -- Find all CityGML files in the directory
os.chdir(DIRECTORY)
# -- Supported extensions
# Old version: types = ('*.gml', '*.GML', '*.xml', '*.XML')
types = ('*.gml', '*.xml')
files_found = []
for files in types:
    files_found.extend(glob.glob(files))
for f in files_found:
    FILENAME = f[:f.rfind('.')]
    FULLPATH = os.path.join(DIRECTORY, f)

    # -- Reading and parsing the CityGML file(s)
    CITYGML = etree.parse(FULLPATH)
    # -- Getting the root of the XML tree
    root = CITYGML.getroot()
    # -- Determine CityGML version
    # If 1.0
    if root.tag == "{http://www.opengis.net/citygml/1.0}CityModel":
        print("CityGML 1.0")
        config.setVersion(1)
        # -- Name spaces
        ns_citygml = "http://www.opengis.net/citygml/1.0"
        ns_gml = "http://www.opengis.net/gml"
        ns_bldg = "http://www.opengis.net/citygml/building/1.0"
        ns_tran = "http://www.opengis.net/citygml/transportation/1.0"
        ns_veg = "http://www.opengis.net/citygml/vegetation/1.0"
        ns_gen = "http://www.opengis.net/citygml/generics/1.0"
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:1.0"
        ns_xlink = "http://www.w3.org/1999/xlink"
        ns_dem = "http://www.opengis.net/citygml/relief/1.0"
        ns_frn = "http://www.opengis.net/citygml/cityfurniture/1.0"
        ns_tun = "http://www.opengis.net/citygml/tunnel/1.0"
        ns_wtr = "http://www.opengis.net/citygml/waterbody/1.0"
        ns_brid = "http://www.opengis.net/citygml/bridge/1.0"
        ns_app = "http://www.opengis.net/citygml/appearance/1.0"

    # added by Th_Fr
    elif root.tag == "{http://www.opengis.net/citygml/3.0}CityModel":
        print("CityGML 3.0")
        config.setVersion(3)
        ns_citygml = "http://www.opengis.net/citygml/3.0"
        ns_con = "http://www.opengis.net/citygml/construction/3.0"
        ns_xlink = "http://www.w3.org/1999/xlink"
        ns_gml = "http://www.opengis.net/gml/3.2"
        ns_bldg = "http://www.opengis.net/citygml/building/3.0"
        ns_app = "http://www.opengis.net/citygml/appearance/3.0"
        ns_pcl = "http://www.opengis.net/citygml/pointcloud/3.0"
        ns_gen = "http://www.opengis.net/citygml/generics/3.0"
        ns_gss = "http://www.isotc211.org/2005/gss"
        na_pfx0 = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
        ns_gsr = "http://www.isotc211.org/2005/gsr"
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_gco = "http://www.isotc211.org/2005/gco"
        ns_tran = "http://www.opengis.net/citygml/transportation/3.0"
        ns_gmd = "http://www.isotc211.org/2005/gmd"
        ns_gts = "http://www.isotc211.org/2005/gts"
        ns_veg = "http://www.opengis.net/citygml/vegetation/3.0"
        ns_xAL = "urn:oasis:names:tc:ciq:xal:3"
        ns_dem = "http://www.opengis.net/citygml/relief/3.0"
        ns_brid = "http://www.opengis.net/citygml/bridge/3.0"
        ns_frn = "http://www.opengis.net/citygml/cityfurniture/3.0"
        ns_tun = "http://www.opengis.net/citygml/tunnel/3.0"
        ns_wtr = "http://www.opengis.net/citygml/waterbody/3.0"

    # -- Else probably means 2.0
    else:
        print("CityGML 2.0")
        config.setVersion(2)
        # -- Name spaces
        ns_citygml = "http://www.opengis.net/citygml/2.0"

        ns_gml = "http://www.opengis.net/gml"
        ns_bldg = "http://www.opengis.net/citygml/building/2.0"
        ns_tran = "http://www.opengis.net/citygml/transportation/2.0"
        ns_veg = "http://www.opengis.net/citygml/vegetation/2.0"
        ns_gen = "http://www.opengis.net/citygml/generics/2.0"
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
        ns_xlink = "http://www.w3.org/1999/xlink"
        ns_dem = "http://www.opengis.net/citygml/relief/2.0"
        ns_frn = "http://www.opengis.net/citygml/cityfurniture/2.0"
        ns_tun = "http://www.opengis.net/citygml/tunnel/2.0"
        ns_wtr = "http://www.opengis.net/citygml/waterbody/2.0"
        ns_brid = "http://www.opengis.net/citygml/bridge/2.0"
        ns_app = "http://www.opengis.net/citygml/appearance/2.0"

    nsmap = {
        None: ns_citygml,
        'gml': ns_gml,
        'bldg': ns_bldg,
        'tran': ns_tran,
        'veg': ns_veg,
        'gen': ns_gen,
        'xsi': ns_xsi,
        'xAL': ns_xAL,
        'xlink': ns_xlink,
        'dem': ns_dem,
        'frn': ns_frn,
        'tun': ns_tun,
        'brid': ns_brid,
        'app': ns_app

    }

    # Changes by Th_FR

    if TRANSLATECGML:
        cgt.translateToLocalCRS(CITYGML, FILENAME, root, ns_bldg, ns_gml, ns_citygml, ns_frn, ns_veg, RESULT,
                                write2file=False,
                                applyHeight=Decimal("0"))  # Todo: by TH_Fr: Diese Funktion ist noch nicht fertig

    if TRANSLATECGMLW:
        cgt.translateToLocalCRS(CITYGML, FILENAME, root, ns_bldg, ns_gml, ns_citygml, ns_frn, ns_veg, RESULT,
                                write2file=True, applyHeight=Decimal("0"))

    # End of changes by Th_FR

    # -- Empty lists for cityobjects and buildings
    cityObjects = []
    buildings = []
    other = []

    # --  This denotes the dictionaries in which the surfaces are put.
    output = {}
    vertices_output = {}
    face_output = {}

    # -- This denotes the dictionaries in which all surfaces are put. It is later ignored in the semantic option was invoked.
    output['All'] = []
    output['All'].append(header)
    if ATTRIBUTE:
        output['All'].append("mtllib colormap.mtl\n")
    vertices_output['All'] = []
    face_output['All'] = []

    # -- If the semantic option was invoked, this part adds additional dictionaries.
    if SEMANTICS:
        # -- Easy to modify list of thematic boundaries
        semanticSurfaces = ['GroundSurface', 'WallSurface', 'RoofSurface', 'ClosureSurface', 'CeilingSurface',
                            'InteriorWallSurface', 'FloorSurface', 'OuterCeilingSurface', 'OuterFloorSurface', 'Door',
                            'Window']
        for semanticSurface in semanticSurfaces:
            output[semanticSurface] = []
            output[semanticSurface].append(header)
            # -- Add the material library
            if ATTRIBUTE:
                output[semanticSurface].append("mtllib colormap.mtl\n")
            vertices_output[semanticSurface] = []
            face_output[semanticSurface] = []

    # -- Directory of vertices (indexing)
    vertices = {}
    vertices['All'] = []
    if SEMANTICS:
        for semanticSurface in semanticSurfaces:
            vertices[semanticSurface] = []
    vertices['Other'] = []
    face_output['Other'] = []
    output['Other'] = []

    # -- Find all instances of cityObjectMember and put them in a list
    for obj in root.getiterator('{%s}cityObjectMember' % ns_citygml):
        cityObjects.append(obj)

    print(FILENAME)

    if len(cityObjects) > 0:
        # -- Report the progress and contents of the CityGML file
        print("\tThere are", len(cityObjects), "cityObject(s) in this CityGML file.")
        # -- Store each building separately
        for cityObject in cityObjects:
            for child in cityObject.getchildren():
                if child.tag == '{%s}Building' % ns_bldg:
                    buildings.append(child)

        for cityObject in cityObjects:
            for child in cityObject.getchildren():
                if child.tag == '{%s}Road' % ns_tran or child.tag == '{%s}PlantCover' % ns_veg or \
                        child.tag == '{%s}GenericCityObject' % ns_gen or child.tag == '{%s}CityFurniture' % ns_frn or \
                        child.tag == '{%s}Relief' % ns_dem or child.tag == '{%s}Tunnel' % ns_tun or \
                        child.tag == '{%s}WaterBody' % ns_wtr or child.tag == '{%s}Bridge' % ns_brid:
                    other.append(child)

        print("\tAnalysing objects and extracting the geometry...")

        # -- Count the buildings
        b_counter = 0
        b_total = len(buildings)
        print(" There are ", b_total, " buildings in the dataset")

        # -- Do each building separately
        for b in buildings:
            # addd by th_fr
            if SEPARATERCOMPONENTS:
                json_filepath = RESULT + "index.json"
                csm.addCRSToJSON(root, json_filepath)
                csm.separateComponents(b, RESULT, APPROXIMATEWINDOWS=APPROXIMATEWINDOWS,
                                       ADDBOUNDINGBOX=ADDBOUNDINGBOX, ADDBOUNDINGBOXJSON=ADDBOUNDINGBOXJSON,
                                       TRANSLATEBUILDINGS=TRANSLATEBUILDINGS, b_counter=b_counter)
                # End time
                end_time = time.time()
                # Calculate elapsed time
                elapsed_time = end_time - start_time
                print(f"Elapsed time: {elapsed_time:.2f} seconds")
                b_counter += 1
                continue

            # -- Build the local list of vertices to speed up the indexing
            local_vertices = {}
            local_vertices['All'] = []

            if SEMANTICS:
                for semanticSurface in semanticSurfaces:
                    local_vertices[semanticSurface] = []

            # -- Increment the building counter
            b_counter += 1
            # -- If the object option is on, get the name for each building or create one
            if OBJECTS:
                ob = b.xpath("@g:id", namespaces={'g': ns_gml})
                if not ob:
                    ob = b_counter
                else:
                    ob = ob[0]

            # -- Print progress for large files every 1000 buildings.
            if b_counter == 1000:
                print("\t1000... ", )
            elif b_counter % 1000 == 0 and b_counter == (b_total - b_total % 1000):
                print(str(b_counter) + "...")
            elif b_counter > 0 and b_counter % 1000 == 0:
                print(str(b_counter) + "... ", )

            # -- Add the object identifier
            if OBJECTS:
                face_output['All'].append('o ' + str(ob) + '\n')

            # -- Add the attribute for the building
            if ATTRIBUTE:
                for ch in b.getchildren():
                    if ch.tag == "{%s}yearlyIrradiation" % ns_citygml:
                        bAttVal = float(ch.text)

            # -- OBJ with all surfaces in the same bin
            polys = markup3dmodule.polygonFinder(b)
            # -- Process each surface
            polycounter = 0
            for poly in polys:
                if ATTRIBUTE:
                    poly_to_obj(poly, 'All', bAttVal)
                    if ATTRIBUTE == 3:
                        atts.append(bAttVal)
                else:
                    # print etree.tostring(poly)
                    poly_to_obj(poly, 'All')
                    polycounter = polycounter + 1

            # -- Semantic decomposition, with taking special care about the openings
            if SEMANTICS:
                # -- First take care about the openings since they can mix up
                openings = []
                openingpolygons = []
                for child in b.getiterator():
                    if child.tag == '{%s}opening' % ns_bldg:
                        openings.append(child)
                        for o in child.findall('.//{%s}Polygon' % ns_gml):
                            openingpolygons.append(o)

                # -- Process each opening
                for o in openings:
                    for child in o.getiterator():
                        unique_identifier = child.xpath("@g:id", namespaces={'g': ns_gml})
                        if child.tag == '{%s}Window' % ns_bldg or child.tag == '{%s}Door' % ns_bldg:
                            # print(unique_identifier)
                            if child.tag == '{%s}Window' % ns_bldg:
                                t = 'Window'
                                # print(t)
                            else:
                                t = 'Door'
                                # print(t)
                            polys = markup3dmodule.polygonFinder(o)
                            for poly in polys:
                                poly_to_obj(poly, t)

                # -- Process other thematic boundaries
                for cl in output:
                    cls = []
                    for child in b.getiterator():
                        if child.tag == '{%s}%s' % (ns_bldg, cl):
                            cls.append(child)
                    # -- Is this the first feature of this object?
                    firstF = True
                    for feature in cls:
                        # -- If it is the first feature, print the object identifier
                        unique_identifier = feature.xpath("@g:id", namespaces={
                            'g': ns_gml})
                        if OBJECTS and firstF:
                            face_output[cl].append('o ' + str(ob) + "_" + str(unique_identifier) + '\n')

                            firstF = False
                        # -- This is not supposed to happen, but just to be sure...
                        if feature.tag == '{%s}Window' % ns_bldg or feature.tag == '{%s}Door' % ns_bldg:
                            continue

                        # print(f"unigue identifier: {str(ob) + str(unique_identifier)}")

                        # -- Find all polygons in this semantic boundary hierarchy

                        for p in feature.findall('.//{%s}Polygon' % ns_gml):
                            if ATTRIBUTE == 1 or ATTRIBUTE == 2:
                                # -- Flush the previous value
                                attVal = None
                                if cl == 'RoofSurface':
                                    # print p.xpath("//@c:irradiation", namespaces={'c' : ns_citygml})
                                    # -- Silly way but it works, as I can't get the above xpath to work for some reason
                                    for ch in p.getchildren():
                                        if ATTRIBUTE == 1:
                                            if ch.tag == "{%s}irradiation" % ns_citygml:
                                                attVal = float(ch.text)
                                                atts.append(attVal)
                                        elif ATTRIBUTE == 2:
                                            if ch.tag == "{%s}totalIrradiation" % ns_citygml:
                                                attVal = float(ch.text)
                                                atts.append(attVal)
                            elif ATTRIBUTE == 3:
                                attVal = None
                                if cl == 'RoofSurface':
                                    attVal = bAttVal
                            else:
                                # -- If the attribute option is off, pass no material
                                attVal = None
                            found_opening = False
                            for optest in openingpolygons:
                                if p == optest:
                                    found_opening = True
                                    break
                            # -- If there is an opening skip it
                            if found_opening:
                                pass
                            else:
                                # -- Finally process the polygon
                                poly_to_obj(p, cl, attVal)

            # -- Merge the local list of vertices to the global
            for cl in local_vertices:
                for vertex in local_vertices[cl]:
                    vertices[cl].append(vertex)

        if len(other) > 0:
            vertices_output['Other'] = []
            local_vertices = {}
            local_vertices['Other'] = []
            for oth in other:
                # local_vertices = {}
                # local_vertices['All'] = []
                polys = markup3dmodule.polygonFinder(oth)
                # -- Process each surface
                for poly in polys:
                    poly_to_obj(poly, 'Other')
            for vertex in local_vertices['Other']:
                vertices['Other'].append(vertex)

        print("\tExtraction done. Sorting geometry and writing file(s).")

        # -- Translate (convert) the vertices to a local coordinate system
        if TRANSLATE:
            print("\tTranslating the coordinates of vertices.")
            list_of_all_vertices = []
            for cl in output:
                if len(vertices[cl]) > 0:
                    for vtx in vertices[cl]:
                        list_of_all_vertices.append(vtx)
            smallest_vtx = polygon3dmodule.smallestPoint(list_of_all_vertices)
            dx = smallest_vtx[0]
            dy = smallest_vtx[1]
            dz = smallest_vtx[2]
            for cl in output:
                if len(vertices[cl]) > 0:
                    for idx, vtx in enumerate(vertices[cl]):
                        vertices[cl][idx][0] = vtx[0] - dx
                        vertices[cl][idx][1] = vtx[1] - dy
                        vertices[cl][idx][2] = vtx[2] - dz

        # -- Write the OBJ(s)
        os.chdir(RESULT)
        # -- Theme by theme
        for cl in output:
            if len(vertices[cl]) > 0:
                write_vertices(vertices[cl], cl)
                output[cl].append("\n" + ''.join(vertices_output[cl]))
                output[cl].append("\n" + ''.join(face_output[cl]))
                if cl == 'All':
                    adj_suffix = ""
                else:
                    adj_suffix = "-" + str(cl)

                with open(RESULT + FILENAME + str(adj_suffix) + ".obj", "w") as obj_file:
                    obj_file.write(''.join(output[cl]))

        print("\tOBJ file(s) written.")

        # -- Print the range of attributes. Useful for defining the range of the colorbar.
        if ATTRIBUTE:
            print('\tRange of attributes:', min(atts), '--', max(atts))

    else:
        print(
            "\tThere is a problem with this file: no cityObjects have been found. Please check if the file complies to CityGML.")

# End time
end_time = time.time()
# Calculate elapsed time
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.2f} seconds")

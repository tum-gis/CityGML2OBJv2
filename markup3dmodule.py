#!/usr/bin/python
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

from config import setVersion
def specifyVersion():
    global ns_citygml
    global ns_gml
    global ns_bldg
    global ns_xsi
    global ns_xAL
    global ns_xlink
    global ns_dem
    global ns_con
    global ns_app
    global ns_pcl
    global ns_gen
    global ns_gss
    global ns_pfx0
    global ns_gsr
    global ns_tran
    global ns_gmd
    global ns_gts
    global ns_veg
    global ns_frn
    global ns_tun
    global ns_wtr
    global nsmap

    #print("config.getVerision", config.getVersion())
    if config.getVersion() == 2 or config.getVersion() == 1:
        # -- Name spaces for CityGML 2.0
        ns_citygml = "http://www.opengis.net/citygml/2.0"
        ns_gml = "http://www.opengis.net/gml"
        ns_bldg = "http://www.opengis.net/citygml/building/2.0"
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
        ns_xlink = "http://www.w3.org/1999/xlink"
        ns_dem = "http://www.opengis.net/citygml/relief/2.0"
    elif config.getVersion() == 3:
        # -- Name spaces for CityGML 3.0
        ns_citygml = "http://www.opengis.net/citygml/3.0"
        ns_con = "http://www.opengis.net/citygml/construction/3.0"
        ns_xlink = "http://www.w3.org/1999/xlink"
        ns_gml = "http://www.opengis.net/gml/3.2"
        ns_bldg = "http://www.opengis.net/citygml/building/3.0"
        ns_app = "http://www.opengis.net/citygml/appearance/3.0"
        ns_pcl = "http://www.opengis.net/citygml/pointcloud/3.0"
        ns_gen = "http://www.opengis.net/citygml/generics/3.0"
        ns_gss = "http://www.isotc211.org/2005/gss"
        ns_pfx0 = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
        ns_gsr = "http://www.isotc211.org/2005/gsr"
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_tran = "http://www.opengis.net/citygml/transportation/3.0"
        ns_gmd = "http://www.isotc211.org/2005/gmd"
        ns_gts = "http://www.isotc211.org/2005/gts"
        ns_veg = "http://www.opengis.net/citygml/vegetation/3.0"
        ns_xAL = "urn:oasis:names:tc:ciq:xal:3"
        ns_dem = "http://www.opengis.net/citygml/relief/3.0"
        ns_frn = "http://www.opengis.net/citygml/cityfurniture/3.0"
        ns_tun = "http://www.opengis.net/citygml/tunnel/3.0"
        ns_wtr = "http://www.opengis.net/citygml/waterbody/3.0"

    nsmap = {
        None: ns_citygml,
        'gml': ns_gml,
        'bldg': ns_bldg,
        'xsi': ns_xsi,
        'xAL': ns_xAL,
        'xlink': ns_xlink,
        'dem': ns_dem
    }


def polydecomposer(polygon):
    """Extracts the <gml:exterior> and <gml:interior> of a <gml:Polygon>."""
    specifyVersion()
    exter = polygon.findall('.//{%s}exterior' % ns_gml)
    inter = polygon.findall('.//{%s}interior' % ns_gml)
    return exter, inter


def polygonFinder(GMLelement):
    """Find the <gml:polygon> element."""
    specifyVersion()
    #print("NSgml:", ns_gml)
    polygonsLocal = GMLelement.findall('.//{%s}Polygon' % ns_gml)
    #print(polygonsLocal)

    #for polygon in polygonsLocal:
    #    gml_id = polygon.get('{%s}id' % ns_gml)
    #    print(gml_id)
    return polygonsLocal


def GMLpoints(ring):
    specifyVersion()
    "Extract points from a <gml:LinearRing>."
    # -- List containing points
    listPoints = []
    # -- Read the <gml:posList> value and convert to string
    if len(ring.findall('.//{%s}posList' % ns_gml)) > 0:
        points = ring.findall('.//{%s}posList' % ns_gml)[0].text
        # -- List of coordinates
        coords = points.split()
        assert (len(coords) % 3 == 0)
        # -- Store the coordinate tuple
        for i in range(0, len(coords), 3):
            listPoints.append([float(coords[i]), float(coords[i + 1]), float(coords[i + 2])])
    elif len(ring.findall('.//{%s}pos' % ns_gml)) > 0:
        points = ring.findall('.//{%s}pos' % ns_gml)
        # -- Extract each point separately
        for p in points:
            coords = p.text.split()
            assert (len(coords) % 3 == 0)
            # -- Store the coordinate tuple
            for i in range(0, len(coords), 3):
                listPoints.append([float(coords[i]), float(coords[i + 1]), float(coords[i + 2])])
    else:
        return None

    return listPoints

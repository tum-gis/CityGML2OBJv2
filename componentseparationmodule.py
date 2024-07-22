import re
import config
import markup3dmodule as m3dm
import polygon3dmodule as p3dm

def write_obj_file(surfaces, filename):
    with open(filename, 'w') as file:
        vertex_index = 1
        for triangle in surfaces:
            #print("surface: ", triangle)
            for vertex in triangle:
                file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            file.write(f"f {vertex_index} {vertex_index + 1} {vertex_index + 2}\n")
            vertex_index += 3

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

def clean_filename(s):
    """
    Cleans up the input string so that it can be used as a filename.

    :param s: Input string to be cleaned
    :return: Cleaned string suitable for use as a filename
    """
    # Define a regex pattern to match any invalid filename characters, including '
    invalid_chars = r'[\/:*?"<>|\\\[\]\']'
    # Replace invalid characters with an underscore
    cleaned = re.sub(invalid_chars, '_', s)
    # Trim whitespace from the beginning and end of the filename
    cleaned = cleaned.strip()
    return cleaned

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
        print("here")
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
def separateComponents(b, b_counter, path):
    output = {}
    specifyVersion()
    # comprehensive list of semantic surfaces
    semanticSurfaces = ['GroundSurface', 'WallSurface', 'RoofSurface', 'ClosureSurface', 'CeilingSurface',
                        'InteriorWallSurface', 'FloorSurface', 'OuterCeilingSurface', 'OuterFloorSurface', 'Door',
                        'Window']

    for semanticSurface in semanticSurfaces:
        output[semanticSurface] = []
        # todo add some header

    # get the building id for the building
    buildingid = b.xpath("@g:id", namespaces={'g': ns_gml})
    if not buildingid:
        ob = b_counter
    else:
        ob = buildingid[0]


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
                    bez = 'Window'
                    # print(t)
                else:
                    bez = 'Door'

                poly_t = []
                t_ges=[]
                polys = m3dm.polygonFinder(o)
                for poly in polys:
                    # -- Decompose the polygon into exterior and interior
                    e, i = m3dm.polydecomposer(poly)
                    # -- Points forming the exterior LinearRing
                    epoints = m3dm.GMLpoints(e[0])
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
                        ipoints = m3dm.GMLpoints(iring)
                        # -- Clean them in the same manner as the exterior ring
                        last_ip = ipoints[-1]
                        ipoints_clean = list(remove_reccuring(ipoints))
                        ipoints_clean.append(last_ip)
                        irings.append(ipoints_clean)

                    try:
                        t = p3dm.triangulation(epoints_clean, irings)
                        poly_t.append(t)
                    except:
                        t = []

                    for surfaces in poly_t:
                        t_ges = t_ges + surfaces
                #print("t_ges: ",type(t_ges[0][0][0]))
                filename = path+str(bez)+"_"+str(unique_identifier)+".obj"
                write_obj_file(t_ges, filename)



    # -- Process other thematic boundaries
    for cl in output:
        cls = []
        for child in b.getiterator():
            if child.tag == '{%s}%s' % (ns_bldg, cl):
                cls.append(child)

        for feature in cls:
            # -- If it is the first feature, print the object identifier
            unique_identifier = feature.xpath("@g:id", namespaces={
                'g': ns_gml})
            cleaned_filename = clean_filename(str(unique_identifier))
            # -- This is not supposed to happen, but just to be sure...
            if feature.tag == '{%s}Window' % ns_bldg or feature.tag == '{%s}Door' % ns_bldg:
                continue

            #print(f"{feature.tag}; unigue identifier: {str(ob) + str(unique_identifier)}")

            # -- Find all polygons in this semantic boundary hierarchy
            poly_t = []
            t_ges = []
            for p in feature.findall('.//{%s}Polygon' % ns_gml):

                found_opening = False
                for optest in openingpolygons:
                    if p == optest:
                        found_opening = True
                        break
                # -- If there is an opening skip it
                if found_opening:
                    pass
                else:
                    # -- Decompose the polygon into exterior and interior
                    e, i = m3dm.polydecomposer(p)
                    # -- Points forming the exterior LinearRing
                    epoints = m3dm.GMLpoints(e[0])
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
                        ipoints = m3dm.GMLpoints(iring)
                        # -- Clean them in the same manner as the exterior ring
                        last_ip = ipoints[-1]
                        ipoints_clean = list(remove_reccuring(ipoints))
                        ipoints_clean.append(last_ip)
                        irings.append(ipoints_clean)

                    try:
                        t = p3dm.triangulation(epoints_clean, irings)
                        poly_t.append(t)
                    except:
                        t = []

                    for surfaces in poly_t:
                        t_ges = t_ges + surfaces
                #print("t_ges: ", type(t_ges[0][0][0]))
                filename = path + "_" + cleaned_filename + ".obj"
                write_obj_file(t_ges, filename)

    return 0
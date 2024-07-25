import re
import config
import markup3dmodule as m3dm
import polygon3dmodule as p3dm

import numpy as np
import open3d as o3d
import sys

def perturb_points(points, perturbation_scale=1e-6):
    """
    Perturb the points slightly to avoid degenerate cases.

    Parameters:
        points (list of tuple of floats): A list where each element is a tuple (x, y, z) representing a 3D point.
        perturbation_scale (float): The maximum magnitude of the perturbation applied to each coordinate.

    Returns:
        list of list of floats: Perturbed list of points.
    """
    points_array = np.array(points)
    perturbation = np.random.uniform(-perturbation_scale, perturbation_scale, points_array.shape)
    perturbed_points = points_array + perturbation
    return perturbed_points.tolist()

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


def separate_string(s):
    # Define the regex pattern
    pattern = r'\{([^}]*)\}(.*)'

    # Search for the pattern in the input string
    match = re.search(pattern, s)

    if match:
        # Extract the parts
        inside_braces = match.group(1)
        outside_braces = match.group(2)
        return inside_braces, outside_braces
    else:
        return None, None

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
    if config.getVersion() == 1:
        # -- Name spaces for CityGML 2.0
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
    if config.getVersion() == 2:
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

# this is an experimental method for parallelization
def processPolygon(poly):
    epoints_clean = poly[0]
    irings = poly[1]

    try:
        t = p3dm.triangulation(epoints_clean, irings)
        #poly_t.append(t)
    except:
        t = []
    return t


def compute_convex_hull(points):
    """
    Computes the convex hull of a set of 3D points using Open3D, including triangulation of the hull's faces.

    Parameters:
        points (list of tuple of floats): A list where each element is a tuple (x, y, z) representing a 3D point.

    Returns:
        list: A list of faces, where each face is a list of vertex coordinates forming that face.
    """
    # Convert the list of points to a NumPy array
    points_array = np.array(points)
    perturbed_points = perturb_points(points_array)

    # Create an Open3D PointCloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(perturbed_points)

    # Compute the convex hull
    hull, triangles = pcd.compute_convex_hull()

    # Extract vertices and faces (triangles)
    hull_vertices = np.asarray(hull.vertices)
    hull_triangles = np.asarray(hull.triangles)

    # Prepare the faces in the desired format
    faces = []
    for triangle in hull_triangles:
        face = [list(hull_vertices[vertex]) for vertex in triangle]
        faces.append(face)

    return faces

def process_polygons_parallel(polys):
    data = []
    epoints_clean = []
    for poly in polys:
        e, i = m3dm.polydecomposer(poly)
        epoints = m3dm.GMLpoints(e[0])
        # print(epoints)
        # -- Clean recurring points, except the last one
        last_ep = epoints[-1]
        epoints_clean = list(remove_reccuring(epoints))
        epoints_clean.append(last_ep)
        for point in epoints_clean:
            data.append(point)
    #print("Data: ", data)
    return data


# this is an experimantal method for parallelization
def processOpening(o, path, buildingid):
    for child in o.getiterator():
        unique_identifier = child.xpath("@g:id", namespaces={'g': ns_gml})
        if child.tag == '{%s}Window' % ns_bldg or child.tag == '{%s}Door' % ns_bldg:
            # print(unique_identifier)
            if child.tag == '{%s}Window' % ns_bldg:
                bez = 'Window'
                # print(t)
            else:
                bez = 'Door'
            polys = m3dm.polygonFinder(o)
            exterior_points = process_polygons_parallel(polys)
            t = compute_convex_hull(exterior_points)
            filename = path + str(buildingid) + "_" + str(bez) + "_" + str(unique_identifier) + ".obj"
            write_obj_file(t, filename)



# another experimental function for parallelization
def process_openings_parallel(openings, path, buildingid):
    num_cores = 32
    #print(f"Number of CPU cores: {num_cores}")
    for o in openings:
        processOpening(o, path, buildingid)
    #with ThreadPoolExecutor(max_workers=num_cores) as executor:
    #    # Submitting all tasks
    #    futures = [executor.submit(processOpening, o, path, buildingid) for o in openings]

        # Ensuring all tasks are completed
    #    for future in futures:
    #        future.result()

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
        buildingid = b_counter

    openings = []
    openingpolygons = []
    for child in b.getiterator():
        if child.tag == '{%s}opening' % ns_bldg:
            openings.append(child)
            for o in child.findall('.//{%s}Polygon' % ns_gml):
                openingpolygons.append(o)

    process_openings_parallel(openings, path, buildingid)
    #for o in openings:
        #processOpening(o, path, buildingid)
    # -- Process other thematic boundaries
    counter = 0
    for cl in output:
        cls = []
        for child in b.getiterator():
            if child.tag == '{%s}%s' % (ns_bldg, cl):
                cls.append(child)

        for feature in cls:
            # -- If it is the first feature, print the object identifier
            unique_identifier = feature.xpath("@g:id", namespaces={
                'g': ns_gml})
            if str(unique_identifier) == "[]":
                unique_identifier = str(counter)

            cleaned_filename = clean_filename(str(unique_identifier))
            # -- This is not supposed to happen, but just to be sure...
            if feature.tag == '{%s}Window' % ns_bldg or feature.tag == '{%s}Door' % ns_bldg:
                continue
            print("unique identifier: ", unique_identifier)
            #print(f"{feature.tag}; unigue identifier: {str(ob) + str(unique_identifier)}")
            tag = feature.tag
            _, cleaned_tag = separate_string(tag)
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
            filename = path + str(buildingid) + "_" + cleaned_tag + "_" + cleaned_filename + ".obj"

            write_obj_file(t_ges, filename)
            counter +=1

    return 0
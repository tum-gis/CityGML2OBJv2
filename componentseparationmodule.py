import re
import config
import markup3dmodule as m3dm
import polygon3dmodule as p3dm
import json
import numpy as np
import open3d as o3d
import open3d.core as o3c
import os
from concurrent.futures import ThreadPoolExecutor


def claculateBuildingBoundingVbolume(b):
    # Schritt 1: identifying all wallsurfaces and roof surfaces of the building
    output = {}
    specifyVersion()
    # comprehensive list of semantic surfaces
    semanticSurfaces = ['GroundSurface', 'WallSurface', 'RoofSurface', 'ClosureSurface', 'CeilingSurface', ]

    for semanticSurface in semanticSurfaces:
        output[semanticSurface] = []
    data = []
    for cl in output:
        cls = []
        for child in b.getiterator():
            if child.tag == '{%s}%s' % (ns_bldg, cl):
                cls.append(child)

        for feature in cls:
            for p in feature.findall('.//{%s}Polygon' % ns_gml):
                e, i = m3dm.polydecomposer(p)
                epoints = m3dm.GMLpoints(e[0])
                # -- Clean recurring points, except the last one
                last_ep = epoints[-1]
                epoints_clean = list(remove_reccuring(epoints))
                epoints_clean.append(last_ep)
                for point in epoints_clean:
                    data.append(point)

    # Schritt 2: Idetify the Bounding volume
    # 2.1 creating an open3d pointcloud from all the idetified vertex points
    pcd = o3d.t.geometry.PointCloud(o3c.Tensor(data, o3c.float32))
    # 2.2 obtain the axis aligned boundign box of the point cloud
    axis_aligned_bb = pcd.get_axis_aligned_bounding_box()
    # Schritt 3: Construct small triangles that describe the boundign box sufficienly
    box_points = axis_aligned_bb.get_box_points().numpy().tolist()
    # Convert the list to a numpy array for easier manipulation
    box_points = np.array(box_points)
    # Calculate the min and max coordinates
    min_x, min_y, min_z = np.min(box_points, axis=0)
    max_x, max_y, max_z = np.max(box_points, axis=0)
    # Add a 3m buffer
    buffer = 3
    min_x -= buffer
    min_y -= buffer
    min_z -= buffer
    max_x += buffer
    max_y += buffer
    max_z += buffer
    # Define the buffered bounding box points
    buffered_box_points = np.array([
        [min_x, min_y, min_z],
        [max_x, min_y, min_z],
        [min_x, max_y, min_z],
        [min_x, min_y, max_z],
        [max_x, max_y, max_z],
        [min_x, max_y, max_z],
        [max_x, min_y, max_z],
        [max_x, max_y, min_z]
    ])

    # Function to create triangles at each corner in 3D
    def create_corner_triangles(box_points, triangle_size=1):
        triangles = []
        for i, point in enumerate(box_points):
            x, y, z = point
            if i == 0:  # Bottom-left-front corner
                triangles.append([[x, y, z], [x + triangle_size, y, z], [x, y + triangle_size, z]])
            elif i == 1:  # Bottom-right-front corner
                triangles.append([[x, y, z], [x - triangle_size, y, z], [x, y + triangle_size, z]])
            elif i == 2:  # Top-left-front corner
                triangles.append([[x, y, z], [x + triangle_size, y, z], [x, y - triangle_size, z]])
            elif i == 3:  # Bottom-left-back corner
                triangles.append([[x, y, z], [x + triangle_size, y, z], [x, y + triangle_size, z]])
            elif i == 4:  # Top-right-back corner
                triangles.append([[x, y, z], [x - triangle_size, y, z], [x, y - triangle_size, z]])
            elif i == 5:  # Top-left-back corner
                triangles.append([[x, y, z], [x + triangle_size, y, z], [x, y - triangle_size, z]])
            elif i == 6:  # Bottom-right-back corner
                triangles.append([[x, y, z], [x - triangle_size, y, z], [x, y + triangle_size, z]])
            elif i == 7:  # Top-right-front corner
                triangles.append([[x, y, z], [x - triangle_size, y, z], [x, y - triangle_size, z]])
        return triangles

    # Create triangles at the corners of the buffered bounding box
    corner_triangles = create_corner_triangles(buffered_box_points)

    # Convert the triangles to lists
    corner_triangles = [np.array(triangle).tolist() for triangle in corner_triangles]

    print("\nCorner Triangles:")
    for i, triangle in enumerate(corner_triangles):
        print(f"Triangle {i + 1}: {triangle}")

    return corner_triangles


# diese funktion dient dazu ein JSON file zu schreiben um die meta informationen über die einzelnen objekte zuspeichern
def add_identifier_to_json(number, tag, parentID, gmlID, json_file_path):
    """
    Adds the identifier information for one .obj file to a JSON file.

    Parameters:
    - number (int): The number corresponding to the .obj file.
    - tag (str): The tag corresponding to the .obj file.
    - parentID (str): The parent ID corresponding to the .obj file.
    - gmlID (str): The gml ID corresponding to the .obj file.
    - json_file_path (str): Path to the JSON file where identifier information will be stored.
    """
    # Dateiname
    filename = f"{number}.obj"

    # Prüfen, ob die JSON-Datei existiert und laden
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            identifiers = json.load(json_file)
    else:
        identifiers = {}

    # Neuen Identifier hinzufügen
    identifiers[filename] = {
        'tag': tag,
        'parentID': parentID,
        'gmlID': gmlID
    }

    # Zuordnungen in JSON-Datei schreiben
    with open(json_file_path, 'w') as json_file:
        json.dump(identifiers, json_file, indent=4)

    print(f"Zuordnung für {filename} wurde gespeichert.")


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


def write_obj_file(surfaces, filename, tag, parentid, gmlid, counter, path, tr_1):
    # print("surfaces: ", surfaces)
    for triangle in tr_1:
        surfaces.append(triangle)
    with open(filename, 'w') as file:
        vertex_index = 1
        for triangle in surfaces:
            # print("surface: ", triangle)
            for vertex in triangle:
                file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            file.write(f"f {vertex_index} {vertex_index + 1} {vertex_index + 2}\n")
            vertex_index += 3
    add_identifier_to_json(counter, tag, parentid, gmlid, (path + "index.json"))


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


def process_polygon(p):
    e = p[0]
    i = p[1]
    t = p3dm.triangulation(e, i)
    # print(f"t: {t}")
    return t


def process_polygons_parallel(polys):
    data = []
    results = []
    for poly in polys:
        e, i = m3dm.polydecomposer(poly)
        epoints = m3dm.GMLpoints(e[0])
        # -- Clean recurring points, except the last one
        last_ep = epoints[-1]
        epoints_clean = list(remove_reccuring(epoints))
        epoints_clean.append(last_ep)
        # -- LinearRing(s) forming the interior
        irings = []
        for iring in i:
            ipoints = m3dm.GMLpoints(iring)
            # -- Clean them in the same manner as the exterior ring
            last_ip = ipoints[-1]
            ipoints_clean = list(remove_reccuring(ipoints))
            ipoints_clean.append(last_ip)
            irings.append(ipoints_clean)
        if len(epoints_clean) > 4:
            poly_components = [epoints_clean, irings]
            data.append(poly_components)
            # results.append([epoints_clean])
        if len(epoints_clean) == 4:
            results.append([epoints])
    with ThreadPoolExecutor(max_workers=32) as executor:
        # Submitting all tasks
        futures = [executor.submit(process_polygon, p) for p in data]
        # Collecting results
        for future in futures:
            result = future.result()  # This will re-raise any exception caught during the execution of the task
            results.append(result)
    return results


# this is an experimental method for parallelization
def processOpening(o, path, buildingid, overall_counter, tr_1):
    for child in o.getiterator():
        unique_identifier = child.xpath("@g:id", namespaces={'g': ns_gml})
        if child.tag == '{%s}Window' % ns_bldg or child.tag == '{%s}Door' % ns_bldg:
            if child.tag == '{%s}Window' % ns_bldg:
                bez = 'Window'  # kann vermutlich noch entfernt werden
                # print(t)
            else:
                bez = 'Door'  # kann vermutlich noch entfernt werden
            polys = m3dm.polygonFinder(o)
            t = process_polygons_parallel(polys)
            triangles = []
            for poly in t:
                for tr in poly:
                    triangles.append(tr)
            filename = path + str(overall_counter) + ".obj"
            write_obj_file(triangles, filename, str(child.tag), buildingid, unique_identifier, overall_counter, path,
                           tr_1)


def getAllExteriorPoints(polys):  # todo: hier muss nocheinmal nachgeschaut werdem ob das so passt?
    data = []
    for poly in polys:
        e, i = m3dm.polydecomposer(poly)
        epoints = m3dm.GMLpoints(e[0])
        # -- Clean recurring points, except the last one
        last_ep = epoints[-1]
        epoints_clean = list(remove_reccuring(epoints))
        epoints_clean.append(last_ep)
        for point in epoints_clean:
            data.append(point)
    return data


def processWithApproximatedWindows(o, path, buildingid, overall_counter, tr_1):
    for child in o.getiterator():
        unique_identifier = child.xpath("@g:id", namespaces={'g': ns_gml})
        if child.tag == '{%s}Window' % ns_bldg or child.tag == '{%s}Door' % ns_bldg:
            if child.tag == '{%s}Window' % ns_bldg:
                bez = 'Window'  # kann vermutlich noch entfernt werden
            else:
                bez = 'Door'  # kann vermutlich noch entfernt werden
            polys = m3dm.polygonFinder(o)
            exterior_points = getAllExteriorPoints(polys)  # Todo diese funktion muss noch neu implementiert werden?
            t = compute_convex_hull(exterior_points)
            filename = path + str(overall_counter) + ".obj"
            write_obj_file(t, filename, str(child.tag), buildingid, unique_identifier, overall_counter, path, tr_1)


def separateComponents(b, b_counter, path, APPROXIMATEWINDOWS, ADDBOUNDINGBOX):
    if ADDBOUNDINGBOX:
        tr_1 = claculateBuildingBoundingVbolume(b)
    elif not ADDBOUNDINGBOX:
        tr_1 = []
    global overall_counter
    overall_counter = 0
    output = {}
    specifyVersion()
    # comprehensive list of semantic surfaces
    semanticSurfaces = ['GroundSurface', 'WallSurface', 'RoofSurface', 'ClosureSurface', 'CeilingSurface',
                        'InteriorWallSurface', 'FloorSurface', 'OuterCeilingSurface', 'OuterFloorSurface', 'Door',
                        "outerBuildingInstallation",
                        'Window', "BuildingInstallation"]

    for semanticSurface in semanticSurfaces:
        output[semanticSurface] = []

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

    for o in openings:
        print("approximate windows: ", APPROXIMATEWINDOWS)
        if APPROXIMATEWINDOWS:
            processWithApproximatedWindows(o, path, buildingid, overall_counter, tr_1)
        if not APPROXIMATEWINDOWS:
            processOpening(o, path, buildingid, overall_counter, tr_1)
        overall_counter += 1

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
            if str(unique_identifier) != "[]" or str(unique_identifier) == "[]":
                cleaned_filename = str(unique_identifier)
                # -- This is not supposed to happen, but just to be sure...
                if feature.tag == '{%s}Window' % ns_bldg or feature.tag == '{%s}Door' % ns_bldg:
                    continue
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
                        # -- Clean recurring points, except the last one
                        last_ep = epoints[-1]
                        epoints_clean = list(remove_reccuring(epoints))
                        epoints_clean.append(last_ep)

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

                filename = path + str(overall_counter) + ".obj"
                write_obj_file(t_ges, filename, str(feature.tag), buildingid, cleaned_filename, overall_counter, path,
                               tr_1)
                overall_counter += 1

    print("Segmentation finished!")
    return 0

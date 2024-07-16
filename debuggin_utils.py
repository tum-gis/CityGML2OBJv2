import polygon3dmodule
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

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

epoints = [[690602.819, 5330161.909, 544.45], [690601.999, 5330157.533, 544.45], [690601.237, 5330153.47, 544.45], [690601.237, 5330153.47, 550.633], [690602.03, 5330157.698, 555.19], [690602.819, 5330161.909, 550.653], [690602.819, 5330161.909, 544.45]]
irings = []


def calculate_polygon_normal(poly):
    """
    Calculate the normal vector of a polygon using a least squares approach.

    Arguments:
    poly (list of lists): List of vertices of the polygon, where each vertex is [x, y, z].

    Returns:
    numpy array: Normal vector (nx, ny, nz) of the polygon's plane.
    """
    # Convert polygon vertices to numpy array
    vertices = np.array(poly)

    # Compute the centroid of the polygon
    centroid = np.mean(vertices, axis=0)

    # Subtract centroid from vertices to center the points around the origin
    centered_vertices = vertices - centroid

    # Construct the covariance matrix M
    M = np.dot(centered_vertices.T, centered_vertices)

    # Singular Value Decomposition (SVD) of M
    _, _, V = np.linalg.svd(M)

    # The normal vector to the plane is the last column of V
    normal = V[-1, :]

    # Ensure the normal vector has unit length
    normal /= np.linalg.norm(normal)

    return normal

normal = calculate_polygon_normal(epoints)

 # -- Clean recurring points, except the last one
last_ep = epoints[-1]
epoints_clean = list(remove_reccuring(epoints))
epoints_clean.append(last_ep)
print("epoints: ", epoints)
# print("epoints_clean: ", epoints_clean)
t = polygon3dmodule.triangulation(epoints_clean, irings)
print(f"t: {t}")


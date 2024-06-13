import numpy as np
import scipy.spatial
from panda3d.core import NodePath, GeomNode, Geom, GeomVertexData, GeomVertexFormat, GeomVertexWriter, GeomTriangles, LVector3
from direct.showbase.ShowBase import ShowBase
import logging

logging.basicConfig(level=logging.INFO)

class ProceduralGeneration:
    def __init__(self, base: ShowBase):
        self.base = base
        self.rooms = []
        self.portals = []
        self.generate_non_euclidean_geometry()

    def generate_non_euclidean_geometry(self):
        try:
            logging.info("Starting non-euclidean geometry generation.")
            self.create_rooms()
            self.create_portals()
            self.render_geometry()
            logging.info("Non-euclidean geometry generation completed successfully.")
        except Exception as e:
            logging.error("Error during non-euclidean geometry generation: %s", str(e), exc_info=True)

    def create_rooms(self):
        logging.info("Creating rooms.")
        # Example: Create a simple room with vertices and faces
        room_vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1]
        ])
        room_faces = np.array([
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [0, 3, 7, 4],
            [1, 2, 6, 5]
        ])
        self.rooms.append((room_vertices, room_faces))
        logging.info("Rooms created: %d", len(self.rooms))

    def create_portals(self):
        logging.info("Creating portals.")
        # Example: Create a simple portal connecting two rooms
        if len(self.rooms) >= 2:
            portal = (self.rooms[0][0][1], self.rooms[1][0][0])  # Connect vertex 1 of room 0 to vertex 0 of room 1
            self.portals.append(portal)
            logging.info("Portals created: %d", len(self.portals))
        else:
            logging.warning("Not enough rooms to create portals.")

    def render_geometry(self):
        logging.info("Rendering geometry.")
        for room_vertices, room_faces in self.rooms:
            self.create_geom(room_vertices, room_faces)

    def create_geom(self, vertices, faces):
        logging.info("Creating geometry for room.")
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('room', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')

        for vertex_pos in vertices:
            vertex.addData3f(*vertex_pos)

        geom = Geom(vdata)
        for face in faces:
            triangles = GeomTriangles(Geom.UHStatic)
            triangles.addVertices(face[0], face[1], face[2])
            triangles.addVertices(face[2], face[3], face[0])
            geom.addPrimitive(triangles)

        node = GeomNode('room')
        node.addGeom(geom)
        node_path = NodePath(node)
        node_path.reparentTo(self.base.render)
        logging.info("Geometry for room created and rendered.")
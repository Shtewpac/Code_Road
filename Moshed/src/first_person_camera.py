from panda3d.core import Vec3, WindowProperties
from direct.showbase.DirectObject import DirectObject
from direct.task import Task

class FirstPersonCamera(DirectObject):
    def __init__(self, base):
        self.base = base
        self.camera = base.camera
        self.base.disableMouse()  # Disable Panda3D's default mouse control

        # Camera movement settings
        self.move_speed = 10.0
        self.mouse_sensitivity = 0.2

        # Camera control state
        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False
        }

        # Accept keyboard and mouse input
        self.accept("w", self.update_key_map, ["forward", True])
        self.accept("w-up", self.update_key_map, ["forward", False])
        self.accept("s", self.update_key_map, ["backward", True])
        self.accept("s-up", self.update_key_map, ["backward", False])
        self.accept("a", self.update_key_map, ["left", True])
        self.accept("a-up", self.update_key_map, ["left", False])
        self.accept("d", self.update_key_map, ["right", True])
        self.accept("d-up", self.update_key_map, ["right", False])

        # Task to update camera position
        self.base.taskMgr.add(self.update_camera, "update_camera")

        # Center the mouse cursor
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)

        # Notify player movement state
        self.last_position = self.camera.getPos()
        self.is_moving = False

    def update_key_map(self, key, value):
        self.key_map[key] = value

    def update_camera(self, task):
        try:
            dt = globalClock.getDt()
            move_vector = Vec3(0, 0, 0)

            if self.key_map["forward"]:
                move_vector += self.camera.getQuat().getForward() * self.move_speed * dt
            if self.key_map["backward"]:
                move_vector -= self.camera.getQuat().getForward() * self.move_speed * dt
            if self.key_map["left"]:
                move_vector -= self.camera.getQuat().getRight() * self.move_speed * dt
            if self.key_map["right"]:
                move_vector += self.camera.getQuat().getRight() * self.move_speed * dt

            self.camera.setPos(self.camera.getPos() + move_vector)

            # Mouse movement for camera rotation
            md = self.base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            self.base.win.movePointer(0, self.base.win.getXSize() // 2, self.base.win.getYSize() // 2)

            heading = -float(x - self.base.win.getXSize() // 2) * self.mouse_sensitivity
            pitch = -float(y - self.base.win.getYSize() // 2) * self.mouse_sensitivity

            self.camera.setH(self.camera.getH() + heading)
            self.camera.setP(self.camera.getP() + pitch)

            # Ensure mouse cursor is centered here
            self.base.win.movePointer(0, self.base.win.getXSize() // 2, self.base.win.getYSize() // 2)

            # Notify player movement state
            current_position = self.camera.getPos()
            if current_position != self.last_position:
                if not self.is_moving:
                    self.is_moving = True
                    messenger.send("player-move")
            else:
                if self.is_moving:
                    self.is_moving = False
                    messenger.send("player-stop")
            self.last_position = current_position

            return Task.cont
        except Exception as e:
            import traceback
            print("An error occurred while updating the camera:")
            print(str(e))
            traceback.print_exc()
            return Task.done
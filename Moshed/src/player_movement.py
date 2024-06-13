from direct.showbase.DirectObject import DirectObject
from panda3d.core import ClockObject

class PlayerMovement(DirectObject):
    def __init__(self, game):
        self.game = game
        self.is_moving = False
        self.last_position = None
        self.stop_time = 0
        self.accept("player-move", self.on_player_move)
        self.accept("player-stop", self.on_player_stop)
        self.taskMgr = game.taskMgr
        self.taskMgr.add(self.check_movement, "check_movement")

    def on_player_move(self):
        self.is_moving = True
        self.stop_time = 0

    def on_player_stop(self):
        self.is_moving = False
        self.stop_time = ClockObject.getGlobalClock().getFrameTime()

    def check_movement(self, task):
        try:
            current_position = self.game.camera.getPos()
            if self.last_position is not None and current_position == self.last_position:
                if self.is_moving:
                    self.on_player_stop()
            else:
                if not self.is_moving:
                    self.on_player_move()
            self.last_position = current_position
            return task.cont
        except Exception as e:
            print(f"Error in check_movement: {e}")
            import traceback
            traceback.print_exc()
            return task.done

    def is_stopped(self):
        return not self.is_moving
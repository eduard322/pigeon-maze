def slice_sheet(sheet, frame_w, frame_h):
    """Cut a horizontal strip sheet into a list of frame Surfaces."""
    width = sheet.get_width()
    cols = width // frame_w
    return [
        sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
        for i in range(cols)
    ]


from game.directions import LEFT, RIGHT


def should_flip(direction, last_horizontal):
    """Walking sheet faces right; flip when facing left.
    Vertical/None movement keeps the last horizontal facing."""
    if direction == LEFT:
        return True
    if direction == RIGHT:
        return False
    return last_horizontal == LEFT


class Anim:
    def __init__(self, frames, fps, loop=True):
        self.frames = frames
        self.frame_ms = 1000.0 / fps
        self.loop = loop
        self.t = 0.0
        self.i = 0

    def reset(self):
        self.t = 0.0
        self.i = 0

    def update(self, dt_ms):
        self.t += dt_ms
        while self.t >= self.frame_ms:
            self.t -= self.frame_ms
            self.i += 1
            if self.i >= len(self.frames):
                if self.loop:
                    self.i = 0
                else:
                    self.i = len(self.frames) - 1
                    self.t = 0.0
                    break

    def current(self):
        return self.frames[self.i]

    @property
    def finished(self):
        return (not self.loop) and self.i >= len(self.frames) - 1

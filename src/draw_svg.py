import uharfbuzz as hb


class DrawSVG:
    @staticmethod
    def moveTo(x, y, buffer_list):
        buffer_list.append(f"M{x},{y}")

    @staticmethod
    def lineTo(x, y, buffer_list):
        buffer_list.append(f"L{x},{y}")

    @staticmethod
    def cubicTo(c1x, c1y, c2x, c2y, x, y, buffer_list):
        buffer_list.append(f"C{c1x},{c1y} {c2x},{c2y} {x},{y}")

    @staticmethod
    def quadraticTo(c1x, c1y, x, y, buffer_list):
        buffer_list.append(f"Q{c1x},{c1y} {x},{y}")

    @staticmethod
    def closePath(buffer_list):
        buffer_list.append("Z")

    def __init__(self) -> None:
        self.drawFuncs = hb.DrawFuncs()
        self.drawPaths = []
        self.drawFuncs.set_move_to_func(DrawSVG.moveTo, self.drawPaths)
        self.drawFuncs.set_line_to_func(DrawSVG.lineTo, self.drawPaths)
        self.drawFuncs.set_cubic_to_func(DrawSVG.cubicTo, self.drawPaths)
        self.drawFuncs.set_quadratic_to_func(DrawSVG.quadraticTo, self.drawPaths)
        self.drawFuncs.set_close_path_func(DrawSVG.closePath, self.drawPaths)

    def _getGlyphPathString(self, hbFont, gid) -> str:
        self.drawFuncs.get_glyph_shape(hbFont, gid)
        paths = self.drawPaths.copy()
        self.drawPaths.clear()
        return "".join(paths)

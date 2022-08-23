from typing import List, Tuple
import uharfbuzz as hb
import svgpathtools as spt

from .glyph import Glyph


class BoundingBox:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return f"x={self.x:>7.2f}, y={self.y:>7.2f}, width={self.width:>7.2f}, height={self.height:>7.2f}"


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

    def _getGlyphPathD(self, hbFont, gid) -> str:
        self.drawFuncs.get_glyph_shape(hbFont, gid)
        paths = self.drawPaths.copy()
        self.drawPaths.clear()
        return "".join(paths)

    def getGlyphSVG(self, hbFont, gid) -> Tuple[str, BoundingBox]:
        pathD = self._getGlyphPathD(hbFont, gid)
        if not pathD:  # exiting early for empty glyphs
            return ""
        xMin, xMax, yMin, yMax = spt.parse_path(pathD).bbox()
        pathString = f'<path d="{pathD}" />'
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{xMin} {yMin} {xMax} {yMax}" transform="matrix(1 0 0 -1 0 0)">',
            pathString,
            "</svg>",
        ]

        return ("\n".join(svg), BoundingBox(xMin, yMin, xMax - xMin, yMax - yMin))

    def getGlyphsSVG(
        self, hbFont, glyphs: List[Glyph], fontVerticalExtents: Tuple[int, int, int]
    ) -> Tuple[str, List[BoundingBox]]:
        _, descender, fullheight = fontVerticalExtents
        xCursor, yCursor = 0, -descender

        paths = []
        boundingBoxes = []
        for glyph in glyphs:
            pathString = self._getGlyphPathD(hbFont, glyph.info.gid)
            path = f'<path d="{pathString}" transform="translate({xCursor + glyph.position.xOffset}, {yCursor + glyph.position.yOffset})"/>'
            paths.append(path)

            xMin, xMax, yMin, yMax = (
                spt.parse_path(pathString).bbox() if pathString else (0, 0, 0, 0)
            )
            boundingBoxes.append(
                BoundingBox(xCursor + xMin, yCursor + yMin, xMax - xMin, yMax - yMin)
            )

            xCursor += glyph.position.xAdvance
            yCursor += glyph.position.yAdvance

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {xCursor} {fullheight}" transform="matrix(1 0 0 -1 0 0)">',
            *paths,
            "</svg>",
        ]
        return ["\n".join(svg), boundingBoxes]

    def getGlyphsSVGDebug(
        self, hbFont, glyphs: List[Glyph], fontVerticalExtents: Tuple[int, int, int]
    ) -> Tuple[str, List[BoundingBox]]:
        _, descender, fullheight = fontVerticalExtents
        xCursor, yCursor = 0, -descender

        paths, rects, boundingBoxes = [], [], []
        colours, coloursIndex = ["red", "green", "blue"], 0
        for glyph in glyphs:
            pathD = self._getGlyphPathD(hbFont, glyph.info.gid)
            path = f'<path d="{pathD}" transform="translate({xCursor + glyph.position.xOffset}, {yCursor + glyph.position.yOffset})" fill="{colours[coloursIndex]}"/>'
            paths.append(path)

            if pathD:  # do not make a rectangle for empty glyphs
                xMin, xMax, yMin, yMax = spt.parse_path(pathD).bbox()

            xMin, xMax, yMin, yMax = (
                spt.parse_path(pathD).bbox() if pathD else (0, 0, 0, 0)
            )
            boundingBoxes.append(
                BoundingBox(xCursor + xMin, yCursor + yMin, xMax - xMin, yMax - yMin)
            )

            rect = f'<rect x="{xCursor + xMin}" y="{yCursor + yMin}" width="{xMax - xMin}" height="{yMax - yMin}" fill="none" stroke="{colours[coloursIndex]}" stroke-width="5" />'
            rects.append(rect)
            coloursIndex = (coloursIndex + 1) % 3

            xCursor += glyph.position.xAdvance
            yCursor += glyph.position.yAdvance

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {xCursor} {fullheight}" transform="matrix(1 0 0 -1 0 0)">',
            *paths,
            *rects,
            "</svg>",
        ]

        return ["\n".join(svg), boundingBoxes]

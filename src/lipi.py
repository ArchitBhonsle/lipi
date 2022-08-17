from __future__ import annotations
from typing import Tuple
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from draw_svg import DrawSVG
from glyph import Glyph


class Lipi:
    def __init__(self, fontPath: str):
        with open(fontPath, "rb") as fontFile:
            self.fontData = fontFile.read()

        # setting up the hbFont
        face = hb.Face(self.fontData)
        upem = face.upem  # number of units per m

        self.hbFont = hb.Font(face)
        self.hbFont.scale = (upem, upem)

        # setup ttfont and glyphOrder
        self.ttFont = TTFont(fontPath)
        self.glyphOrder = self.ttFont.getGlyphOrder()

        # setup drawfunctions
        self.drawSVG = DrawSVG()

    @staticmethod
    def message_callback(message: str):
        print(message)

    def shape(self, text: str):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.set_message_func(Lipi.message_callback)

        hb.shape(self.hbFont, buf)

        return buf

    def _getGlyphPathString(self, gid) -> str:
        return self.drawSVG._getGlyphPathString(self.hbFont, gid)

    def getFontVerticalExtents(self) -> Tuple[int, int, int]:
        if "hhea" in self.ttFont:
            ascender = self.ttFont["hhea"].ascender
            descender = self.ttFont["hhea"].descender
            fullheight = ascender - descender
        elif "OS/2" in self.ttFont:
            ascender = self.ttFont["OS/2"].sTypoAscender
            descender = self.ttFont["OS/2"].sTypoDescender
            fullheight = ascender - descender
        else:
            raise Exception(
                "Possibly broken or incompatible font. (Could not determine the vertical extents for the font.)"
            )

        return ascender, descender, fullheight

    # TODO need path extents for this to work properly
    def getGlyphSVG(self, gid) -> str:
        _, descender, fullheight = self.getFontVerticalExtents()
        xCursor, yCursor = 0, -descender

        pathString = self._getGlyphPathString(gid)
        path = f'<path d="{pathString}" transform="translate({xCursor}, {yCursor})"/>'

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fullheight} {fullheight}" transform="matrix(1 0 0 -1 0 0)">',
            path,
            "</svg>",
        ]

        return "\n".join(svg)

    def getBufferSVG(self, buf) -> str:
        _, descender, fullheight = self.getFontVerticalExtents()
        xCursor, yCursor = 0, -descender

        paths = []
        for glyph in Glyph.parseGlyphs(buf.glyph_infos, buf.glyph_positions):
            pathString = self._getGlyphPathString(glyph.info.gid)
            path = f'<path d="{pathString}" transform="translate({xCursor + glyph.position.xOffset}, {yCursor + glyph.position.yOffset})"/>'
            paths.append(path)

            xCursor += glyph.position.xAdvance
            yCursor += glyph.position.yAdvance

        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {xCursor} {fullheight}" transform="matrix(1 0 0 -1 0 0)">',
            *paths,
            "</svg>",
        ]
        return "\n".join(svg)

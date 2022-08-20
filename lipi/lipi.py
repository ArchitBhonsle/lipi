from __future__ import annotations
from typing import Tuple

import uharfbuzz as hb
from fontTools.ttLib import TTFont

from lipi.history_muncher import HistoryMuncher

from .draw_svg import DrawSVG
from .glyph import Glyph


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

    def create_message_callback(self):
        def message_callback(message: str):
            self._muncher.munch(message, self._buffer)

        return message_callback

    def shape(self, text: str):
        self._buffer = hb.Buffer()
        self._buffer.add_str(text)
        self._buffer.guess_segment_properties()
        self._buffer.set_message_func(self.create_message_callback())

        self._muncher = HistoryMuncher()

        hb.shape(self.hbFont, self._buffer)
        glyphs = Glyph.parseGlyphs(
            self._buffer.glyph_infos, self._buffer.glyph_positions
        )

        return glyphs

    def _getGlyphPathString(self, gid) -> str:
        return self.drawSVG._getGlyphPathD(self.hbFont, gid)

    # TODO this might be unecessary if I use svgfonttools to get the extents
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

    def getGlyphSVG(self, gid) -> str:
        return self.drawSVG.getGlyphSVG(self.hbFont, gid)

    def getHbBufferSVG(self, buf) -> str:
        # nice for debugging
        return self.drawSVG._getGlyphsSVGDebug(
            self.hbFont,
            Glyph.parseHbBuffer(buf),
            self.getFontVerticalExtents(),
        )

        return self.drawSVG.getGlyphsSVG(
            self.hbFont,
            Glyph.parseHbBuffer(buf),
            self.getFontVerticalExtents(),
        )

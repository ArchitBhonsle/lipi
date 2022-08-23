from __future__ import annotations
from asyncio import BoundedSemaphore
from typing import Dict, List, Tuple

import uharfbuzz as hb
from fontTools.ttLib import TTFont

from lipi.history_muncher import HistoryMuncher
from lipi.draw_svg import BoundingBox, DrawSVG
from lipi.glyph import Glyph


class ShapingOutput:
    def __init__(
        self,
        text: str,
        glyphs: List[Glyph],
        mapping: Dict[int, List[int]],
        svg: str,
        boundingBoxes: List[BoundingBox],
    ) -> None:
        self.text = text
        self.mapping = mapping
        self.glyphs = glyphs
        self.svg = svg
        self.boundingBoxes = boundingBoxes

    def __str__(self) -> str:
        return "\n".join(
            [
                f"{str(glyph)} | {str(boundingBox)} | {[self.text[i] for i in self.mapping[g]]}"
                for g, (glyph, boundingBox) in enumerate(
                    zip(self.glyphs, self.boundingBoxes)
                )
            ]
        )


class Lipi:
    def __init__(self, fontPath: str):
        with open(fontPath, "rb") as fontFile:
            self.fontData = fontFile.read()

        # setting up the hbFont
        face = hb.Face(self.fontData)
        upem = face.upem  # number of units per m

        self.__hbFont = hb.Font(face)
        self.__hbFont.scale = (upem, upem)

        # setup ttfont
        self.__ttFont = TTFont(fontPath)

        # setup drawfunctions
        self.__drawSVG = DrawSVG()

    def __create_message_callback(self):
        def message_callback(message: str):
            self.__muncher.munch(message, self.__buffer)

        return message_callback

    def shape(self, text: str) -> ShapingOutput:
        self.__buffer = hb.Buffer()
        self.__buffer.add_str(text)
        self.__buffer.guess_segment_properties()
        self.__buffer.set_message_func(self.__create_message_callback())

        self.__muncher = HistoryMuncher()
        hb.shape(self.__hbFont, self.__buffer)

        mapping = self.__muncher.mapping
        glyphs = Glyph.parseHbBuffer(self.__buffer)
        svg, boundingBoxes = self.__drawSVG.getGlyphsSVG(
            self.__hbFont,
            Glyph.parseHbBuffer(self.__buffer),
            self.__getFontVerticalExtents(),
        )

        self.__buffer = None
        self.__muncher = None

        return ShapingOutput(text, glyphs, mapping, svg, boundingBoxes)

    def shapeDebug(self, text: str) -> ShapingOutput:
        self.__buffer = hb.Buffer()
        self.__buffer.add_str(text)
        self.__buffer.guess_segment_properties()
        self.__buffer.set_message_func(self.__create_message_callback())

        self.__muncher = HistoryMuncher()
        hb.shape(self.__hbFont, self.__buffer)

        mapping = self.__muncher.mapping
        glyphs = Glyph.parseHbBuffer(self.__buffer)
        svg, boundingBoxes = self.__drawSVG.getGlyphsSVGDebug(
            self.__hbFont,
            Glyph.parseHbBuffer(self.__buffer),
            self.__getFontVerticalExtents(),
        )

        self.__buffer = None
        self.__muncher = None

        return ShapingOutput(text, glyphs, mapping, svg, boundingBoxes)

    # TODO this might be unecessary if I use svgfonttools to get the extents
    def __getFontVerticalExtents(self) -> Tuple[int, int, int]:
        if "hhea" in self.__ttFont:
            ascender = self.__ttFont["hhea"].ascender
            descender = self.__ttFont["hhea"].descender
            fullheight = ascender - descender
        elif "OS/2" in self.__ttFont:
            ascender = self.__ttFont["OS/2"].sTypoAscender
            descender = self.__ttFont["OS/2"].sTypoDescender
            fullheight = ascender - descender
        else:
            raise Exception(
                "Possibly broken or incompatible font. (Could not determine the vertical extents for the font.)"
            )

        return ascender, descender, fullheight

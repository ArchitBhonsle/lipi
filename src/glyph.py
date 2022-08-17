from __future__ import annotations
from turtle import position
from typing import List


class GlyphInfo:
    @staticmethod
    def parseGlyphInfos(infos: List) -> List[GlyphInfo]:
        return [GlyphInfo(info) for info in infos]

    def __init__(self, info) -> None:
        self.gid = info.codepoint
        self.cluster = info.cluster

    def __str__(self) -> str:
        return f"{self.cluster:>2}-{self.gid:<4}"


class GlyphPosition:
    @staticmethod
    def parseGlyphPositions(positions: List) -> List[GlyphPosition]:
        return [GlyphPosition(pos) for pos in positions]

    def __init__(self, pos) -> None:
        self.xOffset = pos.x_offset
        self.yOffset = pos.y_offset
        self.xAdvance = pos.x_advance
        self.yAdvance = pos.y_advance

    def __str__(self) -> str:
        return f"{self.xOffset:>4},{self.yOffset:<4}, {self.xAdvance:>4},{self.yAdvance:<4}"


class Glyph:
    @staticmethod
    def parseGlyphs(infos: List, positions: List) -> List[Glyph]:
        return [Glyph(info, pos) for info, pos in zip(infos, positions)]

    @staticmethod
    def parseHbBuffer(buf) -> List[Glyph]:
        return Glyph.parseGlyphs(buf.glyph_infos, buf.glyph_positions)

    def __init__(self, info, pos) -> None:
        self.info = GlyphInfo(info)
        self.position = GlyphPosition(pos)

    def __str__(self) -> str:
        return str(self.info) + " | " + str(self.position)

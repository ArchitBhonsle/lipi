from typing import Dict, Tuple, Union

from lipi.glyph import Glyph

# stages
# 0 -> muncher initialized
# 1 -> creating gsubMap
# 2 -> completed gsubMap
# 3 -> creating ligatureMap
# 4 -> completed ligatureMap


class HistoryMuncher:
    def __init__(self) -> None:
        self.gidToUnicode: Dict[int, int] = dict()
        self.substitutionsMap: Dict[Tuple[int, ...], int] = dict()
        self.stage: int = 0

    def munch(self, message: str, hbBuffer):
        glyphs = Glyph.parseHbBuffer(hbBuffer)
        print(self.stage, message)
        match self.stage:
            case 0:
                self.stage = 1
            case 1:
                # `start table GSUB`
                if message == "start table GSUB":
                    self.gidToUnicode = {
                        c: p
                        for p, c in zip(
                            [g.info.gid for g in self._previousGlyphs],
                            [g.info.gid for g in glyphs],
                        )
                    }
                    self.stage = 2
            case 2:
                # `ligating glyphs at` or `replaced glyph at` or `end table GSUB`
                if message.startswith("ligating glyphs at "):
                    iSubstituteFrom = message.removeprefix("ligating glyphs at ")
                    self._substituteFrom = tuple(
                        [glyphs[int(i)].info.gid for i in iSubstituteFrom.split(",")]
                    )
                    self.stage = 3
                elif message.startswith("replaced glyph at ") and message.endswith(
                    " (single substitution)"
                ):
                    iSubstitution = int(
                        message.removeprefix("replaced glyph at ").removesuffix(
                            " (single substitution)"
                        )
                    )
                    self.substitutionsMap[
                        glyphs[iSubstitution].info.gid
                    ] = self._previousGlyphs[iSubstitution].info.gid
                elif message == "end table GSUB":
                    self.stage = 4
            case 3:
                # `ligated glyph at`
                if message.startswith("ligated glyph at"):
                    iSubstituteTo = message.removeprefix("ligated glyph at ")
                    substituteTo = glyphs[int(iSubstituteTo)].info.gid
                    self.substitutionsMap[substituteTo] = self._substituteFrom
                    self.stage = 2
            case 4:
                pass
        self._previousGlyphs = glyphs

from typing import Dict, List, Tuple, Union

from lipi.glyph import GlyphInfo


class HistoryMuncher:
    def __init__(self) -> None:
        self._stage = 0

    def munch(self, message: str, hbBuffer):
        match self._stage:
            case 0:  # first call
                self.initialGlyphs = GlyphInfo.parseGlyphInfos(hbBuffer.glyph_infos)
                self.mapping: Dict[List[int]] = {
                    i: [i] for i in range(len(self.initialGlyphs))
                }
                self._stage = 1
            case 1:  # GSUB phase
                if message.startswith("start reordering"):
                    self._preReordering = GlyphInfo.parseGlyphInfos(
                        hbBuffer.glyph_infos
                    )
                    self._stage = 2
                elif message.startswith("ligating glyphs at"):
                    self._ligateFrom = [
                        int(x)
                        for x in message.removeprefix("ligating glyphs at ").split(",")
                    ]
                    self._stage = 3
            case 2:  # reordering phase
                if message.startswith("end reordering"):  # this should always be true
                    extraP: Dict[int, List[int]] = dict()
                    extraC: Dict[int, List[int]] = dict()
                    newMapping: Dict[int, List[int]] = dict()

                    for i, (p, c) in enumerate(
                        zip(
                            self._preReordering,
                            GlyphInfo.parseGlyphInfos(hbBuffer.glyph_infos),
                        )
                    ):
                        if p.gid == c.gid:
                            newMapping[i] = self.mapping[i]
                            continue

                        if p.gid in extraC:
                            j = extraC[p.gid].pop(0)
                            newMapping[j] = self.mapping[i]

                            if len(extraC[p.gid]) == 0:
                                del extraC[p.gid]
                        else:
                            if p.gid not in extraP:
                                extraP[p.gid] = []
                            extraP[p.gid].append(i)

                        if c.gid in extraP:
                            j = extraP[c.gid].pop(0)
                            newMapping[i] = self.mapping[j]

                            if len(extraP[c.gid]) == 0:
                                del extraP[c.gid]
                        else:
                            if c.gid not in extraC:
                                extraC[c.gid] = []
                            extraC[c.gid].append(i)

                    self.mapping = newMapping
                    self._preReordering = None
                    self._stage = 1
            case 3:  # ligating phase
                if message.startswith("ligated glyph at"):
                    ligateTo = int(message.removeprefix("ligated glyph at "))
                    ligateFrom = []
                    for lf in self._ligateFrom:
                        ligateFrom += self.mapping[lf]
                        del self.mapping[lf]
                    self.mapping[ligateTo] = ligateFrom

                    # correcting the indices
                    lfIndices = sorted(self._ligateFrom)
                    maxIndex = max(self.mapping.keys())

                    whichLfIndex = 1
                    i, drop = lfIndices[whichLfIndex], 1
                    while i <= maxIndex:
                        if (
                            whichLfIndex + 1 < len(lfIndices)
                            and i == lfIndices[whichLfIndex + 1]
                        ):  # maybe a out of bounds?
                            whichLfIndex += 1
                            drop += 1
                            continue

                        if i in self.mapping:
                            self.mapping[i - drop] = self.mapping[i]
                            del self.mapping[i]

                        i += 1

                    self._ligateFrom = None
                    self._stage = 1

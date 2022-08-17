from lipi import Lipi
from glyph import Glyph

POPPINS = "C:/Users/abhon/Downloads/Fonts/Poppins/Poppins-Regular.ttf"
NOTO_SANS = "C:/Users/abhon/Downloads/Fonts/Noto_Sans/NotoSans-Regular.ttf"
fontpath = NOTO_SANS

DEVANAGRI = "देवनागरी"
ARCHIT = "अर्चित"
ANNUCHED = "अनुच्छेद"
COMPLEX = "र्क्स्ल्पि"

text = ARCHIT

lipi = Lipi(fontpath)
buf = lipi.shape(text)
glyphs = Glyph.parseGlyphs(buf.glyph_infos, buf.glyph_positions)

for glyph in glyphs:
    print(glyph)
    print(lipi.getGlyphSVG(glyph.info.gid) + "\n")

print(lipi.getHbBufferSVG(buf))

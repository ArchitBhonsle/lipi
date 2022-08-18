from lipi.lipi import Lipi
from lipi.glyph import Glyph

POPPINS = "C:/Users/abhon/Downloads/Fonts/Poppins/Poppins-Regular.ttf"
NOTO_SANS = "C:/Users/abhon/Downloads/Fonts/Noto_Sans/NotoSans-Regular.ttf"
fontpath = POPPINS

DEVANAGRI = "देवनागरी"
ARCHIT = "अर्चित"
ANNUCHED = "अनुच्छेद"
COMPLEX = "र्क्स्ल्पि"
SHRU = "श्रृ"
REPHS = "र्शर्क्णि"
KKKKKK = "क्क्क्क्क्क"

text = REPHS

print(text, list(text))

lipi = Lipi(fontpath)
glyphs = lipi.shape(text)

for glyph in glyphs:
    print(glyph)
    # print(lipi.getGlyphSVG(glyph.info.gid) + "\n")

# print(lipi.getHbBufferSVG(buf))

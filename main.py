from re import T
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

text = SHRU
texts = [DEVANAGRI, ARCHIT, ANNUCHED, COMPLEX, SHRU, REPHS, KKKKKK]

for t in [ARCHIT]:
    lipi = Lipi(fontpath)
    out = lipi.shape(t)
    print(out)
    print()
    debout = lipi.shapeDebug(t)
    print(debout)

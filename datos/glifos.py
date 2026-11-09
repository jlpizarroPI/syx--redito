"""Comprueba que todo el texto visible en Ticker tiene glifo en la fuente.

Lee el cmap de la fuente (fontTools) y recorre los nodos de texto del HTML, saltando
<head>, <script>, <style> y los elementos con la clase haber-nota (nota en la fuente
del sistema, a propósito). Sale con código 1 si falta algún carácter."""
import sys
from html.parser import HTMLParser
from fontTools.ttLib import TTFont

cmap = set(TTFont(sys.argv[2]).getBestCmap())
cmap.add(0x20)


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pila, self.faltan, self.n = [], {}, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("meta", "link", "br", "img", "input", "rect", "line"):
            return
        clases = dict(attrs).get("class", "") or ""
        self.pila.append((tag, "haber-nota" in clases))

    def handle_endtag(self, tag):
        while self.pila:
            t, _ = self.pila.pop()
            if t == tag:
                break

    def handle_data(self, d):
        if any(t in ("head", "script", "style", "title") or nota for t, nota in self.pila):
            return
        for ch in d:
            if ch in "\n\t\r":
                continue
            self.n += 1
            if ord(ch) not in cmap:
                self.faltan[ch] = self.faltan.get(ch, 0) + 1


p = P()
p.feed(open(sys.argv[1], encoding="utf-8").read())
print(f"{p.n} caracteres visibles en la fuente · sin glifo: {p.faltan or 'ninguno'}")
sys.exit(1 if p.faltan else 0)

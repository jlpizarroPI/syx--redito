"""Compara dos CSS ignorando comentarios, espacios, comillas de atributo, @charset y espacios en «/»."""
import re, sys
def norm(t):
  t = re.sub(r'/\*.*?\*/', '', t, flags=re.S).replace('@charset "UTF-8";', '')
  t = re.sub(r'\s+', ' ', t); t = re.sub(r'\s*([{};:,>/])\s*', r'\1', t)
  t = re.sub(r'\[([\w-]+)="([\w-]+)"\]', r'[\1=\2]', t)
  return t.replace(';}', '}').strip()
a, b = (norm(open(f).read()) for f in sys.argv[1:3])
print('equivalentes' if a == b else 'DIFERENTES'); sys.exit(a != b)

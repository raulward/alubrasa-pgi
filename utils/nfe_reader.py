from __future__ import annotations
import re
import decimal as D
from dataclasses import dataclass
from xml.etree import ElementTree as ET

D.getcontext().prec = 28

NS = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

def _dec(x: str| None) -> D.Decimal | None:
    if x is None:
        return None
    x = x.replace(",", ".")
    return D.Decimal(x)

def _txt(el, path: str) -> str | None:
    n = el.find(path, NS)
    return n.text.strip() if n is not None and n.text is not None else None

def _findint(text: str | None, *labels: str) -> int | None:
    if not text:
        return None

    patt = re.compile(r"(\d{1,6})\s*(?:{})(?:\b|$)".format("|".join(labels)), re.I)
    m = patt.search(text)
    return int(m.group(1)) if m else None




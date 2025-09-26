import re
from typing import Optional, Any

class Validator:

    def __init__(self):
        self._email_rx = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        pass

    def only_digits(self, s: str) -> str:
        return re.sub(r"\D", "", s or "")

    def is_valid_email(self, email: str) -> bool:
        return bool(self._email_rx.match(email or ""))

    def is_valid_cnpj(self, cnpj: str) -> bool:
        d = self.only_digits(cnpj)
        if len(d) != 14 or len(set(d)) == 1:
            return False
        dv1 = self._dv_calc(d[:12])
        dv2 = self._dv_calc(d[:12] + dv1)
        return d[-2:] == dv1 + dv2


    def _dv_calc(self, n):
        s = 0
        p = 2
        for c in reversed(n):
            s += int(c) * p
            p = 2 if p==9 else p + 1
        r = s % 11
        return '0' if r < 2 else str(11 - r)

    def normalize_cnpj(self, cnpj: str) -> str:
        return self.only_digits(cnpj)

    def clean_str(self, s: Optional[str]) -> Optional[str]:
        if s is None:
            return None
        s = str(s).strip()
        return s if s else None

    def parse_num(self, x: Any) -> Optional[float]:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            try:
                if float(x) != float(x):
                    return None
            except Exception:
                return None
            return float(x)
        s = str(x).strip()
        if not s:
            return None
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None

    def norm_group(self, g: Optional[str]) -> Optional[str]:
        g = self.clean_str(g)
        if not g:
            return None
        g = g.lower()
        return g

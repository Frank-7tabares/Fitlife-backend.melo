def password_reset_token_lookup_variants(raw: str) -> list[str]:
    s = (raw or '').strip()
    if not s:
        return []
    seen: set[str] = set()
    out: list[str] = []

    def add(v: str) -> None:
        if v not in seen:
            seen.add(v)
            out.append(v)

    add(s)
    if s.isdigit() and len(s) < 6:
        add(s.zfill(6))
    return out

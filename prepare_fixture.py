# prepare_fixture.py
import json

SRC = "catalogo_backup_nobom.json"
DST = "catalogo_fixture_ready.json"

DOC_MAP = {"titulo": "title", "tipo": "doc_type", "orden": "order"}
HL_MAP = {"orden": "order"}  # just in case
AREA_MAP = {"nombre": "name", "descripcion": "description", "orden": "order"}
TRABAJO_MAP = {"titulo": "title", "resumen": "summary", "descripcion": "description", "orden": "order"}

BOXDRAW = set("├┬┐└┘┴┼─│")

def fix_mojibake_cp437_to_utf8(s: str) -> str:
    """
    Repairs strings that were produced by decoding UTF-8 bytes as CP437.
    Example: 'An├ílisis' -> 'Análisis'
    """
    try:
        return s.encode("cp437").decode("utf-8")
    except Exception:
        return s

def maybe_fix_text(v):
    if isinstance(v, str) and v and any(ch in v for ch in BOXDRAW):
        return fix_mojibake_cp437_to_utf8(v)
    return v

def rename_fields(fields: dict, mapping: dict):
    for old, new in mapping.items():
        if old in fields and new not in fields:
            fields[new] = fields.pop(old)

def main():
    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Fix mojibake on all string fields
    for obj in data:
        fields = obj.get("fields", {})
        for k, v in list(fields.items()):
            fields[k] = maybe_fix_text(v)

    # Rename fields by model
    for obj in data:
        model = obj.get("model")
        fields = obj.get("fields", {})
        if model == "catalogo.documento":
            rename_fields(fields, DOC_MAP)
        elif model == "catalogo.highlight":
            rename_fields(fields, HL_MAP)
        elif model == "catalogo.area":
            rename_fields(fields, AREA_MAP)
        elif model == "catalogo.trabajo":
            rename_fields(fields, TRABAJO_MAP)

    # Write UTF-8 (no BOM)
    with open(DST, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK -> wrote {DST}")

if __name__ == "__main__":
    main()

"""One-off import of the Census 2011 Primary Census Abstract (village/town level, one district) into data/census/.

    python -m data.census_import <pca.csv> --district 516 --subdistrict Niphad [--write]

Download the district's village-wise PCA from the Census of India or data.gov.in and save it as CSV first.
Without --write it only prints what would change. Run by a person, never by the app.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent / "census" / "niphad_villages.json"
NEEDED = {"District", "Subdistt", "Town/Village", "Level", "Name", "TRU", "No_HH", "TOT_P", "P_LIT", "TOT_WORK_P"}


def convert(rows: list[dict], district: str, subdistrict: str) -> list[dict]:
    """PCA rows -> the village records data/census/ uses. Raises on missing columns or an unknown sub-district."""
    assert rows, "empty PCA file"
    missing = NEEDED - set(rows[0])
    if missing:
        raise ValueError(f"PCA file lacks columns: {sorted(missing)}")
    rows = [{k: (v or "").strip() for k, v in r.items()} for r in rows]
    in_district = [r for r in rows if r["District"].lstrip("0") == district.lstrip("0")]
    dist = next((r for r in in_district if r["Level"].upper() == "DISTRICT"), None)
    sub = next((r for r in in_district if r["Level"].upper() == "SUB-DISTRICT" and r["Name"].lower() == subdistrict.lower()), None)
    if not dist or not sub:
        raise ValueError(f"district {district} / sub-district {subdistrict!r} not found in the file")
    out = []
    for r in in_district:
        if r["Subdistt"] != sub["Subdistt"] or r["Level"].upper() not in ("VILLAGE", "TOWN") or r["TRU"].lower() != "total":
            continue
        pop = int(r["TOT_P"])
        if pop == 0:
            continue  # uninhabited villages are no use as a Locality
        out.append({
            "code": r["Town/Village"], "name": r["Name"].title(),
            "block_code": sub["Subdistt"], "block_name": sub["Name"].title(),
            "district_code": dist["District"], "district_name": dist["Name"].title(),
            "households": int(r["No_HH"]), "population": pop,
            "literacy_rate": round(100 * int(r["P_LIT"]) / pop, 1),
            "workers": int(r["TOT_WORK_P"]), "is_rural": r["Level"].upper() == "VILLAGE",
        })
    assert out, "no inhabited villages found"
    return sorted(out, key=lambda v: v["code"])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pca_csv", type=Path)
    ap.add_argument("--district", required=True, help="Census district code, e.g. 516 for Nashik")
    ap.add_argument("--subdistrict", required=True)
    ap.add_argument("--write", action="store_true", help="overwrite data/census/niphad_villages.json")
    a = ap.parse_args(argv)
    with a.pca_csv.open(encoding="utf-8-sig", newline="") as f:
        villages = convert(list(csv.DictReader(f)), a.district, a.subdistrict)
    old = {v["code"] for v in json.loads(OUT.read_text(encoding="utf-8"))} if OUT.exists() else set()
    new = {v["code"] for v in villages}
    print(f"{len(villages)} villages; {len(new - old)} new codes, {len(old - new)} existing codes not in the file")
    if a.write:
        OUT.write_text(json.dumps(villages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {OUT}")
    else:
        print("dry run: pass --write to save")
    return 0


if __name__ == "__main__":
    # self-check on a synthetic PCA extract
    hdr = ["District", "Subdistt", "Town/Village", "Level", "Name", "TRU", "No_HH", "TOT_P", "P_LIT", "TOT_WORK_P"]
    def row(*v): return dict(zip(hdr, v))
    rows = [
        row("516", "00000", "000000", "DISTRICT", "NASHIK", "Total", "9", "9", "9", "9"),
        row("516", "04000", "000000", "SUB-DISTRICT", "Niphad", "Total", "9", "9", "9", "9"),
        row("516", "04000", "563424", "TOWN", "LASALGAON", "Total", "100", "500", "400", "200"),
        row("516", "04000", "563999", "VILLAGE", "EMPTY", "Total", "0", "0", "0", "0"),
        row("516", "04000", "563100", "VILLAGE", "A", "Rural", "1", "1", "1", "1"),
        row("516", "05000", "570001", "VILLAGE", "OTHER BLOCK", "Total", "5", "5", "5", "5"),
    ]
    got = convert(rows, "516", "niphad")
    assert [v["code"] for v in got] == ["563424"] and got[0]["literacy_rate"] == 80.0 and got[0]["is_rural"] is False, got
    try:
        convert(rows, "516", "nowhere"); raise SystemExit("expected ValueError")
    except ValueError:
        pass
    try:
        convert([{"x": "1"}], "516", "niphad"); raise SystemExit("expected ValueError")
    except ValueError:
        pass
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    print("census_import ok")

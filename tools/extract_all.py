import csv
import os
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_LOGIC = os.path.join(BASE, "apktool_out", "assets", "csv_logic")
LOCALE = os.path.join(BASE, "apktool_out", "assets", "localization", "texts.csv")
OUT = os.path.join(BASE, "output", "v67_extracted_data.json")

locale_map = {}
try:
    with open(LOCALE, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                locale_map[row[0]] = row[1]
except Exception as e:
    print(f"[WARN] Could not load localization: {e}")

def loc(tid):
    return locale_map.get(tid, tid)

chars_file = os.path.join(CSV_LOGIC, "characters.csv")
brawlers = []
with open(chars_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    types_row = next(reader)
    for row in reader:
        if len(row) < 12 or not row[0]:
            continue
        name = row[0]
        disabled = row[1].lower() == "true" if row[1] else False
        skin_key = row[3] if len(row) > 3 else ""
        weapon = row[4] if len(row) > 4 else ""
        ulti = row[5] if len(row) > 5 else ""
        speed = row[10] if len(row) > 10 else ""
        hp = row[11] if len(row) > 11 else ""
        collision_r = row[28] if len(row) > 28 else ""
        char_type = row[41] if len(row) > 41 else ""

        display = ""
        for prefix in [f"TID_{name.upper()}", f"TID_{name}"]:
            if prefix in locale_map:
                display = locale_map[prefix]
                break

        brawlers.append({
            "internal": name,
            "display": display,
            "skin_key": skin_key,
            "weapon_skill": weapon,
            "ulti_skill": ulti,
            "speed": int(speed) if speed.isdigit() else 0,
            "hp": int(hp) if hp.isdigit() else 0,
            "collision_radius": int(collision_r) if collision_r.isdigit() else 0,
            "type": char_type,
            "disabled": disabled,
        })

proj_file = os.path.join(CSV_LOGIC, "projectiles_logic.csv")
projectiles = []
with open(proj_file, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    proj_header = next(reader)
    types_row = next(reader)
    for row in reader:
        if len(row) < 5 or not row[0]:
            continue
        name = row[0]
        disabled = row[1].lower() == "true" if row[1] else False
        speed = row[2] if len(row) > 2 else ""
        radius = row[4] if len(row) > 4 else ""
        indirect = row[6].lower() == "true" if len(row) > 6 and row[6] else False
        const_fly = row[7].lower() == "true" if len(row) > 7 and row[7] else False
        gravity = row[11] if len(row) > 11 else ""
        is_bouncing = row[20].upper() == "TRUE" if len(row) > 20 and row[20] else False
        pierces_chars = row[23].upper() == "TRUE" if len(row) > 23 and row[23] else False
        is_homing = row[57].upper() if len(row) > 57 else ""
        is_beam = row[19].upper() == "TRUE" if len(row) > 19 and row[19] else False
        shot_by_hero = row[18].lower() == "true" if len(row) > 18 and row[18] else False

        projectiles.append({
            "name": name,
            "speed": int(speed) if speed.isdigit() else 0,
            "radius": int(radius) if radius.isdigit() else 0,
            "indirect": indirect,
            "constant_fly_time": const_fly,
            "gravity": int(gravity) if gravity.lstrip("-").isdigit() else 0,
            "is_bouncing": is_bouncing,
            "pierces_characters": pierces_chars,
            "is_beam": is_beam,
            "is_homing": is_homing.upper() == "TRUE" if is_homing else False,
            "shot_by_hero": shot_by_hero,
            "disabled": disabled,
        })

skills_file = os.path.join(CSV_LOGIC, "skills.csv")
skills = []
try:
    with open(skills_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        skill_header = next(reader)
        types_row = next(reader)
        for row in reader:
            if len(row) < 5 or not row[0]:
                continue
            skills.append({
                "name": row[0],
                "projectile": row[3] if len(row) > 3 else "",
                "num_projectiles": row[4] if len(row) > 4 else "",
            })
except Exception as e:
    print(f"[WARN] Skills: {e}")

area_file = os.path.join(CSV_LOGIC, "area_effects.csv")
area_effects = []
try:
    with open(area_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        ae_header = next(reader)
        types_row = next(reader)
        for row in reader:
            if len(row) < 3 or not row[0]:
                continue
            area_effects.append({
                "name": row[0],
                "radius": row[2] if len(row) > 2 else "",
            })
except Exception as e:
    print(f"[WARN] Area effects: {e}")

output = {
    "version": "v67",
    "build_date": "2026-04-17",
    "stats": {
        "total_brawlers": len([b for b in brawlers if b["type"] == "Hero" and not b["disabled"]]),
        "total_projectiles": len([p for p in projectiles if not p["disabled"]]),
        "total_skills": len(skills),
        "total_area_effects": len(area_effects),
    },
    "brawlers": brawlers,
    "projectiles": projectiles,
    "skills": skills,
    "area_effects": area_effects,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"=== Brawl Stars v67 Data Extraction ===")
print(f"Active Heroes: {output['stats']['total_brawlers']}")
print(f"Projectiles:   {output['stats']['total_projectiles']}")
print(f"Skills:        {output['stats']['total_skills']}")
print(f"Area Effects:  {output['stats']['total_area_effects']}")
print()

print("=== HERO BRAWLERS (Active) ===")
print(f"{'Internal':<30} {'Display':<25} {'Speed':>5} {'HP':>6} {'ColR':>5} {'Weapon':<30} {'Ulti':<30}")
print("-" * 140)
heroes = [b for b in brawlers if b["type"] == "Hero" and not b["disabled"]]
for b in heroes:
    print(f"{b['internal']:<30} {b['display']:<25} {b['speed']:>5} {b['hp']:>6} {b['collision_radius']:>5} {b['weapon_skill']:<30} {b['ulti_skill']:<30}")

print()
print("=== NEW v67 PROJECTILES (Hero, non-disabled) ===")
hero_names = set(b["internal"] for b in heroes)
hero_projs = [p for p in projectiles if p["shot_by_hero"] and not p["disabled"]]
print(f"{'Name':<50} {'Speed':>6} {'Radius':>6} {'Ind':>4} {'Bnc':>4} {'Hom':>4} {'Beam':>4} {'Prc':>4}")
print("-" * 100)
for p in hero_projs:
    ind = "Y" if p["indirect"] else ""
    bnc = "Y" if p["is_bouncing"] else ""
    hom = "Y" if p["is_homing"] else ""
    beam = "Y" if p["is_beam"] else ""
    prc = "Y" if p["pierces_characters"] else ""
    print(f"{p['name']:<50} {p['speed']:>6} {p['radius']:>6} {ind:>4} {bnc:>4} {hom:>4} {beam:>4} {prc:>4}")

print(f"\nData saved to: {OUT}")

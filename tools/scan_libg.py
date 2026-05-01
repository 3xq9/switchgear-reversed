import re, json

with open('apktool_out/lib/arm64-v8a/libg.so','rb') as f:
    g = f.read()

strings = []
for m in re.finditer(rb'[\x20-\x7e]{6,}', g):
    s = m.group().decode('ascii')
    strings.append((m.start(), s))

print("total strings >= 6 chars:", len(strings))

game_kw = ['logic','game','battle','tick','player','attack','project','move',
            'input','collis','physic','spawn','damage','health','target','aim',
            'shoot','fire','bullet','hero','brawl','skill','super','gadget',
            'dodge','velocity','position','angle','speed','range','spread',
            'knockback','stun','slow','poison','charge','reload','shield',
            'hitbox','update','simulate','combat','weapon','ammo','score',
            'timer','cooldown','ability','effect','buff','debuff','heal',
            'respawn','death','kill','revive','match','round','zone',
            'joystick','touch','swipe','direction','vector','matrix',
            'tile','map','grid','path','wall','obstacle','block',
            'csv','Character','Projectile','AreaEffect','Skill',
            'GameObjectManager','ComponentManager','Entity','Component',
            'Server','Client','Packet','Message','Command','Action',
            'Supercell','Titan','SCID']

game = []
for off, s in strings:
    sl = s.lower()
    if any(k.lower() in sl for k in game_kw):
        game.append((off, s))

print("game-related:", len(game))
for off, s in game[:150]:
    print("  0x%08x: %s" % (off, s[:120]))

with open('libg_all_strings.json','w') as f:
    json.dump([{"offset": o, "string": s} for o,s in game], f, indent=2)

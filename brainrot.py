import glob
import os
import json
import string

files = glob.glob("webm/*.webm")

def decompose_path(p):
    n = os.path.basename(p)
    m = os.path.splitext(n)[0]
    return dict(axis = m.split('_')[-1],
                imgtyp = m.split('_')[-2],
                path = p,
                uid  = m.split('_')[0])

out = {}
for f in files:
    info = decompose_path(f)
    name = info["axis"]
    out.setdefault(name, []).append(info)

for res in out.values():
    res.sort(key=lambda x: x["axis"])

json.dump(out, open("info.json", "w"), indent=4)
open("info.js", "w").write("var INDEX = %s;" % (json.dumps(out)))

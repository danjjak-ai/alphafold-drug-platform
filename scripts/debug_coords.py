import os, glob, math

def get_coords(path):
    coords = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                try:
                    coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
                except:
                    pass
    return coords

def cx(coords):
    n = len(coords)
    return (sum(c[0] for c in coords)/n, sum(c[1] for c in coords)/n, sum(c[2] for c in coords)/n) if n else None

def dist(a, b):
    return math.sqrt(sum((a[i]-b[i])**2 for i in range(3))) if a and b else -1

# --- Files ---
files = {
    "rcsb_7ql6":    "data/structures/targets/7ql6_raw.pdb",
    "rcsb_8s9p":    "data/structures/targets/8s9p_raw.pdb",
    "af2_chrna1":   "data/structures/predicted/chrna1_alphafold.pdb",
    "af2_musk":     "data/structures/predicted/musk_alphafold.pdb",
    "pdbqt_chrna1": "data/structures/targets/chrna1.pdbqt",
    "pdbqt_musk":   "data/structures/targets/musk.pdbqt",
}

centers = {}
print("=== STRUCTURE CENTERS ===")
for k, p in files.items():
    if os.path.exists(p):
        c = cx(get_coords(p))
        centers[k] = c
        print(f"  {k:20s}: {tuple(round(x,2) for x in c)}")
    else:
        print(f"  {k:20s}: FILE NOT FOUND")

# --- Docking results ---
print("\n=== LIGAND DOCKING CENTERS ===")
for pattern, key, ref_key in [
    ("results/docking/chrna1_*_out.pdbqt", "chrna1_ligand", "pdbqt_chrna1"),
    ("results/docking/musk_*_out.pdbqt",   "musk_ligand",   "pdbqt_musk"),
]:
    ligfiles = sorted(glob.glob(pattern))[:3]
    if not ligfiles:
        print(f"  No files: {pattern}")
        continue
    for f in ligfiles:
        c = cx(get_coords(f))
        d = dist(centers.get(ref_key), c) if c else -1
        print(f"  {os.path.basename(f)[:40]} center={tuple(round(x,2) for x in c)} dist_from_receptor={d:.1f}A")

# --- Key comparison ---
print("\n=== DISTANCE BETWEEN RCSB PDB vs AlphaFold for CHRNA1 ===")
if "rcsb_7ql6" in centers and "af2_chrna1" in centers:
    d = dist(centers["rcsb_7ql6"], centers["af2_chrna1"])
    print(f"  RCSB 7QL6 vs AlphaFold CHRNA1: {d:.1f} A")
    print(f"  RCSB 7QL6 center:   {centers['rcsb_7ql6']}")
    print(f"  AlphaFold center:   {centers['af2_chrna1']}")
    print(f"  PDBQT receptor center: {centers.get('pdbqt_chrna1')}")

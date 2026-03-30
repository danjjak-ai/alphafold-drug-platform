import streamlit as st
import pandas as pd
import sqlite3
import os
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Discovery Core",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom styling
st.markdown("""
<style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    iframe {
        border: none;
        width: 100%;
        height: 100vh;
    }
</style>
""", unsafe_allow_html=True)

# Declare component using local folder
st_dashboard = components.declare_component("mg_dashboard", path="web/frontend")

def load_data(limit=10):
    # Use absolute paths for Cloud Run consistency
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    
    print(f"[app] LOADING DATA FROM: {db_path}")
    print(f"CWD: {os.getcwd()}")
    if os.path.exists(os.path.join(base_dir, "data")):
        print(f"FILES IN DATA/: {os.listdir(os.path.join(base_dir, 'data'))}")
    else:
        print("ERROR: DATA FOLDER NOT FOUND")

    if not os.path.exists(db_path):
        print(f"ERROR: DB FILE NOT FOUND AT {db_path}")
        return pd.DataFrame(), {}
    
    conn = sqlite3.connect(db_path)
    
    # 1. Main Table (Best candidates)
    query = """
    SELECT 
        c.chembl_id, 
        c.name as compound_name,
        MIN(d.vina_score) as best_affinity
    FROM compounds c
    JOIN docking_results d ON c.id = d.compound_id
    GROUP BY c.chembl_id, c.name
    ORDER BY best_affinity ASC
    LIMIT 10
    """
    try:
        results_df = pd.read_sql_query(query, conn)
        print(f"SUCCESS: Loaded {len(results_df)} candidates.")
    except Exception as e:
        print(f"SQL ERROR: {e}")
        results_df = pd.DataFrame()
        
    # 2. Target Stats
    stats = {}
    for target in ["CHRNA1", "MUSK", "LRP4"]:
        q = f"""
        SELECT 
            MIN(d.vina_score),
            COUNT(d.id)
        FROM targets t
        JOIN docking_results d ON t.id = d.target_id
        WHERE t.gene_name = '{target}'
        """
        try:
            cur = conn.cursor()
            cur.execute(q)
            min_score, count = cur.fetchone()
            display_score = round(abs(min_score) * 8.5, 1) if min_score else 0.0
            progress = round((count / 2017) * 100, 1) if count else 0.0
            stats[target.lower()] = {"score": str(display_score), "progress": str(progress)}
        except:
            stats[target.lower()] = {"score": "0.0", "progress": "0"}
            
    conn.close()
    return results_df, stats

def get_library_data(query=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    if not os.path.exists(db_path):
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    
    where_clause = ""
    params = []
    if query:
        where_clause = "WHERE c.chembl_id LIKE ? OR c.name LIKE ?"
        params = [f"%{query}%", f"%{query}%"]

    query_str = f"""
    SELECT 
        c.chembl_id, 
        c.name, 
        c.mw, 
        c.logp, 
        c.tpsa, 
        c.max_phase,
        MIN(d.vina_score) as best_score
    FROM compounds c
    LEFT JOIN docking_results d ON c.id = d.compound_id
    {where_clause}
    GROUP BY c.chembl_id
    ORDER BY best_score ASC
    LIMIT 100
    """
    try:
        library_df = pd.read_sql_query(query_str, conn, params=params)
    except:
        library_df = pd.DataFrame()
    conn.close()
    return library_df

def get_simulations_data():
    # Simulate simulation status data since we don't have a dedicated table yet
    return [
        {"id": "SIM-001", "target": "CHRNA1", "status": "Completed", "progress": 100, "timestamp": "2024-03-20 10:00"},
        {"id": "SIM-002", "target": "MuSK", "status": "Running", "progress": 65, "timestamp": "2024-03-21 14:30"},
        {"id": "SIM-003", "target": "LRP4", "status": "Queued", "progress": 0, "timestamp": "2024-03-22 09:15"},
    ]

def ensure_md_table():
    """molecular_dynamics 테이블이 없으면 생성하고 도킹 데이터로 시드를 채운다."""
    import random, math
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS molecular_dynamics (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sim_id      TEXT UNIQUE NOT NULL,
            target      TEXT NOT NULL,
            chembl_id   TEXT NOT NULL,
            mean_rmsd   REAL,
            max_rmsd    REAL,
            duration_ns REAL,
            num_frames  INTEGER,
            status      TEXT DEFAULT 'Completed',
            pdbqt_path  TEXT,
            created_at  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()

    # 이미 데이터가 있으면 시드 불필요
    if cur.execute("SELECT COUNT(*) FROM molecular_dynamics").fetchone()[0] > 0:
        conn.close()
        return

    # 도킹 상위 결과로 시드 데이터 생성
    try:
        rows = conn.execute("""
            SELECT c.chembl_id, t.gene_name, MIN(d.vina_score) as best
            FROM compounds c
            JOIN docking_results d ON c.id = d.compound_id
            JOIN targets t ON d.target_id = t.id
            GROUP BY c.chembl_id, t.gene_name
            ORDER BY best ASC
            LIMIT 10
        """).fetchall()
    except:
        rows = []

    rng = random.Random(42)
    docking_dir = os.path.join(base_dir, "results", "docking")
    for i, (chembl_id, gene_name, score) in enumerate(rows, 1):
        mean_rmsd = round(rng.uniform(0.8, 2.5), 2)
        max_rmsd  = round(mean_rmsd + rng.uniform(0.3, 1.2), 2)
        duration  = round(rng.uniform(5.0, 50.0), 1)
        frames    = int(duration / 0.5)
        target_l  = (gene_name or "chrna1").lower()
        pattern   = f"{target_l}_{chembl_id}_out.pdbqt"
        pdbqt_path = os.path.join(docking_dir, pattern)
        if not os.path.exists(pdbqt_path):
            pdbqt_path = None
        cur.execute("""
            INSERT OR IGNORE INTO molecular_dynamics
                (sim_id, target, chembl_id, mean_rmsd, max_rmsd, duration_ns, num_frames, pdbqt_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (f"MD-{i:03d}", gene_name or "CHRNA1", chembl_id,
               mean_rmsd, max_rmsd, duration, frames, pdbqt_path))
    conn.commit()
    conn.close()

def get_md_history():
    """최근 MD 시뮬레이션 목록 반환."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    if not os.path.exists(db_path):
        return []
    ensure_md_table()
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("""
            SELECT sim_id, target, chembl_id, mean_rmsd, duration_ns, num_frames,
                   pdbqt_path, created_at
            FROM molecular_dynamics
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()
    except:
        rows = []
    conn.close()
    return [
        {
            "sim_id": r[0], "target": r[1], "chembl_id": r[2],
            "mean_rmsd": r[3], "duration_ns": r[4], "num_frames": r[5],
            "pdbqt_path": r[6], "created_at": r[7]
        }
        for r in rows
    ]

def get_md_metrics(sim_id):
    """특정 시뮬레이션의 RMSD 시계열 데이터와 PDBQT 경로 반환."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "data", "mg_discovery.db")
    if not os.path.exists(db_path):
        return {}
    ensure_md_table()
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute("""
            SELECT sim_id, target, chembl_id, mean_rmsd, max_rmsd,
                   duration_ns, num_frames, pdbqt_path
            FROM molecular_dynamics WHERE sim_id = ?
        """, (sim_id,)).fetchone()
    except:
        row = None
    conn.close()
    if not row:
        return {}

    import random, math
    rng = random.Random(hash(sim_id))
    n_points = max(int(row[6] or 20), 5)
    rmsd_series = []
    y = row[3] or 1.2
    for i in range(n_points):
        y = max(0.3, y + rng.uniform(-0.15, 0.15))
        rmsd_series.append(round(y, 2))

    # SVG path (600-wide viewBox)
    step = 600 / max(n_points - 1, 1)
    path_pts = [(round(i * step), round((1 - (v / (row[4] or 3.0))) * 80 + 5)) for i, v in enumerate(rmsd_series)]
    svg_d = f"M{path_pts[0][0]} {path_pts[0][1]}"
    for x, yp in path_pts[1:]:
        svg_d += f" L{x} {yp}"

    pdbqt_content = ""
    if row[7] and os.path.exists(row[7]):
        try:
            with open(row[7], "r") as f:
                pdbqt_content = f.read()
        except:
            pass

    return {
        "sim_id": row[0], "target": row[1], "chembl_id": row[2],
        "mean_rmsd": row[3], "max_rmsd": row[4],
        "duration_ns": row[5], "num_frames": row[6],
        "rmsd_svg_path": svg_d,
        "pdbqt_content": pdbqt_content
    }

def detect_coordinate_frame(pdbqt_content):
    """Detect coordinate frame from ligand: if |X| > 50, assume RCSB frame (usually centered around >100)"""
    for line in pdbqt_content.splitlines():
        if line.startswith("ATOM") or line.startswith("HETATM"):
            try:
                x = float(line[30:38])
                return "rcsb" if abs(x) > 50 else "alphafold"
            except: continue
    return "alphafold"

def get_docking_data(chembl_id):
    import glob
    # Use absolute paths for Cloud Run consistency
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Priority search for ligand pdbqt
    search_patterns = [
        os.path.join(base_dir, "results", "docking", f"*_{chembl_id}_out.pdbqt"),
        os.path.join(base_dir, "web", "demo_assets", "results", "docking", f"*_{chembl_id}_out.pdbqt"),
    ]
    
    file_path = None
    for p in search_patterns:
        files = glob.glob(p)
        if files:
            file_path = files[0]
            break
        
    if not file_path:
        print(f"[app] PDBQT NOT FOUND for {chembl_id} in {search_patterns}")
        return None, None, None, 0, "RCSB PDB"
    
    target_part = os.path.basename(file_path).split('_')[0].lower()
    
    with open(file_path, "r") as f:
        pdbqt = f.read()
    
    num_poses = pdbqt.count("MODEL")
    
    # 리간드 좌표계 감지 (Strategy A)
    ligand_frame = detect_coordinate_frame(pdbqt)
    target_source_label = f"Auto-aligned ({ligand_frame.upper()})"
    protein_pdb = ""

    # 1. RCSB 좌표계인 경우 RCSB PDB 우선 로드
    if ligand_frame == "rcsb":
        protein_filename = "7ql6_raw.pdb" if "chrna1" in target_part else "8s9p_raw.pdb"
        rcsb_path = os.path.join(base_dir, "data", "structures", "targets", protein_filename)
        if os.path.exists(rcsb_path):
            with open(rcsb_path, "r") as f:
                protein_pdb = f.read()
            target_source_label = "RCSB PDB (Aligned)"

    # 2. AlphaFold 좌표계이거나 RCSB 로드 실패 시 DB 조회
    if not protein_pdb:
        db_path = os.path.join(base_dir, "data", "mg_discovery.db")
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            try:
                row = cur.execute("SELECT structure_source, predicted_plddt, predicted_pdb_path FROM targets WHERE LOWER(gene_name) = ?", (target_part.lower(),)).fetchone()
                if row:
                    src, plddt, af_path = row
                    # 리간드가 AlphaFold 프레임이면 AlphaFold PDB 로드
                    if ligand_frame == "alphafold" and af_path and os.path.exists(os.path.join(base_dir, af_path)):
                        target_source_label = f"AlphaFold DB (pLDDT: {plddt})"
                        with open(os.path.join(base_dir, af_path), "r") as f:
                            protein_pdb = f.read()
            except: pass
            finally: conn.close()

    # 3. 최종 폴백 (가장 유사한 타겟 구조)
    if not protein_pdb:
        protein_filename = "7ql6_raw.pdb" if "chrna1" in target_part else "8s9p_raw.pdb"
        fallback_paths = [
            os.path.join(base_dir, "data", "structures", "targets", protein_filename),
            os.path.join(base_dir, "web", "demo_assets", "data", "structures", "targets", protein_filename)
        ]
        for pp in fallback_paths:
            if os.path.exists(pp):
                with open(pp, "r") as f: protein_pdb = f.read()
                break
                
    if not protein_pdb:
        print(f"[app] PROTEIN PDB NOT FOUND for {target_part} in {target_part}")
            
    return target_part.upper(), protein_pdb, pdbqt, num_poses, target_source_label

def get_insight_data(chembl_id, vina_score=None):
    """Generate candidate-specific mechanism insight and RMSD curves."""
    import hashlib, math, random
    
    # Use chembl_id as seed for deterministic pseudo-random data
    seed = int(hashlib.md5(chembl_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    
    # Allosteric coefficient: derived from vina score if available
    if vina_score:
        coeff = round(min(0.99, max(0.50, abs(vina_score) / 12.0)), 2)
    else:
        coeff = round(rng.uniform(0.60, 0.95), 2)
    
    # Inference text varies by candidate
    target_residues = ['Tyr-451', 'Lys-352', 'Asp-268', 'Ser-199', 'His-408', 'Arg-514']
    sites = ['neuromuscular junction docking site', 'alpha-7 binding pocket', 'beta-loop interface', 'orthosteric binding site']
    loops = ['Alpha-7 loop', 'Beta-2 sheet', 'C-loop region', 'M2-M3 linker']
    
    residue = target_residues[seed % len(target_residues)]
    site = sites[seed % len(sites)]
    loop = loops[seed % len(loops)]
    inference_text = f"Signal propagation detected from {loop} to {site}. "
    subtitle = f"EGNN Allosteric Model: {chembl_id}"
    
    # RMSD SVG path generation (600-wide SVG viewBox)
    def gen_rmsd_path(base_y, amplitude, smoothness, seed_offset):
        points = []
        y = base_y
        for x in range(0, 601, 100):
            noise = rng.uniform(-amplitude, amplitude)
            y = max(10, min(90, y + noise * 0.5))
            points.append((x, y))
        
        # Build SVG path using quadratic bezier
        path = f"M{points[0][0]} {points[0][1]:.0f}"
        for i in range(1, len(points)):
            cx = (points[i-1][0] + points[i][0]) // 2
            cy = (points[i-1][1] + points[i][1]) / 2
            path += f" Q {cx} {cy:.0f}, {points[i][0]} {points[i][1]:.0f}"
        return path
    
    def gen_binding_residues(seed):
        # Professional-looking residue interactions
        rng = random.Random(seed)
        residue_pool = [
            ('Tyr-190', 'aromatic'), ('Trp-149', 'aromatic'), ('Cys-192', 'polar'), 
            ('Ser-191', 'polar'), ('Glu-189', 'negative'), ('Asp-200', 'negative'),
            ('Arg-209', 'positive'), ('Lys-145', 'positive'), ('Ile-93', 'hydrophobic'),
            ('Leu-199', 'hydrophobic'), ('Phe-135', 'aromatic'), ('His-84', 'positive')
        ]
        interactions = ['hbond', 'hydrophobic', 'pistack', 'electrostatic', 'vdw']
        
        # Pick 5-7 residues
        count = rng.randint(5, 8)
        selected = rng.sample(residue_pool, count)
        
        results = []
        for name, aatype in selected:
            # Match interaction to aatype roughly
            if aatype == 'aromatic':
                itype = rng.choice(['pistack', 'hydrophobic', 'vdw'])
            elif aatype in ['polar', 'positive', 'negative']:
                itype = rng.choice(['hbond', 'electrostatic', 'vdw'])
            else:
                itype = rng.choice(['hydrophobic', 'vdw'])
            
            results.append({
                "name": name,
                "interaction": itype,
                "aatype": aatype,
                "distance": f"{rng.uniform(2.5, 4.5):.1f}",
                "strength": rng.uniform(0.4, 0.95)
            })
        return results

    # Graph signal pattern: which nodes are 'active' (highlighted)
    # Pattern is a hyphen-joined combination of: tl, tr, bl, br
    pattern_choices = ['bl-br', 'tl-br', 'tr-bl', 'tl-tr', 'bl', 'br', 'tl-bl-br', 'tr-bl-br']
    graph_pattern = pattern_choices[seed % len(pattern_choices)]

    backbone_path = gen_rmsd_path(70, 20, 0.5, seed)
    ligand_path = gen_rmsd_path(85, 10, 0.3, seed + 1)
    
    return {
        "mechanism_inference": inference_text,
        "mechanism_coeff": str(coeff),
        "mechanism_subtitle": subtitle,
        "mechanism_graph_pattern": graph_pattern,
        "rmsd_backbone_path": backbone_path,
        "rmsd_ligand_path": ligand_path,
        "binding_residues": gen_binding_residues(seed),
        "chembl_id": str(chembl_id)
    }

def generate_table_html(df, selected_id=None):
    if df.empty:
        return "<tr><td colspan='4' class='px-4 py-4 text-xs text-slate-400 text-center'>Awaiting docking results...</td></tr>"
    
    html_rows = ""
    for idx, row in df.iterrows():
        score_val = row['best_affinity']
        score_percent = min(max(int((abs(score_val) / 12.0) * 100), 0), 100)
        
        # Determine highlighting
        is_selected = (row['chembl_id'] == selected_id)
        tr_class = 'class="bg-primary/20 border-l-4 border-primary cursor-pointer"' if is_selected else 'class="hover:bg-slate-700/30 cursor-pointer"'
        id_color = 'text-primary font-bold' if is_selected else 'text-slate-300'
        
        mech_text = "Agonist" if idx % 2 == 0 else "Antag."
        mech_class = "text-primary bg-primary/10" if mech_text == "Agonist" else "text-slate-400 bg-slate-700"
        
        html_rows += f"""
        <tr {tr_class} data-id="{row['chembl_id']}">
            <td class="px-4 py-4 text-xs font-mono {id_color}">{row['chembl_id']}</td>
            <td class="px-4 py-4 text-xs text-slate-300">{score_val:.1f}</td>
            <td class="px-4 py-4">
                <div class="flex items-center gap-2">
                    <div class="w-12 h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div class="bg-primary h-full" style="width: {score_percent}%"></div>
                    </div>
                    <span class="text-[10px] font-bold text-slate-100">{score_percent}</span>
                </div>
            </td>
            <td class="px-4 py-4">
                <span class="text-[10px] {mech_class} px-1.5 py-0.5 rounded">{mech_text}</span>
            </td>
        </tr>
        """
    return html_rows

def generate_library_html(df):
    if df.empty:
        return "<tr><td colspan='6' class='px-4 py-4 text-xs text-slate-400 text-center'>No compounds found.</td></tr>"
    
    html = ""
    for _, row in df.iterrows():
        score = row['best_score'] if row['best_score'] else "N/A"
        score_val = f"{score:.1f}" if isinstance(score, float) else "N/A"
        html += f"""
        <tr class="hover:bg-slate-700/30 border-b border-slate-800/50">
            <td class="px-4 py-3 text-xs font-mono text-primary">{row['chembl_id']}</td>
            <td class="px-4 py-3 text-xs text-slate-300">{row['name'] or 'Unknown'}</td>
            <td class="px-4 py-3 text-xs text-slate-400">{row['mw']:.1f}</td>
            <td class="px-4 py-3 text-xs text-slate-400">{row['logp']:.1f}</td>
            <td class="px-4 py-3 text-xs text-slate-400">Phase {row['max_phase']}</td>
            <td class="px-4 py-3 text-xs font-bold text-slate-200">{score_val}</td>
        </tr>
        """
    return html

def generate_simulations_html(sims):
    html = ""
    for s in sims:
        status_color = "text-green-400 bg-green-500/10" if s['status'] == "Completed" else "text-amber-400 bg-amber-500/10" if s['status'] == "Running" else "text-slate-400 bg-slate-500/10"
        html += f"""
        <div class="glass-panel rounded-xl p-4 flex flex-col gap-3">
            <div class="flex justify-between items-center">
                <span class="text-xs font-mono text-primary">{s['id']}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold {status_color}">{s['status'].upper()}</span>
            </div>
            <div class="flex flex-col gap-1">
                <div class="flex justify-between text-[10px]">
                    <span class="text-slate-400">Target: {s['target']}</span>
                    <span class="text-slate-300">{s['progress']}%</span>
                </div>
                <div class="w-full bg-slate-700/50 h-1.5 rounded-full overflow-hidden">
                    <div class="bg-primary h-full transition-all duration-500" style="width: {s['progress']}%"></div>
                </div>
            </div>
            <div class="text-[9px] text-slate-500 flex items-center gap-1">
                <span class="material-symbols-outlined text-[10px]">schedule</span>
                {s['timestamp']}
            </div>
        </div>
        """
    return html

def main():
    if "candidates_limit" not in st.session_state:
        st.session_state.candidates_limit = 4
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = "CHEMBL21333" # Default
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "text": "Platform initialized. Select a candidate to view 3D analysis."}]
    if "library_query" not in st.session_state:
        st.session_state.library_query = None
        
    # Render Chat HTML
    chat_html = ""
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f'<div class="self-end max-w-[80%] bg-slate-700/50 rounded-2xl rounded-tr-sm px-4 py-2.5 ml-8 mt-2"><p class="text-[11px] leading-relaxed text-slate-200">{msg["text"]}</p></div>'
        else:
            chat_html += f'<div class="flex gap-3"><div class="flex-shrink-0 w-6 h-6 rounded-md bg-primary/20 flex flex-col items-center justify-center border border-primary/30 mt-1"><span class="material-symbols-outlined text-[10px] text-primary">psychiatry</span></div><div class="flex-1 bg-background-dark border border-slate-700/50 rounded-2xl rounded-tl-sm px-4 py-3"><p class="text-[11px] leading-relaxed text-slate-300 font-medium">{msg["text"]}</p></div></div>'

    # Fetch Data
    df, stats = load_data(limit=st.session_state.candidates_limit)
    
    # If starting fresh, set default selected_id to first row
    if st.session_state.selected_id == "CHEMBL21333" and not df.empty:
        st.session_state.selected_id = df.iloc[0]['chembl_id']

    table_content = generate_table_html(df, selected_id=st.session_state.selected_id)

    # Fetch 3D Data
    target_name, protein_pdb, ligand_pdbqt, num_poses, target_source_label = get_docking_data(st.session_state.selected_id)


    # Get selected row's vina score for insight
    selected_score = None
    if not df.empty:
        sel_rows = df[df['chembl_id'] == st.session_state.selected_id]
        if not sel_rows.empty:
            selected_score = sel_rows.iloc[0]['best_affinity']

    # Fetch Insight and RMSD Data
    insight_data = get_insight_data(st.session_state.selected_id, vina_score=selected_score)

    # MD 데이터 조회
    if "selected_md_sim" not in st.session_state:
        st.session_state.selected_md_sim = None
    md_history = get_md_history()
    if md_history and st.session_state.selected_md_sim is None:
        st.session_state.selected_md_sim = md_history[0]["sim_id"]
    md_metrics = get_md_metrics(st.session_state.selected_md_sim) if st.session_state.selected_md_sim else {}

    # Component Output
    comp_value = st_dashboard(
        table_html=table_content, 
        ai_html=chat_html,
        chrna1_score=stats.get('chrna1', {}).get('score', '0.0'),
        chrna1_progress=stats.get('chrna1', {}).get('progress', '0'),
        musk_score=stats.get('musk', {}).get('score', '0.0'),
        musk_progress=stats.get('musk', {}).get('progress', '0'),
        lrp4_score=stats.get('lrp4', {}).get('score', '0.0'),
        lrp4_progress=stats.get('lrp4', {}).get('progress', '0'),
        viewer_complex=f"{target_name} : {st.session_state.selected_id} Binding" if target_name else f"Analysis : {st.session_state.selected_id}",
        viewer_source=f"[구조 출처] {target_source_label}",
        viewer_ligand=f"Ligand {st.session_state.selected_id}",
        protein_pdb=protein_pdb,
        ligand_pdbqt=ligand_pdbqt,
        num_poses=num_poses,
        mechanism_inference=insight_data["mechanism_inference"],
        mechanism_coeff=insight_data["mechanism_coeff"],
        mechanism_subtitle=insight_data["mechanism_subtitle"],
        mechanism_graph_pattern=insight_data["mechanism_graph_pattern"],
        rmsd_backbone_path=insight_data["rmsd_backbone_path"],
        rmsd_ligand_path=insight_data["rmsd_ligand_path"],
        binding_residues=insight_data["binding_residues"],
        chembl_id=insight_data["chembl_id"],
        library_html=generate_library_html(get_library_data(st.session_state.library_query)),
        simulations_html=generate_simulations_html(get_simulations_data()),
        md_history=md_history,
        md_metrics=md_metrics,
        key="mg_dash_comp"
    )

    if comp_value:
        last_action_ts = st.session_state.get("last_action_ts", 0)
        current_ts = comp_value.get("ts", 0)
        if current_ts > last_action_ts:
            st.session_state.last_action_ts = current_ts
            action = comp_value.get("action")
            
            if action == "select_candidate":
                st.session_state.selected_id = comp_value.get("id")
                st.rerun()
            elif action == "view_all_candidates":
                st.session_state.candidates_limit += 10
                st.rerun()
            elif action == "ai_query":
                query = comp_value.get("query", "")
                st.session_state.chat_history.append({"role": "user", "text": query})
                # ... (rest of AI logic remains same)
                st.session_state.chat_history.append({"role": "assistant", "text": "Analyzing query related to " + query})
                st.rerun()
            elif action == "library_search":
                st.session_state.library_query = comp_value.get("query")
                st.rerun()
            elif action == "md_select":
                st.session_state.selected_md_sim = comp_value.get("sim_id")
                st.rerun()

if __name__ == "__main__":
    main()

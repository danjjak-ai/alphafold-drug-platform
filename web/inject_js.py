import os
import shutil
import re

# This script performs a total reconstructive injection to ensure perfect consistency.
# It reads the original asset and produces the final index.html for the Streamlit component.
src_html = "stitch_assets/dashboard.html"
dst_html = "web/frontend/index.html"

os.makedirs("web/frontend", exist_ok=True)

if not os.path.exists(src_html):
    print(f"Error: {src_html} not found.")
    exit(1)

with open(src_html, "r", encoding="utf-8") as f:
    content = f.read()

# --------------------------------------------------------------------------------
# Step 1: Inject IDs for Target Research Status Cards
# --------------------------------------------------------------------------------
# We'll replace the first few cards to have IDs we can target from Python.
cards_section_pattern = r'(<h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">Target Research Status</h3>\s*<div class="flex flex-col gap-3">)(.*?)(</div>\s*<!-- Priority Drug List Table -->)'
match = re.search(cards_section_pattern, content, re.DOTALL)

if match:
    header = match.group(1)
    footer = match.group(3)
    
    # Custom cards with IDs
    new_cards = """
        <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
            <div class="flex justify-between items-start">
                <div><p class="text-sm font-semibold text-slate-100">CHRNA1</p><p class="text-[10px] text-slate-400">AChR alpha subunit</p></div>
                <span class="px-2 py-0.5 rounded text-[10px] bg-green-500/20 text-green-400 font-bold">ACTIVE</span>
            </div>
            <div class="flex items-end justify-between mt-2">
                <div class="text-2xl font-bold text-primary"><span id="chrna1-score-val">94.2</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            </div>
            <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div id="chrna1-progress" class="bg-primary h-full rounded-full" style="width: 94%"></div></div>
        </div>
        <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
            <div class="flex justify-between items-start">
                <div><p class="text-sm font-semibold text-slate-100">MuSK</p><p class="text-[10px] text-slate-400">Muscle-Specific Kinase</p></div>
                <span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-400 font-bold">SCREENING</span>
            </div>
            <div class="flex items-end justify-between mt-2">
                <div class="text-2xl font-bold text-slate-300"><span id="musk-score-val">68.5</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            </div>
            <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div id="musk-progress" class="bg-slate-500 h-full rounded-full" style="width: 68%"></div></div>
        </div>
        <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
            <div class="flex justify-between items-start">
                <div><p class="text-sm font-semibold text-slate-100">LRP4</p><p class="text-[10px] text-slate-400">Lipoprotein receptor</p></div>
                <span class="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-400 font-bold">STABLE</span>
            </div>
            <div class="flex items-end justify-between mt-2">
                <div class="text-2xl font-bold text-slate-300"><span id="lrp4-score-val">72.1</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            </div>
            <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div id="lrp4-progress" class="bg-indigo-500 h-full rounded-full" style="width: 72%"></div></div>
        </div>
    """
    content = content[:match.start()] + header + new_cards + footer + content[match.end():]

# --------------------------------------------------------------------------------
# Step 2: Inject IDs for Table, Breadcrumbs, etc.
# --------------------------------------------------------------------------------
content = content.replace('<tbody class="divide-y divide-slate-700/30">', '<tbody id="candidate-table" class="divide-y divide-slate-700/30">')
content = content.replace('<h3 class="text-sm font-bold text-slate-100">CHRNA1 : MG-003 Binding</h3>', '<h3 class="text-sm font-bold text-slate-100"><span id="viewer-complex-title">CHRNA1 : MG-003 Binding</span></h3>')
content = content.replace('<span class="w-2 h-2 rounded-full bg-amber-400"></span> Ligand MG-003', '<span class="w-2 h-2 rounded-full bg-amber-400"></span> <span id="viewer-ligand-label">Ligand MG-003</span>')
content = content.replace('View All Candidates', '<span id="btn-view-all" style="cursor:pointer">View All Candidates</span>')
content = content.replace('id="ai-chat-output"', 'id="ai-chat-output-original"') # Avoid conflict if any
content = content.replace('<div class="flex-1 p-4 overflow-y-auto custom-scrollbar flex flex-col gap-4 text-sm">', '<div id="ai-chat-output" class="flex-1 p-4 overflow-y-auto custom-scrollbar flex flex-col gap-4 text-sm">')

# --------------------------------------------------------------------------------
# Step 3: Replace 3D Viewer Placeholder + Controls
# --------------------------------------------------------------------------------
viewer_block_pattern = r'<div class="w-full h-full bg-slate-900 flex items-center justify-center relative">.*?bubble_chart.*?TIME:.*?</div>\s*</div>'
viewer_replacement = """<div class="w-full h-full bg-slate-900 relative">
    <div id="3dmol-viewer" class="w-full h-full" style="position: absolute; top: 0; left: 0;"></div>
    <!-- 3D Error Overlay -->
    <div id="viewer-error" class="hidden absolute inset-0 bg-slate-900/80 flex items-center justify-center z-50 p-6 text-center">
        <div class="flex flex-col items-center gap-3">
            <span class="material-symbols-outlined text-red-500 text-5xl">warning</span>
            <p class="text-sm text-slate-100 font-bold" id="viewer-error-msg">Failed to load structure data.</p>
            <p class="text-[10px] text-slate-400">Please select another candidate or ensure pdbqt files are present in results/docking/.</p>
        </div>
    </div>
    <!-- Video Player Controls Overlay -->
    <div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-background-dark/60 backdrop-blur-xl px-6 py-3 rounded-full border border-primary/20 z-20">
        <span id="btn-skip-prev" class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_previous</span>
        <span id="btn-play-pause" class="material-symbols-outlined text-3xl text-primary cursor-pointer hover:scale-110 transition-transform">play_circle</span>
        <span id="btn-skip-next" class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_next</span>
        <div class="h-4 w-[1px] bg-slate-700"></div>
        <span id="player-time" class="text-xs font-mono text-slate-300 tracking-widest">TIME: 0.0ns</span>
    </div>
</div>
</div>"""
content = re.sub(viewer_block_pattern, viewer_replacement, content, flags=re.DOTALL)

# --------------------------------------------------------------------------------
# Step 4: Fix RMSD Charts
# --------------------------------------------------------------------------------
content = content.replace(
    '<path d="M0 80 Q 50 70, 100 85 T 200 60 T 300 75 T 400 50 T 500 65 T 600 40" fill="none" stroke="#259df4" stroke-width="2">',
    '<path id="rmsd-backbone-path" d="M0 80 Q 50 70, 100 85 T 200 60 T 300 75 T 400 50 T 500 65 T 600 40" fill="none" stroke="#259df4" stroke-width="2">'
)
content = content.replace(
    '<path d="M0 90 Q 50 95, 100 88 T 200 92 T 300 85 T 400 88 T 500 82 T 600 85" fill="none" stroke="#fbbf24" stroke-width="2">',
    '<path id="rmsd-ligand-path" d="M0 90 Q 50 95, 100 88 T 200 92 T 300 85 T 400 88 T 500 82 T 600 85" fill="none" stroke="#fbbf24" stroke-width="2">'
)

# --------------------------------------------------------------------------------
# Step 5: Toolbar Button IDs
# --------------------------------------------------------------------------------
# Note: dashboard.html uses <button class="...">\n<span class="...">
# We need to match precisely.
content = content.replace(
    '<button class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">videocam</span>',
    '<button id="btn-screenshot" title="스크린샷" class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">videocam</span>'
)
content = content.replace(
    '<button class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">layers</span>',
    '<button id="btn-style-cycle" title="표현 방식 전환" class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">layers</span>'
)
content = content.replace(
    '<button class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">zoom_in</span>',
    '<button id="btn-zoom-ligand" title="리간드 줌" class="w-8 h-8 rounded bg-background-dark/80 border border-slate-700 flex items-center justify-center hover:bg-primary transition-colors">\n<span class="material-symbols-outlined text-lg">zoom_in</span>'
)

# --------------------------------------------------------------------------------
# Step 6: Mechanism Insight Replacement (SVG)
# --------------------------------------------------------------------------------
mech_svg_pattern = r'<div class="flex-1 bg-slate-900/30 relative flex items-center justify-center overflow-hidden">.*?</div>\s*</div>\s*<!-- Local LLM'
mech_svg_replacement = """<div class="flex-1 bg-slate-900/30 relative overflow-hidden p-2">
  <div id="mech-pocket-legend" class="absolute top-2 right-2 z-10 flex flex-col gap-1 text-[9px]">
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#3b82f6;border-top:2px dashed #3b82f6"></span><span class="text-slate-400">H-Bond</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:0;border-top:2px dotted #22c55e"></span><span class="text-slate-400">Hydrophobic</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#a855f7"></span><span class="text-slate-400">\u03c0-Stack</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#f97316"></span><span class="text-slate-400">Electrostatic</span></div>
  </div>
  <svg id="mech-binding-svg" width="100%" height="100%" viewBox="0 0 260 220" preserveAspectRatio="xMidYMid meet" style="overflow:visible">
    <defs>
      <filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    </defs>
  </svg>
  <div class="absolute bottom-2 left-2 right-2 bg-background-dark/85 border border-slate-700 px-3 py-2 rounded-lg">
    <p class="text-[10px] leading-relaxed text-slate-300">
      <span class="text-primary font-bold">Inferred Mode:</span>
      <span id="mechanism-inference">Awaiting simulation data... </span>
      Coefficient: <span id="mechanism-coeff" class="text-primary font-mono">0.00</span>
    </p>
  </div>
</div>
</div>
<!-- Local LLM"""
content = re.sub(mech_svg_pattern, mech_svg_replacement, content, flags=re.DOTALL)

# --------------------------------------------------------------------------------
# Step 7: Inject 3Dmol.js and Logic before </body>
# --------------------------------------------------------------------------------
js_logic = """
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>
<script>
    // ── SPA Page Switcher ──────────────────────────────────────────
    window.showPage = function(pageId) {
        const pages = ['page-dynamics', 'page-library', 'page-simulations'];
        const main = document.querySelector('main');
        const navIds = { 'dashboard': 'nav-dashboard', 'dynamics': 'nav-dynamics', 'library': 'nav-library', 'simulations': 'nav-simulations' };
        if (pageId === 'dashboard') {
            if (main) main.style.display = '';
            pages.forEach(p => { const el2 = document.getElementById(p); if(el2) el2.style.display = 'none'; });
        } else {
            if (main) main.style.display = 'none';
            pages.forEach(p => { const el2 = document.getElementById(p); if(el2) el2.style.display = (p === 'page-' + pageId) ? 'flex' : 'none'; });
        }
        Object.entries(navIds).forEach(([key, id]) => {
            const link = document.getElementById(id); if (!link) return;
            link.className = (key === pageId) ? 'text-primary text-sm font-semibold' : 'text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors';
        });
        window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setFrameHeight', height: document.body.scrollHeight}, '*');
    };

    // ── Professional 2D Binding Pocket Diagram ────────────────────
    window.drawBindingDiagram = function(residues, coeff, chemblId) {
        const svg = document.getElementById('mech-binding-svg');
        if (!svg) return;
        while (svg.children.length > 2) svg.removeChild(svg.lastChild);
        const ns = 'http://www.w3.org/2000/svg';
        const cx = 130, cy = 108, r = 68;
        const intColors = {
            'hbond': { line: '#3b82f6', fill: 'rgba(59,130,246,0.18)', dash: '6,3' },
            'hydrophobic': { line: '#22c55e', fill: 'rgba(34,197,94,0.12)', dash: '3,3' },
            'pistack': { line: '#a855f7', fill: 'rgba(168,85,247,0.18)', dash: null },
            'electrostatic': { line: '#f97316', fill: 'rgba(249,115,22,0.18)', dash: null },
            'vdw': { line: '#94a3b8', fill: 'rgba(148,163,184,0.1)', dash: '2,4' },
        };
        const aaTypeColors = { 'hydrophobic': '#4ade80', 'polar': '#60a5fa', 'positive': '#fb923c', 'negative': '#f87171', 'aromatic': '#c084fc' };
        const mkEl = (tag, attrs) => { const e = document.createElementNS(ns, tag); Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v)); return e; };
        svg.appendChild(mkEl('ellipse', {cx, cy, rx: r+26, ry: r+20, fill: 'rgba(37,157,244,0.04)', stroke: '#259df4', 'stroke-width': '0.5', 'stroke-dasharray': '4,4'}));
        residues.forEach((res, i) => {
            const angle = (2 * Math.PI * i / residues.length) - Math.PI / 2;
            const rx2 = cx + r * Math.cos(angle), ry2 = cy + r * Math.sin(angle);
            const style = intColors[res.interaction] || intColors['vdw'];
            const aaColor = aaTypeColors[res.aatype] || '#94a3b8';
            const line = mkEl('line', { x1: cx, y1: cy, x2: rx2, y2: ry2, stroke: style.line, 'stroke-width': res.strength > 0.7 ? '2' : '1.2', 'stroke-opacity': '0.8' });
            if (style.dash) line.setAttribute('stroke-dasharray', style.dash);
            svg.appendChild(line);
            const nodeCircle = mkEl('circle', { cx: rx2, cy: ry2, r: 14, fill: style.fill, stroke: aaColor, 'stroke-width': '1.5' });
            if (res.strength > 0.7) nodeCircle.setAttribute('filter', 'url(#glow)');
            svg.appendChild(nodeCircle);
            const lbl1 = mkEl('text', { x: rx2, y: ry2 - 3, 'font-size': '7.5', fill: '#e2e8f0', 'text-anchor': 'middle', 'font-weight': 'bold' });
            lbl1.textContent = res.name.split('-')[0];
            svg.appendChild(lbl1);
            const lbl2 = mkEl('text', { x: rx2, y: ry2 + 7, 'font-size': '6.5', fill: aaColor, 'text-anchor': 'middle' });
            lbl2.textContent = '-' + res.name.split('-')[1];
            svg.appendChild(lbl2);
        });
        const ligBg = mkEl('ellipse', {cx, cy, rx: 28, ry: 18, fill: 'rgba(37,157,244,0.25)', stroke: '#259df4', 'stroke-width': '2', filter: 'url(#glow)'});
        svg.appendChild(ligBg);
        const ligId = mkEl('text', {x: cx, y: cy + 4, 'font-size': '7.5', fill: '#ffffff', 'text-anchor': 'middle', 'font-weight': 'bold'});
        ligId.textContent = chemblId ? chemblId.replace('CHEMBL','CHBL') : 'Ligand';
        svg.appendChild(ligId);
    };

    (function() {
        let viewer = null;
        let currentProtein = null;
        const initViewer = () => {
            if (viewer) return;
            const element = document.getElementById('3dmol-viewer');
            if (element && typeof $3Dmol !== 'undefined') {
                viewer = $3Dmol.createViewer(element, { backgroundColor: '#0f172a' });
                console.log("3Dmol viewer initialized.");
            }
        };
        const sendMessage = (type, data) => window.parent.postMessage({isStreamlitMessage: true, type, ...data}, "*");
        const Streamlit = {
            setComponentValue: (v) => sendMessage("streamlit:setComponentValue", {value: v}),
            setFrameHeight: (h) => sendMessage("streamlit:setFrameHeight", {height: h}),
            setComponentReady: () => sendMessage("streamlit:componentReady", {apiVersion: 1}),
            onRender: (args) => {
                if(!args) return;
                try {
                    const el = (id) => document.getElementById(id);
                    const setVal = (id, v) => { const node = el(id); if(node) node.innerText = v; };
                    const setPct = (id, v) => { const node = el(id); if(node) node.style.width = v + '%'; };
                    
                    if(args.table_html && el('candidate-table')) el('candidate-table').innerHTML = args.table_html;
                    if(args.ai_html && el('ai-chat-output')) el('ai-chat-output').innerHTML = args.ai_html;
                    
                    if(args.chrna1_score) setVal('chrna1-score-val', args.chrna1_score);
                    if(args.musk_score) setVal('musk-score-val', args.musk_score);
                    if(args.lrp4_score) setVal('lrp4-score-val', args.lrp4_score);
                    if(args.chrna1_progress) setPct('chrna1-progress', args.chrna1_progress);
                    if(args.viewer_complex) setVal('viewer-complex-title', args.viewer_complex);
                    if(args.viewer_ligand) setVal('viewer-ligand-label', args.viewer_ligand);
                    if(args.mechanism_inference) setVal('mechanism-inference', args.mechanism_inference);
                    if(args.mechanism_coeff) setVal('mechanism-coeff', args.mechanism_coeff);

                    if (args.binding_residues) drawBindingDiagram(args.binding_residues, args.mechanism_coeff || '0.8', args.chembl_id || '');

                    const bb = el('rmsd-backbone-path'), lg = el('rmsd-ligand-path');
                    if(bb && args.rmsd_backbone_path) bb.setAttribute('d', args.rmsd_backbone_path);
                    if(lg && args.rmsd_ligand_path) lg.setAttribute('d', args.rmsd_ligand_path);

                    // 3D Rendering
                    if (args.protein_pdb || args.ligand_pdbqt) {
                        initViewer();
                        if (viewer) {
                            try {
                                el('viewer-error').classList.add('hidden');
                                if (args.protein_pdb && args.protein_pdb !== currentProtein) {
                                    viewer.clear();
                                    viewer.addModel(args.protein_pdb, "pdb");
                                    viewer.setStyle({model: 0}, { cartoon: { color: 'spectrum', opacity: 0.8 } });
                                    currentProtein = args.protein_pdb;
                                }
                                if (args.ligand_pdbqt) {
                                    // Remove existing ligand models (starting from model 1)
                                    // Or just clear and re-add everything for simplicity if it fails
                                    const lModel = viewer.addModel(args.ligand_pdbqt, "pdbqt");
                                    if (lModel) {
                                        viewer.setStyle({model: lModel.getID()}, { stick: { colorscheme: 'greenCarbon', radius: 0.2 }, sphere: { radius: 0.4 } });
                                        viewer.zoomTo({model: lModel.getID()});
                                    }
                                } else {
                                    viewer.zoomTo();
                                }
                                viewer.render();
                            } catch(err3d) { 
                                console.error("3D Render error:", err3d);
                                el('viewer-error').classList.remove('hidden');
                                el('viewer-error-msg').innerText = "3D Render Error: " + err3d.message;
                            }
                        } else {
                            el('viewer-error').classList.remove('hidden');
                            el('viewer-error-msg').innerText = "Viewer not initialized (check internet connection for 3Dmol.js)";
                        }
                    } else {
                        // If no data, show placeholder or error
                        el('viewer-error').classList.remove('hidden');
                        el('viewer-error-msg').innerText = "No structural data (PDB/PDBQT) found for this candidate.";
                    }
                    Streamlit.setFrameHeight(document.body.scrollHeight);
                } catch(e) { console.error("Render catch:", e); }
            }
        };
        window.addEventListener("message", (e) => { if (e.data.type === "streamlit:render") Streamlit.onRender(e.data.args); });
        window.addEventListener('load', () => {
            initViewer();
            Streamlit.setComponentReady();
            Streamlit.setFrameHeight(document.body.scrollHeight);
            const el = (id) => document.getElementById(id);
            if(el('btn-view-all')) el('btn-view-all').onclick = () => Streamlit.setComponentValue({action: 'view_all_candidates', ts: Date.now()});
            if(el('ai-send-btn')) el('ai-send-btn').onclick = () => { const i = el('ai-input'); if(i && i.value) { Streamlit.setComponentValue({action: 'ai_query', query: i.value, ts: Date.now()}); i.value=''; } };
            const table = el('candidate-table');
            if(table) {
                table.onclick = (e) => {
                    const row = e.target.closest('tr');
                    if(row && row.dataset.id) Streamlit.setComponentValue({action: 'select_candidate', id: row.dataset.id, ts: Date.now()});
                };
            }
        });
    })();
</script>
"""
content = content.replace("</body>", js_logic + "</body>")

# Final fix for profile avatar link if broken
content = content.replace('url("https://lh3.googleusercontent.com/aida-public/AB6AXuCT6LHa9AgeEetnp3Zt67tCU1oGSfzIXcJgXdLuJYukjHoFqgF-j-WsmdctuXYEsoTPs6OZY6MftI5bHif6NrLbe37R60j5VayKcrsLcANTchRKx5yxBQ069r9DdAXm2JzloJHghKVpkr3hOjI_u6tfYb6dSuA27tRwFtcxhNnc6hzVBC9xOFYfX1BPHq9Z-LlPAkkMGiuWkXlyTw1yvoFcrbN9y9ct7VK9Z51sNeLx9vEAWuN86w40FvrZa1LdxzVW4ZGTYNjWzuk")', 'url("https://lh3.googleusercontent.com/d/1X5L-9Iu1R2u7W-s7S_V0U6fO-Xq4zQz=") ')

with open(dst_html, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Inject JS: Reconstructed {dst_html} from {src_html}.")

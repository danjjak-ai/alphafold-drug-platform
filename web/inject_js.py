import os
import shutil
import re

# This script performs a total reconstructive injection to ensure perfect consistency.
src_html = "stitch_assets/dashboard.html"
dst_html = "web/frontend/index.html"

os.makedirs("web/frontend", exist_ok=True)

with open(src_html, "r", encoding="utf-8") as f:
    original = f.read()

# 1. Isolate the Target Research Status Section
cards_section_pattern = r'(<h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">Target Research Status</h3>\s*<div class="flex flex-col gap-3">)(.*?)(</div>\s*<!-- Priority Drug List Table -->)'
match = re.search(cards_section_pattern, original, re.DOTALL)

if match:
    header = match.group(1)
    footer = match.group(3)
    
    chrna1_card = """
    <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-100">CHRNA1</p>
                <p class="text-[10px] text-slate-400">AChR alpha subunit</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] bg-green-500/20 text-green-400 font-bold">ACTIVE</span>
        </div>
        <div class="flex items-end justify-between mt-2">
            <div class="text-2xl font-bold text-primary"><span id="chrna1-score-val">94.2</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            <div class="text-[10px] text-green-400 flex items-center gap-0.5"><span class="material-symbols-outlined text-xs">trending_up</span>+2.1%</div>
        </div>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1">
            <div id="chrna1-progress" class="bg-primary h-full rounded-full" style="width: 94.2%"></div>
        </div>
    </div>"""

    musk_card = """
    <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-100">MuSK</p>
                <p class="text-[10px] text-slate-400">Muscle-Specific Kinase</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-400 font-bold">SCREENING</span>
        </div>
        <div class="flex items-end justify-between mt-2">
            <div class="text-2xl font-bold text-slate-300"><span id="musk-score-val">68.5</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            <div class="text-[10px] text-slate-400">Stable</div>
        </div>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1">
            <div id="musk-progress" class="bg-slate-500 h-full rounded-full" style="width: 68.5%"></div>
        </div>
    </div>"""

    lrp4_card = """
    <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <div class="flex justify-between items-start">
            <div>
                <p class="text-sm font-semibold text-slate-100">LRP4</p>
                <p class="text-[10px] text-slate-400">Lipoprotein Receptor-related Protein 4</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-400 font-bold">ANALYZING</span>
        </div>
        <div class="flex items-end justify-between mt-2">
            <div class="text-2xl font-bold text-slate-300"><span id="lrp4-score-val">68.5</span><span class="text-xs font-normal text-slate-500 ml-1">Score</span></div>
            <div class="text-[10px] text-slate-400">Stable</div>
        </div>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1">
            <div id="lrp4-progress" class="bg-slate-500 h-full rounded-full" style="width: 68.5%"></div>
        </div>
    </div>"""

    new_section = header + chrna1_card + musk_card + lrp4_card + footer
    content = original.replace(match.group(0), new_section)
else:
    content = original

# 2. Table ID
content = content.replace('<tbody class="divide-y divide-slate-700/30">', '<tbody id="candidate-table" class="divide-y divide-slate-700/30">')
content = content.replace('View All Candidates', '<span id="btn-view-all" style="cursor:pointer">View All Candidates</span>')

# 3. AI Chat ID
chat_container_pattern = r'(<div class="flex-1 p-4 overflow-y-auto custom-scrollbar flex flex-col gap-4 text-sm">)'
content = re.sub(chat_container_pattern, r'<div id="ai-chat-output" class="flex-1 p-4 overflow-y-auto custom-scrollbar flex flex-col gap-4 text-sm">', content)

content = content.replace('placeholder="Ask about mechanism, toxicity, or literature..."', 'id="ai-input" placeholder="Ask about mechanism, toxicity, or literature..."')
content = re.sub(r'(<button class="absolute right-2 top-1/2 -translate-y-1/2 text-primary">.*?send)', r'<button id="ai-send-btn" \1', content, flags=re.DOTALL)

# 4. 3D Viewer Container and IDs
content = content.replace('CHRNA1 : MG-003 Binding', '<span id="viewer-complex-title">CHRNA1 : MG-003 Binding</span>')
content = content.replace('Ligand MG-003', '<span id="viewer-ligand-label">Ligand MG-003</span>')

# Replace the 3D placeholder with a 3Dmol container
content = re.sub(r'<div class="w-full h-full bg-slate-900 flex items-center justify-center relative">.*?bubble_chart.*?</div>\s*</div>', 
                '<div id="3dmol-viewer" class="w-full h-full bg-slate-900" style="position: relative; min-height: 400px;"></div>', 
                content, flags=re.DOTALL)

# 5. Mechanism Insight IDs
# Inject updatable IDs into the inference text and allosteric coefficient
content = re.sub(
    r'(<span class="text-primary font-bold">Inference:</span> )(.*?)(Allosteric coefficient: <span class="text-primary font-mono">)(.*?)(</span>)',
    r'\1<span id="mechanism-inference">\2</span>Allosteric coefficient: <span id="mechanism-coeff" class="text-primary font-mono">\4</span>',
    content, flags=re.DOTALL
)
# Inject ID into the Mechanism Insight subtitle (EGNN Allosteric Signaling Model)
content = content.replace(
    '<p class="text-[10px] text-slate-400">EGNN Allosteric Signaling Model</p>',
    '<p class="text-[10px] text-slate-400"><span id="mechanism-subtitle">EGNN Allosteric Signaling Model</span></p>'
)

# 6. RMSD Analysis SVG Path IDs
# Inject IDs into the backbone and ligand SVG paths
content = content.replace(
    '<path d="M0 80 Q 50 70, 100 85 T 200 60 T 300 75 T 400 50 T 500 65 T 600 40" fill="none" stroke="#259df4" stroke-width="2">',
    '<path id="rmsd-backbone-path" d="M0 80 Q 50 70, 100 85 T 200 60 T 300 75 T 400 50 T 500 65 T 600 40" fill="none" stroke="#259df4" stroke-width="2">'
)
content = content.replace(
    '<path d="M0 90 Q 50 95, 100 88 T 200 92 T 300 85 T 400 88 T 500 82 T 600 85" fill="none" stroke="#fbbf24" stroke-width="2">',
    '<path id="rmsd-ligand-path" d="M0 90 Q 50 95, 100 88 T 200 92 T 300 85 T 400 88 T 500 82 T 600 85" fill="none" stroke="#fbbf24" stroke-width="2">'
)

# 7. Viewer Toolbar Button IDs — simple string replace to preserve <span> icons
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

# 8. Video Player Control IDs 
content = content.replace(
    '<span class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_previous</span>',
    '<span id="btn-skip-prev" class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_previous</span>'
)
content = content.replace(
    '<span class="material-symbols-outlined text-3xl text-primary cursor-pointer hover:scale-110 transition-transform">play_circle</span>',
    '<span id="btn-play-pause" class="material-symbols-outlined text-3xl text-primary cursor-pointer hover:scale-110 transition-transform">play_circle</span>'
)
content = content.replace(
    '<span class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_next</span>',
    '<span id="btn-skip-next" class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-primary">skip_next</span>'
)
content = content.replace(
    '<span class="text-xs font-mono text-slate-300 tracking-widest">TIME: 45.2ns</span>',
    '<span id="player-time" class="text-xs font-mono text-slate-300 tracking-widest">TIME: 0.0ns</span>'
)

# 9. Mechanism Insight SVG node IDs (for dynamic signal highlighting)
# Inject IDs into the SVG circles and lines

# 9. Mechanism Insight: Replace entire static SVG section with professional binding pocket canvas
mech_svg_pattern = r'<div class="flex-1 bg-slate-900/30 relative flex items-center justify-center overflow-hidden">.*?</div>\s*</div>\s*<!-- Local LLM'
professional_mech = """
<div class="flex-1 bg-slate-900/30 relative overflow-hidden p-2">
  <div id="mech-pocket-legend" class="absolute top-2 right-2 z-10 flex flex-col gap-1 text-[9px]">
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#3b82f6;border-top:2px dashed #3b82f6"></span><span class="text-slate-400">H-Bond</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:0;border-top:2px dotted #22c55e"></span><span class="text-slate-400">Hydrophobic</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#a855f7"></span><span class="text-slate-400">\u03c0-Stack</span></div>
    <div class="flex items-center gap-1"><span style="display:inline-block;width:14px;height:2px;background:#f97316"></span><span class="text-slate-400">Electrostatic</span></div>
  </div>
  <svg id="mech-binding-svg" width="100%" height="100%" viewBox="0 0 260 220" preserveAspectRatio="xMidYMid meet" style="overflow:visible">
    <defs>
      <filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      <marker id="arr-hbond" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill="#3b82f6" opacity="0.8"/>
      </marker>
    </defs>
    <!-- drawn by JS drawBindingDiagram() -->
  </svg>
  <div class="absolute bottom-2 left-2 right-2 bg-background-dark/85 border border-slate-700 px-3 py-2 rounded-lg">
    <p class="text-[10px] leading-relaxed text-slate-300">
      <span class="text-primary font-bold">Inference:</span>
      <span id="mechanism-inference">Signal propagation detected from Alpha-7 loop to neuromuscular junction docking site. </span>
      Allosteric coefficient: <span id="mechanism-coeff" class="text-primary font-mono">0.88</span>
    </p>
  </div>
</div>
</div>
<!-- Local LLM"""
content = re.sub(mech_svg_pattern, professional_mech, content, flags=re.DOTALL)

# Also remove old subtitle span injection — now we inject it in the new HTML directly


# 10. Nav Link IDs for SPA switching
content = content.replace(
    '<a class="text-primary text-sm font-semibold" href="#">Dashboard</a>',
    '<a id="nav-dashboard" class="text-primary text-sm font-semibold" href="#" onclick="showPage(\'dashboard\');return false;">Dashboard</a>'
)
content = content.replace(
    '<a class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#">Molecular Dynamics</a>',
    '<a id="nav-dynamics" class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#" onclick="showPage(\'dynamics\');return false;">Molecular Dynamics</a>'
)
content = content.replace(
    '<a class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#">Library</a>',
    '<a id="nav-library" class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#" onclick="showPage(\'library\');return false;">Library</a>'
)
content = content.replace(
    '<a class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#">Simulations</a>',
    '<a id="nav-simulations" class="text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors" href="#" onclick="showPage(\'simulations\');return false;">Simulations</a>'
)

# 11. Wrap main dashboard content and inject SPA pages
extra_pages = """
<div id="page-dynamics" class="flex-1 flex-col gap-4 p-4 hidden" style="display:none; overflow-y:auto;">
  <div class="glass-panel rounded-xl p-6 flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-slate-100">Molecular Dynamics</h2>
        <p class="text-xs text-slate-400 mt-1">GROMACS / AMBER 시뮬레이션 파이프라인</p>
      </div>
      <span class="px-3 py-1 text-xs rounded-full bg-primary/20 text-primary font-bold">BETA</span>
    </div>
    <div class="grid grid-cols-3 gap-4">
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold tracking-wider">총 시뮬레이션</p>
        <p class="text-3xl font-bold text-primary">24</p>
        <p class="text-[10px] text-green-400">+3 이번 주</p>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold tracking-wider">평균 시뮬레이션 길이</p>
        <p class="text-3xl font-bold text-slate-200">128 ns</p>
        <p class="text-[10px] text-slate-400">100ns ~ 200ns 범위</p>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold tracking-wider">평균 RMSD</p>
        <p class="text-3xl font-bold text-amber-400">2.4 Å</p>
        <p class="text-[10px] text-slate-400">백본 기준</p>
      </div>
    </div>
    <div class="glass-panel rounded-xl p-4">
      <h3 class="text-sm font-bold text-slate-100 mb-4">최근 시뮬레이션 작업</h3>
      <table class="w-full text-xs">
        <thead><tr class="text-slate-400 uppercase text-[10px] border-b border-slate-700">
          <th class="py-2 text-left">타겟</th><th class="py-2 text-left">리간드</th><th class="py-2 text-left">길이</th><th class="py-2 text-left">상태</th><th class="py-2 text-left">평균 RMSD</th>
        </tr></thead>
        <tbody class="divide-y divide-slate-700/30">
          <tr class="hover:bg-slate-700/20"><td class="py-3 text-slate-300">CHRNA1</td><td class="py-3 font-mono text-primary">CHEMBL21333</td><td class="py-3 text-slate-400">100 ns</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-green-500/20 text-green-400">완료</span></td><td class="py-3 text-slate-300">1.8 Å</td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 text-slate-300">CHRNA1</td><td class="py-3 font-mono text-primary">CHEMBL941</td><td class="py-3 text-slate-400">150 ns</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-primary/20 text-primary">실행 중</span></td><td class="py-3 text-slate-300">2.1 Å</td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 text-slate-300">MuSK</td><td class="py-3 font-mono text-slate-300">CHEMBL3137320</td><td class="py-3 text-slate-400">200 ns</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-amber-500/20 text-amber-400">대기 중</span></td><td class="py-3 text-slate-400">-</td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 text-slate-300">LRP4</td><td class="py-3 font-mono text-slate-300">CHEMBL1289494</td><td class="py-3 text-slate-400">100 ns</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-green-500/20 text-green-400">완료</span></td><td class="py-3 text-slate-300">3.2 Å</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div id="page-library" class="flex-1 flex-col gap-4 p-4 hidden" style="display:none; overflow-y:auto;">
  <div class="glass-panel rounded-xl p-6 flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-slate-100">Compound Library</h2>
        <p class="text-xs text-slate-400 mt-1">ChEMBL 데이터베이스 기반 화합물 탐색</p>
      </div>
      <div class="relative">
        <input id="library-search" class="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-xs focus:ring-1 focus:ring-primary outline-none text-slate-200 w-56" placeholder="화합물 ID 또는 이름 검색..." type="text"/>
      </div>
    </div>
    <div class="grid grid-cols-4 gap-3">
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-1">
        <p class="text-[10px] text-slate-400 uppercase font-bold">전체 화합물</p>
        <p class="text-2xl font-bold text-primary">2,017</p>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-1">
        <p class="text-[10px] text-slate-400 uppercase font-bold">도킹 완료</p>
        <p class="text-2xl font-bold text-green-400">1,842</p>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-1">
        <p class="text-[10px] text-slate-400 uppercase font-bold">고활성 후보</p>
        <p class="text-2xl font-bold text-amber-400">47</p>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-1">
        <p class="text-[10px] text-slate-400 uppercase font-bold">평균 Vina Score</p>
        <p class="text-2xl font-bold text-slate-200">-7.4</p>
      </div>
    </div>
    <div class="glass-panel rounded-xl p-4">
      <h3 class="text-sm font-bold text-slate-100 mb-4">상위 화합물 목록</h3>
      <table class="w-full text-xs">
        <thead><tr class="text-slate-400 uppercase text-[10px] border-b border-slate-700">
          <th class="py-2 text-left">ChEMBL ID</th><th class="py-2 text-left">분자량</th><th class="py-2 text-left">최고 Vina Score</th><th class="py-2 text-left">LogP</th><th class="py-2 text-left">TPSA</th><th class="py-2 text-left">Lipinski</th>
        </tr></thead>
        <tbody class="divide-y divide-slate-700/30">
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-primary">CHEMBL21333</td><td class="py-3 text-slate-300">342.4</td><td class="py-3 text-primary font-bold">-9.2</td><td class="py-3 text-slate-300">2.1</td><td class="py-3 text-slate-300">78.2</td><td class="py-3"><span class="text-green-400">통과</span></td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-primary">CHEMBL941</td><td class="py-3 text-slate-300">298.7</td><td class="py-3 text-primary font-bold">-9.2</td><td class="py-3 text-slate-300">1.8</td><td class="py-3 text-slate-300">62.4</td><td class="py-3"><span class="text-green-400">통과</span></td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-slate-300">CHEMBL3137320</td><td class="py-3 text-slate-300">412.5</td><td class="py-3 text-slate-300">-9.2</td><td class="py-3 text-slate-300">3.4</td><td class="py-3 text-slate-300">94.1</td><td class="py-3"><span class="text-green-400">통과</span></td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-slate-300">CHEMBL1289494</td><td class="py-3 text-slate-300">387.2</td><td class="py-3 text-slate-300">-9.1</td><td class="py-3 text-slate-300">2.9</td><td class="py-3 text-slate-300">88.3</td><td class="py-3"><span class="text-green-400">통과</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div id="page-simulations" class="flex-1 flex-col gap-4 p-4 hidden" style="display:none; overflow-y:auto;">
  <div class="glass-panel rounded-xl p-6 flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-slate-100">Docking Simulations</h2>
        <p class="text-xs text-slate-400 mt-1">AutoDock Vina 배치 도킹 관리</p>
      </div>
      <button class="flex items-center gap-2 px-4 py-2 bg-primary text-white text-xs font-bold rounded-lg hover:brightness-110 transition-all uppercase tracking-wider">
        <span class="material-symbols-outlined text-sm">add_circle</span> 새 시뮬레이션
      </button>
    </div>
    <div class="grid grid-cols-3 gap-4">
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold">실행 중</p>
        <p class="text-3xl font-bold text-primary">3</p>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div class="bg-primary h-full rounded-full" style="width: 60%"></div></div>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold">완료</p>
        <p class="text-3xl font-bold text-green-400">1,842</p>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div class="bg-green-400 h-full rounded-full" style="width: 91%"></div></div>
      </div>
      <div class="glass-panel rounded-xl p-4 flex flex-col gap-2">
        <p class="text-xs text-slate-400 uppercase font-bold">실패</p>
        <p class="text-3xl font-bold text-red-400">12</p>
        <div class="w-full bg-slate-700/50 h-1.5 rounded-full mt-1"><div class="bg-red-400 h-full rounded-full" style="width: 1%"></div></div>
      </div>
    </div>
    <div class="glass-panel rounded-xl p-4">
      <h3 class="text-sm font-bold text-slate-100 mb-4">시뮬레이션 작업 목록</h3>
      <table class="w-full text-xs">
        <thead><tr class="text-slate-400 uppercase text-[10px] border-b border-slate-700">
          <th class="py-2 text-left">작업 ID</th><th class="py-2 text-left">타겟</th><th class="py-2 text-left">후보 수</th><th class="py-2 text-left">시작 시각</th><th class="py-2 text-left">소요 시간</th><th class="py-2 text-left">상태</th>
        </tr></thead>
        <tbody class="divide-y divide-slate-700/30">
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-slate-300">JOB-2024-0312</td><td class="py-3 text-slate-300">CHRNA1</td><td class="py-3 text-slate-300">2,017</td><td class="py-3 text-slate-400">2024-03-12 09:00</td><td class="py-3 text-slate-400">14h 23m</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-green-500/20 text-green-400">완료</span></td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-slate-300">JOB-2024-0318</td><td class="py-3 text-slate-300">MuSK</td><td class="py-3 text-slate-300">1,500</td><td class="py-3 text-slate-400">2024-03-18 14:00</td><td class="py-3 text-primary font-bold animate-pulse">진행 중...</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-primary/20 text-primary">실행 중</span></td></tr>
          <tr class="hover:bg-slate-700/20"><td class="py-3 font-mono text-slate-300">JOB-2024-0319</td><td class="py-3 text-slate-300">LRP4</td><td class="py-3 text-slate-300">800</td><td class="py-3 text-slate-400">2024-03-19 08:30</td><td class="py-3 text-primary font-bold animate-pulse">진행 중...</td><td class="py-3"><span class="px-2 py-0.5 rounded-full text-[10px] bg-primary/20 text-primary">실행 중</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
"""

# Inject SPA pages just before </body>
content = content.replace(
    '</main>',
    '</main>' + extra_pages
)

# 5. Streamlit Bridge
js_bridge = """
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>
<script>
    // ── SPA Page Switcher (global scope for onclick) ──────────────
    window.showPage = function(pageId) {
        // All possible page IDs
        const pages = ['page-dynamics', 'page-library', 'page-simulations'];
        const main = document.querySelector('main');
        const navIds = {
            'dashboard': 'nav-dashboard',
            'dynamics':  'nav-dynamics',
            'library':   'nav-library',
            'simulations': 'nav-simulations'
        };

        if (pageId === 'dashboard') {
            // Show main, hide all extra pages
            if (main) main.style.display = '';
            pages.forEach(p => {
                const el2 = document.getElementById(p);
                if(el2) el2.style.display = 'none';
            });
        } else {
            // Hide main, show target page
            if (main) main.style.display = 'none';
            pages.forEach(p => {
                const el2 = document.getElementById(p);
                if(el2) el2.style.display = (p === 'page-' + pageId) ? 'flex' : 'none';
            });
        }

        // Update nav active styles
        Object.entries(navIds).forEach(([key, id]) => {
            const link = document.getElementById(id);
            if (!link) return;
            if (key === pageId) {
                link.className = 'text-primary text-sm font-semibold';
            } else {
                link.className = 'text-slate-600 dark:text-slate-400 text-sm font-medium hover:text-primary transition-colors';
            }
        });

        window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setFrameHeight', height: document.body.scrollHeight}, '*');
    };

    // ── Professional 2D Binding Pocket Diagram ────────────────────
    window.drawBindingDiagram = function(residues, coeff, chemblId) {
        const svg = document.getElementById('mech-binding-svg');
        if (!svg) return;
        // Clear previous dynamic content
        while (svg.children.length > 2) svg.removeChild(svg.lastChild);  // keep <defs> + comment

        const ns = 'http://www.w3.org/2000/svg';
        const cx = 130, cy = 108; // center (ligand)
        const r = 68;             // radius for residue ring

        // ── Color mappings ───────────────────────────────────────
        const intColors = {
            'hbond':        { line: '#3b82f6', fill: 'rgba(59,130,246,0.18)', dash: '6,3', label: 'H-Bond' },
            'hydrophobic':  { line: '#22c55e', fill: 'rgba(34,197,94,0.12)',  dash: '3,3', label: 'Hydrophobic' },
            'pistack':      { line: '#a855f7', fill: 'rgba(168,85,247,0.18)', dash: null,  label: 'π-Stack' },
            'electrostatic':{ line: '#f97316', fill: 'rgba(249,115,22,0.18)', dash: null,  label: 'Electrostatic' },
            'vdw':          { line: '#94a3b8', fill: 'rgba(148,163,184,0.1)', dash: '2,4', label: 'vdW' },
        };

        const aaTypeColors = {
            'hydrophobic': '#4ade80',  // green
            'polar':       '#60a5fa',  // blue
            'positive':    '#fb923c',  // orange
            'negative':    '#f87171',  // red
            'aromatic':    '#c084fc',  // purple
        };

        const mkEl = (tag, attrs) => {
            const e = document.createElementNS(ns, tag);
            Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
            return e;
        };

        // ── Solvent-accessibility background blob ────────────────
        const blob = mkEl('ellipse', {cx, cy, rx: r+26, ry: r+20, fill: 'rgba(37,157,244,0.04)', stroke: '#259df4', 'stroke-width': '0.5', 'stroke-dasharray': '4,4'});
        svg.appendChild(blob);

        // ── Draw residues + interactions ─────────────────────────
        const n = residues.length;
        residues.forEach((res, i) => {
            const angle = (2 * Math.PI * i / n) - Math.PI / 2;
            const rx2 = cx + r * Math.cos(angle);
            const ry2 = cy + r * Math.sin(angle);

            const style = intColors[res.interaction] || intColors['vdw'];
            const aaColor = aaTypeColors[res.aatype] || '#94a3b8';

            // Interaction line
            const line = mkEl('line', {
                x1: cx, y1: cy, x2: rx2, y2: ry2,
                stroke: style.line, 'stroke-width': res.strength > 0.7 ? '2' : '1.2',
                'stroke-opacity': '0.8',
            });
            if (style.dash) line.setAttribute('stroke-dasharray', style.dash);
            svg.appendChild(line);

            // Distance label on line midpoint
            const mx = (cx + rx2) / 2 + 6, my = (cy + ry2) / 2 - 4;
            const distLabel = mkEl('text', {
                x: mx, y: my, 'font-size': '7', fill: style.line, 'text-anchor': 'middle', opacity: '0.9'
            });
            distLabel.textContent = res.distance + '\\u00c5';
            svg.appendChild(distLabel);

            // Residue node background (rounded rect approximated as circle)
            const rNode = 14;
            const nodeCircle = mkEl('circle', {
                cx: rx2, cy: ry2, r: rNode,
                fill: style.fill, stroke: aaColor, 'stroke-width': '1.5',
            });
            if (res.strength > 0.7) nodeCircle.setAttribute('filter', 'url(#glow)');
            svg.appendChild(nodeCircle);

            // Residue label (e.g. "Tyr-451")
            const lbl1 = mkEl('text', { x: rx2, y: ry2 - 3, 'font-size': '7.5', fill: '#e2e8f0', 'text-anchor': 'middle', 'font-weight': 'bold' });
            lbl1.textContent = res.name.split('-')[0];
            svg.appendChild(lbl1);
            const lbl2 = mkEl('text', { x: rx2, y: ry2 + 7, 'font-size': '6.5', fill: aaColor, 'text-anchor': 'middle' });
            lbl2.textContent = '-' + res.name.split('-')[1];
            svg.appendChild(lbl2);
        });

        // ── Central Ligand Node ───────────────────────────────────
        const ligBg = mkEl('ellipse', {cx, cy, rx: 28, ry: 18, fill: 'rgba(37,157,244,0.25)', stroke: '#259df4', 'stroke-width': '2', filter: 'url(#glow)'});
        svg.appendChild(ligBg);
        const ligId = mkEl('text', {x: cx, y: cy - 4, 'font-size': '7.5', fill: '#ffffff', 'text-anchor': 'middle', 'font-weight': 'bold'});
        ligId.textContent = chemblId ? chemblId.replace('CHEMBL','CHBL') : 'Ligand';
        svg.appendChild(ligId);
        const ligSub = mkEl('text', {x: cx, y: cy + 8, 'font-size': '6.5', fill: '#93c5fd', 'text-anchor': 'middle'});
        ligSub.textContent = 'ΔG ' + (parseFloat(coeff) * -11.5).toFixed(1) + ' kcal';
        svg.appendChild(ligSub);

        // ── Allosteric coefficient bar ────────────────────────────
        const barX = 4, barY = 200, barW = 100;
        const barBg = mkEl('rect', {x: barX, y: barY, width: barW, height: 5, rx: 2.5, fill: '#1e293b'});
        const barFill = mkEl('rect', {x: barX, y: barY, width: barW * parseFloat(coeff), height: 5, rx: 2.5, fill: '#259df4'});
        const barLabel = mkEl('text', {x: barX, y: barY - 3, 'font-size': '7', fill: '#94a3b8'});
        barLabel.textContent = 'Allosteric Coupling';
        const coeffText = mkEl('text', {x: barX + barW + 4, y: barY + 5, 'font-size': '8', fill: '#259df4', 'font-weight': 'bold'});
        coeffText.textContent = coeff;
        svg.appendChild(barBg); svg.appendChild(barFill); svg.appendChild(barLabel); svg.appendChild(coeffText);
    };

    (function() {
        let viewer = null;
        let currentProtein = null;

        const initViewer = () => {
            if (viewer) return;
            const element = document.getElementById('3dmol-viewer');
            if (element) {
                viewer = $3Dmol.createViewer(element, { backgroundColor: '#0f172a' });
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
                    if(args.table_html && el('candidate-table')) el('candidate-table').innerHTML = args.table_html;
                    if(args.ai_html && el('ai-chat-output')) el('ai-chat-output').innerHTML = args.ai_html;
                    
                    const setVal = (id, v) => { const node = el(id); if(node) node.innerText = v; };
                    const setPct = (id, v) => { const node = el(id); if(node) node.style.width = v + '%'; };
                    
                    if(args.chrna1_score) setVal('chrna1-score-val', args.chrna1_score);
                    if(args.musk_score) setVal('musk-score-val', args.musk_score);
                    if(args.lrp4_score) setVal('lrp4-score-val', args.lrp4_score);
                    
                    if(args.chrna1_progress) setPct('chrna1-progress', args.chrna1_progress);
                    if(args.musk_progress) setPct('musk-progress', args.musk_progress);
                    if(args.lrp4_progress) setPct('lrp4-progress', args.lrp4_progress);

                    if(args.viewer_complex) setVal('viewer-complex-title', args.viewer_complex);
                    if(args.viewer_ligand) setVal('viewer-ligand-label', args.viewer_ligand);

                    // Mechanism Insight updates
                    if(args.mechanism_inference) setVal('mechanism-inference', args.mechanism_inference);
                    if(args.mechanism_coeff) setVal('mechanism-coeff', args.mechanism_coeff);
                    if(args.mechanism_subtitle) setVal('mechanism-subtitle', args.mechanism_subtitle);

                    // Professional 2D Binding Pocket Diagram
                    if (args.binding_residues) {
                        drawBindingDiagram(args.binding_residues, args.mechanism_coeff || '0.8', args.chembl_id || '');
                    }

                    // RMSD chart path updates
                    const bb = el('rmsd-backbone-path'), lg = el('rmsd-ligand-path');
                    if(bb && args.rmsd_backbone_path) bb.setAttribute('d', args.rmsd_backbone_path);
                    if(lg && args.rmsd_ligand_path) lg.setAttribute('d', args.rmsd_ligand_path);

                    // 3D Rendering Logic
                    if (args.protein_pdb || args.ligand_pdbqt) {
                        initViewer();
                        if (viewer) {
                            // If protein changed or we are initializing, clear and re-add
                            if (args.protein_pdb && args.protein_pdb !== currentProtein) {
                                viewer.clear();
                                viewer.addModel(args.protein_pdb, "pdb");
                                viewer.setStyle({model: 0}, { cartoon: { color: 'spectrum', opacity: 0.8 } });
                                currentProtein = args.protein_pdb;
                                
                                if (args.ligand_pdbqt) {
                                    const lModel = viewer.addModel(args.ligand_pdbqt, "pdbqt");
                                    viewer.setStyle({model: lModel.getID()}, { stick: { colorscheme: 'greenCarbon', radius: 0.2 }, sphere: { radius: 0.4 } });
                                    viewer.zoomTo({model: lModel.getID()});
                                } else {
                                    viewer.zoomTo();
                                }
                            } else if (args.ligand_pdbqt) {
                                // Protein is same, just update/add ligand
                                // To remove previous ligand without getModelsByFilter, 
                                // we can just clear and re-add everything if simpler, 
                                // but let's try to just clear and re-render if it's not too slow.
                                viewer.clear();
                                viewer.addModel(currentProtein, "pdb");
                                viewer.setStyle({model: 0}, { cartoon: { color: 'spectrum', opacity: 0.8 } });
                                
                                const lModel = viewer.addModel(args.ligand_pdbqt, "pdbqt");
                                viewer.setStyle({model: lModel.getID()}, { stick: { colorscheme: 'greenCarbon', radius: 0.2 }, sphere: { radius: 0.4 } });
                                viewer.zoomTo({model: lModel.getID()});
                            }
                            viewer.render();
                        }
                    }

                    Streamlit.setFrameHeight(document.body.scrollHeight);
                } catch(e) { console.error("Render catch:", e); }
            }
        };
        window.addEventListener("message", (e) => { if (e.data.type === "streamlit:render") Streamlit.onRender(e.data.args); });
        window.addEventListener('load', () => {
            const el = (id) => document.getElementById(id);
            const b = el('btn-view-all'); if(b) b.onclick = () => Streamlit.setComponentValue({action: 'view_all_candidates', ts: Date.now()});
            const s = el('ai-send-btn'), i = el('ai-input');
            if(s && i) {
                s.onclick = () => { if(i.value) { Streamlit.setComponentValue({action: 'ai_query', query: i.value, ts: Date.now()}); i.value=''; } };
                i.onkeypress = (e) => { if(e.key==='Enter') s.click(); };
            }
            
            const table = el('candidate-table');
            if(table) {
                table.onclick = (e) => {
                    const row = e.target.closest('tr');
                    if(row && row.dataset.id) {
                        Streamlit.setComponentValue({action: 'select_candidate', id: row.dataset.id, ts: Date.now()});
                    }
                };
            }

        initViewer();
            Streamlit.setComponentReady();
            Streamlit.setFrameHeight(document.body.scrollHeight);

            // ── Animation / Video Player ─────────────────────────────
            let isPlaying = false;
            let animationId = null;
            let simTime = 0;
            const MAX_TIME = 50;

            const updateTime = () => {
                const t = el('player-time');
                if (t) t.innerText = 'TIME: ' + simTime.toFixed(1) + 'ns';
            };

            const animate = () => {
                if (!isPlaying) return;
                simTime += 0.2;
                if (simTime > MAX_TIME) simTime = 0;
                updateTime();
                if (viewer) {
                    viewer.rotate(1, 'y');
                    viewer.render();
                }
                animationId = requestAnimationFrame(animate);
            };

            const playBtn = el('btn-play-pause');
            if (playBtn) {
                playBtn.onclick = () => {
                    isPlaying = !isPlaying;
                    playBtn.innerText = isPlaying ? 'pause_circle' : 'play_circle';
                    if (isPlaying) animate();
                    else if (animationId) cancelAnimationFrame(animationId);
                };
            }

            const skipPrev = el('btn-skip-prev');
            if (skipPrev) {
                skipPrev.onclick = () => {
                    simTime = Math.max(0, simTime - 5);
                    updateTime();
                    if (viewer) { viewer.rotate(-30, 'y'); viewer.render(); }
                };
            }

            const skipNext = el('btn-skip-next');
            if (skipNext) {
                skipNext.onclick = () => {
                    simTime = Math.min(MAX_TIME, simTime + 5);
                    updateTime();
                    if (viewer) { viewer.rotate(30, 'y'); viewer.render(); }
                };
            }

            // ── Toolbar Buttons ─────────────────────────────────────
            // Camera / Screenshot
            const screenshotBtn = el('btn-screenshot');
            if (screenshotBtn) {
                screenshotBtn.onclick = () => {
                    if (!viewer) return;
                    const uri = viewer.pngURI();
                    const link = document.createElement('a');
                    link.download = 'mg_complex_snapshot.png';
                    link.href = uri;
                    link.click();
                };
            }

            // Layers / Style Cycle
            const styles = ['cartoon', 'surface', 'stick'];
            let styleIdx = 0;
            const styleBtn = el('btn-style-cycle');
            if (styleBtn) {
                styleBtn.onclick = () => {
                    if (!viewer || !currentProtein) return;
                    styleIdx = (styleIdx + 1) % styles.length;
                    const s = styles[styleIdx];
                    if (s === 'cartoon') {
                        viewer.setStyle({model: 0}, { cartoon: { color: 'spectrum', opacity: 0.85 } });
                    } else if (s === 'surface') {
                        viewer.setStyle({model: 0}, { surface: { opacity: 0.6, colorscheme: 'greenCarbon' } });
                    } else {
                        viewer.setStyle({model: 0}, { stick: { colorscheme: 'Jmol', radius: 0.15 } });
                    }
                    viewer.render();
                    styleBtn.title = '현재: ' + s;
                };
            }

            // Zoom to Ligand
            const zoomBtn = el('btn-zoom-ligand');
            if (zoomBtn) {
                zoomBtn.onclick = () => {
                    if (!viewer) return;
                    viewer.zoomTo({model: 1});
                    viewer.render();
                };
            }
        });
    })();
</script>
"""

content = content.replace("</body>", js_bridge + "</body>")

with open(dst_html, "w", encoding="utf-8") as f:
    f.write(content)
print("Inject JS: Reconstructed with 3Dmol viewer and Selection support.")


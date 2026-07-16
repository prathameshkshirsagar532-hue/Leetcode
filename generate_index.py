import os
import json
import re
from concurrent.futures import ThreadPoolExecutor

EXCLUDE_DIRS = {'.git', '.github', '.vscode', 'node_modules'}

def process_folder(folder_name):
    if os.path.isdir(folder_name) and folder_name not in EXCLUDE_DIRS and not folder_name.startswith('.'):
        parts = folder_name.split('_', 3)
        if len(parts) >= 4:
            q_num_str = parts[0]
            if q_num_str.isdigit():
                folder_path = os.path.join('.', folder_name)
                sol_file = ""
                notes_file = ""
                
                try:
                    for file in os.listdir(folder_path):
                        if file.lower() == 'readme.md':
                            notes_file = f"./{folder_name}/{file}"
                        elif file.endswith(('.py', '.cpp', '.java', '.js', '.ts', '.go', '.rs', '.py3')):
                            sol_file = f"./{folder_name}/{file}"
                except Exception:
                    pass

                try:
                    return {
                        "number": q_num_str,
                        "num_int": int(q_num_str),
                        "topic": parts[1],        
                        "difficulty": parts[2],   
                        "title": parts[3].replace('_', ' '),
                        "path": folder_name.replace('\\', '/'),
                        "sol_file": sol_file,
                        "notes_file": notes_file
                    }
                except (ValueError, IndexError):
                    pass
    return None

def build_index():
    all_items = os.listdir('.')
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_folder, all_items)
    
    questions = [r for r in results if r is not None]
    questions.sort(key=lambda x: x['num_int'])
    
    js_content = f"const rawQuestionsData = {json.dumps(questions, indent=2)};"
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"⚡ Success! {len(questions)} questions indexed in data.js")

    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeetCode Premium Vault Dashboard</title>
    <script src="https://tailwindcss.com"></script>
    <link href="https://googleapis.com" rel="stylesheet">
    <link rel="stylesheet" href="https://cloudflare.com">
    <script src="https://jsdelivr.net"></script>
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #090d16; }
        .code-font { font-family: 'JetBrains Mono', monospace; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
        .active-row { background-color: rgba(56, 189, 248, 0.08) !important; border-left: 4px solid #38bdf8 !important; }
        .tab-btn.active { border-color: #38bdf8; color: #38bdf8; background: rgba(56, 189, 248, 0.05); }
    </style>
</head>
<body class="text-slate-300 h-screen overflow-hidden flex flex-col">
    <header class="bg-[#0f172a] border-b border-slate-800 px-6 py-4 flex items-center justify-between shrink-0 shadow-lg">
        <div class="flex items-center gap-3">
            <div class="bg-gradient-to-tr from-amber-500 to-orange-600 p-2.5 rounded-xl shadow-md shadow-orange-900/20">
                <i class="fa-solid fa-cube text-white text-xl"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">LeetCode Studio</h1>
                <p class="text-xs text-slate-500 font-medium tracking-wide">STATE-SAVED PERSISTENT DEVELOPMENT VAULT</p>
            </div>
        </div>
        <div class="bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-2 text-xs font-semibold text-slate-400">
            <i class="fa-solid fa-layer-group text-sky-400 mr-2"></i>Loaded: <span id="displayed-count" class="text-sky-400 font-bold">0</span> / <span id="total-count" class="text-slate-500">0</span> Solved
        </div>
    </header>

    <main class="flex-1 flex flex-col md:flex-row overflow-hidden relative">
        <section id="left-panel" class="w-full md:w-[42%] bg-[#0d1322] border-r border-slate-800 flex flex-col h-full overflow-hidden shrink-0 z-10 transition-all duration-300">
            <div class="p-5 border-b border-slate-800 bg-[#0b101d] space-y-4 shrink-0">
                <div class="relative">
                    <i class="fa-solid fa-magnifying-glass absolute left-4 top-3.5 text-slate-500 text-sm"></i>
                    <input type="text" id="search" placeholder="Search parameters (e.g., Array, Two Sum, #0001)..." 
                           class="w-full pl-11 pr-4 py-3 bg-[#070b14] border border-slate-800 text-slate-200 text-sm rounded-xl focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition placeholder-slate-600">
                </div>

                <div class="bg-[#070b14]/50 border border-slate-800/80 rounded-xl p-3 flex flex-wrap items-center gap-3 justify-between">
                    <span class="text-xs font-semibold uppercase tracking-wider text-slate-500"><i class="fa-solid fa-sliders text-amber-500 mr-1.5"></i> Index Range</span>
                    <div class="flex items-center gap-2">
                        <input type="number" id="range-from" placeholder="Min 200" class="w-20 px-2.5 py-1.5 bg-[#090d16] border border-slate-800 text-center text-xs rounded-md text-slate-300 focus:outline-none focus:border-sky-500">
                        <span class="text-slate-600 text-xs font-bold">to</span>
                        <input type="number" id="range-to" placeholder="Max 400" class="w-20 px-2.5 py-1.5 bg-[#090d16] border border-slate-800 text-center text-xs rounded-md text-slate-300 focus:outline-none focus:border-sky-500">
                        <button id="apply-range" class="bg-sky-600 hover:bg-sky-500 text-white text-xs px-3 py-1.5 rounded-md font-bold transition shadow-sm shadow-sky-900/30">Apply</button>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4 pt-1">
                    <div>
                        <div class="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-2">Category Filters</div>
                        <div id="topic-group" class="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto pr-1"></div>
                    </div>
                    <div>
                        <div class="text-[11px] font-bold text-slate-500 tracking-wider uppercase mb-2">Complexity Matrix</div>
                        <div id="diff-group" class="flex flex-wrap gap-1.5"></div>
                    </div>
                </div>

                <button id="reset-range" class="w-full border border-dashed border-slate-800 hover:border-red-500/30 hover:bg-red-500/5 text-slate-500 hover:text-red-400 text-xs py-2 rounded-xl transition flex items-center justify-center gap-2 font-medium">
                    <i class="fa-solid fa-arrow-rotate-left"></i> Purge Filter & Cache Parameters
                </button>
            </div>

            <div class="flex-1 overflow-y-auto bg-[#090d16]/30 divide-y divide-slate-900/60" id="list-stream"></div>
        </section>
        <section id="right-panel" class="hidden md:flex flex-1 flex-col bg-[#0b0f19] h-full overflow-hidden relative z-0">
            <div id="blank-state" class="absolute inset-0 flex flex-col items-center justify-center p-8 text-center bg-[#090d16]/80 backdrop-blur-sm z-50">
                <div class="bg-slate-900/80 border border-slate-800 p-6 rounded-3xl mb-4 text-slate-600 animate-pulse">
                    <i class="fa-solid fa-code-laptop text-5xl"></i>
                </div>
                <h3 class="text-slate-300 font-bold text-lg">No Architecture Selected</h3>
                <p class="text-slate-500 text-xs mt-1 max-w-xs">Select any LeetCode problem architecture matrix node from the left panel stream view to visualize real-time dynamic source code and production engineering notes.</p>
            </div>

            <div class="bg-[#0f172a] border-b border-slate-800 px-6 py-3 flex items-center justify-between shrink-0">
                <div class="flex items-center gap-3">
                    <span id="active-num" class="code-font text-xs font-bold bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700">#0000</span>
                    <h2 id="active-title" class="text-base font-bold text-white tracking-tight">Select Architecture Node</h2>
                </div>
                <div class="flex items-center bg-[#070b14] p-1 border border-slate-800 rounded-xl">
                    <button onclick="switchTab('notes')" id="btn-tab-notes" class="tab-btn active text-xs font-semibold px-4 py-2 border border-transparent rounded-lg transition flex items-center gap-2"><i class="fa-regular fa-file-lines text-amber-400"></i> Engineering Notes</button>
                    <button onclick="switchTab('code')" id="btn-tab-code" class="tab-btn text-xs font-semibold px-4 py-2 border border-transparent rounded-lg transition flex items-center gap-2"><i class="fa-solid fa-terminal text-emerald-400"></i> Optimized Solution</button>
                </div>
            </div>

            <div class="flex-1 overflow-y-auto p-6 bg-[#090d16]/40">
                <div id="view-notes" class="prose prose-invert max-w-none text-slate-300 space-y-4">
                    <div class="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 text-sm leading-relaxed" id="markdown-canvas"></div>
                </div>
                <div id="view-code" class="hidden h-full flex flex-col">
                    <pre class="bg-[#070b14] border border-slate-800 rounded-2xl p-5 code-font text-xs overflow-auto text-emerald-400 leading-relaxed h-full w-full" id="code-canvas"></pre>
                </div>
            </div>

            <button onclick="toggleMobileViewPanel(true)" class="md:hidden absolute bottom-5 left-5 bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 p-3.5 rounded-full shadow-2xl z-50 transition">
                <i class="fa-solid fa-arrow-left"></i> Back to Stream List
            </button>
        </section>
    </main>
    <script src="data.js"></script>
    <script>
        const data = typeof rawQuestionsData !== 'undefined' ? rawQuestionsData : [];
        let filteredData = [...data];
        let visibleCount = 50;
        let activeQuestion = null;
        let currentTab = 'notes';

        const listStream = document.getElementById('list-stream');
        const searchInput = document.getElementById('search');
        const fromInput = document.getElementById('range-from');
        const toInput = document.getElementById('range-to');
        const rightPanel = document.getElementById('right-panel');
        const leftPanel = document.getElementById('left-panel');
        const blankState = document.getElementById('blank-state');

        const topics = [...new Set(data.map(item => item.topic))].sort();
        const difficulties = ['Easy', 'Medium', 'Hard'];

        document.getElementById('topic-group').innerHTML = topics.map(t => 
            `<label class="cursor-pointer text-[10px] font-semibold px-2 py-1 bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-400 rounded-md transition flex items-center gap-1 select-none" id="lbl-topic-\${t}"><input type="checkbox" class="topic-cb hidden" value="\${t}">\${t}</label>`
        ).join('');
        
        document.getElementById('diff-group').innerHTML = difficulties.map(d => {
            let color = d==='Easy'?'hover:border-emerald-500/40':d==='Medium'?'hover:border-amber-500/40':'hover:border-rose-500/40';
            return `<label class="cursor-pointer text-[10px] font-semibold px-2.5 py-1 bg-slate-900 border border-slate-800 \${color} text-slate-400 rounded-md transition flex items-center gap-1 select-none" id="lbl-diff-\${d}"><input type="checkbox" class="diff-cb hidden" value="\${d}">\${d}</label>`;
        }).join('');

        function filterData() {
            const query = searchInput.value.toLowerCase().trim();
            const fromNum = parseInt(fromInput.value) || 0;
            const toNum = parseInt(toInput.value) || Infinity;
            
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
            const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);

            document.querySelectorAll('.topic-cb').forEach(cb => {
                cb.parentElement.classList.toggle('bg-sky-500/10', cb.checked);
                cb.parentElement.classList.toggle('border-sky-500/40', cb.checked);
                cb.parentElement.classList.toggle('text-sky-400', cb.checked);
            });
            document.querySelectorAll('.diff-cb').forEach(cb => {
                let colorClass = cb.value==='Easy'?'bg-emerald-500/10 border-emerald-500/40 text-emerald-400':
                                 cb.value==='Medium'?'bg-amber-500/10 border-amber-500/40 text-amber-400':
                                 'bg-rose-500/10 border-rose-500/40 text-rose-400';
                cb.parentElement.className = cb.checked ? 
                    `cursor-pointer text-[10px] font-semibold px-2.5 py-1 border rounded-md transition flex items-center gap-1 select-none \${colorClass}` : 
                    `cursor-pointer text-[10px] font-semibold px-2.5 py-1 bg-slate-900 border border-slate-800 text-slate-400 rounded-md transition flex items-center gap-1 select-none`;
            });

            filteredData = data.filter(q => {
                const matchesSearch = q.title.toLowerCase().includes(query) || q.topic.toLowerCase().includes(query) || q.number.includes(query);
                const matchesRange = q.num_int >= fromNum && q.num_int <= toNum;
                const matchesTopic = selectedTopics.length === 0 || selectedTopics.includes(q.topic);
                const matchesDiff = selectedDiffs.length === 0 || selectedDiffs.includes(q.difficulty);
                return matchesSearch && matchesRange && matchesTopic && matchesDiff;
            });

            visibleCount = 50;
            renderStreamList();
            saveGlobalPersistentState();
        }

        function renderStreamList() {
            document.getElementById('total-count').textContent = data.length;
            document.getElementById('displayed-count').textContent = filteredData.length;

            const slice = filteredData.slice(0, visibleCount);
            if (slice.length === 0) {
                listStream.innerHTML = `<div class="p-8 text-center text-xs text-slate-600 font-medium"><i class="fa-solid fa-ban text-lg mb-2 block"></i>No architecture matrix matches active query state!</div>`;
                return;
            }

            listStream.innerHTML = slice.map(q => {
                let diffBadgeColor = q.difficulty==='Easy'?'bg-emerald-500/5 text-emerald-400 border-emerald-500/20':
                                     q.difficulty==='Medium'?'bg-amber-500/5 text-amber-400 border-amber-200/10':
                                     'bg-rose-500/5 text-rose-400 border-rose-500/20';
                let isSelected = activeQuestion && activeQuestion.num_int === q.num_int ? 'active-row' : '';
                
                return `
                    <div onclick="selectArchitectureNode(\${q.num_int})" id="node-\${q.num_int}" class="p-4 bg-transparent hover:bg-slate-900/40 border-l-4 border-transparent cursor-pointer transition flex items-center justify-between group \${isSelected}">
                        <div class="space-y-1.5 max-w-[75%]">
                            <div class="flex items-center gap-2">
                                <span class="code-font text-[11px] font-bold text-slate-500">#\${q.number}</span>
                                <span class="text-[10px] font-semibold px-2 py-0.5 rounded border bg-slate-900/80 border-slate-800 text-slate-400 tracking-wide">\${q.topic}</span>
                                <span class="text-[10px] font-semibold px-2 py-0.5 rounded border \${diffBadgeColor}">\${q.difficulty}</span>
                            </div>
                            <h4 class="text-xs font-bold text-slate-200 group-hover:text-sky-400 transition truncate tracking-tight">\${q.title}</h4>
                        </div>
                        <i class="fa-solid fa-chevron-right text-slate-700 group-hover:text-slate-500 text-xs transition pr-2"></i>
                    </div>
                `;
            }).join('');
        }
        function selectArchitectureNode(numInt) {
            const question = data.find(q => q.num_int === numInt);
            if (!question) return;

            activeQuestion = question;
            
            document.querySelectorAll('.active-row').forEach(el => el.classList.remove('active-row'));
            const selectedRow = document.getElementById(`node-\${numInt}`);
            if (selectedRow) selectedRow.classList.add('active-row');

            document.getElementById('active-num').textContent = `#\${question.number}`;
            document.getElementById('active-title').textContent = question.title;
            
            blankState.classList.add('hidden');
            
            fetchViewportData();
            toggleMobileViewPanel(false);
        }

        function fetchViewportData() {
            if(!activeQuestion) return;
            
            const markdownCanvas = document.getElementById('markdown-canvas');
            const codeCanvas = document.getElementById('code-canvas');

            markdownCanvas.innerHTML = `<div class="text-xs text-slate-500 font-medium py-4 text-center"><i class="fa-solid fa-spinner animate-spin mr-2"></i>Loading notes architecture payload...</div>`;
            codeCanvas.textContent = `// Loading dynamic repository source nodes payload...`;

            if (activeQuestion.notes_file) {
                fetch(activeQuestion.notes_file)
                    .then(res => res.ok ? res.text() : `### Architecture Notes File Empty\\nNo explicit internal text configuration logged at target source path \`\${activeQuestion.notes_file}\`.`)
                    .then(text => { markdownCanvas.innerHTML = marked.parse(text); })
                    .catch(() => { markdownCanvas.innerHTML = `<p class="text-xs text-slate-500 italic">No notes found or unable to access repository layout network node structure.</p>`; });
            } else {
                markdownCanvas.innerHTML = `
                    <div class="border border-dashed border-slate-800 rounded-xl p-6 text-center text-slate-600">
                        <i class="fa-regular fa-folder-open text-2xl mb-2 block"></i>
                        <p class="text-xs font-semibold">README.md Asset Node Missing</p>
                        <p class="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto">Create a README.md inside folder \`\${activeQuestion.path}\` to map persistent notes dynamic payload structures here.</p>
                    </div>`;
            }

            if (activeQuestion.sol_file) {
                fetch(activeQuestion.sol_file)
                    .then(res => res.ok ? res.text() : `// Source module array empty inside node scope target tree allocation.`)
                    .then(code => { codeCanvas.textContent = code; })
                    .catch(() => { codeCanvas.textContent = `// Code file unreadable or failed to pipeline dynamic runtime context link layout mapping.`; });
            } else {
                codeCanvas.textContent = `// Optimization Array Missing.\\n// Please create code files (.py, .cpp, .java) inside folder: \\n// \`\${activeQuestion.path}/\``;
            }
        }

        function switchTab(target) {
            currentTab = target;
            document.getElementById('btn-tab-notes').classList.toggle('active', target === 'notes');
            document.getElementById('btn-tab-code').classList.toggle('active', target === 'code');
            document.getElementById('view-notes').classList.toggle('hidden', target !== 'notes');
            document.getElementById('view-code').classList.toggle('hidden', target !== 'code');
        }

        function toggleMobileViewPanel(showStreamList) {
            if (window.innerWidth >= 768) return;
            if (showStreamList) {
                leftPanel.classList.remove('hidden');
                leftPanel.classList.add('w-full');
                rightPanel.classList.add('hidden');
            } else {
                leftPanel.classList.add('hidden');
                rightPanel.classList.remove('hidden');
                rightPanel.classList.add('w-full');
            }
        }

        function saveGlobalPersistentState() {
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
            const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);
            localStorage.setItem('elitePremiumCodingVaultState', JSON.stringify({
                search: searchInput.value, from: fromInput.value, to: toInput.value, topics: selectedTopics, diffs: selectedDiffs
            }));
        }

        function loadGlobalPersistentState() {
            const state = JSON.parse(localStorage.getItem('elitePremiumCodingVaultState'));
            if (!state) { renderStreamList(); return; }
            searchInput.value = state.search || ''; fromInput.value = state.from || ''; toInput.value = state.to || '';
            
            if (state.topics) state.topics.forEach(t => { const cb = document.querySelector(`.topic-cb[value="\${t}"]`); if (cb) cb.checked = true; });
            if (state.diffs) state.diffs.forEach(d => { const cb = document.querySelector(`.diff-cb[value="\${d}"]`); if (cb) cb.checked = true; });
            filterData();
        }

        listStream.addEventListener('scroll', () => {
            if ((listStream.innerHeight + listStream.scrollY) >= listStream.scrollHeight - 80) {
                if (visibleCount < filteredData.length) { visibleCount += 30; renderStreamList(); }
            }
        });

        searchInput.addEventListener('input', filterData);
        document.getElementById('apply-range').addEventListener('click', filterData);
        document.querySelectorAll('.topic-cb, .diff-cb').forEach(cb => cb.addEventListener('change', filterData));
        
        document.getElementById('reset-range').addEventListener('click', () => {
            searchInput.value = ''; fromInput.value = ''; toInput.value = '';
            document.querySelectorAll('.topic-cb, .diff-cb').forEach(cb => cb.checked = false);
            localStorage.removeItem('elitePremiumCodingVaultState');
            filterData();
            blankState.classList.remove('hidden');
        });

        loadGlobalPersistentState();
        toggleMobileViewPanel(true);
    </script>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("🌐 Ultra Premium Live Split-Screen Dashboard Generated successfully!")

if __name__ == "__main__":
    build_index()

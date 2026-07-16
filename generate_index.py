import os
import json
from concurrent.futures import ThreadPoolExecutor

EXCLUDE_DIRS = {'.git', '.github', '.vscode', 'node_modules'}

def process_folder(folder_name):
    """Har folder ko super fast processing ke liye function"""
    if os.path.isdir(folder_name) and folder_name not in EXCLUDE_DIRS and not folder_name.startswith('.'):
        parts = folder_name.split('_', 3)
        if len(parts) >= 4:
            if parts[0].isdigit():
                try:
                    q_num_int = int(parts[0])
                except (ValueError, IndexError):
                    q_num_int = 9999
                return {
                    "number": parts[0],
                    "num_int": q_num_int,
                    "topic": parts[1],
                    "difficulty": parts[2],
                    "title": parts[3].replace('_', ' '),
                    "path": folder_name.replace('\\', '/')
                }
    return None

def build_index():
    all_items = os.listdir('.')
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_folder, all_items)
    
    questions = [r for r in results if r is not None]
    questions.sort(key=lambda x: x['num_int'])
    
    # Base layout header string configuration
    html_start = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Persistent Coding Vault</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; max-width: 1100px; margin: 0 auto; padding: 20px; }
        h1 { color: #58a6ff; text-align: center; margin-bottom: 5px; }
        .stats { text-align: center; color: #8b949e; margin-bottom: 25px; font-size: 14px; }
        .filter-section { background: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 25px; }
        .search-box { width: 100%; padding: 12px; font-size: 15px; border: 1px solid #30363d; background: #0d1117; color: #c9d1d9; border-radius: 6px; box-sizing: border-box; margin-bottom: 15px; }
        .search-box:focus { outline: none; border-color: #58a6ff; }
        .range-container { display: flex; gap: 15px; align-items: center; margin-bottom: 20px; background: #21262d; padding: 12px; border-radius: 6px; border: 1px solid #30363d; flex-wrap: wrap; }
        .range-input { background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 8px; border-radius: 4px; width: 100px; font-size: 14px; text-align: center; }
        .range-input:focus { outline: none; border-color: #58a6ff; }
        .range-btn { background: #238636; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .range-btn:hover { background: #2ea043; }
        .reset-btn { background: #da3637; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .reset-btn:hover { background: #f85149; }
        .filter-group-title { font-weight: bold; margin-bottom: 8px; color: #8b949e; font-size: 13px; text-transform: uppercase; }
        .checkbox-container { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
        .checkbox-label { background: #21262d; border: 1px solid #30363d; padding: 6px 12px; border-radius: 20px; font-size: 13px; cursor: pointer; display: flex; align-items: center; user-select: none; }
        .checkbox-label input { display: none; }
        .checkbox-label.active { background: rgba(88, 166, 255, 0.15); border-color: #58a6ff; color: #58a6ff; }
        table { width: 100%; border-collapse: collapse; background: #161b22; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #30363d; font-size: 14px; }
        th { background: #21262d; color: #f0f6fc; }
        tr:hover { background: #1f242c; }
        a { color: #58a6ff; text-decoration: none; font-weight: bold; }
        .badge { padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; background: #21262d; border: 1px solid #30363d; }
        .diff-easy { border-color: #238636; color: #2ea043; }
        .diff-medium { border-color: #9e6a03; color: #d29922; }
        .diff-hard { border-color: #da3637; color: #f85149; }
    </style>
</head>
<body>
    <h1>🚀 My State-Saved Coding Vault</h1>
"""

    html_stats = '<div class="stats">Showing <span id="displayed-count" style="color: #58a6ff; font-weight: bold;">0</span> of <span id="total-count">' + str(len(questions)) + '</span> Questions</div>'

    html_end = """
    <div class="filter-section">
        <div class="filter-group-title">🎯 Set Question Range</div>
        <div class="range-container">
            <label>From Q.No:</label>
            <input type="number" id="range-from" class="range-input" placeholder="e.g. 200" min="1">
            <label>To Q.No:</label>
            <input type="number" id="range-to" class="range-input" placeholder="e.g. 300" min="1">
            <button id="apply-range" class="range-btn">Apply Range</button>
            <button id="reset-range" class="reset-btn">Clear All Settings</button>
        </div>
        <input type="text" id="search" class="search-box" placeholder="Instant Search by Title or Number...">
        <div class="filter-group-title">Topics</div>
        <div id="topic-group" class="checkbox-container"></div>
        <div class="filter-group-title">Difficulty</div>
        <div id="diff-group" class="checkbox-container"></div>
    </div>
    <table>
        <thead>
            <tr>
                <th style="width: 10%;">Q.No</th>
                <th style="width: 15%;">Topic</th>
                <th style="width: 15%;">Difficulty</th>
                <th style="width: 50%;">Title</th>
                <th style="width: 10%;">Link</th>
            </tr>
        </thead>
        <tbody id="table-body"></tbody>
    </table>
    <script>
"""    html_js_data = "const data = " + json.dumps(questions) + ";\n"

    html_js_logic = """        let filteredData = [...data];
        let visibleCount = 50; 
        const tbody = document.getElementById('table-body');
        const searchInput = document.getElementById('search');
        const fromInput = document.getElementById('range-from');
        const toInput = document.getElementById('range-to');
        const topics = [...new Set(data.map(item => item.topic))].sort();
        const difficulties = [...new Set(data.map(item => item.difficulty))].sort();
        
        document.getElementById('topic-group').innerHTML = topics.map(t => `<label class="checkbox-label" id="lbl-topic-${t}"><input type="checkbox" class="topic-cb" value="${t}">${t}</label>`).join('');
        document.getElementById('diff-group').innerHTML = difficulties.map(d => `<label class="checkbox-label" id="lbl-diff-${d}"><input type="checkbox" class="diff-cb" value="${d}">${d}</label>`).join('');
        
        function saveState() {
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
            const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);
            const state = {
                search: searchInput.value,
                from: fromInput.value,
                to: toInput.value,
                topics: selectedTopics,
                diffs: selectedDiffs
            };
            localStorage.setItem('codingVaultState', JSON.stringify(state));
        }
        function loadState() {
            const savedState = localStorage.getItem('codingVaultState');
            if (!savedState) return;
            const state = JSON.parse(savedState);
            searchInput.value = state.search || '';
            fromInput.value = state.from || '';
            toInput.value = state.to || '';
            if (state.topics) {
                state.topics.forEach(t => {
                    const cb = document.querySelector(`.topic-cb[value="${t}"]`);
                    if (cb) {
                        cb.checked = true;
                        const lbl = document.getElementById(`lbl-topic-${t}`);
                        if (lbl) lbl.classList.add('active');
                    }});}
            if (state.diffs) {
                state.diffs.forEach(d => {
                    const cb = document.querySelector(`.diff-cb[value="${d}"]`);
                    if (cb) {
                        cb.checked = true;
                        const lbl = document.getElementById(`lbl-diff-${d}`);
                        if (lbl) lbl.classList.add('active');
                    }});}
        }
        function renderTable() {
            const itemsToRender = filteredData.slice(0, visibleCount);
            tbody.innerHTML = itemsToRender.map(item => `
                <tr>
                    <td><code>#${item.number}</code></td>
                    <td><span class="badge">${item.topic}</span></td>
                    <td><span class="badge diff-${item.difficulty.toLowerCase()}">${item.difficulty}</span></td>
                    <td><strong>${item.title}</strong></td>
                    <td><a href="./${item.path}/" target="_blank">View 📄</a></td>
                </tr>
            `).join('');
            document.getElementById('displayed-count').innerText = itemsToRender.length;
            document.getElementById('total-count').innerText = filteredData.length;
        }
        function filterData() {
            const searchVal = searchInput.value.toLowerCase().trim();
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
            const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);
            const fromNum = parseInt(fromInput.value) || 0;
            const toNum = parseInt(toInput.value) || Infinity;
            filteredData = data.filter(item => {
                const matchesSearch = item.number.includes(searchVal) || item.title.toLowerCase().includes(searchVal);
                const matchesTopic = selectedTopics.length === 0 || selectedTopics.includes(item.topic);
                const matchesDiff = selectedDiffs.length === 0 || selectedDiffs.includes(item.difficulty);
                const matchesRange = item.num_int >= fromNum && item.num_int <= toNum;
                return matchesSearch && matchesTopic && matchesDiff && matchesRange;
            });
            visibleCount = 50; 
            renderTable();
            saveState();
        }
        document.querySelectorAll('.checkbox-container').forEach(container => {
            container.addEventListener('click', (e) => {
                const label = e.target.closest('.checkbox-label');
                if (!label) return;
                const cb = label.querySelector('input');
                if (e.target !== cb) { cb.checked = !cb.checked; }
                label.classList.toggle('active', cb.checked);
                filterData();
            });
        });
        window.addEventListener('scroll', () => {
            if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
                if (visibleCount < filteredData.length) { visibleCount += 50; renderTable(); }
            }
        });
        document.getElementById('apply-range').addEventListener('click', filterData);
        document.getElementById('reset-range').addEventListener('click', () => {
            fromInput.value = ''; toInput.value = ''; searchInput.value = '';
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
            document.querySelectorAll('.checkbox-label').forEach(lbl => lbl.classList.remove('active'));
            localStorage.removeItem('codingVaultState');
            filterData();
        });
        function debounce(func, delay) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), delay);
            };
        }
        searchInput.addEventListener('input', debounce(filterData, 150));
        loadState();  
        filterData(); 
    </script>
</body>
</html>
"""

    full_html = html_start + html_stats + html_end + html_js_data + html_js_logic
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    print("⚡ Stable dashboard generated without any python syntax bugs!")

if __name__ == "__main__":
    build_index()

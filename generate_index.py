import os
import json
from concurrent.futures import ThreadPoolExecutor

EXCLUDE_DIRS = {'.git', '.github', '.vscode', 'node_modules'}

def process_folder(folder_name):
    if os.path.isdir(folder_name) and folder_name not in EXCLUDE_DIRS and not folder_name.startswith('.'):
        parts = folder_name.split('_', 3)
        if len(parts) >= 4:
            q_num_str = parts[0]
            if q_num_str.isdigit():
                try:
                    return {
                        "number": q_num_str,
                        "num_int": int(q_num_str),
                        "topic": parts[1],        # Array, String, etc.
                        "difficulty": parts[2],   # Easy, Medium, Hard
                        "title": parts[3].replace('_', ' '),
                        "path": folder_name.replace('\\', '/')
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
    
    # 1. Sabse pehle data.js generate karein
    js_content = f"const rawQuestionsData = {json.dumps(questions, indent=2)};"
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"⚡ Success! {len(questions)} questions indexed in data.js")

    # 2. Ab automatic index.html file generate karein
    html_template = """<!DOCTYPE html>
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
        .diff-Easy { border-color: #238636; color: #2ea043; }
        .diff-Medium { border-color: #9e6a03; color: #d29922; }
        .diff-Hard { border-color: #da3637; color: #f85149; }
    </style>
</head>
<body>
    <h1>🚀 My State-Saved Coding Vault</h1>
    <div class="stats">Showing <span id="displayed-count" style="color: #58a6ff; font-weight: bold;">0</span> of <span id="total-count">0</span> Questions</div>
    
    <div class="filter-section">
        <div class="filter-group-title">🎯 Set Question Range</div>
        <div class="range-container">
            <label>From Q.No:</label>
            <input type="number" id="range-from" class="range-input" placeholder="e.g. 200" min="1">
            <label>To Q.No:</label>
            <input type="number" id="range-to" class="range-input" placeholder="e.g. 400" min="1">
            <button id="apply-range" class="range-btn">Apply Range</button>
            <button id="reset-range" class="reset-btn">Clear All Settings</button>
        </div>
        <input type="text" id="search" class="search-box" placeholder="Instant Search by Title, Topic, or Number (e.g., Array)...">
        
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

    <script src="data.js"></script>
    <script>
        const data = typeof rawQuestionsData !== 'undefined' ? rawQuestionsData : [];
        let filteredData = [...data];
        let visibleCount = 50; 

        const tbody = document.getElementById('table-body');
        const searchInput = document.getElementById('search');
        const fromInput = document.getElementById('range-from');
        const toInput = document.getElementById('range-to');

        const topics = [...new Set(data.map(item => item.topic))].sort();
        const difficulties = [...new Set(data.map(item => item.difficulty))].sort();
        
        document.getElementById('topic-group').innerHTML = topics.map(t => 
            `<label class="checkbox-label" id="lbl-topic-${t}"><input type="checkbox" class="topic-cb" value="${t}">${t}</label>`
        ).join('');
        
        document.getElementById('diff-group').innerHTML = difficulties.map(d => 
            `<label class="checkbox-label" id="lbl-diff-${d}"><input type="checkbox" class="diff-cb" value="${d}">${d}</label>`
        ).join('');
        
        function filterData() {
            const query = searchInput.value.toLowerCase().trim();
            const fromNum = parseInt(fromInput.value) || 0;
            const toNum = parseInt(toInput.value) || Infinity;
            
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
            const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);

            document.querySelectorAll('.topic-cb, .diff-cb').forEach(cb => {
                cb.parentElement.classList.toggle('active', cb.checked);
            });

            filteredData = data.filter(q => {
                const matchesSearch = q.title.toLowerCase().includes(query) || 
                                      q.topic.toLowerCase().includes(query) || 
                                      q.number.includes(query);
                const matchesRange = q.num_int >= fromNum && q.num_int <= toNum;
                const matchesTopic = selectedTopics.length === 0 || selectedTopics.includes(q.topic);
                const matchesDiff = selectedDiffs.length === 0 || selectedDiffs.includes(q.difficulty);

                return matchesSearch && matchesRange && matchesTopic && matchesDiff;
            });

            visibleCount = 50; 
            renderTable();
            saveState();
        }

        function renderTable() {
            document.getElementById('total-count').textContent = data.length;
            document.getElementById('displayed-count').textContent = filteredData.length;

            const slice = filteredData.slice(0, visibleCount);
            if (slice.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#8b949e;">No questions match your active filters! 🔍</td></tr>`;
                return;
            }

            tbody.innerHTML = slice.map(q => `
                <tr>
                    <td><code>#${q.number}</code></td>
                    <td><span class="badge">${q.topic}</span></td>
                    <td><span class="badge diff-${q.difficulty}">${q.difficulty}</span></td>
                    <td>${q.title}</td>
                    <td><a href="./${q.path}" target="_blank">View ↗</a></td>
                </tr>
            `).join('');
        }

        function saveState() {
            const selectedTopics = Array.from(document.querySelectorAll('.topic-cb:checked')).map(cb => cb.value);
                    const selectedDiffs = Array.from(document.querySelectorAll('.diff-cb:checked')).map(cb => cb.value);
        localStorage.setItem('codingVaultState', JSON.stringify({
            search: searchInput.value, 
            from: fromInput.value, 
            to: toInput.value, 
            topics: selectedTopics, 
            diffs: selectedDiffs
        }));
    }

    function loadState() {
        const state = JSON.parse(localStorage.getItem('codingVaultState'));
        if (!state) { renderTable(); return; }
        searchInput.value = state.search || ''; 
        fromInput.value = state.from || ''; 
        toInput.value = state.to || '';
        
        if (state.topics) {
            state.topics.forEach(t => { 
                const cb = document.querySelector(`.topic-cb[value="${t}"]`); 
                if (cb) cb.checked = true; 
            });
        }
        if (state.diffs) {
            state.diffs.forEach(d => { 
                const cb = document.querySelector(`.diff-cb[value="${d}"]`); 
                if (cb) cb.checked = true; 
            });
        }
        filterData();
    }

    window.addEventListener('scroll', () => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            if (visibleCount < filteredData.length) { 
                visibleCount += 50; 
                renderTable(); 
            }
        }
    });

    searchInput.addEventListener('input', filterData);
    document.getElementById('apply-range').addEventListener('click', filterData);
    document.querySelectorAll('.topic-cb, .diff-cb').forEach(cb => cb.addEventListener('change', filterData));
    
    document.getElementById('reset-range').addEventListener('click', () => {
        searchInput.value = ''; 
        fromInput.value = ''; 
        toInput.value = '';
        document.querySelectorAll('.topic-cb, .diff-cb').forEach(cb => cb.checked = false);
        localStorage.removeItem('codingVaultState');
        filterData();
    });

    loadState();
</script>
</body>
</html>
"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    print("🌐 Dashboard index.html automatic generate ho gayi hai!")

if __name__ == "__main__":
    build_index()

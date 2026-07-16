// High-Velocity Application State Interface
let state = {
    dataset: typeof rawQuestionsData !== 'undefined' ? rawQuestionsData : [],
    searchQuery: "",
    rangeFrom: null,
    rangeTo: null,
    activeTopics: new Set(),
    activeDiffs: new Set(),
    // Feature 3: Cache restoration fallback logic
    selectedId: localStorage.getItem('dashboard_last_q_num') || null,
    activeTab: localStorage.getItem('dashboard_last_tab') || 'sol'
};

// Cached System DOM References
const elements = {
    search: document.getElementById('search'),
    rangeFrom: document.getElementById('range-from'),
    rangeTo: document.getElementById('range-to'),
    applyRange: document.getElementById('apply-range'),
    resetRange: document.getElementById('reset-range'),
    topicGroup: document.getElementById('topic-group'),
    diffGroup: document.getElementById('diff-group'),
    listStream: document.getElementById('list-stream'),
    displayedCount: document.getElementById('displayed-count'),
    totalCount: document.getElementById('total-count'),
    blankState: document.getElementById('blank-state'),
    paneSol: document.getElementById('pane-sol'),
    paneNotes: document.getElementById('pane-notes'),
    tabSol: document.getElementById('tab-sol'),
    tabNotes: document.getElementById('tab-notes'),
    solFilename: document.getElementById('sol-filename'),
    codeBlock: document.getElementById('code-block'),
    markdownBlock: document.getElementById('markdown-block'),
    selectedMeta: document.getElementById('selected-meta')
};

// Feature 2: Complex Extension-to-Language Compiler Map for Highlight.js
const LANGUAGE_CLASS_MAP = {
    'py': 'language-python',
    'py3': 'language-python',
    'cpp': 'language-cpp',
    'c': 'language-c',
    'cs': 'language-csharp',
    'java': 'language-java',
    'js': 'language-javascript',
    'ts': 'language-typescript',
    'go': 'language-go',
    'rs': 'language-rust',
    'kt': 'language-kotlin',
    'rb': 'language-ruby',
    'sh': 'language-bash'
};

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

window.addEventListener('DOMContentLoaded', () => {
    if (elements.totalCount) elements.totalCount.textContent = state.dataset.length;
    buildFilterFacets();
    applyStateFilters();
    injectCopyButtonEngine(); // Feature 1 Setup
    
    // Auto-Restoration validation anchor
    if (state.selectedId) {
        const cachedItem = state.dataset.find(item => item.number === state.selectedId);
        if (cachedItem) selectArchItem(cachedItem);
    } else {
        switchPaneTab(state.activeTab);
    }
    
    if (elements.search) {
        elements.search.addEventListener('input', debounce((e) => {
            state.searchQuery = e.target.value.toLowerCase().trim();
            applyStateFilters();
        }, 150));
    }

    if (elements.applyRange) {
        elements.applyRange.addEventListener('click', () => {
            state.rangeFrom = elements.rangeFrom.value ? parseInt(elements.rangeFrom.value, 10) : null;
            state.rangeTo = elements.rangeTo.value ? parseInt(elements.rangeTo.value, 10) : null;
            applyStateFilters();
        });
    }

    if (elements.resetRange) {
        elements.resetRange.addEventListener('click', () => {
            if (elements.rangeFrom) elements.rangeFrom.value = '';
            if (elements.rangeTo) elements.rangeTo.value = '';
            if (elements.search) elements.search.value = '';
            state.rangeFrom = null;
            state.rangeTo = null;
            state.searchQuery = "";
            state.activeTopics.clear();
            state.activeDiffs.clear();
            localStorage.removeItem('dashboard_last_q_num');
            
            document.querySelectorAll('.filter-pill').forEach(pill => {
                pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700";
            });
            applyStateFilters();
        });
    }
});

function buildFilterFacets() {
    const topics = new Set();
    const diffs = new Set();
    state.dataset.forEach(item => {
        if(item.topic) topics.add(item.topic);
        if(item.difficulty) diffs.add(item.difficulty);
    });

    if (elements.topicGroup) {
        elements.topicGroup.innerHTML = '';
        Array.from(topics).sort().forEach(topic => {
            const pill = document.createElement('button');
            pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700";
            pill.textContent = topic;
            pill.onclick = () => toggleFacetFilter('topic', topic, pill);
            elements.topicGroup.appendChild(pill);
        });
    }

    if (elements.diffGroup) {
        elements.diffGroup.innerHTML = '';
        Array.from(diffs).sort().forEach(diff => {
            const pill = document.createElement('button');
            pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700";
            pill.textContent = diff;
            pill.onclick = () => toggleFacetFilter('diff', diff, pill);
            elements.diffGroup.appendChild(pill);
        });
    }
}

function toggleFacetFilter(type, value, element) {
    const activeSet = (type === 'topic') ? state.activeTopics : state.activeDiffs;
    if(activeSet.has(value)) {
        activeSet.delete(value);
        element.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700";
    } else {
        activeSet.add(value);
        if (type === 'topic') {
            element.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-sky-500 bg-sky-500 text-white transition";
        } else {
            const colorMap = { 'Easy': 'bg-emerald-500 border-emerald-500', 'Medium': 'bg-amber-500 border-amber-500', 'Hard': 'bg-red-500 border-red-500' };
            element.className = `filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border text-white transition ${colorMap[value] || 'bg-slate-700'}`;
        }
    }
    applyStateFilters();
}

function applyStateFilters() {
    const filtered = state.dataset.filter(item => {
        if (state.searchQuery && !item.title.toLowerCase().includes(state.searchQuery) && !item.number.includes(state.searchQuery)) return false;
        if (state.rangeFrom !== null && item.num_int < state.rangeFrom) return false;
        if (state.rangeTo !== null && item.num_int > state.rangeTo) return false;
        if (state.activeTopics.size > 0 && !state.activeTopics.has(item.topic)) return false;
        if (state.activeDiffs.size > 0 && !state.activeDiffs.has(item.difficulty)) return false;
        return true;
    });

    if (elements.displayedCount) elements.displayedCount.textContent = filtered.length;
    renderListStream(filtered);
}

function renderListStream(items) {
    if (!elements.listStream) return;
    elements.listStream.innerHTML = '';

    if (items.length === 0) {
        if (elements.blankState) elements.blankState.classList.remove('hidden');
        return;
    }
    if (elements.blankState) elements.blankState.classList.add('hidden');

    const fragment = document.createDocumentFragment();
    const diffColors = { 
        'Easy': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', 
        'Medium': 'text-amber-400 bg-amber-500/10 border-amber-500/20', 
        'Hard': 'text-red-400 bg-red-500/10 border-red-500/20' 
    };

    items.forEach(item => {
        const card = document.createElement('div');
        card.id = `q-row-${item.number}`;
        const isActive = state.selectedId === item.number ? 'active-row bg-slate-800/80 border-l-4 border-sky-500' : 'border-l-4 border-transparent';
        card.className = `p-4 cursor-pointer hover:bg-slate-900/40 flex items-center justify-between gap-4 transition-all ${isActive}`;
        
        card.innerHTML = `
            <div class="flex items-start gap-3 min-w-0"> 
                <span class="code-font text-xs font-bold text-slate-500 mt-0.5">#${item.number}</span> 
                <div class="min-w-0"> 
                    <h4 class="text-sm font-semibold text-slate-200 truncate">${item.title}</h4> 
                    <div class="flex items-center gap-2 mt-1.5 flex-wrap"> 
                        <span class="px-2 py-0.5 text-[10px] font-bold rounded border uppercase ${diffColors[item.difficulty] || ''}">${item.difficulty}</span> 
                        <span class="px-2 py-0.5 text-[10px] font-semibold rounded bg-slate-800 text-slate-400 border border-slate-700/60 uppercase">${item.topic}</span> 
                    </div> 
                </div> 
            </div>
        `;

        card.onclick = () => selectArchItem(item);
        fragment.appendChild(card);
    });

    elements.listStream.appendChild(fragment);
}

async function selectArchItem(item) {
    state.selectedId = item.number;
    // Feature 3: Cache state injection to handle browser reload
    localStorage.setItem('dashboard_last_q_num', item.number);
    
    document.querySelectorAll('[id^="q-row-"]').forEach(r => {
        r.classList.remove('active-row', 'bg-slate-800/80', 'border-sky-500');
        r.classList.add('border-transparent');
    });
    const activeRow = document.getElementById(`q-row-${item.number}`);
    if (activeRow) {
        activeRow.classList.add('active-row', 'bg-slate-800/80', 'border-sky-500');
        activeRow.classList.remove('border-transparent');
    }
    
if (elements.blankState) elements.blankState.classList.add('hidden');
if (elements.selectedMeta) elements.selectedMeta.textContent = `Path: ${item.path}`;

let codeData = "// Code source file missing / not mapped.";
let notesData = "No markdown documentation available for this architecture.";

const ext = item.sol_file ? item.sol_file.split('.').pop().toLowerCase() : '';

if (elements.solFilename) {
    elements.solFilename.textContent = item.sol_file ? item.sol_file.split('/').pop() : 'No File';
}

const fetchPromises = [];

if (item.sol_file) {
    fetchPromises.push(
        fetch(item.sol_file)
            .then(res => res.ok ? res.text() : `// Error: Failed to target source file (${res.status})`)
            .then(text => { codeData = text; })
            .catch(e => { codeData = `// Transport Interface Fault: ${e.message}`; })
    );
}

if (item.notes_file) {
    fetchPromises.push(
        fetch(item.notes_file)
            .then(res => res.ok ? res.text() : `**Error:** Failed to parse Markdown container (${res.status})`)
            .then(text => { notesData = text; })
            .catch(e => { notesData = `_Transport Documentation Fault:_ ${e.message}`; })
    );
}

if (fetchPromises.length > 0) {
    if (elements.codeBlock) elements.codeBlock.textContent = "// Syncing remote components...";
    await Promise.all(fetchPromises);
}

if (elements.codeBlock) {
    elements.codeBlock.textContent = codeData;
    // Feature 2: Clean mapping implementation without dynamic class accumulation
    elements.codeBlock.className = "code-font " + (LANGUAGE_CLASS_MAP[ext] || 'language-plaintext');
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(elements.codeBlock);
    }
}

if (elements.markdownBlock) {
    if (typeof marked !== 'undefined') {
        elements.markdownBlock.innerHTML = marked.parse(notesData);
    } else {
        elements.markdownBlock.textContent = notesData;
    }
}

switchPaneTab(state.activeTab);

function switchPaneTab(targetTab) {
    state.activeTab = targetTab;
    localStorage.setItem('dashboard_last_tab', targetTab); // Cache state persistent sync
    
    if (!elements.tabSol || !elements.tabNotes || !elements.paneSol || !elements.paneNotes) return;
    
    elements.tabSol.classList.remove('active');
    elements.tabNotes.classList.remove('active');
    elements.paneSol.classList.add('hidden');
    elements.paneNotes.classList.add('hidden');
    
    if (targetTab === 'sol') {
        elements.tabSol.classList.add('active');
        elements.paneSol.classList.remove('hidden');
    } else {
        elements.tabNotes.classList.add('active');
        elements.paneNotes.classList.remove('hidden');
    }
}

// Feature 1: Modern Copy-to-Clipboard Action Bridge Injector
function injectCopyButtonEngine() {
    const paneSol = document.getElementById('pane-sol');
    if (!paneSol) return;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = "absolute top-20 right-10 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 hover:border-slate-500 text-slate-300 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2 transition-all z-10 shadow-md font-medium active:scale-95";
    copyBtn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy`;
    
    copyBtn.onclick = async () => {
        if (!elements.codeBlock) return;
        const targetText = elements.codeBlock.textContent;
        
        try {
            await navigator.clipboard.writeText(targetText);
            copyBtn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copied!`;
            copyBtn.classList.add('border-emerald-500/40', 'bg-emerald-950/20');
        } catch (err) {
            // Fallback for isolated local testing security contexts
            const textarea = document.createElement('textarea');
            textarea.value = targetText;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            copyBtn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Copied!`;
        }
        
        setTimeout(() => {
            copyBtn.innerHTML = `<i class="fa-regular fa-copy"></i> Copy`;
            copyBtn.className = "absolute top-20 right-10 bg-slate-800/80 hover:bg-slate-700 border border-slate-700/60 hover:border-slate-500 text-slate-300 text-xs px-3 py-1.5 rounded-lg flex items-center gap-2 transition-all z-10 shadow-md font-medium active:scale-95";
        }, 2000);
    };
    
    // Solution panel contextual absolute parent constraint
    paneSol.style.position = 'relative';
    paneSol.appendChild(copyBtn);
}

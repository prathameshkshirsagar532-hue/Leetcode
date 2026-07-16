let state = {
    dataset: typeof rawQuestionsData !== 'undefined' ? rawQuestionsData : [],
    searchQuery: "",
    rangeFrom: null,
    rangeTo: null,
    activeTopics: new Set(),
    activeDiffs: new Set(),
    selectedId: localStorage.getItem('dashboard_last_q_num') || null,
    activeTab: localStorage.getItem('dashboard_last_tab') || 'sol'
};

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

const LANGUAGE_CLASS_MAP = {
    'py': 'language-python', 'py3': 'language-python', 'cpp': 'language-cpp',
    'c': 'language-c', 'cs': 'language-csharp', 'java': 'language-java',
    'js': 'language-javascript', 'ts': 'language-typescript', 'go': 'language-go',
    'rs': 'language-rust', 'kt': 'language-kotlin', 'rb': 'language-ruby', 'sh': 'language-bash'
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
    injectCopyButtonEngine();
    
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
            state.rangeFrom = null; state.rangeTo = null; state.searchQuery = "";
            state.activeTopics.clear(); state.activeDiffs.clear();
            localStorage.removeItem('dashboard_last_q_num');
            
            document.querySelectorAll('.filter-pill').forEach(pill => {
                pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700 cursor-pointer";
            });
            applyStateFilters();
        });
    }

    if (elements.tabSol) elements.tabSol.addEventListener('click', () => switchPaneTab('sol'));
    if (elements.tabNotes) elements.tabNotes.addEventListener('click', () => switchPaneTab('notes'));
});

function buildFilterFacets() {
    const topics = new Set(); const diffs = new Set();
    state.dataset.forEach(item => {
        if(item.topic) topics.add(item.topic);
        if(item.difficulty) diffs.add(item.difficulty);
    });

    if (elements.topicGroup) {
        elements.topicGroup.innerHTML = '';
        Array.from(topics).sort().forEach(topic => {
            const pill = document.createElement('button');
            pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700 cursor-pointer";
            pill.textContent = topic;
            pill.onclick = () => toggleFacetFilter('topic', topic, pill);
            elements.topicGroup.appendChild(pill);
        });
    }

    if (elements.diffGroup) {
        elements.diffGroup.innerHTML = '';
        Array.from(diffs).sort().forEach(diff => {
            const pill = document.createElement('button');
            pill.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700 cursor-pointer";
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
        element.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-slate-800 bg-slate-900/60 text-slate-400 transition hover:border-slate-700 cursor-pointer";
    } else {
        activeSet.add(value);
        if (type === 'topic') {
            element.className = "filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border border-sky-500 bg-sky-500 text-white transition cursor-pointer shadow-md shadow-sky-500/20";
        } else {
            const colorMap = { 'Easy': 'bg-emerald-500 border-emerald-500 shadow-emerald-500/10', 'Medium': 'bg-amber-500 border-amber-500 shadow-amber-500/10', 'Hard': 'bg-red-500 border-red-500 shadow-red-500/10' };
            element.className = `filter-pill text-[10px] px-2.5 py-1 font-semibold rounded-md border text-white transition cursor-pointer shadow-md ${colorMap[value] || 'bg-slate-700'}`;
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
    const diffColors = { 'Easy': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20', 'Medium': 'text-amber-400 bg-amber-500/10 border-amber-500/20', 'Hard': 'text-red-400 bg-red-500/10 border-red-500/20' };

    items.forEach(item => {
        const card = document.createElement('div');
        card.id = `q-row-${item.number}`;
        const isSelected = state.selectedId === item.number;
        const activeClass = isSelected ? 'bg-slate-900 border-l-4 border-sky-500 shadow-inner' : 'border-l-4 border-transparent bg-slate-900/20';
        card.className = `p-3.5 cursor-pointer hover:bg-slate-900/60 rounded-r-lg border-b border-slate-900/60 transition-all ${activeClass}`;
        const diffBadge = diffColors[item.difficulty] || 'text-slate-400 bg-slate-500/10 border-slate-500/20';

        card.innerHTML = `
            <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-[10px] font-mono font-bold text-slate-500">#${item.number}</span>
                        <span class="px-1.5 py-0.5 text-[9px] font-bold rounded border ${diffBadge}">${item.difficulty}</span>
                    </div>
                    <h3 class="text-xs font-bold text-slate-200 truncate tracking-wide">${item.title}</h3>
                    <p class="text-[10px] text-slate-500 font-medium mt-0.5 truncate tracking-wide">${item.topic || 'General'}</p>
                </div>
            </div>
        `;
        card.onclick = () => selectArchItem(item);
        fragment.appendChild(card);
    });
    elements.listStream.appendChild(fragment);
}

function selectArchItem(item) {
    if (!item) return;
    document.querySelectorAll('[id^="q-row-"]').forEach(row => {
        row.classList.remove('bg-slate-900', 'border-sky-500', 'shadow-inner');
        row.classList.add('border-transparent', 'bg-slate-900/20');
    });

    const activeRow = document.getElementById(`q-row-${item.number}`);
    if (activeRow) {
        activeRow.classList.remove('border-transparent', 'bg-slate-900/20');
        activeRow.classList.add('bg-slate-900', 'border-sky-500', 'shadow-inner');
    }

    state.selectedId = item.number;
    localStorage.setItem('dashboard_last_q_num', item.number);
// Metadata, Highlighting, aur Code Block Core System Pipeline
if (elements.selectedMeta) {
    elements.selectedMeta.innerHTML = `
        <div class="flex items-center gap-3 animate-fade-in">
            <div class="h-10 w-10 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-center font-mono font-black text-xs text-sky-400 shadow-inner">#${item.number}</div>
            <div>
                <h2 class="text-sm font-extrabold text-white tracking-wide leading-tight">${item.title}</h2>
                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">${item.topic || 'General Matrix'}</p>
            </div>
        </div>
    `;
}

if (elements.codeBlock && item.code) {
    elements.solFilename.textContent = item.filename || `solution.${item.extension || 'py'}`;
    elements.codeBlock.className = '';
    const targetLangClass = LANGUAGE_CLASS_MAP[item.extension] || 'language-plaintext';
    elements.codeBlock.classList.add(targetLangClass);
    elements.codeBlock.textContent = item.code;
    
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(elements.codeBlock);
    }
} else if (elements.codeBlock) {
    elements.codeBlock.textContent = '// No code solution compiled for this challenge node.';
}

if (elements.markdownBlock) {
    if (item.notes) {
        elements.markdownBlock.innerHTML = typeof marked !== 'undefined' ? marked.parse(item.notes) : item.notes;
    } else {
        elements.markdownBlock.innerHTML = '<div class="text-slate-600 italic font-medium py-2">No structural analysis notes cataloged for this workspace node.</div>';
    }
}

switchPaneTab(state.activeTab);


// Active Solution aur Analysis Notes Viewport Switch Tab System
function switchPaneTab(tabKey) {
    state.activeTab = tabKey;
    localStorage.setItem('dashboard_last_tab', tabKey);
    
    const activeTabStyle = "border-sky-500 text-sky-400 bg-slate-900/30";
    const inactiveTabStyle = "border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900/10";

    if (tabKey === 'sol') {
        if (elements.paneSol) elements.paneSol.classList.remove('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.add('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${activeTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${inactiveTabStyle}`;
    } else {
        if (elements.paneSol) elements.paneSol.classList.add('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.remove('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${inactiveTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${activeTabStyle}`;
    }
}


// Clipboard Async Engine Factory Button Controller
function injectCopyButtonEngine() {
    const copyBtn = document.getElementById('copy-solution-btn');
    if (!copyBtn || !elements.codeBlock) return;
    
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(elements.codeBlock.textContent);
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = `<span class="text-[10px] text-emerald-400 font-extrabold tracking-widest uppercase">Copied!</span>`;
            copyBtn.disabled = true;
            
            setTimeout(() => { 
                copyBtn.innerHTML = originalHTML; 
                copyBtn.disabled = false; 
            }, 2000);
        } catch (err) { 
            console.error(err); 
        }
    });
}

// Metadata, Highlighting, aur Code Block Core System Pipeline
if (elements.selectedMeta) {
    elements.selectedMeta.innerHTML = `
        <div class="flex items-center gap-3 animate-fade-in">
            <div class="h-10 w-10 bg-slate-900 border border-slate-800 rounded-lg flex items-center justify-center font-mono font-black text-xs text-sky-400 shadow-inner">#${item.number}</div>
            <div>
                <h2 class="text-sm font-extrabold text-white tracking-wide leading-tight">${item.title}</h2>
                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-0.5">${item.topic || 'General Matrix'}</p>
            </div>
        </div>
    `;
}

if (elements.codeBlock && item.code) {
    elements.solFilename.textContent = item.filename || `solution.${item.extension || 'py'}`;
    elements.codeBlock.className = '';
    const targetLangClass = LANGUAGE_CLASS_MAP[item.extension] || 'language-plaintext';
    elements.codeBlock.classList.add(targetLangClass);
    elements.codeBlock.textContent = item.code;
    
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(elements.codeBlock);
    }
} else if (elements.codeBlock) {
    elements.codeBlock.textContent = '// No code solution compiled for this challenge node.';
}

if (elements.markdownBlock) {
    if (item.notes) {
        elements.markdownBlock.innerHTML = typeof marked !== 'undefined' ? marked.parse(item.notes) : item.notes;
    } else {
        elements.markdownBlock.innerHTML = '<div class="text-slate-600 italic font-medium py-2">No structural analysis notes cataloged for this workspace node.</div>';
    }
}

switchPaneTab(state.activeTab);


// Active Solution aur Analysis Notes Viewport Switch Tab System
function switchPaneTab(tabKey) {
    state.activeTab = tabKey;
    localStorage.setItem('dashboard_last_tab', tabKey);
    
    const activeTabStyle = "border-sky-500 text-sky-400 bg-slate-900/30";
    const inactiveTabStyle = "border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-900/10";

    if (tabKey === 'sol') {
        if (elements.paneSol) elements.paneSol.classList.remove('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.add('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${activeTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${inactiveTabStyle}`;
    } else {
        if (elements.paneSol) elements.paneSol.classList.add('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.remove('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${inactiveTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-3 border-b-2 font-bold text-[10px] tracking-wider uppercase transition-all cursor-pointer ${activeTabStyle}`;
    }
}


// Clipboard Async Engine Factory Button Controller
function injectCopyButtonEngine() {
    const copyBtn = document.getElementById('copy-solution-btn');
    if (!copyBtn || !elements.codeBlock) return;
    
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(elements.codeBlock.textContent);
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = `<span class="text-[10px] text-emerald-400 font-extrabold tracking-widest uppercase">Copied!</span>`;
            copyBtn.disabled = true;
            
            setTimeout(() => { 
                copyBtn.innerHTML = originalHTML; 
                copyBtn.disabled = false; 
            }, 2000);
        } catch (err) { 
            console.error(err); 
        }
    });
}

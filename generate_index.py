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
        if (cachedItem) {
            selectArchItem(cachedItem);
        } else {
            switchPaneTab(state.activeTab);
        }
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

    // Set up tab event listeners
    if (elements.tabSol) {
        elements.tabSol.addEventListener('click', () => switchPaneTab('sol'));
    }
    if (elements.tabNotes) {
        elements.tabNotes.addEventListener('click', () => switchPaneTab('notes'));
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
        
        const isSelected = state.selectedId === item.number;
        const activeClass = isSelected ? 'bg-slate-800/80 border-l-4 border-sky-500' : 'border-l-4 border-transparent';
        
        card.className = `p-4 cursor-pointer hover:bg-slate-900/40 transition-all border-b border-slate-800/60 ${activeClass}`;
        
        const diffBadge = diffColors[item.difficulty] || 'text-slate-400 bg-slate-500/10 border-slate-500/20';

        card.innerHTML = `
            <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs font-mono font-bold text-slate-500">#${item.number}</span>
                        <span class="px-2 py-0.5 text-[10px] font-medium rounded border ${diffBadge}">${item.difficulty}</span>
                    </div>
                    <h3 class="text-sm font-semibold text-slate-200 truncate">${item.title}</h3>
                    <p class="text-xs text-slate-400 mt-1 truncate">${item.topic || 'General'}</p>
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

    // Manage UI active rows
    document.querySelectorAll('[id^="q-row-"]').forEach(row => {
        row.classList.remove('bg-slate-800/80', 'border-sky-500');
        row.classList.add('border-transparent');
    });

const activeRow = document.getElementById(`q-row-${item.number}`);
if (activeRow) {
    activeRow.classList.remove('border-transparent');
    activeRow.classList.add('bg-slate-800/80', 'border-sky-500');
}

// Persist identity state
state.selectedId = item.number;
localStorage.setItem('dashboard_last_q_num', item.number);

// Update Header Metadata Panel
if (elements.selectedMeta) {
    elements.selectedMeta.innerHTML = `
        <div class="flex items-center gap-3"> 
            <span class="text-lg font-mono font-black text-slate-400">#${item.number}</span> 
            <div> 
                <h2 class="text-base font-bold text-white leading-tight">${item.title}</h2> 
                <p class="text-xs text-slate-500 font-medium mt-0.5">${item.topic || ''}</p> 
            </div> 
        </div>`;
}

// Process Feature 2: Highlighting Code Logic
if (elements.codeBlock && item.code) {
    elements.solFilename.textContent = item.filename || `solution.${item.extension || 'py'}`;
    
    // Remove old language classes
    elements.codeBlock.className = '';
    const targetLangClass = LANGUAGE_CLASS_MAP[item.extension] || 'language-plaintext';
    elements.codeBlock.classList.add(targetLangClass, 'text-xs', 'font-mono');
    elements.codeBlock.textContent = item.code;
    
    if (typeof hljs !== 'undefined') {
        hljs.highlightElement(elements.codeBlock);
    }
} else if (elements.codeBlock) {
    elements.codeBlock.textContent = '// No code solution provided.';
}

// Handle Notes Markdown Engine Rendering
if (elements.markdownBlock) {
    if (item.notes) {
        if (typeof marked !== 'undefined') {
            elements.markdownBlock.innerHTML = marked.parse(item.notes);
        } else {
            elements.markdownBlock.textContent = item.notes;
        }
    } else {
        elements.markdownBlock.innerHTML = 'No notes compiled for this challenge.';
    }
}

switchPaneTab(state.activeTab);

function switchPaneTab(tabKey) {
    state.activeTab = tabKey;
    localStorage.setItem('dashboard_last_tab', tabKey);
    
    const activeTabStyle = "border-sky-500 text-sky-400 bg-slate-800/40";
    const inactiveTabStyle = "border-transparent text-slate-400 hover:text-slate-300 hover:bg-slate-900/40";
    
    if (tabKey === 'sol') {
        if (elements.paneSol) elements.paneSol.classList.remove('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.add('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-2 border-b-2 font-medium text-sm transition-all ${activeTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-2 border-b-2 font-medium text-sm transition-all ${inactiveTabStyle}`;
    } else {
        if (elements.paneSol) elements.paneSol.classList.add('hidden');
        if (elements.paneNotes) elements.paneNotes.classList.remove('hidden');
        if (elements.tabSol) elements.tabSol.className = `px-4 py-2 border-b-2 font-medium text-sm transition-all ${inactiveTabStyle}`;
        if (elements.tabNotes) elements.tabNotes.className = `px-4 py-2 border-b-2 font-medium text-sm transition-all ${activeTabStyle}`;
    }
}

// Feature 1: Global Clipboard Engine Factory
function injectCopyButtonEngine() {
    const copyBtn = document.getElementById('copy-solution-btn');
    if (!copyBtn || !elements.codeBlock) return;
    
    copyBtn.addEventListener('click', async () => {
        const textToCopy = elements.codeBlock.textContent;
        try {
            await navigator.clipboard.writeText(textToCopy);
            const originalHTML = copyBtn.innerHTML;
            copyBtn.innerHTML = `
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"> 
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path> 
                </svg> 
                <span class="text-xs text-emerald-400 font-medium">Copied!</span>`;
            copyBtn.disabled = true;
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHTML;
                copyBtn.disabled = false;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    });
}

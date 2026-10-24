/**
 * DDCET Preparation Application - Frontend Engine (Vanilla JS)
 * Offline-first, responsive, keyboard-navigable.
 */

const App = {
    state: {
        activeTab: 'tab-today',
        hierarchy: [],
        settings: {},
        activeSession: null,
        currentQuestionIndex: 0,
        timerInterval: null,
        secondsRemaining: 0,
        secondsElapsed: 0,
        isPaused: false,
        stagedImportFile: null,
        bankPage: 1,
        bankLimit: 20
    },

    init: function () {
        this.bindEvents();
        this.loadHierarchy();
        this.loadSettings();
        this.loadTodayDashboard();
        this.loadDueRevisions();
        this.loadQuestionBank(1);
    },

    renderContent: function (text) {
        if (!text) return '';
        let str = String(text);

        // Regex to tokenize math vs text:
        // 1. Display math: $$...$$ or \[...\]
        // 2. Inline math: $...$ or \(...\)
        const mathRegex = /(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|(?<!\\)\$((?:\\\$|[^\$])+?)\$|\\\([\s\S]*?\\\))/g;

        let lastIndex = 0;
        let htmlResult = '';
        let match;

        while ((match = mathRegex.exec(str)) !== null) {
            const matchIndex = match.index;
            const fullMatch = match[0];

            // Render preceding non-math text using Markdown
            if (matchIndex > lastIndex) {
                const textChunk = str.substring(lastIndex, matchIndex);
                htmlResult += this.renderMarkdownOnly(textChunk);
            }

            // Extract pure math formula
            let isDisplay = false;
            let mathCode = '';

            if (fullMatch.startsWith('$$') && fullMatch.endsWith('$$')) {
                isDisplay = true;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('\\[') && fullMatch.endsWith('\\]')) {
                isDisplay = true;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('\\(') && fullMatch.endsWith('\\)')) {
                isDisplay = false;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('$') && fullMatch.endsWith('$')) {
                isDisplay = false;
                mathCode = fullMatch.slice(1, -1).trim();
            }

            // Restore escaped dollar signs within math
            mathCode = mathCode.replace(/\\\$/g, '$');

            // Render directly with KaTeX without going through markdown parser
            if (typeof katex !== 'undefined') {
                try {
                    htmlResult += katex.renderToString(mathCode, {
                        displayMode: isDisplay,
                        throwOnError: false,
                        output: 'htmlAndMathml'
                    });
                } catch (e) {
                    htmlResult += isDisplay
                        ? `<div class="katex-display">${this.escapeHtml(mathCode)}</div>`
                        : `<span class="math-inline">${this.escapeHtml(mathCode)}</span>`;
                }
            } else {
                htmlResult += isDisplay
                    ? `<div class="katex-display">${this.escapeHtml(mathCode)}</div>`
                    : `<span class="math-inline">${this.escapeHtml(mathCode)}</span>`;
            }

            lastIndex = matchIndex + fullMatch.length;
        }

        // Render remaining text after last math token
        if (lastIndex < str.length) {
            const remainingText = str.substring(lastIndex);
            htmlResult += this.renderMarkdownOnly(remainingText);
        }

        return htmlResult;
    },

    renderMarkdownOnly: function (text) {
        if (!text) return '';
        if (typeof marked !== 'undefined' && marked.parseInline) {
            // If text contains block elements (headings, double newlines, lists)
            if (text.includes('\n\n') || /^\s*(?:#{1,6}|[-*]\s|\d+\.\s)/m.test(text)) {
                return marked.parse(text, { breaks: true, gfm: true });
            }
            return marked.parseInline(text, { breaks: true, gfm: true });
        }
        return this.escapeHtml(text)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    },

    escapeHtml: function (str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    bindEvents: function () {
        // Navigation Tab Switching
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetTab = btn.getAttribute('data-tab');
                this.switchTab(targetTab);
            });
        });

        // 1-Click Start Today's Session
        const btnDaily = document.getElementById('btn-start-daily');
        if (btnDaily) {
            btnDaily.addEventListener('click', () => {
                this.startSession('daily_mixed', null, 20);
            });
        }

        // Global Keyboard Navigation for Question Engine
        window.addEventListener('keydown', (e) => {
            if (!this.state.activeSession || document.getElementById('session-overlay').classList.contains('hidden')) {
                return;
            }
            // Do not trigger if typing in an input
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
                return;
            }

            const key = e.key.toUpperCase();
            if (['A', 'B', 'C', 'D'].includes(key)) {
                this.selectOption(key);
            } else if (['1', '2', '3', '4'].includes(key)) {
                const map = { '1': 'A', '2': 'B', '3': 'C', '4': 'D' };
                this.selectOption(map[key]);
            } else if (key === 'ENTER' || key === 'N') {
                this.nextQuestion();
            } else if (key === 'P' || e.key === 'ArrowLeft') {
                this.prevQuestion();
            } else if (key === 'M') {
                this.toggleReviewMark();
            }
        });

        // Setup Drag & Drop for Import
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('import-file-input');
        if (dropZone && fileInput) {
            dropZone.addEventListener('click', () => fileInput.click());
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#1e40af';
            });
            dropZone.addEventListener('dragleave', () => {
                dropZone.style.borderColor = '#e2e8f0';
            });
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.style.borderColor = '#e2e8f0';
                if (e.dataTransfer.files.length) {
                    this.handleImportFile(e.dataTransfer.files[0]);
                }
            });
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length) {
                    this.handleImportFile(e.target.files[0]);
                }
            });
        }
    },

    switchTab: function (tabId) {
        this.state.activeTab = tabId;
        document.querySelectorAll('.nav-btn').forEach(b => {
            b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
        });
        document.querySelectorAll('.tab-pane').forEach(p => {
            p.classList.toggle('active', p.id === tabId);
        });

        if (tabId === 'tab-today') this.loadTodayDashboard();
        if (tabId === 'tab-revision') this.loadDueRevisions();
        if (tabId === 'tab-analytics') this.loadAnalytics();
        if (tabId === 'tab-bank') this.loadQuestionBank(this.state.bankPage);
        if (tabId === 'tab-settings') this.loadSettings();
    },

    // -------------------------------------------------------------
    // Data Loaders
    // -------------------------------------------------------------
    loadHierarchy: function () {
        fetch('/api/questions/hierarchy')
            .then(res => res.json())
            .then(data => {
                this.state.hierarchy = data.hierarchy || [];
                this.populateSubjectDropdowns();
            })
            .catch(err => console.error("Error loading hierarchy:", err));
    },

    populateSubjectDropdowns: function () {
        const selects = ['practice-subject-select', 'bank-filter-subject'];
        selects.forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            const currentVal = el.value;
            el.innerHTML = '<option value="">All Subjects</option>';
            this.state.hierarchy.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                el.appendChild(opt);
            });
            if (currentVal) el.value = currentVal;
        });
    },

    onSubjectChange: function () {
        const subSelect = document.getElementById('practice-subject-select');
        const topSelect = document.getElementById('practice-topic-select');
        if (!subSelect || !topSelect) return;

        const subId = parseInt(subSelect.value);
        topSelect.innerHTML = '<option value="">All Topics</option>';
        if (!subId) return;

        const subject = this.state.hierarchy.find(s => s.id === subId);
        if (subject && subject.topics) {
            subject.topics.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = t.name;
                topSelect.appendChild(opt);
            });
        }
    },

    loadSettings: function () {
        fetch('/api/settings')
            .then(res => res.json())
            .then(data => {
                this.state.settings = data.settings || {};
                this.applySettingsToUI();
                this.loadBackupsList();
            })
            .catch(err => console.error("Error loading settings:", err));
    },

    applySettingsToUI: function () {
        const s = this.state.settings;
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el && val !== undefined) el.value = val;
        };
        setVal('cfg-daily-target', s.daily_target_minutes);
        setVal('cfg-session-size', s.session_default_size);
        setVal('cfg-mark-correct', s.marking_correct);
        setVal('cfg-mark-incorrect', s.marking_incorrect);
        setVal('cfg-mock-mins', s.mock_exam_duration_mins);
        setVal('cfg-mock-questions', s.mock_exam_total_questions);
        setVal('cfg-w-weakness', s.priority_weight_weakness);
        setVal('cfg-w-revision', s.priority_weight_revision);
        setVal('cfg-w-syllabus', s.priority_weight_syllabus);
        setVal('cfg-w-neglect', s.priority_weight_neglect);
        setVal('cfg-w-speed', s.priority_weight_speed);

        // Mock banner
        const mockDur = document.getElementById('mock-cfg-duration');
        if (mockDur) mockDur.textContent = `${s.mock_exam_duration_mins || 90} Minutes`;
        const mockQ = document.getElementById('mock-cfg-questions');
        if (mockQ) mockQ.textContent = `${s.mock_exam_total_questions || 100} MCQs`;
        const mockM = document.getElementById('mock-cfg-marking');
        if (mockM) mockM.textContent = `${s.marking_incorrect || -0.25} Marks`;
    },

    saveSettings: function (e) {
        e.preventDefault();
        const payload = {
            settings: {
                daily_target_minutes: document.getElementById('cfg-daily-target').value,
                session_default_size: document.getElementById('cfg-session-size').value,
                marking_correct: document.getElementById('cfg-mark-correct').value,
                marking_incorrect: document.getElementById('cfg-mark-incorrect').value,
                mock_exam_duration_mins: document.getElementById('cfg-mock-mins').value,
                mock_exam_total_questions: document.getElementById('cfg-mock-questions').value,
                priority_weight_weakness: document.getElementById('cfg-w-weakness').value,
                priority_weight_revision: document.getElementById('cfg-w-revision').value,
                priority_weight_syllabus: document.getElementById('cfg-w-syllabus').value,
                priority_weight_neglect: document.getElementById('cfg-w-neglect').value,
                priority_weight_speed: document.getElementById('cfg-w-speed').value,
            }
        };

        fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                alert('Settings saved successfully!');
                this.state.settings = data.settings;
                this.applySettingsToUI();
            })
            .catch(err => alert('Failed to save settings: ' + err));
    },

    // -------------------------------------------------------------
    // Today Dashboard & Analytics
    // -------------------------------------------------------------
    loadTodayDashboard: function () {
        fetch('/api/analytics/dashboard')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-answered-today').textContent = data.answered_today;
                document.getElementById('stat-time-today').textContent = `${data.time_spent_today_minutes} mins spent`;
                document.getElementById('stat-accuracy-today').textContent = `${data.accuracy_today}%`;
                document.getElementById('stat-correct-today').textContent = `${data.correct_today} correct`;
                document.getElementById('stat-due-today').textContent = data.due_revisions_count;
                document.getElementById('nav-rev-badge').textContent = data.due_revisions_count;

                const rec = data.recommended_action;
                if (rec) {
                    document.getElementById('stat-focus-topic').textContent = rec.recommended_topic;
                    document.getElementById('stat-focus-reason').textContent = rec.why_recommended;
                    document.getElementById('today-due-summary').textContent = `${data.due_revisions_count} questions waiting for spaced repetition review.`;
                    document.getElementById('today-recommended-summary').textContent = `Focused questions on ${rec.recommended_topic} (${rec.recommended_subject}).`;
                }

                // Daily Diagnosis
                const diag = data.daily_summary;
                if (diag) {
                    document.getElementById('diag-improved').textContent = diag.what_improved;
                    document.getElementById('diag-weak').textContent = diag.what_remains_weak;
                    document.getElementById('diag-mistake').textContent = diag.recurring_mistake;
                    document.getElementById('diag-comparison').textContent = diag.session_comparison;
                }
            })
            .catch(err => console.error("Error loading dashboard:", err));
    },

    loadAnalytics: function () {
        fetch('/api/analytics/dashboard')
            .then(res => res.json())
            .then(data => {
                document.getElementById('an-overall-accuracy').textContent = `${data.overall_accuracy}%`;
                document.getElementById('an-total-attempts').textContent = `${data.total_attempts} total attempts`;
                document.getElementById('an-avg-speed').textContent = `${data.avg_solving_speed_seconds}s`;
                document.getElementById('an-topic-coverage').textContent = `${data.syllabus_coverage.topic_coverage_pct}%`;
                document.getElementById('an-topics-ratio').textContent = `${data.syllabus_coverage.attempted_topics} / ${data.syllabus_coverage.total_topics} topics`;
                document.getElementById('an-question-coverage').textContent = `${data.syllabus_coverage.question_coverage_pct}%`;
                document.getElementById('an-questions-ratio').textContent = `${data.syllabus_coverage.attempted_questions} / ${data.syllabus_coverage.total_questions} verified MCQs`;

                // Render mock history table
                this.renderMockHistory(data.mock_history || []);
            });

        // Load Adaptive Priorities
        fetch('/api/analytics/adaptive-priorities')
            .then(res => res.json())
            .then(data => {
                this.renderAdaptivePriorities(data.priorities || []);
            });
    },

    renderAdaptivePriorities: function (list) {
        const tbody = document.getElementById('adaptive-priorities-table');
        if (!tbody) return;
        if (!list.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No topic data available yet.</td></tr>';
            return;
        }

        tbody.innerHTML = list.map(item => `
            <tr>
                <td><strong>${item.subject_name}</strong> &rsaquo; ${item.topic_name}</td>
                <td><strong style="color:#1e40af">${(item.priority * 100).toFixed(1)}%</strong></td>
                <td>${(item.components.weakness_score * 100).toFixed(0)}%</td>
                <td>${item.metrics.overdue_revisions} due</td>
                <td>${item.metrics.days_since_practice} days</td>
                <td>${item.is_diagnostic ? '<span class="badge" style="background:#0284c7">Diagnostic</span>' : '<span class="tag">Active</span>'}</td>
                <td><small style="color:#475569">${item.explanation}</small></td>
            </tr>
        `).join('');
    },

    renderMockHistory: function (history) {
        const tbody = document.getElementById('mock-history-table');
        if (!tbody) return;
        if (!history.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No mock exams taken yet.</td></tr>';
            return;
        }
        tbody.innerHTML = history.map(m => `
            <tr>
                <td>${m.completed_at ? m.completed_at.replace('T', ' ').split('.')[0] : '—'}</td>
                <td><strong>${m.total_score.toFixed(2)}</strong></td>
                <td>${m.accuracy_pct}%</td>
                <td class="text-success">${m.correct_count}</td>
                <td class="text-danger">${m.incorrect_count}</td>
                <td>${m.unanswered_count}</td>
                <td>${Math.floor(m.time_taken_seconds / 60)}m ${m.time_taken_seconds % 60}s</td>
            </tr>
        `).join('');
    },

    // -------------------------------------------------------------
    // Revision Queue & Mistake Patterns
    // -------------------------------------------------------------
    loadDueRevisions: function () {
        fetch('/api/revision/due')
            .then(res => res.json())
            .then(data => {
                document.getElementById('rev-total-count').textContent = data.due_count;
                document.getElementById('nav-rev-badge').textContent = data.due_count;
                const container = document.getElementById('rev-list-container');
                if (!data.questions.length) {
                    container.innerHTML = '<p class="empty-state">No revisions overdue right now. All caught up!</p>';
                    return;
                }
                container.innerHTML = data.questions.map(q => `
                    <div class="card" style="padding: 1rem; border-left: 4px solid #ef4444;">
                        <div class="flex-between">
                            <strong>${q.subject} &rsaquo; ${q.topic}</strong>
                            <span class="tag difficulty-${q.difficulty}">${q.difficulty}</span>
                        </div>
                        <div style="margin: 0.5rem 0; font-size: 0.95rem;">${this.renderContent(q.question)}</div>
                        <div class="flex-between" style="font-size: 0.8rem; color: #64748b;">
                            <span>Interval: ${q.interval_days} days | Attempts: ${q.total_attempts}</span>
                            <span>Last error: ${q.mistake_label}</span>
                        </div>
                    </div>
                `).join('');
            });

        fetch('/api/revision/mistakes')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('mistake-patterns-container');
                if (!data.mistake_patterns.length) {
                    container.innerHTML = '<p class="empty-state">No mistakes recorded yet.</p>';
                    return;
                }
                container.innerHTML = data.mistake_patterns.map(m => `
                    <div style="margin-bottom: 0.75rem;">
                        <div class="flex-between" style="font-size: 0.88rem; margin-bottom: 0.2rem;">
                            <strong>${m.label}</strong>
                            <span>${m.count} times (${m.percentage}%)</span>
                        </div>
                        <div class="progress-track" style="height: 8px; border-radius: 4px;">
                            <div class="progress-fill" style="width: ${m.percentage}%; background: #dc2626;"></div>
                        </div>
                        <small style="color: #64748b;">Most frequent in: ${m.example_topic}</small>
                    </div>
                `).join('');
            });
    },

    // -------------------------------------------------------------
    // Question Bank Browsing & Management
    // -------------------------------------------------------------
    loadQuestionBank: function (page) {
        this.state.bankPage = page || 1;
        const subId = document.getElementById('bank-filter-subject').value;
        const diff = document.getElementById('bank-filter-difficulty').value;
        const ver = document.getElementById('bank-filter-verified').value;
        const search = document.getElementById('bank-search').value.trim();

        let url = `/api/questions?page=${this.state.bankPage}&limit=${this.state.bankLimit}`;
        if (subId) url += `&subject_id=${subId}`;
        if (diff) url += `&difficulty=${diff}`;
        if (ver) url += `&verified_only=${ver}`;
        if (search) url += `&search=${encodeURIComponent(search)}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                this.renderBankTable(data);
            })
            .catch(err => console.error("Error loading bank:", err));
    },

    renderBankTable: function (data) {
        const tbody = document.getElementById('bank-table-body');
        const countSpan = document.getElementById('bank-results-count');
        const pagDiv = document.getElementById('bank-pagination');

        countSpan.textContent = `Showing ${data.questions.length} of ${data.total} questions (Page ${data.page} of ${data.pages})`;

        if (!data.questions.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center">No questions found matching criteria.</td></tr>';
            pagDiv.innerHTML = '';
            return;
        }

        tbody.innerHTML = data.questions.map(q => `
            <tr>
                <td><code>${q.id}</code></td>
                <td>
                    <div style="font-size:0.95rem; font-weight:600;">${this.renderContent(q.question)}</div>
                    <div style="font-size:0.82rem; color:#64748b; margin-top:0.35rem; display:flex; flex-wrap:wrap; gap:0.5rem;">
                        <span><strong>A:</strong> ${this.renderContent(q.options.A)}</span>
                        <span><strong>B:</strong> ${this.renderContent(q.options.B)}</span>
                        <span><strong>C:</strong> ${this.renderContent(q.options.C)}</span>
                        <span><strong>D:</strong> ${this.renderContent(q.options.D)}</span>
                    </div>
                </td>
                <td>${q.subject} &rsaquo; ${q.topic}</td>
                <td><span class="tag difficulty-${q.difficulty}">${q.difficulty}</span></td>
                <td><strong style="color:#059669">${q.correct_answer}</strong></td>
                <td>${q.verified ? '<span class="tag" style="background:#dcfce7; color:#166534;">Verified</span>' : '<span class="tag">Unverified</span>'}</td>
            </tr>
        `).join('');

        // Pagination buttons
        let pagHtml = '';
        if (data.page > 1) {
            pagHtml += `<button class="btn btn-outline btn-sm" onclick="App.loadQuestionBank(${data.page - 1})">Prev</button> `;
        }
        pagHtml += `<span style="font-size:0.85rem; margin: 0 0.5rem;">Page ${data.page}/${data.pages}</span>`;
        if (data.page < data.pages) {
            pagHtml += `<button class="btn btn-outline btn-sm" onclick="App.loadQuestionBank(${data.page + 1})">Next</button>`;
        }
        pagDiv.innerHTML = pagHtml;
    },

    onBankFilterChange: function () {
        this.loadQuestionBank(1);
    },

    onSearchKey: function (e) {
        if (e.key === 'Enter') {
            this.loadQuestionBank(1);
        }
    },

    resetBankFilters: function () {
        document.getElementById('bank-search').value = '';
        document.getElementById('bank-filter-subject').value = '';
        document.getElementById('bank-filter-difficulty').value = '';
        document.getElementById('bank-filter-verified').value = '';
        this.loadQuestionBank(1);
    },

    loadDemoQuestions: function () {
        if (!confirm("Load sample demonstration questions into the database? These are clearly marked as sample demo data.")) return;
        fetch('/api/load-sample-demo', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(`Sample demo questions loaded! Valid: ${data.result.imported}, Duplicates: ${data.result.exact_duplicates_count}`);
                this.loadHierarchy();
                this.loadQuestionBank(1);
                this.loadTodayDashboard();
            })
            .catch(err => alert("Failed to load demo: " + err));
    },

    exportBank: function (fmt) {
        window.location.href = `/api/import-export/export/questions?format_type=${fmt}`;
    },

    exportQuarantined: function () {
        window.location.href = `/api/import-export/export/quarantine`;
    },

    // -------------------------------------------------------------
    // Import & Inspection System
    // -------------------------------------------------------------
    openImportModal: function () {
        document.getElementById('import-preview-section').classList.add('hidden');
        document.getElementById('btn-commit-import').disabled = true;
        document.getElementById('import-modal').classList.remove('hidden');
    },

    closeImportModal: function () {
        document.getElementById('import-modal').classList.add('hidden');
        this.state.stagedImportFile = null;
    },

    handleImportFile: function (file) {
        this.state.stagedImportFile = file;
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/import-export/preview', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                document.getElementById('import-preview-section').classList.remove('hidden');
                document.getElementById('prev-total').textContent = data.total_read;
                document.getElementById('prev-valid').textContent = data.valid_count;
                document.getElementById('prev-exact').textContent = data.exact_duplicates_count;
                document.getElementById('prev-rejected').textContent = data.rejected_count;

                const btnCommit = document.getElementById('btn-commit-import');
                btnCommit.disabled = data.valid_count === 0;

                // Render probable duplicates flagged
                const flaggedSec = document.getElementById('prev-flagged-section');
                const flaggedList = document.getElementById('prev-flagged-list');
                if (data.probable_duplicates && data.probable_duplicates.length) {
                    flaggedSec.classList.remove('hidden');
                    flaggedList.innerHTML = data.probable_duplicates.map(p => `
                        <div class="card" style="padding:0.5rem; background:#fffbeb; margin-bottom:0.4rem; font-size:0.85rem;">
                            <strong>Row ${p.row} (ID: ${p.id}):</strong> ${p.question}
                            <div style="color:#d97706; margin-top:0.2rem;">
                                ${p.candidates.map(c => `&bull; Similar to existing (${(c.similarity_score * 100).toFixed(0)}% match): "${c.existing_text}"`).join('<br>')}
                            </div>
                        </div>
                    `).join('');
                } else {
                    flaggedSec.classList.add('hidden');
                }

                // Render rejection errors
                const errSec = document.getElementById('prev-errors-section');
                const errList = document.getElementById('prev-errors-list');
                if (data.rejected && data.rejected.length) {
                    errSec.classList.remove('hidden');
                    errList.innerHTML = data.rejected.map(r => `
                        <div class="card" style="padding:0.5rem; background:#fef2f2; margin-bottom:0.4rem; font-size:0.85rem;">
                            <strong>Row ${r.row} (ID: ${r.id || 'N/A'}):</strong> <span class="text-danger">${r.error}</span>
                        </div>
                    `).join('');
                } else {
                    errSec.classList.add('hidden');
                }
            })
            .catch(err => alert("File preview inspection failed: " + err));
    },

    commitImport: function () {
        if (!this.state.stagedImportFile) return;
        const formData = new FormData();
        formData.append('file', this.state.stagedImportFile);

        fetch('/api/import-export/commit', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                alert(`Import Complete!\nSuccessfully Imported: ${data.imported}\nExact Duplicates Skipped: ${data.exact_duplicates_count}\nRejected/Quarantined: ${data.rejected_count}`);
                this.closeImportModal();
                this.loadHierarchy();
                this.loadQuestionBank(1);
                this.loadTodayDashboard();
            })
            .catch(err => alert("Import failed: " + err));
    },

    // -------------------------------------------------------------
    // Database Backup & Restore
    // -------------------------------------------------------------
    createBackup: function () {
        fetch('/api/import-export/backup/create', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(`Backup created successfully: ${data.filename}`);
                this.loadBackupsList();
            })
            .catch(err => alert("Backup creation failed: " + err));
    },

    loadBackupsList: function () {
        fetch('/api/import-export/backup/list')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('backups-list');
                if (!container) return;
                if (!data.backups.length) {
                    container.innerHTML = '<p class="empty-state">No backups created yet.</p>';
                    return;
                }
                container.innerHTML = data.backups.map(b => `
                    <div class="card flex-between" style="padding: 0.6rem 1rem;">
                        <div>
                            <strong>${b.filename}</strong>
                            <div class="sub-text">${(b.size_bytes / 1024).toFixed(1)} KB | ${b.created_at.replace('T', ' ').split('.')[0]}</div>
                        </div>
                        <button class="btn btn-outline btn-sm" onclick="App.restoreBackup('${b.filepath.replace(/\\/g, '\\\\')}')">Restore</button>
                    </div>
                `).join('');
            });
    },

    restoreBackup: function (filepath) {
        if (!confirm("Are you sure you want to restore from this backup? Your current database will be backed up safely before restore.")) return;
        fetch('/api/import-export/backup/restore', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ backup_path: filepath })
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                this.loadTodayDashboard();
                this.loadHierarchy();
                this.loadQuestionBank(1);
            })
            .catch(err => alert("Restore failed: " + err));
    },

    // -------------------------------------------------------------
    // Practice & Exam Engine Execution
    // -------------------------------------------------------------
    startSession: function (sessionType, sizeElId, explicitSize) {
        let size = explicitSize || 20;
        if (sizeElId) {
            const el = document.getElementById(sizeElId);
            if (el) size = parseInt(el.value);
        }

        const payload = {
            session_type: sessionType,
            size: size
        };

        this.launchSessionRequest(payload);
    },

    startTopicPractice: function () {
        const subId = document.getElementById('practice-subject-select').value;
        const topId = document.getElementById('practice-topic-select').value;
        const size = parseInt(document.getElementById('mode-topic-size').value);

        if (!subId && !topId) {
            alert("Please select a subject or topic to begin topic drill.");
            return;
        }

        const payload = {
            session_type: topId ? 'topic' : 'subject',
            size: size,
            subject_id: subId ? parseInt(subId) : null,
            topic_id: topId ? parseInt(topId) : null
        };
        this.launchSessionRequest(payload);
    },

    startTimedPractice: function () {
        const size = parseInt(document.getElementById('mode-timed-size').value);
        const mins = parseInt(document.getElementById('mode-timed-mins').value);
        const payload = {
            session_type: 'timed',
            size: size,
            time_limit_minutes: mins
        };
        this.launchSessionRequest(payload);
    },

    launchSessionRequest: function (payload) {
        fetch('/api/practice/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(res => {
                if (!res.ok) return res.json().then(e => { throw new Error(e.detail || 'Could not start session'); });
                return res.json();
            })
            .then(sessionData => {
                this.state.activeSession = sessionData;
                this.state.currentQuestionIndex = 0;
                this.state.isPaused = false;
                this.state.secondsElapsed = 0;
                this.openSessionOverlay();
            })
            .catch(err => alert("Session initiation error: " + err.message));
    },

    openSessionOverlay: function () {
        const overlay = document.getElementById('session-overlay');
        overlay.classList.remove('hidden');

        const isMock = this.state.activeSession.session_type === 'full_mock';
        const typeLabels = {
            'daily_mixed': 'Daily Mixed Practice',
            'subject': 'Subject Drill',
            'topic': 'Topic Drill',
            'weak_topic': 'Weak-Topic Practice',
            'revision_only': 'Spaced Revision Session',
            'timed': 'Timed Speed Drill',
            'full_mock': 'Full DDCET Mock Exam'
        };
        document.getElementById('session-badge-type').textContent = typeLabels[this.state.activeSession.session_type] || 'Practice Session';

        // Timer initialization
        if (this.state.timerInterval) clearInterval(this.state.timerInterval);
        const timeLimit = this.state.activeSession.time_limit_seconds;
        if (timeLimit > 0) {
            this.state.secondsRemaining = timeLimit;
        } else {
            this.state.secondsRemaining = 0;
        }

        this.updateTimerDisplay();
        this.state.timerInterval = setInterval(() => {
            if (!this.state.isPaused) {
                this.state.secondsElapsed++;
                if (this.state.activeSession.time_limit_seconds > 0) {
                    this.state.secondsRemaining--;
                    if (this.state.secondsRemaining <= 0) {
                        clearInterval(this.state.timerInterval);
                        alert("Time is up! Auto-submitting examination.");
                        this.finishSession();
                    }
                }
                this.updateTimerDisplay();
            }
        }, 1000);

        this.renderCurrentQuestion();
        this.renderPalette();
    },

    updateTimerDisplay: function () {
        const timerEl = document.getElementById('session-timer-display');
        let sec = this.state.activeSession.time_limit_seconds > 0 ? this.state.secondsRemaining : this.state.secondsElapsed;
        sec = Math.max(0, sec);
        const m = Math.floor(sec / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        timerEl.textContent = `${m}:${s}`;
    },

    togglePauseSession: function () {
        this.state.isPaused = !this.state.isPaused;
        const btn = document.getElementById('btn-pause-session');
        btn.textContent = this.state.isPaused ? 'Resume' : 'Pause';
    },

    renderCurrentQuestion: function () {
        const s = this.state.activeSession;
        const idx = this.state.currentQuestionIndex;
        const q = s.questions[idx];

        // Header info & progress
        document.getElementById('session-progress-text').textContent = `Question ${idx + 1} of ${s.questions.length}`;
        const pct = ((idx + 1) / s.questions.length) * 100;
        document.getElementById('session-progress-bar').style.width = `${pct}%`;

        // Question Meta
        document.getElementById('q-meta-subject').textContent = q.subject;
        document.getElementById('q-meta-topic').textContent = q.topic;
        document.getElementById('q-meta-subtopic').textContent = q.subtopic;
        const diffEl = document.getElementById('q-meta-diff');
        diffEl.textContent = q.difficulty;
        diffEl.className = `tag difficulty-tag difficulty-${q.difficulty}`;
        document.getElementById('q-meta-id').textContent = `ID: ${q.question_id}`;

        // Question Text (Rendered with KaTeX Math & Markdown)
        document.getElementById('q-text').innerHTML = this.renderContent(q.question);

        // Render Options A, B, C, D (Rendered with KaTeX Math & Markdown)
        const optContainer = document.getElementById('q-options');
        const keys = ['A', 'B', 'C', 'D'];
        const isMock = s.session_type === 'full_mock';

        optContainer.innerHTML = keys.map(k => {
            const isSelected = q.selected_option === k;
            let optClass = 'option-card';
            if (isSelected) optClass += ' selected';

            // Show immediate feedback if NOT mock exam and answered
            if (!isMock && q.is_answered) {
                if (k === q.correct_answer) {
                    optClass += ' correct';
                } else if (isSelected && !q.is_correct) {
                    optClass += ' incorrect';
                }
            }

            const renderedOptText = this.renderContent(q.options[k] || '');
            return `
                <div class="${optClass}" onclick="App.selectOption('${k}')">
                    <span class="option-badge">${k}</span>
                    <span class="option-text">${renderedOptText}</span>
                </div>
            `;
        }).join('');

        // Review mark button state
        const btnReview = document.getElementById('btn-review-q');
        btnReview.classList.toggle('btn-warning', q.is_marked_for_review);

        // Feedback / Explanation area (Non-mock practice only)
        const feedbackBox = document.getElementById('q-feedback-area');
        if (!isMock && q.is_answered) {
            feedbackBox.classList.remove('hidden');
            const statusEl = document.getElementById('q-feedback-status');
            if (q.is_correct) {
                statusEl.innerHTML = '<span class="text-success">✓ Correct Answer!</span>';
            } else {
                statusEl.innerHTML = `<span class="text-danger">✗ Incorrect. Correct answer is Option ${q.correct_answer}.</span>`;
            }

            document.getElementById('q-explanation-text').innerHTML = this.renderContent(q.explanation || 'No explanation provided.');

            // Show mistake chips if wrong
            const mistakeSec = document.getElementById('mistake-tagging-section');
            if (!q.is_correct) {
                mistakeSec.classList.remove('hidden');
                document.querySelectorAll('.chip-btn').forEach(btn => {
                    btn.classList.toggle('active', btn.getAttribute('data-mistake') === q.mistake_category);
                    btn.onclick = () => this.tagMistake(btn.getAttribute('data-mistake'));
                });
            } else {
                mistakeSec.classList.add('hidden');
            }

            // Confidence selector
            document.querySelectorAll('.conf-btn').forEach(btn => {
                btn.classList.toggle('active', btn.getAttribute('data-conf') === (q.confidence || 'medium'));
                btn.onclick = () => this.setConfidence(btn.getAttribute('data-conf'));
            });
        } else {
            feedbackBox.classList.add('hidden');
        }

        // Navigation controls
        document.getElementById('btn-prev-q').disabled = idx === 0;
        const btnNext = document.getElementById('btn-next-q');
        if (idx === s.questions.length - 1) {
            btnNext.textContent = s.session_type === 'full_mock' ? 'Submit Exam' : 'Finish Session';
        } else {
            btnNext.textContent = 'Next Question →';
        }
    },

    selectOption: function (optionKey) {
        const s = this.state.activeSession;
        const idx = this.state.currentQuestionIndex;
        const q = s.questions[idx];

        // In Practice mode, prevent changing after answering if already confirmed, or allow toggling
        q.selected_option = optionKey;
        q.is_answered = true;

        const isMock = s.session_type === 'full_mock';
        if (!isMock) {
            q.is_correct = (optionKey === q.correct_answer);
        }

        // Send auto-save to backend
        fetch('/api/practice/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: s.session_id,
                question_id: q.question_id,
                selected_option: optionKey,
                time_spent_seconds: 5,
                is_marked_for_review: q.is_marked_for_review,
                confidence: q.confidence || 'medium',
                mistake_category: q.mistake_category
            })
        }).catch(err => console.error("Auto-save error:", err));

        this.renderCurrentQuestion();
        this.renderPalette();
    },

    tagMistake: function (category) {
        const q = this.state.activeSession.questions[this.state.currentQuestionIndex];
        q.mistake_category = category;
        this.selectOption(q.selected_option);
    },

    setConfidence: function (conf) {
        const q = this.state.activeSession.questions[this.state.currentQuestionIndex];
        q.confidence = conf;
        this.selectOption(q.selected_option);
    },

    toggleReviewMark: function () {
        const q = this.state.activeSession.questions[this.state.currentQuestionIndex];
        q.is_marked_for_review = !q.is_marked_for_review;
        this.renderCurrentQuestion();
        this.renderPalette();
    },

    nextQuestion: function () {
        const s = this.state.activeSession;
        if (this.state.currentQuestionIndex < s.questions.length - 1) {
            this.state.currentQuestionIndex++;
            this.renderCurrentQuestion();
            this.renderPalette();
        } else {
            this.confirmFinishSession();
        }
    },

    prevQuestion: function () {
        if (this.state.currentQuestionIndex > 0) {
            this.state.currentQuestionIndex--;
            this.renderCurrentQuestion();
            this.renderPalette();
        }
    },

    jumpToQuestion: function (index) {
        if (index >= 0 && index < this.state.activeSession.questions.length) {
            this.state.currentQuestionIndex = index;
            this.renderCurrentQuestion();
            this.renderPalette();
        }
    },

    renderPalette: function () {
        const s = this.state.activeSession;
        const grid = document.getElementById('session-palette-grid');
        if (!grid) return;

        grid.innerHTML = s.questions.map((q, idx) => {
            let cls = 'palette-btn';
            if (idx === this.state.currentQuestionIndex) {
                cls += ' current';
            } else if (q.is_marked_for_review) {
                cls += ' reviewed';
            } else if (q.is_answered) {
                cls += ' answered';
            }
            return `<button class="${cls}" onclick="App.jumpToQuestion(${idx})">${idx + 1}</button>`;
        }).join('');
    },

    confirmFinishSession: function () {
        const s = this.state.activeSession;
        const answeredCount = s.questions.filter(q => q.is_answered).length;
        const total = s.questions.length;

        const msg = `You have answered ${answeredCount} of ${total} questions.\nAre you sure you want to finish and submit this session?`;
        if (confirm(msg)) {
            this.finishSession();
        }
    },

    finishSession: function () {
        if (this.state.timerInterval) clearInterval(this.state.timerInterval);
        const s = this.state.activeSession;

        fetch('/api/practice/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: s.session_id,
                time_taken_seconds: this.state.secondsElapsed
            })
        })
            .then(res => res.json())
            .then(summary => {
                document.getElementById('session-overlay').classList.add('hidden');
                this.showSummaryModal(summary);
                this.loadTodayDashboard();
                this.loadDueRevisions();
            })
            .catch(err => alert("Session completion error: " + err));
    },

    showSummaryModal: function (summary) {
        document.getElementById('sum-score').textContent = summary.total_score.toFixed(2);
        document.getElementById('sum-accuracy').textContent = `${summary.accuracy_pct}%`;
        const m = Math.floor(summary.time_taken_seconds / 60);
        const s = summary.time_taken_seconds % 60;
        document.getElementById('sum-time').textContent = `${m}m ${s}s`;
        document.getElementById('sum-correct').textContent = summary.correct_count;
        document.getElementById('sum-incorrect').textContent = summary.incorrect_count;
        document.getElementById('sum-unanswered').textContent = summary.unanswered_count;
        document.getElementById('sum-avg-speed').textContent = `${summary.average_time_per_question}s`;

        // Subject Breakdown
        const subBox = document.getElementById('sum-subject-breakdown');
        subBox.innerHTML = summary.subject_breakdown.map(sb => `
            <div style="font-size:0.88rem; margin-bottom:0.35rem;">
                <strong>${sb.subject}:</strong> ${sb.correct}/${sb.total} Correct (${((sb.correct / sb.total) * 100).toFixed(0)}%)
            </div>
        `).join('');

        // Mistake breakdown
        const misBox = document.getElementById('sum-mistake-breakdown');
        if (summary.mistake_breakdown && summary.mistake_breakdown.length) {
            misBox.innerHTML = summary.mistake_breakdown.map(mb => `
                <span class="tag" style="background:#fee2e2; color:#dc2626; margin-right:0.4rem;">
                    ${mb.mistake_category}: ${mb.count}
                </span>
            `).join('');
        } else {
            misBox.innerHTML = '<span class="sub-text">No mistakes tagged in this session.</span>';
        }

        document.getElementById('summary-overlay').classList.remove('hidden');
    },

    closeSummaryModal: function () {
        document.getElementById('summary-overlay').classList.add('hidden');
        this.state.activeSession = null;
        this.switchTab('tab-today');
    }
};

// Initialize Application on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

/**
 * Main application client-side script for AI YouTube Comment Intelligence
 */

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

const App = {
    state: {
        comments: [],
        filteredComments: [],
        currentPage: 1,
        pageSize: 15,
        currentFilter: 'all',
        currentSort: 'quality_desc',
        searchQuery: ''
    },

    init() {
        this.initTheme();
        this.initMobileNav();
        this.initModals();
        this.initUploadTabs();
        this.initDropzone();
    },

    // -------------------------------------------------------------
    // Dark / Light Theme Management
    // -------------------------------------------------------------
    initTheme() {
        const savedTheme = localStorage.getItem('agy_theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeButton(savedTheme);

        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme');
                const nextTheme = current === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', nextTheme);
                localStorage.setItem('agy_theme', nextTheme);
                this.updateThemeButton(nextTheme);
                if (window.AppCharts && typeof window.AppCharts.updateTheme === 'function') {
                    window.AppCharts.updateTheme();
                }
            });
        }
    },

    updateThemeButton(theme) {
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (!toggleBtn) return;
        if (theme === 'dark') {
            toggleBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"></circle>
                    <line x1="12" y1="1" x2="12" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="23"></line>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                    <line x1="1" y1="12" x2="3" y2="12"></line>
                    <line x1="21" y1="12" x2="23" y2="12"></line>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
            `;
            toggleBtn.title = "Switch to Light Mode";
        } else {
            toggleBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
            `;
            toggleBtn.title = "Switch to Dark Mode";
        }
    },

    // -------------------------------------------------------------
    // Mobile Sidebar Toggle
    // -------------------------------------------------------------
    initMobileNav() {
        const toggle = document.getElementById('mobileNavToggle');
        const sidebar = document.querySelector('.app-sidebar');
        if (toggle && sidebar) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
            // Close sidebar when clicking outside on mobile
            document.addEventListener('click', (e) => {
                if (!sidebar.contains(e.target) && !toggle.contains(e.target) && sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                }
            });
        }
    },

    // -------------------------------------------------------------
    // Toast Notifications
    // -------------------------------------------------------------
    showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span>${message}</span>
        `;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    },

    // -------------------------------------------------------------
    // Modals
    // -------------------------------------------------------------
    initModals() {
        const backdrop = document.getElementById('commentDetailModal');
        if (!backdrop) return;

        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) {
                this.closeCommentModal();
            }
        });

        const closeBtn = document.getElementById('modalCloseBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeCommentModal());
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeCommentModal();
        });
    },

    openCommentModal(comment) {
        const modal = document.getElementById('commentDetailModal');
        if (!modal) return;

        document.getElementById('modalAuthor').textContent = comment.author || 'Anonymous Viewer';
        document.getElementById('modalDate').textContent = comment.published_at || 'Recent';
        document.getElementById('modalText').textContent = comment.comment_text || '';
        document.getElementById('modalLikes').textContent = (comment.likes || 0) + ' likes';

        // Sentiment badge
        const sentEl = document.getElementById('modalSentiment');
        const sentBadge = comment.sentiment === 'Positive' ? 'badge-positive' :
                         (comment.sentiment === 'Negative' ? 'badge-negative' : 'badge-neutral');
        const compound = comment.sentiment_scores?.compound !== undefined ? comment.sentiment_scores.compound.toFixed(2) : '0.00';
        sentEl.className = `badge ${sentBadge}`;
        sentEl.textContent = `${comment.sentiment} (Compound: ${compound})`;

        // Emotion
        const emoEl = document.getElementById('modalEmotion');
        emoEl.textContent = (comment.primary_emotion || 'neutral').toUpperCase();

        // Quality
        const qualityScore = comment.quality?.quality_score ?? 0;
        const qualityGrade = comment.quality?.quality_grade || 'Average';
        document.getElementById('modalQualityScore').textContent = `${qualityScore} / 100`;
        document.getElementById('modalQualityGrade').textContent = qualityGrade;
        document.getElementById('modalFeedbackType').textContent = comment.quality?.feedback_type || 'General Discussion';
        document.getElementById('modalExplanation').textContent = comment.quality?.explanation || 'Standard audience comment.';

        // Toxicity
        const toxStatus = comment.toxicity?.status || 'Safe';
        const toxScore = comment.toxicity?.toxicity_score ?? 0.0;
        const toxEl = document.getElementById('modalToxicity');
        toxEl.textContent = `${toxStatus} (${Math.round(toxScore * 100)}%)`;
        toxEl.className = `badge ${comment.toxicity?.is_toxic ? 'badge-toxic' : 'badge-positive'}`;

        // Emotion breakdown bars
        const emoScores = comment.emotion_scores || {};
        const emoContainer = document.getElementById('modalEmotionBreakdown');
        if (emoContainer) {
            emoContainer.innerHTML = '';
            for (const [emo, val] of Object.entries(emoScores)) {
                const row = document.createElement('div');
                row.style.cssText = 'display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;';
                row.innerHTML = `
                    <span style="text-transform: capitalize; color: var(--text-muted);">${emo}</span>
                    <span style="font-weight: 600;">${val}</span>
                `;
                emoContainer.appendChild(row);
            }
        }

        modal.classList.add('active');
    },

    closeCommentModal() {
        const modal = document.getElementById('commentDetailModal');
        if (modal) modal.classList.remove('active');
    },

    copyCommentText(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Comment copied to clipboard!', 'success');
        }).catch(() => {
            this.showToast('Unable to copy to clipboard', 'warning');
        });
    },

    // -------------------------------------------------------------
    // Upload Tabs & Ingestion Handling
    // -------------------------------------------------------------
    initUploadTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        if (!tabBtns.length) return;

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.style.display = 'none');

                btn.classList.add('active');
                const target = document.getElementById(btn.dataset.target);
                if (target) target.style.display = 'block';
            });
        });
    },

    initDropzone() {
        const dropzone = document.getElementById('fileDropzone');
        const fileInput = document.getElementById('fileInput');
        if (!dropzone || !fileInput) return;

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length) {
                fileInput.files = files;
                this.updateDropzonePreview(files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                this.updateDropzonePreview(fileInput.files[0]);
            }
        });
    },

    updateDropzonePreview(file) {
        const preview = document.getElementById('dropzonePreview');
        if (!preview) return;
        const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
        preview.innerHTML = `
            <div style="margin-top: 12px; font-weight: 600; color: var(--primary);">
                📄 Selected: ${file.name} (${sizeMb} MB)
            </div>
        `;
    },

    // Submit analysis async with animated progress
    submitCommentAnalysis(formData) {
        const submitBtn = document.getElementById('analyzeSubmitBtn');
        const loadingBox = document.getElementById('analysisLoadingState');
        const errorBox = document.getElementById('analysisErrorState');

        if (submitBtn) submitBtn.disabled = true;
        if (loadingBox) loadingBox.style.display = 'block';
        if (errorBox) errorBox.style.display = 'none';

        fetch('/api/analyze-comments', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json().then(data => ({ status: res.status, body: data })))
        .then(result => {
            if (result.status === 200 && result.body.success) {
                this.showToast(`Analyzed ${result.body.total_comments} comments successfully!`, 'success');
                window.location.href = result.body.redirect_url;
            } else {
                if (submitBtn) submitBtn.disabled = false;
                if (loadingBox) loadingBox.style.display = 'none';
                if (errorBox) {
                    errorBox.style.display = 'block';
                    errorBox.textContent = result.body.error || 'Failed to analyze comments.';
                }
            }
        })
        .catch(err => {
            if (submitBtn) submitBtn.disabled = false;
            if (loadingBox) loadingBox.style.display = 'none';
            if (errorBox) {
                errorBox.style.display = 'block';
                errorBox.textContent = 'Network or server error: ' + err.message;
            }
        });
    },

    // Trigger demo data load
    loadDemoData() {
        const formData = new FormData();
        formData.append('is_demo', 'true');
        formData.append('video_title', 'Full-Stack AI Project Tutorial (Demo Data)');
        this.submitCommentAnalysis(formData);
    },

    // Delete session
    deleteSession(sessionId) {
        if (!confirm('Are you sure you want to delete this analysis session?')) return;

        fetch(`/api/history/${sessionId}`, { method: 'DELETE' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.showToast('Session deleted successfully', 'success');
                    setTimeout(() => window.location.reload(), 600);
                } else {
                    this.showToast(data.error || 'Failed to delete session', 'danger');
                }
            })
            .catch(err => {
                this.showToast('Error deleting session', 'danger');
            });
    },

    // -------------------------------------------------------------
    // Comment Explorer Client Reactivity
    // -------------------------------------------------------------
    initCommentExplorer(allComments) {
        this.state.comments = allComments || [];
        this.state.filteredComments = [...this.state.comments];
        this.state.currentPage = 1;

        const searchEl = document.getElementById('commentSearchInput');
        if (searchEl) {
            searchEl.addEventListener('input', (e) => {
                this.state.searchQuery = e.target.value.toLowerCase().trim();
                this.state.currentPage = 1;
                this.applyFiltersAndRender();
            });
        }

        const sortEl = document.getElementById('commentSortSelect');
        if (sortEl) {
            sortEl.addEventListener('change', (e) => {
                this.state.currentSort = e.target.value;
                this.applyFiltersAndRender();
            });
        }

        const pills = document.querySelectorAll('.filter-pill');
        pills.forEach(pill => {
            pill.addEventListener('click', () => {
                pills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                this.state.currentFilter = pill.dataset.filter;
                this.state.currentPage = 1;
                this.applyFiltersAndRender();
            });
        });

        this.applyFiltersAndRender();
    },

    applyFiltersAndRender() {
        let list = [...this.state.comments];

        // 1. Apply Filter
        const f = this.state.currentFilter;
        if (f === 'positive') {
            list = list.filter(c => c.sentiment === 'Positive');
        } else if (f === 'neutral') {
            list = list.filter(c => c.sentiment === 'Neutral');
        } else if (f === 'negative') {
            list = list.filter(c => c.sentiment === 'Negative');
        } else if (f === 'toxic') {
            list = list.filter(c => c.toxicity?.is_toxic);
        } else if (f === 'constructive') {
            list = list.filter(c => c.quality?.is_constructive);
        } else if (f === 'high_quality') {
            list = list.filter(c => (c.quality?.quality_score || 0) >= 75);
        }

        // 2. Apply Search
        if (this.state.searchQuery) {
            const q = this.state.searchQuery;
            list = list.filter(c => 
                (c.comment_text && c.comment_text.toLowerCase().includes(q)) ||
                (c.author && c.author.toLowerCase().includes(q))
            );
        }

        // 3. Apply Sort
        const sortMode = this.state.currentSort;
        if (sortMode === 'quality_desc') {
            list.sort((a, b) => (b.quality?.quality_score || 0) - (a.quality?.quality_score || 0));
        } else if (sortMode === 'likes_desc') {
            list.sort((a, b) => (b.likes || 0) - (a.likes || 0));
        } else if (sortMode === 'positive_desc') {
            list.sort((a, b) => (b.sentiment_scores?.compound || 0) - (a.sentiment_scores?.compound || 0));
        } else if (sortMode === 'negative_desc') {
            list.sort((a, b) => (a.sentiment_scores?.compound || 0) - (b.sentiment_scores?.compound || 0));
        } else if (sortMode === 'newest') {
            list.sort((a, b) => (b.published_at || '').localeCompare(a.published_at || ''));
        }

        this.state.filteredComments = list;
        this.renderTable();
    },

    renderTable() {
        const tbody = document.getElementById('commentsTableBody');
        const countEl = document.getElementById('explorerTotalCount');
        const paginationInfo = document.getElementById('paginationInfo');
        const prevBtn = document.getElementById('paginationPrev');
        const nextBtn = document.getElementById('paginationNext');

        if (!tbody) return;

        const total = this.state.filteredComments.length;
        if (countEl) countEl.textContent = `${total} comments found`;

        const totalPages = Math.ceil(total / this.state.pageSize) || 1;
        if (this.state.currentPage > totalPages) this.state.currentPage = totalPages;

        const startIdx = (this.state.currentPage - 1) * this.state.pageSize;
        const pageItems = this.state.filteredComments.slice(startIdx, startIdx + this.state.pageSize);

        if (paginationInfo) {
            paginationInfo.textContent = `Page ${this.state.currentPage} of ${totalPages}`;
        }
        if (prevBtn) prevBtn.disabled = this.state.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.state.currentPage >= totalPages;

        if (pageItems.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
                        No comments match the selected filters or search query.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = '';
        pageItems.forEach(c => {
            const tr = document.createElement('tr');
            
            const sentClass = c.sentiment === 'Positive' ? 'badge-positive' : 
                             (c.sentiment === 'Negative' ? 'badge-negative' : 'badge-neutral');
            
            const qScore = c.quality?.quality_score || 0;
            const qClass = qScore >= 75 ? 'badge-quality-good' : (qScore >= 50 ? 'badge-quality-avg' : 'badge-quality-low');

            const toxBadge = c.toxicity?.is_toxic ? 
                '<span class="badge badge-toxic">Toxic</span>' : 
                '<span class="badge badge-positive">Safe</span>';

            tr.innerHTML = `
                <td style="font-weight: 600; white-space: nowrap;">${this.escapeHtml(c.author || 'Anonymous')}</td>
                <td>
                    <div class="table-comment-text" title="${this.escapeHtml(c.comment_text)}">
                        ${this.escapeHtml(c.comment_text)}
                    </div>
                </td>
                <td><span class="badge ${sentClass}">${c.sentiment}</span></td>
                <td><span style="font-size: 0.8rem; text-transform: capitalize;">${c.primary_emotion || 'neutral'}</span></td>
                <td><span class="badge ${qClass}">${qScore}/100</span></td>
                <td>${toxBadge}</td>
                <td style="font-weight: 600;">👍 ${c.likes || 0}</td>
            `;

            tr.addEventListener('click', () => {
                this.openCommentModal(c);
            });

            tbody.appendChild(tr);
        });
    },

    prevPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
            this.renderTable();
        }
    },

    nextPage() {
        const totalPages = Math.ceil(this.state.filteredComments.length / this.state.pageSize);
        if (this.state.currentPage < totalPages) {
            this.state.currentPage++;
            this.renderTable();
        }
    },

    escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
};

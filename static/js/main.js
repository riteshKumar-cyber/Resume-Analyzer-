/**
 * RESUME ANALYZER - MAIN JAVASCRIPT
 * Handles Drag & Drop, API Communication, Theme Toggling, Dashboard Rendering, and Toasts.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------------------------------
    // 1. THEME TOGGLE LOGIC
    // --------------------------------------------------------------------------
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    htmlElement.setAttribute('data-theme', savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        showToast(`Switched to ${newTheme} mode`, 'info');
    });

    // --------------------------------------------------------------------------
    // 2. DOM ELEMENTS SELECTION
    // --------------------------------------------------------------------------
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const fileSelectedBox = document.getElementById('fileSelectedBox');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeDisplay = document.getElementById('fileSizeDisplay');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');

    const uploadCard = document.getElementById('uploadCard');
    const loadingContainer = document.getElementById('loadingContainer');
    const progressBarFill = document.getElementById('progressBarFill');
    const loadingText = document.getElementById('loadingText');
    const loadingSubtext = document.getElementById('loadingSubtext');

    const dashboard = document.getElementById('dashboard');
    const copySummaryBtn = document.getElementById('copySummaryBtn');
    const printPdfBtn = document.getElementById('printPdfBtn');
    const analyzeNewBtn = document.getElementById('analyzeNewBtn');

    let currentSelectedFile = null;
    const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB

    // --------------------------------------------------------------------------
    // 3. FILE UPLOAD & DRAG AND DROP HANDLERS
    // --------------------------------------------------------------------------
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'));
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    dropzone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileSelection();
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showToast('Invalid file format. Please select a .pdf file.', 'error');
            return;
        }

        if (file.size > MAX_FILE_SIZE_BYTES) {
            showToast('File size exceeds maximum allowed limit of 10MB.', 'error');
            return;
        }

        currentSelectedFile = file;
        fileNameDisplay.textContent = file.name;
        fileSizeDisplay.textContent = formatBytes(file.size);

        fileSelectedBox.style.display = 'flex';
        analyzeBtn.disabled = false;
        showToast('PDF file uploaded & ready for analysis.', 'success');
    }

    function resetFileSelection() {
        currentSelectedFile = null;
        fileInput.value = '';
        fileSelectedBox.style.display = 'none';
        analyzeBtn.disabled = true;
    }

    // --------------------------------------------------------------------------
    // 4. API CALL & ANALYZE SUBMISSION
    // --------------------------------------------------------------------------
    analyzeBtn.addEventListener('click', async () => {
        if (!currentSelectedFile) return;

        // Show Loading UI
        uploadCard.style.display = 'none';
        dashboard.style.display = 'none';
        loadingContainer.style.display = 'block';

        // Simulate animated loading progress steps
        let progress = 10;
        progressBarFill.style.width = '10%';

        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.floor(Math.random() * 15) + 5;
                if (progress > 90) progress = 90;
                progressBarFill.style.width = `${progress}%`;

                if (progress > 30 && progress <= 60) {
                    loadingText.textContent = "Analyzing document content...";
                    loadingSubtext.textContent = "Evaluating skills, experience, and keywords...";
                } else if (progress > 60) {
                    loadingText.textContent = "Generating Insights & ATS Score...";
                    loadingSubtext.textContent = "Formatting strengths, weaknesses, and career roadmap...";
                }
            }
        }, 600);

        const formData = new FormData();
        formData.append('file', currentSelectedFile);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            clearInterval(progressInterval);
            progressBarFill.style.width = '100%';

            if (response.ok && result.success) {
                setTimeout(() => {
                    loadingContainer.style.display = 'none';
                    populateDashboard(result.data, result.filename);
                    dashboard.style.display = 'block';
                    dashboard.scrollIntoView({ behavior: 'smooth' });
                    showToast('Resume analysis completed successfully!', 'success');
                }, 400);
            } else {
                throw new Error(result.error || 'Failed to analyze resume.');
            }

        } catch (err) {
            clearInterval(progressInterval);
            loadingContainer.style.display = 'none';
            uploadCard.style.display = 'block';
            showToast(err.message || 'An error occurred during analysis.', 'error');
        }
    });

    // Re-analyze new file
    if (analyzeNewBtn) {
        analyzeNewBtn.addEventListener('click', () => {
            dashboard.style.display = 'none';
            uploadCard.style.display = 'block';
            resetFileSelection();
            uploadCard.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // --------------------------------------------------------------------------
    // 5. POPULATE DASHBOARD RESULTS
    // --------------------------------------------------------------------------
    function populateDashboard(data, filename) {
        // ATS Score Gauge Animation
        const score = data.ats_score || 0;
        const atsScoreNumber = document.getElementById('atsScoreNumber');
        const atsGaugeFill = document.getElementById('atsGaugeFill');
        const atsBadge = document.getElementById('atsBadge');

        // Animate counter
        animateCounter(atsScoreNumber, 0, score, 1200);

        // Gauge stroke calculation (Circumference ~ 440)
        const offset = 440 - (440 * score / 100);
        atsGaugeFill.style.strokeDashoffset = offset;

        // Score color and status text
        if (score >= 80) {
            atsGaugeFill.style.stroke = 'var(--success)';
            atsBadge.textContent = 'Excellent Match';
            atsBadge.style.background = 'var(--success-bg)';
            atsBadge.style.color = 'var(--success)';
        } else if (score >= 60) {
            atsGaugeFill.style.stroke = 'var(--warning)';
            atsBadge.textContent = 'Moderate Match';
            atsBadge.style.background = 'var(--warning-bg)';
            atsBadge.style.color = 'var(--warning)';
        } else {
            atsGaugeFill.style.stroke = 'var(--danger)';
            atsBadge.textContent = 'Needs Revision';
            atsBadge.style.background = 'var(--danger-bg)';
            atsBadge.style.color = 'var(--danger)';
        }

        // Summary & Experience Level
        document.getElementById('summaryText').textContent = data.summary || 'No summary available.';
        document.getElementById('expLevelChip').textContent = data.experience_level || 'N/A';

        // Technical & Soft Skills
        renderTags('techSkillsList', data.technical_skills, 'skill-tag');
        renderTags('softSkillsList', data.soft_skills, 'skill-tag');

        // Missing Skills
        renderTags('missingSkillsList', data.missing_skills, 'missing-tag');

        // Strengths & Weaknesses
        renderList('strengthsList', data.strengths, 'success');
        renderList('weaknessesList', data.weaknesses, 'danger');

        // Suggestions & Grammar
        renderList('suggestionsList', data.improvement_suggestions, 'info');
        renderList('grammarList', data.grammar_suggestions, 'warning');

        // Best Suitable Job Roles
        const rolesList = document.getElementById('recommendedRolesList');
        rolesList.innerHTML = '';
        if (data.recommended_roles && data.recommended_roles.length > 0) {
            data.recommended_roles.forEach(role => {
                const div = document.createElement('div');
                div.className = 'role-item';
                div.innerHTML = `<span>${role}</span> <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>`;
                rolesList.appendChild(div);
            });
        }

        // Career Roadmap
        const roadmapList = document.getElementById('careerRoadmapList');
        roadmapList.innerHTML = '';
        if (data.career_roadmap && data.career_roadmap.length > 0) {
            data.career_roadmap.forEach((step, index) => {
                const div = document.createElement('div');
                div.className = 'roadmap-step';
                div.innerHTML = `
                    <div class="roadmap-step-badge">${index + 1}</div>
                    <p>${step}</p>
                `;
                roadmapList.appendChild(div);
            });
        }

        // Interview Preparation Tips
        const interviewList = document.getElementById('interviewTipsList');
        interviewList.innerHTML = '';
        if (data.interview_prep_tips && data.interview_prep_tips.length > 0) {
            data.interview_prep_tips.forEach(tip => {
                const div = document.createElement('div');
                div.className = 'interview-item';
                div.innerHTML = `
                    <div class="bullet-icon icon-info">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                    </div>
                    <p style="font-size:0.95rem; color: var(--text-secondary);">${tip}</p>
                `;
                interviewList.appendChild(div);
            });
        }
    }

    // --------------------------------------------------------------------------
    // 6. HELPER FUNCTIONS & RENDERING UTILS
    // --------------------------------------------------------------------------
    function renderTags(elementId, items, className) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<span class="text-muted" style="font-size:0.85rem;">None detected</span>';
            return;
        }
        items.forEach(item => {
            const span = document.createElement('span');
            span.className = className;
            span.textContent = item;
            container.appendChild(span);
        });
    }

    function renderList(elementId, items, type) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<li>No items listed.</li>';
            return;
        }

        let iconSvg = '';
        if (type === 'success') {
            iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        } else if (type === 'danger') {
            iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
        } else if (type === 'warning') {
            iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
        } else {
            iconSvg = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
        }

        items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="bullet-icon icon-${type}">${iconSvg}</div>
                <span>${item}</span>
            `;
            container.appendChild(li);
        });
    }

    function animateCounter(element, start, end, duration) {
        let startTime = null;
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        }
        window.requestAnimationFrame(step);
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // --------------------------------------------------------------------------
    // 7. TOAST NOTIFICATIONS SYSTEM
    // --------------------------------------------------------------------------
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        let iconSvg = '';
        if (type === 'success') {
            iconSvg = `<svg class="toast-icon icon-success" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
        } else if (type === 'error') {
            iconSvg = `<svg class="toast-icon icon-danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
        } else {
            iconSvg = `<svg class="toast-icon icon-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
        }

        toast.innerHTML = `
            ${iconSvg}
            <div class="toast-message">${message}</div>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Export & Print Actions
    if (copySummaryBtn) {
        copySummaryBtn.addEventListener('click', () => {
            const summary = document.getElementById('summaryText').textContent;
            const score = document.getElementById('atsScoreNumber').textContent;
            const fullText = `Resume Analysis Summary:\nATS Score: ${score}/100\n\n${summary}`;

            navigator.clipboard.writeText(fullText).then(() => {
                showToast('Summary copied to clipboard!', 'success');
            }).catch(() => {
                showToast('Failed to copy text.', 'error');
            });
        });
    }

    if (printPdfBtn) {
        printPdfBtn.addEventListener('click', () => {
            window.print();
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const practicalStartInput = document.getElementById('practical-start');
    const practicalEndInput = document.getElementById('practical-end');
    const titlesContainer = document.getElementById('dynamic-titles-container');
    const alertContainer = document.getElementById('alert-container');
    const loadDataBtn = document.getElementById('btn-load-data');
    const form = document.getElementById('termwork-form');
    const loadingOverlay = document.getElementById('page-loading-overlay');
    const successState = document.getElementById('success-state');
    const createAnotherBtn = document.getElementById('btn-create-another');
    


    // === Staggered Reveal Animation for Form Elements ===
    const formElements = document.querySelectorAll('.col-md-6, .col-md-4, .col-md-12, .col-12:not(:first-child)');
    formElements.forEach((el, index) => {
        el.classList.add('reveal-item');
        el.style.animationDelay = `${index * 0.05}s`;
    });

    // === Class Dropdown Logic ===
    const classParts = ['class-branch', 'class-year', 'class-section'];
    const classCombined = document.getElementById('class-combined');
    const branchCombined = document.getElementById('branch-combined');

    // Show/hide custom input when "Custom" is selected
    classParts.forEach(id => {
        const select = document.getElementById(id);
        const customInput = document.getElementById(id + '-custom');
        
        select.addEventListener('change', () => {
            if (select.value === 'custom') {
                customInput.classList.remove('d-none');
                customInput.focus();
            } else {
                customInput.classList.add('d-none');
                customInput.value = '';
            }
            updateClassCombined();
        });
        customInput.addEventListener('input', updateClassCombined);
    });

    function updateClassCombined() {
        const parts = classParts.map(id => {
            const select = document.getElementById(id);
            const customInput = document.getElementById(id + '-custom');
            return select.value === 'custom' ? customInput.value.trim() : (select.value || '');
        });
        if (classCombined) classCombined.value = parts.filter(p => p).join('-');
        
        if (branchCombined) {
            const branchSel = document.getElementById('class-branch');
            const branchCustom = document.getElementById('class-branch-custom');
            branchCombined.value = branchSel.value === 'custom' ? branchCustom.value.trim() : (branchSel.value || '');
        }
    }
    
    // Title length zone classifier
    function titleZone(len) {
        if (len === 0)   return '';
        if (len <= 43)   return 'short';
        if (len <= 115)  return 'medium';
        return 'long';
    }

    // Dynamically generate practical titles based on start/end range
    function generateTitleFields() {
        const start = parseInt(practicalStartInput.value) || 0;
        const end   = parseInt(practicalEndInput.value)   || 0;
        let html = '';

        if (start > 0 && end >= start && (end - start + 1) <= 50) {
            html += `<h6 class="w-100 fw-bold mt-2 mb-3 text-secondary">Practical Titles <small class="fw-normal">(Optional)</small></h6>`;
            let idx = 0;
            for (let i = start; i <= end; i++) {
                idx++;
                let delay = Math.min(idx * 0.05, 0.5);
                html += `
                <div class="col-md-6 mb-3 dynamic-field" style="animation-delay: ${delay}s">
                    <label class="form-label text-muted small fw-bold d-flex align-items-center justify-content-between">
                        <span>Experiment ${i} Title</span>
                        <span class="char-counter" id="counter-${i}">0</span>
                    </label>
                    <input type="text" class="form-control title-input" name="title_${i}"
                           placeholder="Enter title for Exp ${i}" data-exp="${i}">
                </div>`;
            }
        } else if (end > 0 && start > 0 && (end - start + 1) > 50) {
            html = '<div class="alert alert-warning w-100"><i class="fa-solid fa-triangle-exclamation me-2"></i> Maximum 50 practicals allowed at once.</div>';
        }
        titlesContainer.innerHTML = html;

        // Attach live char counter + color-coding
        titlesContainer.querySelectorAll('.title-input').forEach(input => {
            const exp = input.dataset.exp;
            const counter = document.getElementById(`counter-${exp}`);
            const update = () => {
                const len  = input.value.length;
                const zone = titleZone(len);
                if (counter) {
                    counter.textContent = len;
                    counter.className = 'char-counter' + (zone ? ` zone-${zone}` : '');
                }
                input.className = 'form-control title-input' + (zone ? ` title-${zone}` : '');
            };
            input.addEventListener('input', update);
        });
    }

    practicalStartInput.addEventListener('input', generateTitleFields);
    practicalEndInput.addEventListener('input', generateTitleFields);

    // Save and Load from Local Storage
    function saveFormData(currentForm) {
        const formData = new FormData(currentForm);
        const dataObj = {};
        for (let [key, value] of formData.entries()) {
            dataObj[key] = value;
        }
        // Also save class dropdown parts separately
        dataObj['_class_branch'] = document.getElementById('class-branch').value;
        dataObj['_class_year']   = document.getElementById('class-year').value;
        dataObj['_class_section']= document.getElementById('class-section').value;
        localStorage.setItem('termworkFormData', JSON.stringify(dataObj));
    }

    loadDataBtn.addEventListener('click', () => {
        const savedData = localStorage.getItem('termworkFormData');
        if (savedData) {
            const dataObj = JSON.parse(savedData);

            // Restore normal inputs first (skip title_ and private _ keys for now)
            for (const key in dataObj) {
                if (key.startsWith('_') || key.startsWith('title_')) continue;
                const input = document.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = dataObj[key];
                    if (key === 'practical_start' || key === 'practical_end') {
                        input.dispatchEvent(new Event('input'));
                    }
                }
            }

            // Restore class dropdowns
            const branchSel  = document.getElementById('class-branch');
            const yearSel    = document.getElementById('class-year');
            const sectionSel = document.getElementById('class-section');
            const restoreSelect = (sel, val) => {
                if (!val) return;
                // Check if value exists as an option
                const exists = [...sel.options].some(o => o.value === val);
                if (exists) {
                    sel.value = val;
                } else {
                    sel.value = 'custom';
                    const customInput = document.getElementById(sel.id + '-custom');
                    customInput.value = val;
                    customInput.classList.remove('d-none');
                }
                sel.dispatchEvent(new Event('change'));
            };
            restoreSelect(branchSel,  dataObj['_class_branch']);
            restoreSelect(yearSel,    dataObj['_class_year']);
            restoreSelect(sectionSel, dataObj['_class_section']);
            updateClassCombined();

            // Restore title fields after the dynamic fields have been generated
            setTimeout(() => {
                for (const key in dataObj) {
                    if (!key.startsWith('title_')) continue;
                    const input = document.querySelector(`[name="${key}"]`);
                    if (input) input.value = dataObj[key];
                }
            }, 100);

            showAlert('Data loaded from previous session.', 'info');
        } else {
            showAlert('No previous data found.', 'warning');
        }
    });

    // Form Submit handling
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Basic Validation - HTML5
        if (!form.checkValidity()) {
            e.stopPropagation();
            form.classList.add('was-validated');
            showAlert('Please fill in all required fields marked with *.', 'danger');
            return;
        }

        // Save base data to localStorage
        saveFormData(form);

        // UI State: Loading
        form.classList.add('d-none');
        loadingOverlay.classList.remove('d-none');
        successState.classList.add('d-none');
        alertContainer.innerHTML = '';
        // Reset loading bar animation
        const lb = document.getElementById('loading-bar');
        if (lb) { lb.style.animation = 'none'; lb.offsetHeight; lb.style.animation = ''; }

        try {
            const formData = new FormData(form);
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // UI State: Reset Loading
            loadingOverlay.classList.add('d-none');

            if (result.success) {
                // Show Success State
                successState.classList.remove('d-none');
                launchConfetti();

                // Restart Lottie animation so it plays now (not while hidden)
                const lottieEl = successState.querySelector('lottie-player');
                if (lottieEl) {
                    lottieEl.seek(0);
                    lottieEl.play();
                }
                
                // Update buttons with download URLs
                document.getElementById('download-pdf-btn').href = result.download_pdf;
                document.getElementById('download-docx-btn').href = result.download_docx;
                
                // Auto trigger PDF download
                window.location.href = result.download_pdf;
                
            } else {
                form.classList.remove('d-none');
                showAlert(result.message || 'Error generating document', 'danger');
            }
        } catch (error) {
            loadingOverlay.classList.add('d-none');
            form.classList.remove('d-none');
            showAlert('Server error. Ensure the Flask server is running and the template.docx exists.', 'danger');
            console.error(error);
        }
    });

    createAnotherBtn.addEventListener('click', (e) => {
        e.preventDefault();
        successState.classList.add('d-none');
        form.classList.remove('d-none');
        form.reset();
        document.getElementById('practical-start').dispatchEvent(new Event('input'));
    });

    function showAlert(message, type) {
        alertContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show shadow-sm" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        // Shake the alert for errors
        if (type === 'danger') {
            const alertEl = alertContainer.querySelector('.alert');
            if (alertEl) { alertEl.classList.add('shake'); }
        }
        // Auto dismiss after 5 seconds
        if(type === 'info' || type === 'success') {
            setTimeout(() => {
                const alertEl = alertContainer.querySelector('.alert');
                if(alertEl) {
                    const bsAlert = new bootstrap.Alert(alertEl);
                    bsAlert.close();
                }
            }, 5000);
        }
    }

    // =========================================
    // ANIMATED WIDGETS
    // =========================================

    // --- Typewriter tagline ---
    const typewriterEl = document.getElementById('typewriter-text');
    const phrases = [
        'Automate your multi-page termwork in seconds.',
        'CSE & IT branch templates ready.',
        'PDF & DOCX generated instantly.',
        'Smart title-length detection built in.',
    ];
    let phraseIdx = 0, charIdx = 0, deleting = false;
    function typeStep() {
        const current = phrases[phraseIdx];
        if (!deleting) {
            typewriterEl.textContent = current.slice(0, ++charIdx);
            if (charIdx === current.length) { deleting = true; setTimeout(typeStep, 1800); return; }
        } else {
            typewriterEl.textContent = current.slice(0, --charIdx);
            if (charIdx === 0) { deleting = false; phraseIdx = (phraseIdx + 1) % phrases.length; }
        }
        setTimeout(typeStep, deleting ? 35 : 55);
    }
    typeStep();

    // --- Ripple effect on all buttons ---
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px`;
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // --- Step indicator activation on scroll ---
    const sectionStepMap = [
        { selector: '[name="name"]',          stepId: 'step-1' },
        { selector: '[name="subject"]',        stepId: 'step-2' },
        { selector: '#practical-start',        stepId: 'step-3' },
        { selector: '#btn-generate',           stepId: 'step-4' },
    ];
    function updateSteps() {
        let lastFilled = -1;
        sectionStepMap.forEach((item, i) => {
            const el = document.querySelector(item.selector);
            if (el && el.value && el.value.trim() !== '') lastFilled = i;
        });
        sectionStepMap.forEach((item, i) => {
            const stepEl = document.getElementById(item.stepId);
            const lineEl = stepEl ? stepEl.nextElementSibling : null;
            if (!stepEl) return;
            stepEl.classList.remove('active', 'done');
            if (i <= lastFilled)      stepEl.classList.add('done');                          // ← was i < lastFilled
            else if (i === lastFilled + 1 || (lastFilled === -1 && i === 0)) stepEl.classList.add('active');
            if (lineEl && lineEl.classList.contains('step-line')) {
                lineEl.classList.toggle('done-line', i < lastFilled);
            }
        });
    }
    document.querySelectorAll('input, select').forEach(el => el.addEventListener('input', updateSteps));
    updateSteps();

    // --- IntersectionObserver scroll-reveal ---
    const revealEls = document.querySelectorAll('.col-12, .col-md-6, .col-md-4, .col-md-12');
    revealEls.forEach(el => el.classList.add('reveal-section'));
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
    }, { threshold: 0.12 });
    revealEls.forEach(el => revealObserver.observe(el));

    // --- Confetti burst on success ---
    function launchConfetti() {
        const container = document.getElementById('confetti-container');
        if (!container) return;
        container.innerHTML = '';
        const colors = ['#10B981','#F472B6','#FBBF24','#34D399','#60A5FA','#A78BFA'];
        for (let i = 0; i < 80; i++) {
            const piece = document.createElement('div');
            piece.className = 'confetti-piece';
            const size = Math.random() * 10 + 6;
            piece.style.cssText = `
                left: ${Math.random() * 100}%;
                width: ${size}px; height: ${size}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                animation-duration: ${Math.random() * 2 + 1.5}s;
                animation-delay: ${Math.random() * 0.8}s;
                border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
            `;
            container.appendChild(piece);
        }
        setTimeout(() => { container.innerHTML = ''; }, 4000);
    }

    // Patch success handler to also launch confetti
    const origFetch = window.fetch;
    // We'll hook into the result.success check via the existing handler already in place.
    // Instead, we expose launchConfetti globally for the submit handler to call.
    window.launchConfetti = launchConfetti;

});


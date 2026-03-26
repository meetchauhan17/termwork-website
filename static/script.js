document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const practicalStartInput = document.getElementById('practical-start');
    const practicalEndInput = document.getElementById('practical-end');
    const titlesContainer = document.getElementById('dynamic-titles-container');
    const alertContainer = document.getElementById('alert-container');
    const loadDataBtn = document.getElementById('btn-load-data');
    const form = document.getElementById('termwork-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const successState = document.getElementById('success-state');
    const createAnotherBtn = document.getElementById('btn-create-another');
    
    // === Class Dropdown Logic ===
    const classParts = ['class-branch', 'class-year', 'class-section'];
    const classCombined = document.getElementById('class-combined');

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
        classCombined.value = parts.filter(p => p).join('-');
    }
    
    // Dynamically generate practical titles based on start/end range
    function generateTitleFields() {
        const start = parseInt(practicalStartInput.value) || 0;
        const end = parseInt(practicalEndInput.value) || 0;
        let html = '';
        
        if (start > 0 && end >= start && (end - start + 1) <= 50) {
            html += '<h6 class="w-100 fw-bold mt-2 mb-3 text-secondary">Practical Titles (Optional)</h6>';
            let idx = 0;
            for (let i = start; i <= end; i++) {
                idx++;
                let delay = Math.min(idx * 0.05, 0.5);
                html += `
                <div class="col-md-6 mb-3 dynamic-field" style="animation-delay: ${delay}s">
                    <label class="form-label text-muted small fw-bold">Experiment ${i} Title</label>
                    <input type="text" class="form-control" name="title_${i}" placeholder="Enter title for Exp ${i}">
                </div>
                `;
            }
        } else if (end > 0 && start > 0 && (end - start + 1) > 50) {
            html = '<div class="alert alert-warning w-100"><i class="fa-solid fa-triangle-exclamation me-2"></i> Maximum 50 practicals allowed at once.</div>';
        }
        titlesContainer.innerHTML = html;
    }

    practicalStartInput.addEventListener('input', generateTitleFields);
    practicalEndInput.addEventListener('input', generateTitleFields);

    // Save and Load from Local Storage
    function saveFormData(currentForm) {
        const formData = new FormData(currentForm);
        const dataObj = {};
        for (let [key, value] of formData.entries()) {
            // Don't save individual titles as they generate dynamically based on count
            if (!key.startsWith('title_')) { 
                dataObj[key] = value;
            }
        }
        localStorage.setItem('termworkFormData', JSON.stringify(dataObj));
    }

    loadDataBtn.addEventListener('click', () => {
        const savedData = localStorage.getItem('termworkFormData');
        if (savedData) {
            const dataObj = JSON.parse(savedData);
            for (const key in dataObj) {
                const input = document.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = dataObj[key];
                    // Trigger input event to generate titles if it's a range field
                    if (key === 'practical_start' || key === 'practical_end') {
                        input.dispatchEvent(new Event('input'));
                    }
                }
            }
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
});

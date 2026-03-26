document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const practicalCountInput = document.getElementById('practical-count');
    const titlesContainer = document.getElementById('dynamic-titles-container');
    const alertContainer = document.getElementById('alert-container');
    const loadDataBtn = document.getElementById('btn-load-data');
    const form = document.getElementById('termwork-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const successState = document.getElementById('success-state');
    const createAnotherBtn = document.getElementById('btn-create-another');
    
    // Dynamically generate practical titles based on number input
    practicalCountInput.addEventListener('input', (e) => {
        const count = parseInt(e.target.value) || 0;
        let html = '';
        
        if (count > 0 && count <= 50) {
            html += '<h6 class="w-100 fw-bold mt-2 mb-3 text-secondary">Practical Titles (Optional)</h6>';
            for (let i = 1; i <= count; i++) {
                let delay = Math.min(i * 0.05, 0.5); // Stagger fade-in delay
                html += `
                <div class="col-md-6 mb-3 dynamic-field" style="animation-delay: ${delay}s">
                    <label class="form-label text-muted small fw-bold">Experiment ${i} Title</label>
                    <input type="text" class="form-control" name="title_${i}" placeholder="Enter title for Exp ${i}">
                </div>
                `;
            }
        } else if (count > 50) {
            html = '<div class="alert alert-warning w-100"><i class="fa-solid fa-triangle-exclamation me-2"></i> Maximum 50 practicals allowed.</div>';
        }
        titlesContainer.innerHTML = html;
    });

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
                    // Trigger input event to generate titles if it's the count field
                    if (key === 'practical_count') {
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
        document.getElementById('practical-count').dispatchEvent(new Event('input'));
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

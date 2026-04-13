// CSRF Token handling
const getCSRFToken = () => {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
        document.querySelector('input[name="csrf_token"]')?.value;
};

// Auto-dismiss alerts dengan timing berbeda berdasarkan type
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const alertType = alert.classList.contains('alert-success') ? 'success' :
            alert.classList.contains('alert-danger') ? 'danger' :
                alert.classList.contains('alert-warning') ? 'warning' : 'info';

        let dismissTime = 5000; // Default 5 detik

        // Success messages lebih cepat (3 detik) karena biasanya informatif
        if (alertType === 'success') {
            dismissTime = 3000;
        }
        // Error messages lebih lama (7 detik) karena penting
        else if (alertType === 'danger') {
            dismissTime = 7000;
        }

        setTimeout(() => {
            if (alert.isConnected) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, dismissTime);
    });

    // Confirm sebelum delete actions
    const deleteButtons = document.querySelectorAll('a[onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('Apakah Anda yakin ingin menghapus?')) {
                e.preventDefault();
            }
        });
    });

    // CSRF Protection untuk semua forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Validasi CSRF token untuk form yang tidak menggunakan WTForms
            if (!form.querySelector('input[name="csrf_token"]') && !form.querySelector('input[name="csrf_token"]')) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = getCSRFToken();
                form.appendChild(csrfInput);
            }
        });
    });
});

// Function untuk AJAX requests dengan CSRF
function makeRequest(url, method = 'POST', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: data ? JSON.stringify(data) : null
    });
}


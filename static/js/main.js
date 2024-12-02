// Theme Management
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    const body = document.body;
    const icon = document.querySelector('#theme-toggle i');

    if (theme === 'dark') {
        body.classList.add('dark-theme');
        if (icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    } else {
        body.classList.remove('dark-theme');
        if (icon) {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
}

function toggleTheme(event) {
    if (event) {
        event.preventDefault();
    }
    const body = document.body;
    const icon = document.querySelector('#theme-toggle i');
    const isDark = body.classList.toggle('dark-theme');
    
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    if (icon) {
        if (isDark) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }
}

// Profile Dropdown
function toggleDropdown() {
    const dropdown = document.querySelector('.profile-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

// Notification Management
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.main-content');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        setTimeout(() => notification.remove(), 5000);
    }
}

function toggleNotifications(event) {
    if (event) {
        event.preventDefault();
    }
    const dropdown = document.querySelector('.notification-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
        if (dropdown.classList.contains('active')) {
            fetchNotifications();
        }
    }
}

function fetchNotifications() {
    fetch('/notifications')
        .then(response => response.json())
        .then(notifications => {
            const container = document.querySelector('.notification-dropdown');
            if (!container) return;

            // Clear existing notifications except the header
            const header = container.querySelector('.notification-header');
            container.innerHTML = '';
            if (header) container.appendChild(header);

            // Add notifications
            notifications.forEach(notification => {
                const notifElement = document.createElement('div');
                notifElement.className = 'notification-item';
                notifElement.innerHTML = `
                    <div class="notification-content">
                        <p>${notification.message}</p>
                        <span class="notification-time">${notification.time}</span>
                    </div>
                `;
                container.appendChild(notifElement);
            });
        })
        .catch(error => console.error('Error fetching notifications:', error));
}

// Active Link Management
function setActiveLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        const li = link.parentElement;
        if (link.getAttribute('href') === currentPath) {
            li.classList.add('active');
        } else {
            li.classList.remove('active');
        }
    });
}

// Search Functionality
function initializeSearch() {
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            // Add your search logic here
            console.log('Searching for:', e.target.value);
        });
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initializeTheme();
    
    // Set active link
    setActiveLink();
    
    // Initialize search
    initializeSearch();

    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.profile-section')) {
            const dropdown = document.querySelector('.profile-dropdown');
            if (dropdown && dropdown.classList.contains('active')) {
                dropdown.classList.remove('active');
            }
        }
    });

    // Profile Dropdown Toggle
    const profileBtn = document.querySelector('.profile-btn');
    if (profileBtn) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleDropdown();
        });
    }

    // Notification button click handler
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', toggleNotifications);
    }

    // IP Address validation
    const ipInput = document.getElementById('server-ip');
    const ipValidationMessage = document.querySelector('.ip-validation-message');

    if (ipInput) {
        ipInput.addEventListener('input', function() {
            const ipPattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            if (!ipPattern.test(this.value)) {
                ipValidationMessage.style.display = 'block';
                this.setCustomValidity('Invalid IP address format');
            } else {
                ipValidationMessage.style.display = 'none';
                this.setCustomValidity('');
            }
        });
    }

    // Form submission handler
    const addServerForm = document.querySelector('.add-server-form');
    if (addServerForm) {
        addServerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Validate IP address
            const ipPattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            if (!ipPattern.test(data['server-ip'])) {
                alert('Please enter a valid IP address');
                return;
            }

            // Here you would typically send the data to your server
            console.log('Form submitted with data:', data);
            alert('Server/Device added successfully!');
            this.reset();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.getElementById('nav-menu');
    const menuClose = document.querySelector('.menu-close');
    const overlay = document.getElementById('overlay');
    
    // Toggle menu on button click
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default action
            e.stopPropagation(); // Stop event from bubbling
            navMenu.classList.add('active');
            overlay.classList.add('active');
            document.body.classList.add('no-scroll');
            
            // Ensure menu stays on top and unblurred
            navMenu.style.zIndex = '1001';
            navMenu.style.backdropFilter = 'none';
        });
    }
    
    // Close menu when clicking the X
    if (menuClose) {
        menuClose.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default action
            e.stopPropagation(); // Stop event from bubbling
            navMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('no-scroll');
        });
    }
    
    // Close menu when clicking the overlay
    if (overlay) {
        overlay.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default action
            e.stopPropagation(); // Stop event from bubbling
            navMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('no-scroll');
        });
    }
    
    // Prevent clicks on menu items from propagating to elements underneath
    const menuItems = navMenu.querySelectorAll('a');
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Don't stop propagation completely, as you want the link to work
            // But do prevent it from reaching elements outside the menu
            e.stopPropagation();
        });
    });
    
    // Handle window resize to reset menu state on desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            navMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.classList.remove('no-scroll');
        }
    });
});
// Modern JavaScript for Cityplots Origin Landing Page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNavigation();
    initializeAnimations();
    initializeCounters();
    initializeCarousel();
    initializeSmoothScrolling();
    initializeVideoPlayButton();
    initializeFormHandling();
    
    console.log('Cityplots Origin landing page initialized successfully!');
});

// Navigation functionality
function initializeNavigation() {
    const navbar = document.querySelector('.glass-nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Handle navbar background on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(10, 10, 10, 0.98)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(8, 8, 8, 0.95)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.05)';
        }
    });
    
    // Active nav link highlighting
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {

            navLinks.forEach(l => l.classList.remove('active'));

            this.classList.add('active');

            const navbarToggler = document.querySelector('.navbar-toggler');
            const navbarCollapse = document.querySelector('.navbar-collapse');
            
            if (navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    });
}

// Advanced animation system using Intersection Observer
function initializeAnimations() {
    // Intersection Observer for scroll-triggered animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                
                // Trigger staggered animations for child elements
                const staggeredElements = entry.target.querySelectorAll('[class*="stagger-"]');
                staggeredElements.forEach((el, index) => {
                    setTimeout(() => {
                        el.classList.add('in-view');
                    }, index * 100);
                });
            }
        });
    }, observerOptions);
    
    // Observe all animate-on-scroll elements
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
    
    // Trigger initial animations for hero section
    setTimeout(() => {
        const heroElements = document.querySelectorAll('.hero-content [class*="animate-"]');
        heroElements.forEach((el, index) => {
            setTimeout(() => {
                el.style.animationPlayState = 'running';
            }, index * 200);
        });
    }, 500);
}

// Animated counters
function initializeCounters() {
    const counters = document.querySelectorAll('.counter');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.getAttribute('data-target'));
        const current = parseInt(counter.textContent);
        const increment = target / 50; // Adjust speed
        
        if (current < target) {
            counter.textContent = Math.ceil(current + increment);
            setTimeout(() => animateCounter(counter), 50);
        } else {
            counter.textContent = target;
        }
    };
    
    // Intersection Observer for counters
    const counterObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => counterObserver.observe(counter));
}

// Enhanced carousel functionality
function initializeCarousel() {
    const carousel = document.querySelector('#propertyCarousel');
    if (!carousel) return;
    
    // Add hover pause functionality
    carousel.addEventListener('mouseenter', function() {
        const bsCarousel = bootstrap.Carousel.getInstance(carousel);
        if (bsCarousel) {
            bsCarousel.pause();
        }
    });
    
    carousel.addEventListener('mouseleave', function() {
        const bsCarousel = bootstrap.Carousel.getInstance(carousel);
        if (bsCarousel) {
            bsCarousel.cycle();
        }
    });
    
    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        const bsCarousel = bootstrap.Carousel.getInstance(carousel);
        if (!bsCarousel) return;
        
        if (e.key === 'ArrowLeft') {
            bsCarousel.prev();
        } else if (e.key === 'ArrowRight') {
            bsCarousel.next();
        }
    });
}

// Smooth scrolling for navigation links
function initializeSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Scroll indicator functionality
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', function() {
            window.scrollTo({
                top: window.innerHeight,
                behavior: 'smooth'
            });
        });
    }
}

// Video play button functionality
function initializeVideoPlayButton() {
    const playButton = document.querySelector('.video-play-btn');
    const videoContainer = document.querySelector('.video-container iframe');
    
    if (playButton && videoContainer) {
        playButton.addEventListener('click', function() {
            // Get current src and add autoplay parameter
            const currentSrc = videoContainer.src;
            const newSrc = currentSrc.includes('?') ? 
                currentSrc + '&autoplay=1' : 
                currentSrc + '?autoplay=1';
            
            videoContainer.src = newSrc;
            
            // Hide play button
            this.parentElement.style.opacity = '0';
            setTimeout(() => {
                this.parentElement.style.display = 'none';
            }, 300);
        });
    }
}

// Form handling and modal functionality
function initializeFormHandling() {
    // Contact form handling
    const contactForms = document.querySelectorAll('form');
    
    contactForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic form validation
            const inputs = this.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            
            if (isValid) {
                // Simulate form submission
                showNotification('Thank you! We will contact you soon.', 'success');
                this.reset();
            } else {
                showNotification('Please fill in all required fields.', 'error');
            }
        });
    });
    
    // Phone number click to call
    const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    phoneLinks.forEach(link => {
        link.addEventListener('click', function() {
            showNotification('Initiating call...', 'info');
        });
    });
}

// Utility function for notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Advanced features

// Parallax effect for hero section
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;
    const heroVideo = document.querySelector('.hero-video');
    
    if (heroVideo) {
        heroVideo.style.transform = `translateY(${rate}px)`;
    }
});

// function updateFavicon() {
//     const sections = ['home', 'features', 'gallery', 'plots', 'amenities', 'location'];
//     const colors = ['#859F3D', '#6B7C32', '#4A7C59', '#68A678', '#A8D5BA', '#5A6B2A'];
    
//     const scrollPosition = window.scrollY;
//     const windowHeight = window.innerHeight;
//     const sectionIndex = Math.min(Math.floor(scrollPosition / windowHeight), sections.length - 1);

//     const canvas = document.createElement('canvas');
//     canvas.width = 32;
//     canvas.height = 32;
//     const ctx = canvas.getContext('2d');
    
//     ctx.fillStyle = colors[sectionIndex];
//     ctx.fillRect(0, 0, 32, 32);
//     ctx.fillStyle = 'white';
//     ctx.font = '20px Arial';
//     ctx.fillText('C', 8, 22);
    
//     const favicon = document.querySelector('link[rel="icon"]') || document.createElement('link');
//     favicon.rel = 'icon';
//     favicon.href = canvas.toDataURL();
    
//     if (!document.querySelector('link[rel="icon"]')) {
//         document.head.appendChild(favicon);
//     }
// }

// window.addEventListener('scroll', updateFavicon);
// updateFavicon(); 

function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

function preloadResources() {
    const criticalImages = [
        'https://images.pexels.com/photos/323705/pexels-photo-323705.jpeg',
    
    ];
    
    criticalImages.forEach(src => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = src;
        link.as = 'image';
        document.head.appendChild(link);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    preloadResources();
    initializeLazyLoading();
    initializePlotGrid();
});


function initializePlotGrid() {
    const plotItems = document.querySelectorAll('.plot-item');
    const plotTitle = document.getElementById('plotTitle');
    const plotPrice = document.getElementById('plotPrice');
    const plotSize = document.getElementById('plotSize');
    const plotLocation = document.getElementById('plotLocation');
    const plotFacing = document.getElementById('plotFacing');

    const plotAmenities = document.getElementById('plotAmenities');
    const plotStatus = document.getElementById('plotStatus');
    const inquireBtn = document.getElementById('inquireBtn');
    const plotDetailCard = document.getElementById('plotDetailCard');
    
    plotItems.forEach(plotItem => {
    plotItem.addEventListener('mouseenter', function () {
        const plotNumber = this.getAttribute('data-plot');
        const price = this.getAttribute('data-price');
        const size = this.getAttribute('data-size');
        const location = this.getAttribute('data-location');
        const facing = this.getAttribute('data-facing');
        const amenities = this.getAttribute('data-description');
        const isPremium = this.classList.contains('premium');
        const isSold = this.classList.contains('sold');

        plotTitle.textContent = `Plot #${plotNumber}`;
        plotPrice.textContent = `₹${price} Lakhs`;
        plotSize.textContent = `${parseInt(size).toLocaleString()} sq ft`;
        plotLocation.textContent = location;
        plotFacing.textContent = `${facing} `;

        plotAmenities.innerHTML = '';
        amenities.split(', ').forEach(amenity => {
            const tag = document.createElement('span');
            tag.className = 'amenity-tag';
            tag.textContent = amenity;
            plotAmenities.appendChild(tag);
        });

        if (isSold) {
            plotStatus.textContent = 'SOLD';
            plotStatus.className = 'plot-status-badge sold';
        } else if (isPremium) {
            plotStatus.textContent = 'PREMIUM';
            plotStatus.className = 'plot-status-badge premium';
        } else {
            plotStatus.textContent = 'AVAILABLE';
            plotStatus.className = 'plot-status-badge available';
        }
        plotDetailCard.style.transform = 'translateY(-5px)';
        plotDetailCard.style.boxShadow = '0 20px 40px rgba(133, 159, 61, 0.2)';
        this.style.transform = 'scale(1.15)';
        this.style.zIndex = '10';
    });

    plotItem.addEventListener('mouseleave', function () {
        plotDetailCard.style.transform = '';
        plotDetailCard.style.boxShadow = '';

        this.style.transform = '';
        this.style.zIndex = '';
    });

    plotItem.addEventListener('click', function () {
        if (window.innerWidth <= 768) {
            this.dispatchEvent(new Event('mouseenter'));
            plotDetailCard.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    });
});

    document.addEventListener('mousemove', function(e) {
        const isOverPlot = e.target.closest('.plot-item');
        const isOverCard = e.target.closest('.plot-detail-card');
        
        if (!isOverPlot && !isOverCard) {
            resetPlotCard();
        }
    });
    
    function resetPlotCard() {
        plotTitle.textContent = 'Select a Plot';
        plotPrice.textContent = '--';
        plotSize.textContent = '--';
        plotLocation.textContent = '--';
        plotFacing.textContent = '--';
        plotAmenities.innerHTML = '<span class="amenity-tag">Hover over a plot</span>';
        plotStatus.textContent = 'HOVER TO VIEW';
        plotStatus.className = 'plot-status-badge';

    }
    
    function showInquiryModal(plotNumber, price, size, location) {
        const modalHtml = `
            <div class="modal fade" id="inquiryModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-olive text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-map-marker-alt me-2"></i>
                                Plot #${plotNumber} Inquiry
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="plot-summary mb-4">
                                <div class="row g-3">
                                    <div class="col-6">
                                        <div class="text-center p-3 bg-light rounded">
                                            <strong>Price</strong><br>
                                            <span class="text-olive">₹${price} Lakhs</span>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="text-center p-3 bg-light rounded">
                                            <strong>Size</strong><br>
                                            <span class="text-olive">${parseInt(size).toLocaleString()} sq ft</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <form id="inquiryForm">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">Full Name *</label>
                                        <input type="text" class="form-control" required>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">Phone Number *</label>
                                        <input type="tel" class="form-control" required>
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label">Email Address *</label>
                                        <input type="email" class="form-control" required>
                                    </div>
                                    <div class="col-12">
                                        <label class="form-label">Message</label>
                                        <textarea class="form-control" rows="3" placeholder="Any specific questions about this plot?"></textarea>
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" form="inquiryForm" class="btn btn-olive">
                                <i class="fas fa-paper-plane me-2"></i>Send Inquiry
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('inquiryModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('inquiryModal'));
        modal.show();
        
        // Handle form submission
        document.getElementById('inquiryForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simulate form submission
            showNotification(`Thank you! We'll contact you about Plot #${plotNumber} soon.`, 'success');
            modal.hide();
            
            // Clean up modal after hiding
            setTimeout(() => {
                document.getElementById('inquiryModal').remove();
            }, 500);
        });
        
        // Clean up modal when hidden
        document.getElementById('inquiryModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }
    
    // Initialize with default state
    resetPlotCard();
}

// Custom cursor effect for interactive elements
function initializeCustomCursor() {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--olive);
        pointer-events: none;
        z-index: 9999;
        transition: transform 0.1s ease;
        mix-blend-mode: difference;
        display: none;
    `;
    document.body.appendChild(cursor);
    
    document.addEventListener('mousemove', function(e) {
        cursor.style.left = e.clientX - 10 + 'px';
        cursor.style.top = e.clientY - 10 + 'px';
        cursor.style.display = 'block';
    });
    
    // Hide cursor when mouse leaves window
    document.addEventListener('mouseleave', function() {
        cursor.style.display = 'none';
    });
    
    // Scale cursor on hover over interactive elements
    const interactiveElements = document.querySelectorAll('a, button, .btn, .card, .amenity-card');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            cursor.style.transform = 'scale(2)';
        });
        
        el.addEventListener('mouseleave', function() {
            cursor.style.transform = 'scale(1)';
        });
    });
}

if (window.innerWidth > 768) {
    initializeCustomCursor();
}

function initializeBackgroundMusic() {
    const musicToggle = document.createElement('button');
    musicToggle.innerHTML = '<i class="fas fa-music"></i>';
    musicToggle.className = 'btn btn-olive position-fixed';
    musicToggle.style.cssText = 'bottom: 20px; left: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px;';
    
    const audio = new Audio('path/to/background-music.mp3');
    audio.loop = true;
    audio.volume = 0.3;
    
    let isPlaying = false;
    
    musicToggle.addEventListener('click', function() {
        if (isPlaying) {
            audio.pause();
            this.innerHTML = '<i class="fas fa-music"></i>';
        } else {
            audio.play();
            this.innerHTML = '<i class="fas fa-pause"></i>';
        }
        isPlaying = !isPlaying;
    });

}

window.CityplotsOrigin = {
    initializeNavigation,
    initializeAnimations,
    initializeCounters,
    showNotification
};

const video = document.getElementById('scroll-video');

  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        if (video.paused) {
          video.play();
        }
      } else {
        if (!video.paused) {
          video.pause();
        }
      }
    },
    {
      threshold: 0.6, 
    }
  );

  observer.observe(document.getElementById('video-section'));
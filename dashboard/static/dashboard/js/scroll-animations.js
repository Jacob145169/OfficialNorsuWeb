/**
 * Smooth Scroll Animations
 * Adds fade-in and slide-up effects as elements come into view
 */

(function() {
    'use strict';
    
    // Check if animations should be enabled
    const enableAnimations = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Configuration
    const config = {
        threshold: 0.05,
        rootMargin: '0px 0px -30px 0px',
        animationDelay: 50
    };
    
    // Add CSS for animations only if enabled
    const style = document.createElement('style');
    style.textContent = `
        /* Smooth scroll behavior */
        html {
            scroll-behavior: smooth;
        }
        
        /* Navbar scroll effect */
        .norsu-header {
            transition: all 0.3s ease;
        }
        
        .norsu-header.scrolled {
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            background-color: rgba(255, 255, 255, 0.98);
        }
        
        /* Progress indicator */
        .scroll-progress {
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #3f5f94, #2aa2d5);
            width: 0%;
            z-index: 9999;
            transition: width 0.1s ease;
        }
        
        ${enableAnimations ? `
        /* Scroll Animation Base Styles - Only if animations enabled */
        .scroll-animate {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease-out, transform 0.5s ease-out;
        }
        
        .scroll-animate.animate-in {
            opacity: 1;
            transform: translateY(0);
        }
        
        /* Fade animations */
        .fade-in {
            opacity: 0;
            transition: opacity 0.6s ease-out;
        }
        
        .fade-in.animate-in {
            opacity: 1;
        }
        
        /* Stagger children animations */
        .stagger-children > * {
            opacity: 0;
            transform: translateY(15px);
            transition: opacity 0.4s ease-out, transform 0.4s ease-out;
        }
        
        .stagger-children.animate-in > *:nth-child(1) { transition-delay: 0.05s; }
        .stagger-children.animate-in > *:nth-child(2) { transition-delay: 0.1s; }
        .stagger-children.animate-in > *:nth-child(3) { transition-delay: 0.15s; }
        .stagger-children.animate-in > *:nth-child(4) { transition-delay: 0.2s; }
        .stagger-children.animate-in > *:nth-child(5) { transition-delay: 0.25s; }
        .stagger-children.animate-in > *:nth-child(6) { transition-delay: 0.3s; }
        
        .stagger-children.animate-in > * {
            opacity: 1;
            transform: translateY(0);
        }
        ` : ''}
        
        /* Ensure content is always visible on mobile or if animations disabled */
        @media (max-width: 768px) {
            .scroll-animate,
            .fade-in,
            .stagger-children > * {
                opacity: 1 !important;
                transform: none !important;
            }
        }
        
        /* Reduce motion for accessibility */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
            
            .scroll-animate,
            .fade-in,
            .stagger-children > * {
                opacity: 1 !important;
                transform: none !important;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Only initialize animations on desktop
    if (!enableAnimations || window.innerWidth <= 768) {
        console.log('Scroll animations disabled for mobile or reduced motion preference');
        initBasicFeatures();
        return;
    }
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: config.threshold,
        rootMargin: config.rootMargin
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Add delay for staggered effect
                setTimeout(() => {
                    entry.target.classList.add('animate-in');
                }, index * config.animationDelay);
                
                // Unobserve after animation
                setTimeout(() => {
                    observer.unobserve(entry.target);
                }, 1000);
            }
        });
    }, observerOptions);
    
    // Auto-detect and animate elements
    function initScrollAnimations() {
        // Only on desktop
        if (window.innerWidth <= 768) return;
        
        // Automatically add scroll-animate class to major sections
        const autoAnimateSelectors = [
            '.top-cards',
            '.main-section',
            '.colleges-section',
            '.alumni',
            '.programs-offered-section',
            '.uv-news-section',
            '.location-section'
        ];
        
        autoAnimateSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (!el.classList.contains('scroll-animate')) {
                    el.classList.add('scroll-animate');
                }
            });
        });
        
        // Add stagger effect to card containers (desktop only)
        const cardContainers = document.querySelectorAll(
            '.top-cards, .programs-offered-grid, .uv-news-grid'
        );
        cardContainers.forEach(container => {
            container.classList.add('stagger-children');
        });
        
        // Observe all elements with animation classes
        const animatedElements = document.querySelectorAll(
            '.scroll-animate, .fade-in, .stagger-children'
        );
        
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }
    
    // Basic features that work on all devices
    function initBasicFeatures() {
        initNavbarScroll();
        initSmoothScroll();
        initProgressIndicator();
    }
    
    // Navbar scroll effect
    function initNavbarScroll() {
        const navbar = document.querySelector('.norsu-header');
        if (!navbar) return;
        
        let ticking = false;
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScroll = window.pageYOffset;
                    
                    if (currentScroll > 100) {
                        navbar.classList.add('scrolled');
                    } else {
                        navbar.classList.remove('scrolled');
                    }
                    
                    ticking = false;
                });
                
                ticking = true;
            }
        }, { passive: true });
    }
    
    // Smooth scroll for anchor links
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '#!') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // Progress indicator
    function initProgressIndicator() {
        const progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        document.body.appendChild(progressBar);
        
        let ticking = false;
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                    const scrolled = (window.pageYOffset / windowHeight) * 100;
                    progressBar.style.width = Math.min(scrolled, 100) + '%';
                    ticking = false;
                });
                
                ticking = true;
            }
        }, { passive: true });
    }
    
    // Initialize based on device
    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                if (enableAnimations && window.innerWidth > 768) {
                    initScrollAnimations();
                }
                initBasicFeatures();
            });
        } else {
            if (enableAnimations && window.innerWidth > 768) {
                initScrollAnimations();
            }
            initBasicFeatures();
        }
    }
    
    // Start initialization
    init();
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            // Disable animations on mobile
            if (window.innerWidth <= 768) {
                document.querySelectorAll('.scroll-animate, .fade-in, .stagger-children > *').forEach(el => {
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            }
        }, 250);
    });
})();

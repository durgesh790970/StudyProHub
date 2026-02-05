/**
 * Test Flow JavaScript
 * Handles difficulty selection, highlighting, and navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Difficulty Selection Page
    initDifficultySelection();
    
    // Initialize Instructions Page
    initInstructions();
});

/**
 * Initialize difficulty selection functionality
 */
function initDifficultySelection() {
    const difficultyBtns = document.querySelectorAll('.difficulty-btn');
    
    if (difficultyBtns.length === 0) {
        // Not on difficulty selection page
        return;
    }

    const nextBtn = document.getElementById('nextBtn');
    const selectedDifficultyDiv = document.getElementById('selectedDifficulty');
    const difficultyText = document.getElementById('difficultyText');
    let selectedDifficulty = null;

    /**
     * Handle difficulty button click
     */
    difficultyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            difficultyBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button with animation
            this.classList.add('active');
            
            // Add ripple effect
            addRippleEffect(this, event);
            
            // Store selected difficulty
            selectedDifficulty = this.dataset.difficulty;
            
            // Update selected difficulty display
            updateSelectedDisplay(selectedDifficulty, difficultyText, selectedDifficultyDiv);
            
            // Show and enable next button
            showNextButton(nextBtn);
            
            // Log selection
            console.log('Difficulty selected: ' + selectedDifficulty);
        });

        // Add hover effect
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });

        btn.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });

    /**
     * Handle next button click
     */
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            if (selectedDifficulty) {
                // Add loading state
                this.disabled = true;
                const originalText = this.textContent;
                this.textContent = 'Loading...';
                
                // Navigate to instructions page after brief delay for UX
                setTimeout(() => {
                    window.location.href = getInstructionsUrl(selectedDifficulty);
                }, 300);
            }
        });
    }
}

/**
 * Update selected difficulty display
 */
function updateSelectedDisplay(difficulty, textElement, displayDiv) {
    const difficultyLabel = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
    textElement.textContent = difficultyLabel;
    
    // Add animation
    displayDiv.style.display = 'block';
    displayDiv.style.animation = 'slideIn 0.3s ease';
}

/**
 * Show next button with animation
 */
function showNextButton(btn) {
    if (btn) {
        btn.style.display = 'inline-block';
        btn.disabled = false;
        btn.classList.add('show');
        
        // Trigger animation
        setTimeout(() => {
            btn.style.opacity = '1';
            btn.style.transform = 'scale(1)';
        }, 10);
    }
}

/**
 * Add ripple effect on button click
 */
function addRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');

    element.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Get instructions URL with difficulty parameter
 */
function getInstructionsUrl(difficulty) {
    // This should match the URL pattern in urls.py
    return '/test-instructions/?difficulty=' + difficulty;
}

/**
 * Initialize instructions page functionality
 */
function initInstructions() {
    const startTestBtn = document.getElementById('startTestBtn');
    
    if (!startTestBtn) {
        // Not on instructions page
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const difficulty = urlParams.get('difficulty') || 'medium';

    /**
     * Store difficulty in session/localStorage for quiz page
     */
    sessionStorage.setItem('testDifficulty', difficulty);
    console.log('Test difficulty stored: ' + difficulty);

    /**
     * Handle start test button click
     */
    startTestBtn.addEventListener('click', function() {
        // Add loading state
        startTestBtn.disabled = true;
        const originalText = startTestBtn.textContent;
        startTestBtn.textContent = 'Starting...';
        startTestBtn.style.opacity = '0.7';

        // Prevent double clicks
        startTestBtn.style.pointerEvents = 'none';

        // Navigate to quiz page after brief delay
        setTimeout(() => {
            window.location.href = getQuizUrl(difficulty);
        }, 500);
    });

    /**
     * Prevent accidental page refresh/close
     */
    let testStarted = false;
    window.addEventListener('beforeunload', function(e) {
        if (testStarted) {
            e.preventDefault();
            e.returnValue = 'Are you sure? The test will be lost.';
        }
    });

    /**
     * Mark test as started when button is clicked
     */
    startTestBtn.addEventListener('click', function() {
        testStarted = true;
    });
}

/**
 * Get quiz URL with difficulty parameter
 */
function getQuizUrl(difficulty) {
    // This should match your quiz URL pattern
    return '/quiz.html?difficulty=' + difficulty + '&type=aptitude';
}

/**
 * Utility: Format difficulty level for display
 */
function formatDifficulty(difficulty) {
    const map = {
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard'
    };
    return map[difficulty.toLowerCase()] || difficulty;
}

/**
 * Utility: Get difficulty color
 */
function getDifficultyColor(difficulty) {
    const colors = {
        'easy': '#22c55e',
        'medium': '#f59e0b',
        'hard': '#ef4444'
    };
    return colors[difficulty.toLowerCase()] || '#2563eb';
}

/**
 * Utility: Get difficulty icon
 */
function getDifficultyIcon(difficulty) {
    const icons = {
        'easy': '🟢',
        'medium': '🟡',
        'hard': '🔴'
    };
    return icons[difficulty.toLowerCase()] || '❓';
}

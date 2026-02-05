/* ===================================
   TEST PAGE JAVASCRIPT
   =================================== */

class TestPage {
  constructor(config) {
    this.config = config; // {company, difficulty, totalQuestions: 20, timeLimit: 1800}
    this.currentQuestion = 0;
    this.answers = {};
    this.timeRemaining = config.timeLimit;
    this.questions = [];
    this.timerInterval = null;
    this.testStarted = false;
    this.userEmail = null; // Store logged-in user email
    this.userName = null;  // Store logged-in user name
    
    this.init();
  }

  async init() {
    try {
      // Fetch logged-in user's email from backend
      await this.fetchUserInfo();
      
      // Setup event listeners first (including Start Test button)
      this.setupEventListeners();

      // Check if coming from URL params or saved state
      if (this.config.company && this.config.difficulty) {
        // Auto-start if company and difficulty are provided via config
        await this.loadQuestionsAndStart();
      }
      // Otherwise, wait for user to select company/difficulty and click Start Test

    } catch (error) {
      console.error('Failed to initialize test:', error);
      this.showError('Failed to load test. Please refresh the page.');
    }
  }

  async fetchUserInfo() {
    try {
      const response = await fetch('/api/get-user-email/');
      const data = await response.json();
      
      if (data.ok) {
        this.userEmail = data.email;
        this.userName = data.name || 'Candidate';
        console.log('Logged-in user:', data.email);
      } else {
        console.warn('User not authenticated:', data.error);
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  }

  async loadQuestions() {
    try {
      const response = await fetch(
        `/api/get-questions/?company=${this.config.company}&difficulty=${this.config.difficulty}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.questions = data.questions || [];
      console.log(`Loaded ${this.questions.length} questions`);
    } catch (error) {
      console.error('Failed to load questions:', error);
      throw error;
    }
  }

  setupEventListeners() {
    // Start test button
    const startBtn = document.getElementById('startTestBtn');
    if (startBtn) {
      startBtn.addEventListener('click', () => this.startTestFromSelector());
    }

    // Navigation buttons
    document.getElementById('prevBtn').addEventListener('click', () => this.prevQuestion());
    // Next button uses a handler that can act as Next or Submit depending on state
    document.getElementById('nextBtn').addEventListener('click', (e) => this.handleNextClick(e));
    document.getElementById('submitBtn').addEventListener('click', () => this.submitImmediately());

    // Options (event delegation)
    document.getElementById('optionsContainer').addEventListener('click', (e) => {
      const option = e.target.closest('.option');
      if (option) {
        this.selectOption(option);
      }
    });

    // Modal close buttons
    document.getElementById('continueBtn').addEventListener('click', () => {
      this.closeModal('unansweredModal');
      this.nextQuestion();
    });

    document.getElementById('cancelSubmitBtn').addEventListener('click', () => {
      this.closeModal('submitModal');
    });

    document.getElementById('confirmSubmitBtn').addEventListener('click', () => {
      // Do not close modal before reading the email input — submitTest will handle modal visibility
      this.submitTest();
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') this.prevQuestion();
      if (e.key === 'ArrowRight') this.nextQuestion();
    });

    // Make Next button visually blue to match request
    const nextBtn = document.getElementById('nextBtn');
    if (nextBtn) {
      nextBtn.style.backgroundColor = '#2563eb';
      nextBtn.style.borderColor = '#2563eb';
      nextBtn.style.color = '#ffffff';
    }
  }

  startTestFromSelector() {
    const company = document.getElementById('companySelect').value;
    const difficulty = document.getElementById('difficultySelect').value;

    // Update internal config
    this.config.company = company;
    this.config.difficulty = difficulty;

    // Update header (show test header and hide selector)
    const selector = document.getElementById('selectorContainer');
    if (selector) selector.style.display = 'none';
    const header = document.getElementById('testHeaderContent');
    if (header) header.style.display = 'flex';

    // Update company name and difficulty badge
    const companyNameEl = document.getElementById('companyName');
    if (companyNameEl) companyNameEl.textContent = company.charAt(0).toUpperCase() + company.slice(1);
    const badge = document.getElementById('difficultyBadge');
    if (badge) {
      badge.textContent = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
      badge.className = 'difficulty-badge ' + difficulty;
    }

    // Update company logo (if static image exists)
    const logoImg = document.getElementById('companyLogoImg');
    const logoContainer = document.getElementById('companyLogo');
    if (logoImg && logoContainer) {
      const logoPath = `/static/accounts/img/logos/${company.toLowerCase()}.svg`;
      logoImg.src = logoPath;
      // show container; if image fails to load, onerror hides it
      logoContainer.style.display = 'block';
    }

    // Reset answers and state
    this.currentQuestion = 0;
    this.answers = {};
    this.questions = [];
    this.timeRemaining = this.config.timeLimit;

    // Load questions inline and start timer
    this.loadQuestionsAndStart();
  }

  async loadQuestionsAndStart() {
    try {
      await this.loadQuestions();

      if (this.questions.length === 0) {
        this.showError('No questions found for this difficulty level');
        return;
      }

      // Clear any existing timer
      if (this.timerInterval) clearInterval(this.timerInterval);

      // Display first question
      this.displayQuestion(0);
      this.startTimer();
      this.testStarted = true;
      this.saveState();
    } catch (error) {
      console.error('Failed to load questions:', error);
      this.showError('Failed to load questions. Please try again.');
    }
  }

  displayQuestion(index) {
    if (index < 0 || index >= this.questions.length) return;

    this.currentQuestion = index;
    const question = this.questions[index];

    // Update question header
    document.getElementById('questionNumber').textContent = `Q${index + 1}`;
    document.getElementById('questionText').textContent = question.question_text;

    // Update progress
    const progress = ((index + 1) / this.questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
    document.getElementById('currentQuestion').textContent = index + 1;
    document.getElementById('totalQuestions').textContent = this.questions.length;

    // Update answered count
    const answered = Object.keys(this.answers).length;
    document.getElementById('answeredCount').textContent = `${answered} answered`;

    // Update live score display (max = questions.length)
    this.updateScoreDisplay();

    // Display options
    this.displayOptions(question);

    // Update navigation buttons
    document.getElementById('prevBtn').disabled = index === 0;
    document.getElementById('nextBtn').disabled = index === this.questions.length - 1;

    // Show submit button only on last question
    if (index === this.questions.length - 1) {
      const nextBtn = document.getElementById('nextBtn');
      const submitBtn = document.getElementById('submitBtn');
      const submitContainer = document.getElementById('submitContainer');
      if (nextBtn) {
        nextBtn.style.display = 'none';
        nextBtn.style.visibility = 'hidden';
      }
      if (submitContainer) {
        // prefer flex layout for container if present; fallback to block
        submitContainer.style.display = 'flex';
        submitContainer.style.visibility = 'visible';
      }
      if (submitBtn) {
        submitBtn.style.display = '';
        submitBtn.style.visibility = 'visible';
        submitBtn.disabled = false;
      } else {
        console.warn('submitBtn not found in DOM');
      }
    } else {
      const nextBtn = document.getElementById('nextBtn');
      const submitBtn = document.getElementById('submitBtn');
      const submitContainer = document.getElementById('submitContainer');
      if (nextBtn) {
        nextBtn.style.display = '';
        nextBtn.style.visibility = 'visible';
      }
      if (submitBtn) {
        submitBtn.style.display = 'none';
        submitBtn.style.visibility = 'hidden';
      }
      if (submitContainer) {
        submitContainer.style.display = 'none';
        submitContainer.style.visibility = 'hidden';
      }
    }

    // Scroll to top
    document.querySelector('.test-content').scrollTop = 0;

    // Save state
    this.saveState();
  }

  displayOptions(question) {
    const container = document.getElementById('optionsContainer');
    container.innerHTML = '';

    const options = [
      { label: 'A', text: question.option_a },
      { label: 'B', text: question.option_b },
      { label: 'C', text: question.option_c },
      { label: 'D', text: question.option_d }
    ];

    options.forEach((opt) => {
      const div = document.createElement('div');
      div.className = 'option';
      
      // Add selected class if already answered
      if (this.answers[this.currentQuestion] === opt.label) {
        div.classList.add('selected');
      }

      div.innerHTML = `
        <div class="option-radio">
          ${this.answers[this.currentQuestion] === opt.label ? '✓' : ''}
        </div>
        <div class="option-label">${opt.label}</div>
        <div class="option-text">${opt.text}</div>
      `;

      container.appendChild(div);
    });
  }

  selectOption(optionElement) {
    // Remove previous selection
    document.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));

    // Add selection to clicked option
    optionElement.classList.add('selected');

    // Update radio indicator
    optionElement.querySelector('.option-radio').textContent = '✓';

    // Store answer
    const optionLabel = optionElement.querySelector('.option-label').textContent;
    this.answers[this.currentQuestion] = optionLabel;

    // Save state
    this.saveState();

    // Update live score after selecting
    this.updateScoreDisplay();

    // Update Next button state in case we're on last question
    this.updateNextButtonForLastQuestion();

    console.log(`Q${this.currentQuestion + 1} answered: ${optionLabel}`);
  }

  // Calculate current score based on selected answers
  calculateScore() {
    let score = 0;
    let max = 0;

    for (let i = 0; i < this.questions.length; i++) {
      const q = this.questions[i];
      const correct = (q.correct_answer || '').toString().trim().toUpperCase();

      // assume 1 mark per question unless q.marks provided
      const mark = q.marks ? Number(q.marks) || 1 : 1;
      max += mark;

      const given = this.answers[i];
      if (given && given.toString().trim().toUpperCase() === correct) {
        score += mark;
      }
    }

    return { score, max };
  }

  updateScoreDisplay() {
    const el = document.getElementById('liveScore');
    if (!el) return;
    const { score, max } = this.calculateScore();
    el.textContent = `${score} / ${max}`;
  }

  // Handle clicks on Next button: either go Next or submit if acting as Submit
  handleNextClick(e) {
    if (this.currentQuestion === this.questions.length - 1 && this.nextAsSubmit) {
      // On last question and Next is acting as Submit
      const given = this.answers[this.currentQuestion];
      if (given) {
        this.submitImmediately();
      } else {
        // Show unanswered modal with list
        const unanswered = this.getUnansweredQuestions();
        this.showUnansweredWarning(unanswered);
      }
    } else {
      this.nextQuestion();
    }
  }

  // Update Next button to act as Submit on the last question
  updateNextButtonForLastQuestion() {
    const nextBtn = document.getElementById('nextBtn');
    const lastIndex = this.questions.length - 1;
    if (!nextBtn) return;

    if (this.currentQuestion === lastIndex) {
      this.nextAsSubmit = true;
      nextBtn.textContent = 'Submit Test ✓';
      nextBtn.style.backgroundColor = '#2563eb';
      nextBtn.style.borderColor = '#2563eb';
      nextBtn.style.color = '#ffffff';
    } else {
      this.nextAsSubmit = false;
      nextBtn.textContent = 'Next →';
      // restore neutral style
      nextBtn.style.backgroundColor = '';
      nextBtn.style.borderColor = '';
      nextBtn.style.color = '';
    }
  }

  nextQuestion() {
    if (this.currentQuestion < this.questions.length - 1) {
      this.displayQuestion(this.currentQuestion + 1);
    }
  }

  prevQuestion() {
    if (this.currentQuestion > 0) {
      this.displayQuestion(this.currentQuestion - 1);
    }
  }

  confirmSubmit() {
    // Check for unanswered questions
    const unanswered = this.getUnansweredQuestions();

    if (unanswered.length > 0) {
      this.showUnansweredWarning(unanswered);
    } else {
      this.showSubmitConfirmation();
    }
  }

  // New: immediate submit flow triggered by Submit button
  submitImmediately() {
    const unanswered = this.getUnansweredQuestions();
    if (unanswered.length > 0) {
      // show unanswered modal so user can choose
      this.showUnansweredWarning(unanswered);
      return;
    }

    // No unanswered -> directly submit
    this.closeModal('unansweredModal');
    this.submitTest();
  }

  getUnansweredQuestions() {
    const unanswered = [];
    for (let i = 0; i < this.questions.length; i++) {
      if (!this.answers[i]) {
        unanswered.push(i + 1);
      }
    }
    return unanswered;
  }

  showUnansweredWarning(unanswered) {
    const modal = document.getElementById('unansweredModal');
    const list = document.getElementById('unansweredList');
    
    list.innerHTML = unanswered.slice(0, 5).join(', ') + 
      (unanswered.length > 5 ? `, and ${unanswered.length - 5} more` : '');

    this.openModal('unansweredModal');
  }

  showSubmitConfirmation() {
    // Skip confirmation modal - submit directly
    this.submitImmediately();
  }

  async submitTest() {
    try {
      // Stop timer
      if (this.timerInterval) clearInterval(this.timerInterval);

      // Calculate results
      const totalQuestions = this.questions.length;
      const answeredCount = Object.keys(this.answers).length;
      const { score, max } = this.calculateScore();

      // Determine correct/wrong counts (assuming 1 mark per question unless marks vary)
      let correct = 0;
      let wrong = 0;
      for (let i = 0; i < this.questions.length; i++) {
        const q = this.questions[i];
        const correctAns = (q.correct_answer || '').toString().trim().toUpperCase();
        const given = (this.answers[i] || '').toString().trim().toUpperCase();
        if (!given) {
          // unanswered
        } else if (given === correctAns) {
          correct += 1;
        } else {
          wrong += 1;
        }
      }

      const percentage = totalQuestions ? Math.round((correct / totalQuestions) * 100) : 0;

      // Pass/Fail logic: total=20 && correct>=13 => PASS
      const isPass = (totalQuestions === 20 && correct >= 13);
      const statusText = isPass ? 'PASS' : 'FAIL';
      const message = isPass ? 'Congratulations! You are PASS 🎉' : 'Better luck next time! ❌';

      // Use logged-in user's email automatically (or fallback to localStorage)
      let userEmail = this.userEmail || localStorage.getItem('userEmail') || '';
      let userName = this.userName || localStorage.getItem('userFullName') || localStorage.getItem('userName') || 'Candidate';
      
      // If still no email, the user is not logged in - show warning
      if (!userEmail) {
        alert('⚠️ You are not logged in. Please login first to save results automatically.');
        this.showMessage('Please login to save your results to your profile.');
        return;
      }

      // Store email in localStorage for future use
      if (userEmail) {
        localStorage.setItem('userEmail', userEmail);
      }

      // Clear saved state
      sessionStorage.removeItem('testState');

      // Build payload to send to backend - with logged-in user's email
      const payload = {
        company: this.config.company,
        difficulty: this.config.difficulty,
        total_questions: totalQuestions,
        answered: answeredCount,
        correct: correct,
        wrong: wrong,
        percentage: percentage,
        time_remaining: this.timeRemaining,
        answers: this.answers,
        email: userEmail,
        name: userName,
        timestamp: new Date().toISOString()
      };

      // Include time limit so server can compute time taken if needed
      if (this.config && this.config.timeLimit) payload.time_limit = this.config.timeLimit;

      // Store in sessionStorage for result page
      sessionStorage.setItem('testResult', JSON.stringify(payload));

      // Attempt to POST to backend endpoint which should persist results and send email server-side
      let backendOk = false;
      let emailSent = false;
      try {
        const resp = await fetch('/api/submit-test/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCsrfToken()
          },
          body: JSON.stringify(payload)
        });

        if (resp.ok) {
          const json = await resp.json().catch(() => ({}));
          backendOk = true;
          const serverMsg = json.message || 'Result submitted to server.';
          const emailSentFromServer = json.email_sent || false;
          if (emailSentFromServer) {
            emailSent = true;
            this.showMessage(serverMsg + ' Email sent by server.');
          } else {
            this.showMessage(serverMsg + ' Backend accepted results.');
          }
        } else {
          console.warn('Backend returned non-OK for /api/submit-test/', resp.status);
        }
      } catch (beErr) {
        console.error('Failed to submit results to backend:', beErr);
      }

      // Redirect to result page to show results and auto-send email
      setTimeout(() => {
        window.location.href = '/test-result/';
      }, 1000);

    } catch (error) {
      console.error('Failed to finalize test results:', error);
      this.showError('Failed to finalize test. Please try again.');
    }
  }

  startTimer() {
    this.updateTimerDisplay();

    this.timerInterval = setInterval(() => {
      this.timeRemaining--;

      this.updateTimerDisplay();

      // Warning at 5 minutes
      if (this.timeRemaining === 300) {
        this.showTimeWarning();
      }

      // Auto-submit at 0
      if (this.timeRemaining <= 0) {
        clearInterval(this.timerInterval);
        this.autoSubmit();
      }

      // Save state periodically
      if (this.timeRemaining % 10 === 0) {
        this.saveState();
      }
    }, 1000);
  }

  updateTimerDisplay() {
    const display = document.querySelector('.timer-display');
    display.textContent = this.formatTime(this.timeRemaining);

    const timerElement = document.querySelector('.timer');

    // Update styling based on time remaining
    if (this.timeRemaining <= 60) {
      timerElement.classList.remove('warning');
      timerElement.classList.add('critical');
    } else if (this.timeRemaining <= 300) {
      timerElement.classList.remove('critical');
      timerElement.classList.add('warning');
    } else {
      timerElement.classList.remove('warning', 'critical');
    }
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  showTimeWarning() {
    // Visual feedback - pulse animation on timer
    const timer = document.querySelector('.timer');
    timer.style.animation = 'pulse 0.5s infinite';
  }

  async autoSubmit() {
    console.log('Time expired. Auto-submitting test...');
    this.closeModal('unansweredModal');
    this.closeModal('submitModal');
    await this.submitTest();
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'flex';
    }
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'none';
    }
  }

  showError(message) {
    // Create error banner
    const banner = document.createElement('div');
    banner.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #fee2e2;
      color: #991b1b;
      padding: 16px 24px;
      border-radius: 8px;
      border-left: 4px solid #dc2626;
      z-index: 2000;
      font-weight: 600;
    `;
    banner.textContent = message;
    document.body.appendChild(banner);

    // Auto-remove after 5 seconds
    setTimeout(() => banner.remove(), 5000);
  }

  showMessage(message) {
    // Non-error message banner
    const banner = document.createElement('div');
    banner.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #ecfccb;
      color: #365314;
      padding: 12px 20px;
      border-radius: 8px;
      border-left: 4px solid #65a30d;
      z-index: 2000;
      font-weight: 600;
    `;
    banner.textContent = message;
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 5000);
  }

  saveState() {
    const state = {
      currentQuestion: this.currentQuestion,
      answers: this.answers,
      timeRemaining: this.timeRemaining,
      timestamp: new Date().toISOString()
    };
    sessionStorage.setItem('testState', JSON.stringify(state));
  }

  restoreState() {
    const saved = sessionStorage.getItem('testState');
    if (saved) {
      const state = JSON.parse(saved);
      this.currentQuestion = state.currentQuestion;
      this.answers = state.answers;
      this.timeRemaining = state.timeRemaining;
      console.log('Test state restored from sessionStorage');
    }
  }

  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;

    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }

    return cookieValue;
  }
}

// Initialize when page loads
window.TestPage = TestPage;

document.addEventListener('DOMContentLoaded', () => {
  // Get URL parameters
  const params = new URLSearchParams(window.location.search);
  const company = params.get('company') || 'google';
  const difficulty = params.get('difficulty') || 'medium';

  // Initialize test
  window.testInstance = new TestPage({
    company,
    difficulty,
    totalQuestions: 20,
    timeLimit: 1800 // 30 minutes in seconds
  });
});

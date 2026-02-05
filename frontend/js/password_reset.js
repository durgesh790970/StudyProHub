/**
 * Password Reset Page - Interactive Features
 * Handles form validation, submission, and UX enhancements
 */

document.addEventListener('DOMContentLoaded', () => {
  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Find form elements
  const form = document.querySelector('.reset-form');
  const emailInput = document.querySelector('input[name="email"]');
  const submitBtn = document.querySelector('.btn-primary');
  const errorList = document.querySelector('.errorlist');

  if (!form) return; // No form on this page

  // Real-time email validation
  if (emailInput) {
    emailInput.addEventListener('blur', () => {
      validateEmail(emailInput);
    });

    emailInput.addEventListener('input', () => {
      // Clear error styling on change
      emailInput.classList.remove('is-invalid');
    });
  }

  // Form submission handler
  if (form) {
    form.addEventListener('submit', (e) => {
      // Don't prevent default - let Django handle it, but show loading
      if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        setTimeout(() => {
          submitBtn.textContent = 'Sending...';
        }, 100);
      }
    });
  }

  // Password reset confirmation form (new password input)
  const newPasswordInputs = document.querySelectorAll('input[name="new_password1"], input[name="new_password2"]');
  if (newPasswordInputs.length > 0) {
    setupPasswordValidation(newPasswordInputs);
  }

  // Show/hide password toggles
  setupPasswordToggles();

  // Auto-focus email field
  if (emailInput && !emailInput.value) {
    emailInput.focus();
  }

  function validateEmail(input) {
    const value = input.value.trim();
    if (!value) {
      input.classList.add('is-invalid');
      showError('Email is required');
      return false;
    }
    if (!emailRegex.test(value)) {
      input.classList.add('is-invalid');
      showError('Please enter a valid email address');
      return false;
    }
    input.classList.remove('is-invalid');
    clearErrors();
    return true;
  }

  function setupPasswordValidation(inputs) {
    inputs.forEach((input) => {
      input.addEventListener('input', () => {
        validatePasswords(inputs[0], inputs[1]);
      });
    });
  }

  function validatePasswords(pwd1, pwd2) {
    if (pwd1.value && pwd2.value && pwd1.value !== pwd2.value) {
      pwd2.classList.add('is-invalid');
      showError('Passwords do not match');
      return false;
    }
    pwd2.classList.remove('is-invalid');
    if (pwd1.value && pwd1.value.length < 8) {
      pwd1.classList.add('is-invalid');
      showError('Password must be at least 8 characters');
      return false;
    }
    pwd1.classList.remove('is-invalid');
    if (pwd2.value && pwd1.value === pwd2.value) {
      clearErrors();
      return true;
    }
    return true;
  }

  function setupPasswordToggles() {
    const toggles = document.querySelectorAll('.password-toggle');
    toggles.forEach((toggle) => {
      toggle.addEventListener('click', () => {
        const input = toggle.parentElement.querySelector('input');
        if (input.type === 'password') {
          input.type = 'text';
          toggle.textContent = '👁️‍🗨️ Hide';
        } else {
          input.type = 'password';
          toggle.textContent = '👁️ Show';
        }
      });
    });
  }

  function showError(message) {
    clearErrors();
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';
    errorDiv.innerHTML = `<span class="message-icon">⚠️</span><div>${message}</div>`;
    form.insertBefore(errorDiv, form.firstChild);
  }

  function clearErrors() {
    const existing = document.querySelector('.message.error');
    if (existing) existing.remove();
  }

  // Animate message appearance
  const messages = document.querySelectorAll('.message');
  messages.forEach((msg) => {
    msg.style.animation = 'slideUp 0.4s ease';
  });
});

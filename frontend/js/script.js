document.addEventListener('DOMContentLoaded', ()=>{
  // footer year
  const y = new Date().getFullYear();
  const yearEl = document.getElementById('year'); if(yearEl) yearEl.textContent = y;

  // Login / OTP flow (phone -> send OTP -> show OTP input)
  const phoneForm = document.getElementById('phone-form');
  const otpForm = document.getElementById('otp-form');
  const alertPlaceholder = document.getElementById('alert-placeholder');

  let demoOtp = null;
  let resendTimer = null;

  function showAlert(msg, type = 'info'){
    if(!alertPlaceholder) return;
    const cls = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-error' : 'alert-info';
    alertPlaceholder.innerHTML = `<div class="alert ${cls} fade-in">${msg}</div>`;
    // auto clear for non-error messages
    if(type !== 'error') setTimeout(()=>{ if(alertPlaceholder.innerHTML.includes(msg)) alertPlaceholder.innerHTML = ''; }, 4500);
  }

  function startResendCountdown(seconds = 30){
    const resendBtn = document.getElementById('resend');
    if(!resendBtn) return;
    let s = seconds;
    resendBtn.disabled = true;
    resendBtn.textContent = `Resend (${s}s)`;
    resendTimer = setInterval(()=>{
      s -= 1;
      if(s <= 0){
        clearInterval(resendTimer);
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend';
      } else {
        resendBtn.textContent = `Resend (${s}s)`;
      }
    }, 1000);
  }

  if(phoneForm){
    phoneForm.addEventListener('submit', (e)=>{
      e.preventDefault();
      const phoneInput = document.getElementById('phone');
      if(!phoneInput) return;
      const phone = phoneInput.value.replace(/\D/g,'');
      if(phone.length !== 10){
        showAlert('Please enter a valid 10-digit phone number', 'error');
        phoneInput.focus();
        return;
      }

      const submitBtn = phoneForm.querySelector('button') || phoneForm.querySelector('#send-otp');
      if(submitBtn){ submitBtn.disabled = true; submitBtn.textContent = 'Sending...'; }
      // If a server-side OTP API is provided, call it. Otherwise, fallback to demo behaviour.
      const otpApiBase = window.OTP_API_URL || null; // set this in page to enable real API
      if(otpApiBase){
        fetch(otpApiBase.replace(/\/$/, '') + '/send', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: phone })
        }).then(r=>r.json()).then(data=>{
          if(submitBtn){ submitBtn.disabled = false; submitBtn.textContent = 'Send OTP'; }
          if(data && data.success){
            showAlert(data.message || 'OTP sent to your number', 'success');
            if(otpForm){ otpForm.classList.remove('d-none'); otpForm.classList.add('fade-in'); const otpInput = document.getElementById('otp-input'); if(otpInput) otpInput.focus(); }
            startResendCountdown(data.expiresIn || 30);
          } else {
            showAlert((data && data.message) ? data.message : 'Failed to send OTP, please try again', 'error');
          }
        }).catch(err=>{
          if(submitBtn){ submitBtn.disabled = false; submitBtn.textContent = 'Send OTP'; }
          console.error('OTP send error', err);
          showAlert('Unable to contact OTP service. Falling back to demo OTP.', 'info');
          // fallback to demo
          demoOtp = String(Math.floor(1000 + Math.random() * 9000));
          showAlert('OTP sent — use code ' + demoOtp + ' (demo)', 'success');
          if(otpForm){ otpForm.classList.remove('d-none'); otpForm.classList.add('fade-in'); const otpInput = document.getElementById('otp-input'); if(otpInput) otpInput.focus(); }
          startResendCountdown(30);
        });
      } else {
        // Simulate sending OTP (demo mode)
        setTimeout(()=>{
          demoOtp = String(Math.floor(1000 + Math.random() * 9000));
          if(submitBtn){ submitBtn.disabled = false; submitBtn.textContent = 'Send OTP'; }
          showAlert('OTP sent — use code ' + demoOtp + ' (demo)', 'success');

          if(otpForm){
            otpForm.classList.remove('d-none');
            otpForm.classList.add('fade-in');
            const otpInput = document.getElementById('otp-input'); if(otpInput) otpInput.focus();
          }
          startResendCountdown(30);
        }, 700);
      }
    });
  }

  if(otpForm){
    otpForm.addEventListener('submit', (e)=>{
      e.preventDefault();
      const otpInput = document.getElementById('otp-input');
      if(!otpInput) return;
      const code = otpInput.value.trim();
      if(!code){ showAlert('Please enter the OTP', 'error'); otpInput.focus(); return; }
      const otpApiBase = window.OTP_API_URL || null;
      if(otpApiBase){
        // verify via server
        const phone = (document.getElementById('phone')||{}).value.replace(/\D/g,'');
        fetch(otpApiBase.replace(/\/$/, '') + '/verify', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ phone: phone, code: code }) })
          .then(r=>r.json()).then(data=>{
            if(data && data.success){ showAlert(data.message || 'Login successful! Redirecting...', 'success'); setTimeout(()=> window.location.href = data.redirect || 'index.html', 900); }
            else { showAlert((data && data.message) ? data.message : 'Incorrect OTP. Try again or resend.', 'error'); }
          }).catch(err=>{ console.error('OTP verify error', err); showAlert('Verification failed. Try again.', 'error'); });
      } else {
        if(code === demoOtp){
          showAlert('Login successful! Redirecting...', 'success');
          setTimeout(()=> window.location.href = 'index.html', 900);
        } else {
          showAlert('Incorrect OTP. Try again or resend.', 'error');
        }
      }
    });

    const resendBtn = document.getElementById('resend');
    if(resendBtn){
      resendBtn.addEventListener('click', ()=>{
        const otpApiBase = window.OTP_API_URL || null;
        const phone = (document.getElementById('phone')||{}).value.replace(/\D/g,'');
        if(otpApiBase){
          fetch(otpApiBase.replace(/\/$/, '') + '/send', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ phone: phone }) })
            .then(r=>r.json()).then(data=>{
              if(data && data.success){ showAlert(data.message || 'OTP resent', 'info'); startResendCountdown(data.expiresIn || 30); }
              else showAlert((data && data.message) ? data.message : 'Unable to resend OTP', 'error');
            }).catch(err=>{ console.error('resend error', err); showAlert('Unable to contact OTP service. Try again later.', 'error'); });
        } else {
          // regenerate demo OTP and restart countdown
          demoOtp = String(Math.floor(1000 + Math.random() * 9000));
          showAlert('New OTP sent — use code ' + demoOtp + ' (demo)', 'info');
          startResendCountdown(30);
        }
      });
    }
  }

  // Quiz app (dynamic) — now supports sectioned quizzes with timers, shuffle, progress and localStorage
  const quizApp = document.getElementById('quizApp');
  if(quizApp){
    // load data from script tag if present
    let raw = null;
    const qTag = document.getElementById('quiz-data');
    try { raw = qTag ? JSON.parse(qTag.textContent) : null; } catch(e){ raw = null; }

    // Normalize sections
    let sections = [];
    if(raw && Array.isArray(raw)){
      sections = [{ id: 'default', title: 'Quiz', questions: raw }];
    } else if(raw && raw.sections && Array.isArray(raw.sections)){
      sections = raw.sections.map((s,idx)=>({ id: s.id || ('s'+idx), title: s.title || (`Section ${idx+1}`), questions: s.questions || [] }));
    } else {
      // fallback (shouldn't happen because quiz.html generates sections)
      const makeQ = (pref,i)=>({ q: `${pref} Question ${i}`, options: ['Option A','Option B','Option C','Option D'], answer: (i-1)%4 });
      const apt = { id:'aptitude', title:'Aptitude (Quantitative, Logical, Verbal Ability)', questions: [] };
      const tech = { id:'technical', title:'Technical (Core subjects or coding questions)', questions: [] };
      const hr = { id:'hr', title:'HR (Personal and situational interview questions)', questions: [] };
      for(let i=1;i<=10;i++){ apt.questions.push(makeQ('Aptitude',i)); tech.questions.push(makeQ('Technical',i)); hr.questions.push(makeQ('HR',i)); }
      sections = [apt, tech, hr];
    }

    // Helpers
    function shuffleArray(arr){
      for(let i=arr.length-1;i>0;i--){ const j = Math.floor(Math.random()*(i+1)); [arr[i],arr[j]] = [arr[j],arr[i]]; }
    }

    // simple Levenshtein distance (char-level)
    function levenshtein(a, b) {
      if (a === b) return 0;
      const al = a.length, bl = b.length;
      if (al === 0) return bl;
      if (bl === 0) return al;
      const matrix = Array(al + 1).fill(null).map(()=>Array(bl + 1).fill(0));
      for (let i = 0; i <= al; i++) matrix[i][0] = i;
      for (let j = 0; j <= bl; j++) matrix[0][j] = j;
      for (let i = 1; i <= al; i++) {
        for (let j = 1; j <= bl; j++) {
          const cost = a[i-1] === b[j-1] ? 0 : 1;
          matrix[i][j] = Math.min(
            matrix[i-1][j] + 1,
            matrix[i][j-1] + 1,
            matrix[i-1][j-1] + cost
          );
        }
      }
      return matrix[al][bl];
    }

    // Compute simple speech metrics comparing transcript to sampleAnswer
    function computeSpeechScores(transcript, sample, durationSec, confPercent){
      const t = (transcript || '').toLowerCase().replace(/[.,!?;:\/]/g,'').trim();
      const s = (sample || '').toLowerCase().replace(/[.,!?;:\/]/g,'').trim();
      const lenT = t.length; const lenS = s.length;
      const dist = levenshtein(t, s);
      const accuracy = lenS === 0 ? 0 : Math.max(0, Math.round((1 - (dist / Math.max(lenS, lenT || 1))) * 100));

      // pronunciation: prefer provided confidence (0-100) if available
      let pronunciation = confPercent != null ? Math.round(confPercent) : Math.round(accuracy * 0.9);

      // clarity: words per minute heuristic
      const words = t ? t.split(/\s+/).filter(Boolean).length : 0;
      const wpm = durationSec > 0 ? Math.round((words / durationSec) * 60) : 0;
      // ideal speaking rate ~ 110-160 wpm; score drops outside that range
      let clarity = 100 - Math.min(70, Math.abs(wpm - 135));
      clarity = Math.max(25, Math.round(clarity));

      // spelling/errors: count mismatched words (simple approach)
      const sampleWords = s.split(/\s+/).filter(Boolean);
      const transWords = t.split(/\s+/).filter(Boolean);
      let mismatches = 0;
      const len = Math.max(sampleWords.length, transWords.length);
      for (let i = 0; i < len; i++){
        const sw = sampleWords[i] || '';
        const tw = transWords[i] || '';
        if (!sw || !tw) { if (sw !== tw) mismatches++; continue; }
        const d = levenshtein(sw, tw);
        if (d > Math.max(1, Math.floor(sw.length * 0.25))) mismatches++;
      }

      return { pronunciation: pronunciation, accuracy: accuracy, clarity: clarity, spellingErrors: mismatches, wpm: wpm };
    }

    // Render a beautiful inline SVG bar chart for HR feedback
    function hrGraphHtml(scores){
      const p = Math.max(0, Math.min(100, Math.round(scores.pronunciation || 0)));
      const a = Math.max(0, Math.min(100, Math.round(scores.accuracy || 0)));
      const c = Math.max(0, Math.min(100, Math.round(scores.clarity || 0)));
      const width = 400;  // Increased width for better spacing
      const barH = 260;   // Increased height for vertical bars
      const gap = 100;    // Increased gap between bars
      const bottomLabel = 40;  // More space for labels
      const svgHeight = barH + bottomLabel + 30;
      const barW = 50;    // Slightly wider bars
      
      const makeBar = (label, val, x) => {
        const barHeight = Math.round(barH * (val/100));
        const glowId = `glow-${label.toLowerCase()}`;
        return `
          <g transform="translate(${x},0)">
            <defs>
              <filter id="${glowId}" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3" result="blur"/>
                <feFlood flood-opacity="0.2"/>
                <feComposite in2="blur" operator="in"/>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <rect x="0" y="0" width="${barW}" height="${barH}" rx="6" class="metric-bg"></rect>
            <rect x="0" y="${barH - barHeight}" width="${barW}" height="${barHeight}" rx="6" 
                  class="metric-bar-${label.toLowerCase()}" filter="url(#${glowId})"></rect>
            <text x="${barW/2}" y="${barH + 25}" class="metric-label" text-anchor="middle">${label}</text>
            <text x="${barW/2}" y="${barH - barHeight - 15}" class="metric-value" text-anchor="middle">${val}%</text>
          </g>
        `;
      };
      
      const svg = `<svg width="${width}" height="${svgHeight}" viewBox="0 0 ${width} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="pronunciationGradient" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" style="stop-color:#4299e1;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2b6cb0;stop-opacity:1" />
          </linearGradient>
          <linearGradient id="accuracyGradient" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" style="stop-color:#48bb78;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2f855a;stop-opacity:1" />
          </linearGradient>
          <linearGradient id="clarityGradient" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" style="stop-color:#ecc94b;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#d69e2e;stop-opacity:1" />
          </linearGradient>
        </defs>
        ${makeBar('Pronunciation', p, 50)}
        ${makeBar('Accuracy', a, 175)}
        ${makeBar('Clarity', c, 300)}
      </svg>`;
      // Calculate improvement metrics
      const spellingAccuracy = Math.max(0, Math.min(100, Math.round((1 - scores.spellingErrors/10) * 100))); // Convert errors to accuracy
      const fluencyScore = Math.max(0, Math.min(100, Math.round((scores.wpm / 150) * 100))); // WPM to fluency score (150 WPM is considered fluent)
      const overallScore = Math.round((p + a + c) / 3); // Average of all scores
      
      return `<div class="feedback-box">${svg}
        <div class="stats-box">
          <div class="stat-item">
            <span class="stat-label">Overall Score</span>
            <span class="stat-value">${overallScore}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Fluency</span>
            <span class="stat-value">${fluencyScore}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Word Accuracy</span>
            <span class="stat-value">${spellingAccuracy}%</span>
          </div>
        </div>
      </div>`;
    }

    // Compute averages for HR section answers at index idx
    function getHrAverages(idx){
      const answers = state.answers[idx] || [];
      const vals = answers.filter(a=>a && a.scores);
      if(vals.length === 0) return { pronunciation:0, accuracy:0, clarity:0 };
      const sum = vals.reduce((acc,a)=>{
        acc.pron = (acc.pron || 0) + (a.scores.pronunciation || 0);
        acc.acc = (acc.acc || 0) + (a.scores.accuracy || 0);
        acc.clr = (acc.clr || 0) + (a.scores.clarity || 0);
        return acc;
      }, {});
      return { pronunciation: Math.round(sum.pron/vals.length), accuracy: Math.round(sum.acc/vals.length), clarity: Math.round(sum.clr/vals.length) };
    }

    // Config
    const defaultSectionTimeSec = 15 * 60; // 15 minutes per section (optional)
    let shuffleEnabled = true;
    let timersEnabled = true;

    // State
    let state = {
      sectionIndex: 0,
      qIndex: 0,
      answers: sections.map(s=>Array(s.questions.length).fill(null)),
      scores: sections.map(()=>0),
      timers: sections.map(()=>defaultSectionTimeSec),
      timerIntervals: [],
      finished: sections.map(()=>false)
    };

    // Apply initial shuffle if enabled
    if(shuffleEnabled){ sections.forEach(s=>shuffleArray(s.questions)); }

    // Render section buttons (with unattempted highlight)
    function renderSectionList(){
      const el = document.createElement('div'); el.style.display='flex'; el.style.gap='.5rem'; el.style.marginBottom='1rem';
      sections.forEach((s,idx)=>{
        const btn = document.createElement('button'); btn.className='btn'; btn.textContent = `${s.title} (${s.questions.length})`; btn.style.flex='1';
        const unattempted = s.questions.length - state.answers[idx].filter(a=>a!=null).length;
        if(unattempted>0) btn.title = `${unattempted} unanswered`;
        if(idx === state.sectionIndex) btn.style.border = '2px solid #2b6cb0';
        if(state.finished[idx]) btn.classList.add('muted');
        if(unattempted>0) btn.classList.toggle('section-warning', true);
        btn.addEventListener('click', ()=>{ state.sectionIndex = idx; state.qIndex = 0; renderQuiz(); });
        el.appendChild(btn);
      });
      return el;
    }

    // Render top controls: shuffle toggle, timer display, progress, submit all
    function renderControls(){
      const controls = document.createElement('div'); controls.className='quiz-controls';

      // Shuffle checkbox
      const shuffleLabel = document.createElement('label'); shuffleLabel.style.display='flex'; shuffleLabel.style.alignItems='center'; shuffleLabel.style.gap='.4rem';
      const shuffleCb = document.createElement('input'); shuffleCb.type='checkbox'; shuffleCb.checked = shuffleEnabled;
      shuffleCb.addEventListener('change', ()=>{ shuffleEnabled = shuffleCb.checked; });
      const shuffleText = document.createElement('span'); shuffleText.className='muted'; shuffleText.textContent='Shuffle questions';
      shuffleLabel.appendChild(shuffleCb); shuffleLabel.appendChild(shuffleText);
      controls.appendChild(shuffleLabel);

      // Timer display for current section
      if(timersEnabled){
        const timerSpan = document.createElement('div'); timerSpan.className='timer'; timerSpan.style.marginLeft='auto'; timerSpan.id='sectionTimer';
        controls.appendChild(timerSpan);
      }

      // Progress bar
      const progressWrap = document.createElement('div'); progressWrap.style.width='100%'; progressWrap.style.maxWidth='260px'; progressWrap.style.marginLeft='1rem';
      const progress = document.createElement('div'); progress.className='progress';
      const fill = document.createElement('div'); fill.className='progress-fill'; fill.style.width='0%'; progress.appendChild(fill); progressWrap.appendChild(progress);
      controls.appendChild(progressWrap);

      // Submit All button
      const submitBtn = document.createElement('button'); submitBtn.className='btn'; submitBtn.textContent='Submit All'; submitBtn.addEventListener('click', submitAll);
      controls.appendChild(submitBtn);

      return controls;
    }

    // Timer management
    function startTimers(){
      // clear existing
      state.timerIntervals.forEach(i=>clearInterval(i)); state.timerIntervals = [];
      sections.forEach((s,si)=>{
        const interval = setInterval(()=>{
          if(state.finished[si]){ clearInterval(interval); return; }
          state.timers[si] = Math.max(0, state.timers[si]-1);
          if(si === state.sectionIndex) updateTimerDisplay();
          if(state.timers[si] === 0){ state.finished[si] = true; clearInterval(interval); // auto-finish section
            // if current section timed out, move to results for that section
            if(si === state.sectionIndex){ renderQuiz(); }
          }
        }, 1000);
        state.timerIntervals.push(interval);
      });
      updateTimerDisplay();
    }

    function formatTime(sec){ const m = Math.floor(sec/60); const s = sec%60; return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`; }
    function updateTimerDisplay(){ const el = document.getElementById('sectionTimer'); if(!el) return; const t = state.timers[state.sectionIndex]; el.textContent = timersEnabled ? `Time: ${formatTime(t)}` : ''; }

    // Submit all sections, validate unattempted
    function submitAll(){
      // check unattempted
      const unattemptedCounts = sections.map((s,idx)=> s.questions.length - state.answers[idx].filter(a=>a!=null).length);
      const totalUnattempted = unattemptedCounts.reduce((a,b)=>a+b,0);
      if(totalUnattempted>0){
        // highlight and show notice
        quizApp.querySelectorAll('.unattempted-note').forEach(n=>n.remove());
        const note = document.createElement('div'); note.className='unattempted-note'; note.innerHTML = `<strong>${totalUnattempted} unanswered question(s)</strong> — Please review before submitting.<br>${sections.map((s,idx)=> unattemptedCounts[idx]>0 ? `<div>${s.title}: ${unattemptedCounts[idx]} unanswered</div>` : '').join('')}`;
        quizApp.prepend(note);
        // add temporary highlight to section buttons
        // re-render section list to reflect highlights
        renderQuiz();
        // scroll to top of quizApp so user sees the message
        quizApp.scrollIntoView({ behavior:'smooth' });
        return;
      }

      // compute scores (handle HR sections differently)
      state.scores = sections.map((s,idx)=>{
        if(s.id === 'hr'){
          // For HR, compute average accuracy percent from stored scores (if any)
          const answers = state.answers[idx] || [];
          const vals = answers.map(a => (a && a.scores && typeof a.scores.accuracy === 'number') ? a.scores.accuracy : 0);
          const sum = vals.reduce((a,b)=>a+b,0);
          return answers.length ? Math.round(sum / answers.length) : 0; // percent
        } else {
          return state.answers[idx].reduce((acc,ans,i)=> acc + ((ans===s.questions[i].answer)?1:0), 0);
        }
      });
      // overall for numeric sections: sum of non-HR correct counts; for display keep total questions count separately
      const overall = state.scores.reduce((a,b)=>a+b,0);

      // save to localStorage
      try{
        const storeKey = 'studypro_quiz_results';
        const existing = JSON.parse(localStorage.getItem(storeKey) || '[]');
        existing.push({ timestamp: new Date().toISOString(), sections: sections.map((s,idx)=>({ id: s.id, title: s.title, score: state.scores[idx], total: s.questions.length })), overall });
        localStorage.setItem(storeKey, JSON.stringify(existing));
      }catch(e){ console.error('localStorage save failed', e); }

      // show results and review with circular progress
      quizApp.innerHTML = `<div style="text-align:center">
        <h3>Performance Summary</h3>
        <div style="margin-top:1rem;text-align:left">${sections.map((s,idx)=>{
          if(s.id === 'hr'){
            const avg = getHrAverages(idx);
            const overallScore = Math.round((avg.pronunciation + avg.accuracy + avg.clarity) / 3);
            const makeCircle = (percentage, size) => {
              const radius = size * 0.4;
              const circumference = radius * 2 * Math.PI;
              const offset = circumference - (percentage / 100) * circumference;
              return `
                <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" class="circular-progress">
                  <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#e2e8f0" stroke-width="8"/>
                  <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" 
                         stroke="url(#circleGradient)" stroke-width="8"
                         stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                         transform="rotate(-90 ${size/2} ${size/2})"/>
                  <defs>
                    <linearGradient id="circleGradient">
                      <stop offset="0%" stop-color="#4299e1"/>
                      <stop offset="100%" stop-color="#2b6cb0"/>
                    </linearGradient>
                  </defs>
                  <text x="50%" y="50%" text-anchor="middle" dy=".3em" class="progress-text">${percentage}%</text>
                </svg>
              `;
            };

            let feedbackMessage = '';
            if (overallScore >= 90) {
                feedbackMessage = 'Outstanding performance! You\'re ready for real interviews! 🌟';
            } else if (overallScore >= 75) {
                feedbackMessage = 'Great progress! Keep refining your communication skills! 👏';
            } else if (overallScore >= 60) {
                feedbackMessage = 'Good effort! Regular practice will help you improve! 💪';
            } else {
                feedbackMessage = 'Keep practicing! Every attempt brings you closer to your goal! 🎯';
            }

            return `<div style="background:#fff;padding:1.5rem;border-radius:12px;margin-bottom:1rem;box-shadow:0 8px 30px rgba(2,6,23,0.08)">
              <div style="font-weight:600;font-size:1.2rem;margin-bottom:1rem">${s.title}</div>
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:2rem">
                <div style="flex:1">
                  <div style="margin-bottom:1rem">${makeCircle(overallScore, 200)}</div>
                  <div class="feedback-message">${feedbackMessage}</div>
                </div>
                <div style="flex:2">${hrGraphHtml(avg)}</div>
              </div>
            </div>`;
          } else {
            return `<div style="background:#fff;padding:1.5rem;border-radius:12px;margin-bottom:1rem;box-shadow:0 8px 30px rgba(2,6,23,0.08)">
              <div style="font-weight:600;font-size:1.2rem">${s.title}</div>
              <div style="margin-top:1rem">Score: <strong>${state.scores[idx]} / ${s.questions.length}</strong></div>
            </div>`;
          }
        }).join('')}</div>
        <div style="margin-top:1rem"><strong>Overall (sum of numeric section scores): ${overall}</strong></div>
        <div style="margin-top:1rem;display:flex;gap:.5rem;justify-content:center">
          <button id="reviewAll" class="btn">Review Answers</button>
          <button id="retakeAll" class="btn">Retake (Shuffle: ${shuffleEnabled ? 'On' : 'Off'})</button>
        </div>
      </div>`;

      document.getElementById('retakeAll').addEventListener('click', ()=>{
        // reset state
        state = { sectionIndex:0, qIndex:0, answers: sections.map(s=>Array(s.questions.length).fill(null)), scores: sections.map(()=>0), timers: sections.map(()=>defaultSectionTimeSec), timerIntervals: [], finished: sections.map(()=>false) };
        if(shuffleEnabled) sections.forEach(s=>shuffleArray(s.questions));
        renderQuiz(); startTimers();
      });

      document.getElementById('reviewAll').addEventListener('click', ()=>{
        // render review of all questions with detailed feedback and improvement circles
        quizApp.innerHTML = `<div style="text-align:left">${sections.map((s,si)=>`<div class="section-review"><h3 class="section-title">${s.title}</h3>${s.questions.map((q,qi)=>{
          const user = state.answers[si][qi];
          if(s.id === 'hr' || q.sampleAnswer){
            // HR: show transcript, scores, and improvement needed
            if(!user){
              return `<div class="review-card not-attempted">
                <div class="question-header">Question ${qi+1}</div>
                <div class="question-text">${q.q}</div>
                <div class="warning-message">Not attempted - Practice this question for improvement</div>
                <div class="sample-answer">Sample answer: <em>${q.sampleAnswer || ''}</em></div>
              </div>`;
            }
            const sc = user.scores || {};
            const overallScore = Math.round((sc.pronunciation + sc.accuracy + sc.clarity) / 3);
            const improvementNeeded = 100 - overallScore;
            
            // Create circular progress for this question
            const makeQuestionCircle = (score, size, color) => {
              const radius = size * 0.4;
              const circumference = radius * 2 * Math.PI;
              const offset = circumference - (score / 100) * circumference;
              return `
                <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" class="question-progress">
                  <defs>
                    <linearGradient id="circleGradient${qi}" gradientTransform="rotate(90)">
                      <stop offset="0%" stop-color="${color}"/>
                      <stop offset="100%" stop-color="${color}" stop-opacity="0.6"/>
                    </linearGradient>
                  </defs>
                  <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="#e2e8f0" stroke-width="6"/>
                  <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" 
                         stroke="url(#circleGradient${qi})" stroke-width="6"
                         stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
                         transform="rotate(-90 ${size/2} ${size/2})"/>
                  <text x="50%" y="45%" text-anchor="middle" class="score-text">${score}%</text>
                  <text x="50%" y="65%" text-anchor="middle" class="score-label">Score</text>
                </svg>`;
            };

            // Determine improvement message and color based on score
            let messageColor, improvementMessage;
            if(overallScore >= 90) {
              messageColor = '#2f855a';
              improvementMessage = 'Excellent! Keep maintaining this level.';
            } else if(overallScore >= 75) {
              messageColor = '#2b6cb0';
              improvementMessage = `Good performance! Focus on improving the remaining ${improvementNeeded}% by practicing pronunciation and clarity.`;
            } else if(overallScore >= 60) {
              messageColor = '#d69e2e';
              improvementMessage = `You're on the right track! Dedicate more practice time to improve the remaining ${improvementNeeded}%.`;
            } else {
              messageColor = '#e53e3e';
              improvementMessage = `This needs significant practice. Focus on improving ${improvementNeeded}% by working on all aspects.`;
            }

            return `<div class="review-card">
              <div class="question-header">Question ${qi+1}</div>
              <div class="question-text">${q.q}</div>
              <div class="response-section">
                <div class="response-text">
                  <strong>Your Response:</strong><br>
                  ${user.transcript || ''}
                </div>
                <div class="sample-answer">
                  <strong>Sample Answer:</strong><br>
                  ${q.sampleAnswer || ''}
                </div>
              </div>
              <div class="feedback-section">
                <div class="progress-circles">
                  ${makeQuestionCircle(overallScore, 120, messageColor)}
                  <div class="detailed-scores">
                    <div class="score-item">
                      <span class="score-label">Pronunciation:</span>
                      <span class="score-value" style="color: ${messageColor}">${sc.pronunciation || 0}%</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Accuracy:</span>
                      <span class="score-value" style="color: ${messageColor}">${sc.accuracy || 0}%</span>
                    </div>
                    <div class="score-item">
                      <span class="score-label">Clarity:</span>
                      <span class="score-value" style="color: ${messageColor}">${sc.clarity || 0}%</span>
                    </div>
                  </div>
                </div>
                <div class="improvement-message" style="color: ${messageColor}">${improvementMessage}</div>
              </div>
            </div>`;
          } else {
            const correct = q.answer;
            const userText = user==null?'<em>Not answered</em>':String.fromCharCode(65+user)+'. '+q.options[user];
            return `<div style="background:#fff;padding:.75rem;border-radius:8px;margin-bottom:.5rem;box-shadow:0 6px 18px rgba(2,6,23,0.04)">
              <div style="font-weight:600">Q${qi+1}. ${q.q}</div>
              <div style="margin-top:.5rem">Your answer: <strong>${userText}</strong></div>
              <div>Correct answer: <strong>${String.fromCharCode(65+correct)}. ${q.options[correct]}</strong></div>
              <div style="margin-top:.5rem">${user===correct ? '<span class="alert alert-success">Correct</span>' : '<span class="alert alert-error">Incorrect</span>'}</div>
            </div>`;
          }
        }).join('')}</div>`).join('')}</div>
        <div style="margin-top:1rem;display:flex;gap:.5rem;justify-content:center">
          <button id="backToResults" class="btn">Back</button>
        </div>`;

        document.getElementById('backToResults').addEventListener('click', ()=> submitAll());
      });
    }

    // Main render
    function renderQuiz(){
      const section = sections[state.sectionIndex];
      const total = section.questions.length;
      const cur = section.questions[state.qIndex];

      quizApp.innerHTML = '';

      // controls + section selector
      quizApp.appendChild(renderControls());
      quizApp.appendChild(renderSectionList());

      // header
      const header = document.createElement('div'); header.style.display='flex'; header.style.justifyContent='space-between'; header.style.alignItems='center'; header.style.marginBottom='.5rem';
      const hleft = document.createElement('strong'); hleft.textContent = `${section.title} — Question ${state.qIndex+1} / ${total}`;
      const hright = document.createElement('small'); hright.className = 'muted'; hright.textContent = `Score: ${state.scores[state.sectionIndex]}`;
      header.appendChild(hleft); header.appendChild(hright);
      quizApp.appendChild(header);

      // progress bar update
      const answered = state.answers[state.sectionIndex].filter(a=>a!=null).length;
      const pct = Math.round((answered/total)*100);
      const fillEl = quizApp.querySelector('.progress-fill'); if(fillEl) fillEl.style.width = pct + '%';

      // question
      const qdiv = document.createElement('div'); qdiv.style.marginBottom = '.75rem'; qdiv.innerHTML = `<div style="font-weight:600">${cur.q}</div>`;
      quizApp.appendChild(qdiv);

      // Render options or, for HR/sampleAnswer questions, render voice recording UI
      const opts = document.createElement('div'); opts.style.display='grid'; opts.style.gap='.5rem';
      if(section.id === 'hr' || cur.sampleAnswer){
        // Voice recording UI
        const note = document.createElement('div'); note.className='muted'; note.style.marginBottom='.5rem';
        note.textContent = 'Record your spoken answer using the microphone, then submit. You will receive a short feedback report.';
        opts.appendChild(note);

        const controls = document.createElement('div'); controls.className = 'recording-controls';
        const recBtn = document.createElement('button'); recBtn.className='recording-btn'; recBtn.innerHTML = '<span>Start Recording</span>';
        const stopBtn = document.createElement('button'); stopBtn.className='recording-btn stop'; stopBtn.innerHTML = '<span>Stop</span>'; stopBtn.disabled = true;
        const submitRec = document.createElement('button'); submitRec.className='recording-btn submit'; submitRec.innerHTML = '<span>Submit Answer</span>'; submitRec.disabled = true;
        controls.appendChild(recBtn); controls.appendChild(stopBtn); controls.appendChild(submitRec);
        opts.appendChild(controls);

        const transcriptEl = document.createElement('div'); transcriptEl.className = 'transcript-box'; transcriptEl.id = 'hrTranscript'; 
        transcriptEl.textContent = state.answers[state.sectionIndex][state.qIndex]?.transcript || 'Your answer will appear here...';
        opts.appendChild(transcriptEl);

        const feedbackEl = document.createElement('div'); feedbackEl.style.marginTop='.5rem'; feedbackEl.id = 'hrFeedback';
        if(state.answers[state.sectionIndex][state.qIndex] && state.answers[state.sectionIndex][state.qIndex].scores){
          const s = state.answers[state.sectionIndex][state.qIndex].scores;
          feedbackEl.innerHTML = hrGraphHtml(s) + `<div style="margin-top:.5rem" class="muted">Spelling/Errors: ${s.spellingErrors}, WPM: ${s.wpm}</div>`;
        }
        opts.appendChild(feedbackEl);

        // Speech recognition setup
        let recognition = null; let recogStart = 0; let lastTranscript = '';
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
        if(!SpeechRecognition){
          const warn = document.createElement('div'); warn.className='alert alert-error'; warn.textContent = 'Speech recognition not supported in this browser.'; opts.appendChild(warn);
          recBtn.disabled = true;
        } else {
          recBtn.addEventListener('click', ()=>{
            recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = true;
            recognition.continuous = true;  // Enable continuous recording
            lastTranscript = '';
            recBtn.disabled = true; stopBtn.disabled = false; submitRec.disabled = true;
            transcriptEl.innerHTML = '<div class="recording-indicator">Recording in progress...</div>';
            recogStart = Date.now();

            // Add recording animation
            const indicator = transcriptEl.querySelector('.recording-indicator');
            let dots = 0;
            const updateDots = setInterval(() => {
              if (indicator) {
                dots = (dots + 1) % 4;
                indicator.textContent = 'Recording in progress' + '.'.repeat(dots);
              }
            }, 500);

            recognition.onresult = (ev)=>{
              let interim = '';
              let final = '';
              let avgConf = 0; let confCount = 0;
              for(let i=ev.resultIndex;i<ev.results.length;i++){
                const r = ev.results[i];
                if(r.isFinal){ final += r[0].transcript + ' '; avgConf += (r[0].confidence || 0); confCount++; }
                else interim += r[0].transcript + ' ';
              }
              const displayed = (final + interim).trim();
              transcriptEl.innerHTML = `<div class="recording-indicator">Recording in progress${'.'.repeat(dots)}</div><div class="transcript-text">${displayed}</div>`;
              lastTranscript = displayed;
              // store interim confidence if available
              recognition._lastConfidence = confCount? Math.round((avgConf/confCount)*100): null;
            };
            recognition.onerror = (e)=>{ transcriptEl.textContent = 'Error: ' + e.error; stopBtn.disabled = true; recBtn.disabled = false; };
            recognition.onend = ()=>{ stopBtn.disabled = true; recBtn.disabled = false; submitRec.disabled = lastTranscript.trim()?false:true; };
            recognition.start();
          });

          stopBtn.addEventListener('click', ()=>{
            try{ recognition && recognition.stop(); }catch(e){}
          });

          submitRec.addEventListener('click', ()=>{
            const transcript = lastTranscript.trim();
            const durationSec = Math.max(1, Math.round((Date.now() - recogStart)/1000));
            // compute simple scores
            const sample = (cur.sampleAnswer || '').trim();
            const scores = computeSpeechScores(transcript, sample, durationSec, recognition && recognition._lastConfidence);
            // store into state.answers as object
            state.answers[state.sectionIndex][state.qIndex] = { transcript: transcript, duration: durationSec, rawConfidence: recognition && recognition._lastConfidence, scores: scores };
            
            // Show feedback with encouragement message
            const overallScore = Math.round((scores.pronunciation + scores.accuracy + scores.clarity) / 3);
            let message = '';
            if (overallScore >= 90) {
                message = 'Excellent! Your communication skills are outstanding! 🌟';
            } else if (overallScore >= 75) {
                message = 'Great job! Keep up the good work! 👏';
            } else if (overallScore >= 60) {
                message = 'Good progress! With more practice, you\'ll do even better! 💪';
            } else {
                message = 'Keep practicing! Every attempt makes you stronger. You\'ve got this! 🎯';
            }
            
            feedbackEl.innerHTML = hrGraphHtml(scores) + 
                `<div class="encouragement-message">${message}</div>` +
                `<div class="improvement-tips">Focus areas for improvement:
                    ${scores.pronunciation < 70 ? '• Practice clear pronunciation<br>' : ''}
                    ${scores.accuracy < 70 ? '• Work on answer accuracy<br>' : ''}
                    ${scores.clarity < 70 ? '• Improve speech clarity<br>' : ''}
                </div>`;
            
            transcriptEl.innerHTML = `<div class="final-transcript">${transcript}</div>`;
            submitRec.disabled = true;
          });
        }

      } else {
        // Render neutral-styled options with checkbox-like behavior.
        cur.options.forEach((opt,i)=>{
          const b = document.createElement('button');
          b.className = 'quiz-opt btn option-neutral';
          b.style.textAlign = 'left';
          b.style.background = '#ffffff';
          b.style.border = '1px solid #e6edf3';
          b.style.color = '#1f2937';
          b.style.boxShadow = 'none';
          b.style.padding = '0.6rem 0.75rem';
          b.style.display = 'flex';
          b.style.alignItems = 'center';
          b.style.gap = '0.6rem';
          b.dataset.index = i;

          // Create a visual checkbox element (not an actual input) so we can control state easily
          const chk = document.createElement('span');
          chk.className = 'option-checkbox';
          chk.style.width = '18px';
          chk.style.height = '18px';
          chk.style.border = '1.5px solid #cbd5e0';
          chk.style.borderRadius = '4px';
          chk.style.display = 'inline-block';
          chk.style.flex = '0 0 auto';
          chk.style.boxSizing = 'border-box';
          if(state.answers[state.sectionIndex][state.qIndex] === i){
            chk.style.background = '#2b6cb0';
            chk.innerHTML = '\u2713'; // checkmark
            chk.style.color = '#fff';
            chk.style.display = 'inline-flex';
            chk.style.alignItems = 'center';
            chk.style.justifyContent = 'center';
            chk.style.fontWeight = '700';
            chk.style.fontSize = '12px';
          }

          const txt = document.createElement('span');
          txt.textContent = `${String.fromCharCode(65+i)}. ${opt}`;
          txt.style.flex = '1';

          b.appendChild(chk);
          b.appendChild(txt);

          // If this question already has an answer, lock options (disable them)
          const alreadyAnswered = state.answers[state.sectionIndex][state.qIndex] != null;
          if(alreadyAnswered) b.disabled = true;
          if(state.finished[state.sectionIndex]) b.disabled = true;

          b.addEventListener('click', ()=>{
            // If an answer already exists, do nothing (prevent change)
            if(state.answers[state.sectionIndex][state.qIndex] != null) return;
            if(state.finished[state.sectionIndex]) return;

            // Record the answer and lock the options for this question
            state.answers[state.sectionIndex][state.qIndex] = i;
            // update numeric score for section
            state.scores[state.sectionIndex] = state.answers[state.sectionIndex].reduce((acc,ans,idx)=> acc + ((ans===section.questions[idx].answer)?1:0), 0);

            // Re-render so selected option shows checked state and buttons are disabled
            renderQuiz();
          });

          opts.appendChild(b);
        });
      }
      quizApp.appendChild(opts);

      // navigation
      const nav = document.createElement('div'); nav.style.display='flex'; nav.style.gap='.5rem'; nav.style.marginTop='1rem'; nav.style.justifyContent='space-between'; nav.style.alignItems='center';
      const navLeft = document.createElement('div');
      const prevBtn = document.createElement('button'); prevBtn.className='btn'; prevBtn.textContent='Previous'; prevBtn.disabled = state.qIndex===0; prevBtn.addEventListener('click', ()=>{ if(state.qIndex>0){ state.qIndex -=1; renderQuiz(); }});
      const nextBtn = document.createElement('button'); nextBtn.className='btn'; nextBtn.textContent='Next'; nextBtn.disabled = state.qIndex>=total-1; nextBtn.addEventListener('click', ()=>{ if(state.qIndex<total-1){ state.qIndex +=1; renderQuiz(); }});
      navLeft.appendChild(prevBtn); navLeft.appendChild(nextBtn);
      const finishBtn = document.createElement('button'); finishBtn.className='btn'; finishBtn.textContent='Finish Section'; finishBtn.addEventListener('click', finishSection);
      nav.appendChild(navLeft); nav.appendChild(finishBtn);
      quizApp.appendChild(nav);

      // feedback
      const feedback = document.createElement('div'); feedback.id='quizFeedback'; feedback.style.marginTop='.75rem';
      const userAns = state.answers[state.sectionIndex][state.qIndex];
      if(section.id === 'hr' || cur.sampleAnswer){
        if(userAns && userAns.scores){
          const s = userAns.scores;
          feedback.innerHTML = `<div class="alert alert-info">Pronunciation: ${s.pronunciation}% &nbsp; Accuracy: ${s.accuracy}% &nbsp; Clarity: ${s.clarity}%</div>`;
        } else if(userAns && userAns.transcript){
          feedback.innerHTML = `<div class="alert alert-info">Transcript recorded. Submit to get feedback.</div>`;
        }
      } else {
        if(userAns != null){
          const correct = section.questions[state.qIndex].answer;
          if(userAns === correct) feedback.innerHTML = `<div class="alert alert-success">Correct 🎉</div>`;
          else feedback.innerHTML = `<div class="alert alert-error">Incorrect — correct answer: ${String.fromCharCode(65+correct)}.</div>`;
        }
      }
      if(state.finished[state.sectionIndex]) feedback.innerHTML = `<div class="alert alert-info">Section time finished — answers locked.</div>` + feedback.innerHTML;
      quizApp.appendChild(feedback);

      // update timer display
      updateTimerDisplay();
    }

    function finishSection(){
      state.scores = sections.map((s,idx)=> state.answers[idx].reduce((acc,ans,i)=> acc + ((ans===s.questions[i].answer)?1:0), 0));
      quizApp.innerHTML = `<div style="text-align:center">
        <h3>Section Results - ${sections[state.sectionIndex].title}</h3>
        <div style="margin-top:1rem;text-align:left">${sections.map((s,idx)=>`<div style="background:#fff;padding:.75rem;border-radius:8px;margin-bottom:.5rem;box-shadow:0 6px 18px rgba(2,6,23,0.04)">
          <div style="font-weight:600">${s.title}</div>
          <div style="margin-top:.5rem">Score: <strong>${state.scores[idx]} / ${s.questions.length}</strong></div>
        </div>`).join('')}</div>
        <div style="margin-top:1rem;display:flex;gap:.5rem;justify-content:center">
          <button id="goAll" class="btn">Submit All</button>
          <button id="retakeThis" class="btn">Retake This Section</button>
        </div>
      </div>`;

      document.getElementById('retakeThis').addEventListener('click', ()=>{
        state.answers[state.sectionIndex] = Array(sections[state.sectionIndex].questions.length).fill(null);
        state.scores[state.sectionIndex] = 0;
        if(shuffleEnabled) shuffleArray(sections[state.sectionIndex].questions);
        renderQuiz();
      });
      document.getElementById('goAll').addEventListener('click', ()=> submitAll());
    }

    // Start timers and initial render
    renderQuiz();
    if(timersEnabled) startTimers();
  }

  // Video preview modal handler (static site)
  const videoModal = document.getElementById('videoModal');
  const videoFrame = document.getElementById('videoModalFrame');
  const videoModalTitle = document.getElementById('videoModalTitle');
  if(videoModal){
    document.querySelectorAll('[data-video-id]').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const id = btn.dataset.videoId;
        const title = btn.dataset.title || 'Preview';
        videoFrame.src = `https://www.youtube.com/embed/${id}?autoplay=1&rel=0`;
        videoModalTitle.textContent = title;
        videoModal.style.display = 'flex';
      });
    });

    document.getElementById('closeVideoModal').addEventListener('click', ()=>{
      videoFrame.src = '';
      videoModal.style.display = 'none';
    });
  }

  // PDF search/filter (static)
  const pdfSearch = document.getElementById('pdfSearch');
  if(pdfSearch){
    pdfSearch.addEventListener('input', ()=>{
      const q = pdfSearch.value.trim().toLowerCase();
      document.querySelectorAll('#pdfList .card').forEach(card=>{
        const text = card.textContent.trim().toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }

  // Video search (static)
  const videoSearch = document.getElementById('videoSearch');
  if(videoSearch){
    videoSearch.addEventListener('input', ()=>{
      const q = videoSearch.value.trim().toLowerCase();
      document.querySelectorAll('#videoGrid .card').forEach(card=>{
        const text = card.textContent.trim().toLowerCase();
        card.style.display = text.includes(q) ? '' : 'none';
      });
    });
  }
});
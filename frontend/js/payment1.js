class PaymentSystem {
    constructor() {
        this.overlay = null;
        this.currentPdfId = null;
        this.init();
    }

    init() {
        // Create and append payment overlay HTML (includes method selection)
        const overlayHtml = `
            <div class="payment-overlay" id="paymentOverlay">
                <div class="payment-modal">
                    <span class="close">&times;</span>
                    <h3 id="paymentTitle">Complete Payment</h3>

                    <div class="method-area" id="methodArea">
                      <button class="method-btn" data-method="PhonePe">PhonePe</button>
                      <button class="method-btn" data-method="GPay">Google Pay</button>
                      <button class="method-btn" data-method="PayTM">PayTM</button>
                    </div>

                                        <div class="qr-area" id="qrArea" style="display:none;">
                                                <p id="qrNote">Scan QR code to pay or open UPI app</p>
                                                <div id="qrCode"></div>
                                                <div class="payment-amount">₹99.00</div>
                                                <div class="countdown" id="countdown">Waiting: 30s</div>
                        <!-- Removed "Open in selected app" and "Choose a different method" per request -->
                                        </div>

                                        <div class="transaction-area" id="transactionArea" style="display:none;">
                                                <label for="transactionId">Enter UPI Transaction ID:</label>
                                                <input type="text" id="transactionId" placeholder="Enter transaction ID after payment">
                                                <div class="spinner" id="verifySpinner"></div>
                                                <button class="btn-verify" id="verifyBtn">Verify Payment</button>
                                        </div>
                                        <div class="error-msg" id="errorMsg"></div>
                                        <div class="success-msg" id="successMsg"></div>
                                        <div style="display:none;margin-top:.5rem" id="modalBackWrap">
                                            <button id="modalBackBtn" class="modal-back-action">Back</button>
                                        </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', overlayHtml);
        
        this.overlay = document.getElementById('paymentOverlay');
        this.bindEvents();
        // When the payment system initializes, update any cards that were
        // previously paid (stored in localStorage) so their Purchase buttons
        // become Open PDF buttons immediately on page load / after redirect.
        this.updatePaidButtons();
    }

    bindEvents() {
        // Close button event
        const closeBtn = this.overlay.querySelector('.close');
        closeBtn.addEventListener('click', () => this.hidePaymentOverlay());

        // Click outside modal to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hidePaymentOverlay();
            }
        });

        // Verify button click
        const verifyBtn = document.getElementById('verifyBtn');
        verifyBtn.addEventListener('click', () => this.verifyPayment());
        // Modal back action (shown after successful verify)
        const modalBack = document.getElementById('modalBackBtn');
        modalBack.addEventListener('click', () => this._onModalBack());

        // When user selects a method
        this.overlay.querySelectorAll('.method-btn').forEach(mb => {
            mb.addEventListener('click', (e) => {
                const method = mb.getAttribute('data-method');
                this.selectMethod(method);
            });
        });

        // Bind purchase buttons (explicit class)
        document.querySelectorAll('.purchase-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const pdfId = btn.getAttribute('data-pdf-id') || null;
                // Try to infer company title from closest card if pdfId missing
                const card = btn.closest('.card');
                const title = card ? (card.querySelector('h4') && card.querySelector('h4').textContent.trim()) : pdfId;
                this.showPaymentOverlay(title);
            });
        });

        // Support legacy 'Parches' anchors: event delegation
        document.body.addEventListener('click', (e) => {
            const el = e.target;
            if ((el.tagName === 'A' || el.tagName === 'BUTTON') && el.classList.contains('btn')) {
                const txt = el.textContent.trim().toLowerCase();
                if (txt.includes('parch') || txt.includes('purchase')) {
                    e.preventDefault();
                    const card = el.closest('.card');
                    const title = card ? (card.querySelector('h4') && card.querySelector('h4').textContent.trim()) : null;
                    this.showPaymentOverlay(title);
                }
            }
        });
    }

    showPaymentOverlay(pdfId) {
        this.currentPdfId = pdfId;
        this.overlay.style.display = 'flex';
        
        // Hide method selection and show QR directly
        document.getElementById('methodArea').style.display = 'none';
        document.getElementById('qrArea').style.display = 'block';
        document.getElementById('qrNote').textContent = 'Scan QR code to pay ₹99';
        
        // Generate QR code
        const qrContainer = document.getElementById('qrCode');
        qrContainer.innerHTML = '';
        const qrImage = document.createElement('img');
        qrImage.src = 'assets/img/upi_qr_durgesh_99.png';
        qrImage.alt = 'QR Code';
        qrImage.style.width = '300px';
        qrImage.style.height = 'auto';
        qrContainer.appendChild(qrImage);

        // Reset form state
        document.getElementById('transactionId').value = '';
        document.getElementById('errorMsg').style.display = 'none';
        document.getElementById('successMsg').style.display = 'none';
        document.getElementById('verifySpinner').style.display = 'none';
        
        // Update title to include PDF/company name if available
        const titleEl = document.getElementById('paymentTitle');
        if (this.currentPdfId) titleEl.textContent = `Buy — ${this.currentPdfId}`;
        else titleEl.textContent = 'Buy — PDF';
        
        // Start countdown to show transaction ID input
        this._startCountdown(10);
    }

    showMethodSelection() {
        document.getElementById('methodArea').style.display = 'flex';
        document.getElementById('qrArea').style.display = 'none';
        document.getElementById('qrCode').innerHTML = '';
        this.selectedMethod = null;
    }

    hidePaymentOverlay() {
        this.overlay.style.display = 'none';
        this.currentPdfId = null;
    }

    generateQRCode(method) {
        const qrContainer = document.getElementById('qrCode');
        qrContainer.innerHTML = ''; // Clear previous QR code

        // Use the exact UPI link format
		const qrImage = document.createElement('img');
        qrImage.src = 'backend/study-website/assets/img/upi_qr_durgesh_99.png'; // Yahan apna QR image URL ya file daalein
        qrImage.alt = 'QR Code';
        qrContainer.appendChild(qrImage);
        const upiLink = 'backend/study-website/assets/img/upi_qr_durgesh_99.png';
        // store for open intent
        this.lastUpiLink = upiLink;

        if (window.QRCode) {
            new QRCode(qrContainer, {
                text: upiLink,
                width: 300,
                height: 200,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H  // Highest error correction level
            });
        } else {
            qrContainer.textContent = upiLink;
        }
    }

    showVerificationModal(title) {
        this.currentPdfId = title;
        this.overlay.style.display = 'flex';
        // Show only transaction area
        document.getElementById('methodArea').style.display = 'none';
        document.getElementById('qrArea').style.display = 'none';
        document.getElementById('transactionArea').style.display = 'block';
        document.getElementById('modalBackWrap').style.display = 'none';
        // Reset messages
        document.getElementById('errorMsg').style.display = 'none';
        document.getElementById('successMsg').style.display = 'none';
        document.getElementById('verifySpinner').style.display = 'none';
        document.getElementById('transactionId').value = '';
        document.getElementById('transactionId').focus();
        // Update title
        const titleEl = document.getElementById('paymentTitle');
        titleEl.textContent = title ? `Verify Payment — ${title}` : 'Verify Payment';
    }

    selectMethod(method) {
        this.selectedMethod = method;
        // hide method list and show qr
        document.getElementById('methodArea').style.display = 'none';
        document.getElementById('qrArea').style.display = 'block';
        document.getElementById('qrNote').textContent = `Use ${method} or scan QR to pay ₹99.`;
        this.generateQRCode(method);
        // start 30s countdown then reveal transaction input
        this._startCountdown(30);
    }

    _startCountdown(seconds) {
        const countdownEl = document.getElementById('countdown');
        const txArea = document.getElementById('transactionArea');
        txArea.style.display = 'none';
        countdownEl.style.display = 'block';
        let s = seconds;
        countdownEl.textContent = `Waiting: ${s}s`;
        if (this._countdownInterval) clearInterval(this._countdownInterval);
        this._countdownInterval = setInterval(() => {
            s -= 1;
            if (s <= 0) {
                clearInterval(this._countdownInterval);
                countdownEl.style.display = 'none';
                txArea.style.display = 'block';
                document.getElementById('transactionId').focus();
            } else {
                countdownEl.textContent = `Waiting: ${s}s`;
            }
        }, 1000);
    }

    openUpiIntent() {
        // Attempt to open UPI link directly - mobile browsers will forward to apps that register UPI
        if (this.lastUpiLink) {
            window.location.href = this.lastUpiLink;
        }
    }

    async verifyPayment() {
        const transactionId = document.getElementById('transactionId').value.trim();
        const errorMsg = document.getElementById('errorMsg');
        const successMsg = document.getElementById('successMsg');
        const spinner = document.getElementById('verifySpinner');
        
        if (!transactionId) {
            errorMsg.textContent = 'Please enter the transaction ID';
            errorMsg.style.display = 'block';
            return;
        }

        // Show spinner, hide messages
        spinner.style.display = 'inline-block';
        errorMsg.style.display = 'none';
        successMsg.style.display = 'none';

        try {
            // For this demo, we'll treat any entered transactionId as valid.
            // In production you MUST verify the transaction server-side.
            const company = this._companyFromTitle(this.currentPdfId || '');

            // Try to find a data-pdf-id for the company/card so we can persist
            // a stable paid flag. If not found, fall back to a safe string.
            const pdfId = this._getPdfIdForCompany(company) || (this.currentPdfId || 'pdf').replace(/\s+/g, '-').toLowerCase();

            // Enforce globally: a transaction ID can be used only once across all companies.
            // Check all saved paid_* entries; if any entry already used this transactionId,
            // reject and show an error.
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (!key || !key.startsWith('paid_')) continue;
                try {
                    const stored = JSON.parse(localStorage.getItem(key));
                    if (!stored || !stored.transactionId) continue;
                    if (stored.transactionId === transactionId) {
                        // Optionally include which stored key used it (helps debugging)
                        const usedBy = key.slice('paid_'.length) || 'another purchase';
                        errorMsg.textContent = `This transaction ID has already been used (${usedBy}). Please Pay 99 and use the transaction ID.`;
                        errorMsg.style.display = 'block';
                        spinner.style.display = 'none';
                        return;
                    }
                } catch (e) {
                    // ignore malformed entries
                }
            }

            // Persist paid marker in localStorage so that on reload the page
            // updates the UI to show "Open PDF" instead of Purchase.
            localStorage.setItem('paid_' + pdfId, JSON.stringify({
                transactionId: transactionId,
                method: this.selectedMethod || null,
                paidAt: Date.now()
            }));

            // Indicate success to user
            successMsg.textContent = 'Payment recorded! Redirecting back...';
            successMsg.style.display = 'block';

            // Brief delay so user sees success, then reload the page (acts as redirect)
            setTimeout(() => {
                // Refresh the page (this will run updatePaidButtons on init)
                try { window.location.href = window.location.pathname; } catch (e) { window.location.reload(); }
            }, 1000);
        } catch (error) {
            errorMsg.textContent = 'An error occurred. Please try again.';
            errorMsg.style.display = 'block';
        } finally {
            spinner.style.display = 'none';
        }
    }

    // Find the data-pdf-id attribute for a card matching the given company/title
    _getPdfIdForCompany(company) {
        if (!company) return null;
        const cards = document.querySelectorAll('.card');
        let found = null;
        cards.forEach(c => {
            const h4 = c.querySelector('h4');
            if (!h4) return;
            const text = h4.textContent.trim();
            if (text.toLowerCase().startsWith(company.toLowerCase())) {
                const purchaseBtn = c.querySelector('.purchase-btn');
                if (purchaseBtn) found = purchaseBtn.getAttribute('data-pdf-id');
            }
        });
        return found;
    }

    // Convert any previously-paid cards into Open PDF buttons on page load
    updatePaidButtons() {
        document.querySelectorAll('.card').forEach(card => {
            const purchaseBtn = card.querySelector('.purchase-btn');
            if (!purchaseBtn) return;
            const pdfId = purchaseBtn.getAttribute('data-pdf-id') || '';
            if (!pdfId) return;
            const key = 'paid_' + pdfId;
            if (localStorage.getItem(key)) {
                // Update the button to Open PDF
                this._makeOpenPdf(purchaseBtn, pdfId, card);
            }
        });
    }

    _makeOpenPdf(button, pdfId, card) {
        button.textContent = 'Open PDF';
        button.classList.remove('purchase-btn');
        button.classList.add('open-pdf-btn');
        button.style.background = '#2563eb';
        button.style.color = '#fff';
        // Navigate to company-specific PDF page
        button.onclick = () => {
            try {
                // Extract company name from pdfId or card title
                let company = '';
                if (pdfId) {
                    company = pdfId.split('-')[0]; // e.g., "capgemini-1" -> "capgemini"
                } else {
                    const title = card.querySelector('h4')?.textContent.trim() || '';
                    company = this._companyFromTitle(title).toLowerCase();
                }
                if (company) {
                    window.location.href = `company-pdfs/pdf-${company}.html`;
                }
            } catch (e) {
                console.error(e);
            }
        };
    }

    _companyFromTitle(title) {
        if (!title) return '';
        // split on long dash/emdash or regular hyphen-like char
        const parts = title.split('—');
        if (parts.length > 1) return parts[0].trim();
        // try hyphen
        const parts2 = title.split('-');
        if (parts2.length > 1) return parts2[0].trim();
        // fallback: first word(s) till first space with uppercase
        return title.split('\n')[0].trim();
    }

    _onModalBack() {
        // when modal Back is clicked, update the originating card's Preview button to Open PDF
        // try to find a card that matches the paid company/title
        const company = this._lastPaidCompany || this._companyFromTitle(this.currentPdfId || '');
        if (!company) {
            this.hidePaymentOverlay();
            return;
        }

        // find card by matching the h4 text starting with company name
        const cards = document.querySelectorAll('.card');
        let targetCard = null;
        cards.forEach(c => {
            const h4 = c.querySelector('h4');
            if (!h4) return;
            const text = h4.textContent.trim();
            if (text.toLowerCase().startsWith(company.toLowerCase())) {
                targetCard = c;
            }
        });

        if (!targetCard) {
            // fallback: use the card whose title contains the currentPdfId
            cards.forEach(c => {
                const h4 = c.querySelector('h4');
                if (!h4) return;
                const text = h4.textContent.trim();
                if (this.currentPdfId && text.includes(this.currentPdfId)) targetCard = c;
            });
        }

        if (targetCard) {
            // find preview button
            const previewBtn = Array.from(targetCard.querySelectorAll('button')).find(b => b.textContent.trim().toLowerCase().includes('preview'));
            if (previewBtn) {
                previewBtn.textContent = 'Open PDF';
                previewBtn.onclick = () => {
                    // Show verification modal instead of direct download
                    const title = targetCard.querySelector('h4')?.textContent.trim() || '';
                    this.showVerificationModal(title);
                };
                // also change style to indicate primary
                previewBtn.style.background = '#2563eb';
                previewBtn.style.color = '#fff';
            }
        }

        this.hidePaymentOverlay();
    }
}

// Initialize payment system when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.paymentSystem = new PaymentSystem();
});
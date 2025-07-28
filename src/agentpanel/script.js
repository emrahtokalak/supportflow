class ChatInterface {
    constructor() {
        this.apiBaseUrl = window.location.origin; // Same origin as web interface
        this.currentSessionId = null;
        this.isConnected = false;
        this.messageQueue = [];
        
        this.initializeElements();
        this.attachEventListeners();
        this.checkConnection();
        this.showCustomerInfoModal();
    }
    
    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.sessionStatusBtn = document.getElementById('sessionStatusBtn');
        this.newSessionBtn = document.getElementById('newSessionBtn');
        this.escalateBtn = document.getElementById('escalateBtn');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.connectionText = document.getElementById('connectionText');
        this.sessionInfo = document.getElementById('sessionInfo');
        this.sessionId = document.getElementById('sessionId');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Modals
        this.sessionModal = document.getElementById('sessionModal');
        this.customerInfoModal = document.getElementById('customerInfoModal');
        this.customerInfoForm = document.getElementById('customerInfoForm');
    }
    
    attachEventListeners() {
        // Send message
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Quick actions
        document.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
        
        // Header controls
        this.sessionStatusBtn.addEventListener('click', () => this.showSessionStatus());
        this.newSessionBtn.addEventListener('click', () => this.startNewSession());
        this.escalateBtn.addEventListener('click', () => this.escalateToHuman());
        
        // Customer info form
        this.customerInfoForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.startNewSessionWithInfo();
        });
        
        document.getElementById('skipCustomerInfo').addEventListener('click', () => {
            this.startNewSessionWithInfo(null);
        });
        
        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });
        
        // Close modals on backdrop click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });
    }
    
    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateConnectionStatus(true, data.message);
            } else {
                this.updateConnectionStatus(false, data.message);
            }
        } catch (error) {
            this.updateConnectionStatus(false, 'API bağlantısı kurulamadı');
        }
    }
    
    updateConnectionStatus(connected, message) {
        this.isConnected = connected;
        this.connectionStatus.className = `fas fa-circle status-indicator ${connected ? 'connected' : 'disconnected'}`;
        this.connectionText.textContent = message;
        
        // Enable/disable controls based on connection
        this.sendBtn.disabled = !connected;
        this.messageInput.disabled = !connected;
    }
    
    showCustomerInfoModal() {
        this.showModal(this.customerInfoModal);
    }
    
    showModal(modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    closeModal(modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
    
    async startNewSessionWithInfo(customerInfo = null) {
        this.closeModal(this.customerInfoModal);
        
        if (customerInfo === null) {
            // Get form data if not skipped
            const formData = new FormData(this.customerInfoForm);
            customerInfo = {};
            for (let [key, value] of formData.entries()) {
                if (value.trim()) {
                    customerInfo[key] = value.trim();
                }
            }
            
            if (Object.keys(customerInfo).length === 0) {
                customerInfo = null;
            }
        }
        
        this.currentSessionId = null;
        this.updateSessionInfo();
        this.clearChat();
        
        // Add welcome message
        this.addMessage('bot', 'Merhaba! Size nasıl yardımcı olabilirim?');
        
        console.log('Yeni session başlatılıyor:', customerInfo);
    }
    
    startNewSession() {
        this.showCustomerInfoModal();
    }
    
    clearChat() {
        const messages = this.chatMessages.querySelectorAll('.message');
        messages.forEach(msg => msg.remove());
    }
    
    updateSessionInfo() {
        if (this.currentSessionId) {
            this.sessionInfo.style.display = 'block';
            this.sessionId.textContent = `Session: ${this.currentSessionId.substring(0, 8)}...`;
        } else {
            this.sessionInfo.style.display = 'none';
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId,
                    model: "gemma3:latest",
                    customer_info: this.getCustomerInfoFromForm()
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'API hatası');
            }
            
            const data = await response.json();
            
            // Update session info
            if (data.session_id && data.session_id !== this.currentSessionId) {
                this.currentSessionId = data.session_id;
                this.updateSessionInfo();
            }
            
            // Add bot response
            this.addMessage('bot', data.response, {
                category: data.category,
                requiresHuman: data.requires_human,
                escalationReason: data.escalation_reason,
                turnCount: data.turn_count
            });
            
            // Show escalation button if needed
            if (data.requires_human) {
                this.escalateBtn.style.display = 'block';
                this.showEscalationNotice(data.escalation_reason);
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessage('bot', `Üzgünüm, bir hata oluştu: ${error.message}`, { isError: true });
        } finally {
            this.showLoading(false);
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }
    
    getCustomerInfoFromForm() {
        if (!this.currentSessionId) {
            // Only for first message
            const formData = new FormData(this.customerInfoForm);
            const customerInfo = {};
            for (let [key, value] of formData.entries()) {
                if (value.trim()) {
                    customerInfo[key] = value.trim();
                }
            }
            return Object.keys(customerInfo).length > 0 ? customerInfo : null;
        }
        return null;
    }
    
    addMessage(sender, content, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = `${sender}-avatar`;
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        // Add metadata if available
        if (metadata.category || metadata.turnCount) {
            const metaDiv = document.createElement('div');
            metaDiv.className = 'message-meta';
            
            if (metadata.category) {
                const categoryBadge = document.createElement('span');
                categoryBadge.className = 'category-badge';
                categoryBadge.textContent = metadata.category;
                metaDiv.appendChild(categoryBadge);
            }
            
            if (metadata.turnCount) {
                const turnInfo = document.createElement('span');
                turnInfo.textContent = `Turn: ${metadata.turnCount}`;
                metaDiv.appendChild(turnInfo);
            }
            
            messageContent.appendChild(metaDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showEscalationNotice(reason) {
        const noticeDiv = document.createElement('div');
        noticeDiv.className = 'escalation-notice';
        noticeDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>Bu konuda insan temsilci desteği gerekebilir. Sebep: ${reason}</span>
        `;
        this.chatMessages.appendChild(noticeDiv);
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
    
    async showSessionStatus() {
        if (!this.currentSessionId) {
            alert('Aktif session bulunmuyor.');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/session/${this.currentSessionId}/status`);
            if (!response.ok) {
                throw new Error('Session bilgisi alınamadı');
            }
            
            const data = await response.json();
            
            const details = document.getElementById('sessionDetails');
            details.innerHTML = `
                <div class="form-group">
                    <label>Session ID:</label>
                    <p>${data.session_id}</p>
                </div>
                <div class="form-group">
                    <label>Durum:</label>
                    <p>${data.is_active ? 'Aktif' : 'Pasif'}</p>
                </div>
                <div class="form-group">
                    <label>Turn Sayısı:</label>
                    <p>${data.turn_count}</p>
                </div>
                <div class="form-group">
                    <label>İnsan Desteği:</label>
                    <p>${data.requires_human ? 'Gerekli' : 'Gerekli değil'}</p>
                </div>
                ${data.escalation_reason ? `
                <div class="form-group">
                    <label>Escalation Sebebi:</label>
                    <p>${data.escalation_reason}</p>
                </div>
                ` : ''}
                <div class="form-group">
                    <label>Session Süresi:</label>
                    <p>${data.session_duration_minutes} dakika</p>
                </div>
                <div class="form-group">
                    <label>Son Aktivite:</label>
                    <p>${new Date(data.last_activity).toLocaleString('tr-TR')}</p>
                </div>
            `;
            
            this.showModal(this.sessionModal);
            
        } catch (error) {
            console.error('Session status error:', error);
            alert('Session bilgisi alınamadı: ' + error.message);
        }
    }
    
    async escalateToHuman() {
        if (!this.currentSessionId) {
            alert('Aktif session bulunmuyor.');
            return;
        }
        
        const reason = prompt('Escalation sebebini belirtiniz:');
        if (!reason) return;
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/session/${this.currentSessionId}/escalate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    reason: reason
                })
            });
            
            if (!response.ok) {
                throw new Error('Escalation işlemi başarısız');
            }
            
            this.addMessage('bot', 'Bu görüşme insan temsilci desteği için işaretlendi. En kısa sürede bir temsilcimiz sizinle iletişime geçecektir.', { isEscalation: true });
            this.escalateBtn.style.display = 'none';
            
        } catch (error) {
            console.error('Escalation error:', error);
            alert('Escalation işlemi başarısız: ' + error.message);
        }
    }
}

// Initialize the chat interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});

// Health check interval
setInterval(async () => {
    const chatInterface = window.chatInterface;
    if (chatInterface) {
        await chatInterface.checkConnection();
    }
}, 30000); // Check every 30 seconds

/**
 * Main Loading Screen Logic
 * Handles status message rotation, progress bar animation, and success transition
 */

class LoadingScreen {
    constructor() {
        this.statusMessages = [
            "✦ Checking your configuration…",
            "✦ Validating prompt structure…",
            "✦ Preparing voice selection…",
            "✦ Allocating AI resources…",
            "✦ Starting agent training…"
        ];
        
        this.currentMessageIndex = 0;
        this.messageRotationInterval = 2500; // 2.5 seconds
        this.progressDuration = 14000; // 14 seconds
        this.startTime = Date.now();
        
        this.statusMessageEl = document.getElementById('statusMessage');
        this.progressBarEl = document.getElementById('progressBar');
        this.successOverlay = document.getElementById('successOverlay');
        this.orbCore = document.querySelector('.orb-core');
        
        this.init();
    }
    
    init() {
        // Start status message rotation
        this.rotateStatusMessages();
        
        // Monitor progress completion
        this.monitorProgress();
    }
    
    rotateStatusMessages() {
        setInterval(() => {
            this.currentMessageIndex = (this.currentMessageIndex + 1) % this.statusMessages.length;
            this.updateStatusMessage();
        }, this.messageRotationInterval);
    }
    
    updateStatusMessage() {
        // Fade out
        this.statusMessageEl.style.opacity = '0';
        this.statusMessageEl.style.transform = 'translateY(5px)';
        
        setTimeout(() => {
            // Update text
            this.statusMessageEl.textContent = this.statusMessages[this.currentMessageIndex];
            
            // Fade in
            this.statusMessageEl.style.opacity = '1';
            this.statusMessageEl.style.transform = 'translateY(0)';
        }, 300);
    }
    
    monitorProgress() {
        const checkProgress = setInterval(() => {
            const elapsed = Date.now() - this.startTime;
            const progress = Math.min((elapsed / this.progressDuration) * 100, 100);
            
            // Progress bar is animated via CSS, but we check when it's complete
            if (progress >= 99.5) {
                clearInterval(checkProgress);
                setTimeout(() => this.showSuccess(), 300);
            }
        }, 100);
    }
    
    showSuccess() {
        // Change orb to success state
        this.orbCore.classList.add('success');
        
        // Update status message to success
        this.statusMessageEl.style.opacity = '0';
        setTimeout(() => {
            this.statusMessageEl.textContent = "✓ Initialization Complete! Launching your AI Training environment…";
            this.statusMessageEl.style.color = '#10b981';
            this.statusMessageEl.style.fontWeight = '600';
            this.statusMessageEl.style.opacity = '1';
        }, 300);
        
        // Show success overlay after brief pause
        setTimeout(() => {
            this.successOverlay.classList.add('active');
            
            // Simulate redirect after 1.5 seconds
            setTimeout(() => {
                this.redirectToTraining();
            }, 1500);
        }, 1500);
    }
    
    redirectToTraining() {
        // In a real implementation, this would navigate to the training screen
        // For demo purposes, we'll show a message in console and could redirect to another page
        
        console.log('Redirecting to AI Training Screen...');
        
        // Example redirect (uncomment and modify URL as needed):
        // window.location.href = '/training';
        
        // For demo, we'll just log the completion
        document.querySelector('.success-text').textContent = 'Demo Complete - Training screen would load here';
    }
}

// Initialize loading screen when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new LoadingScreen();
});

// Add smooth transitions to status message
document.addEventListener('DOMContentLoaded', () => {
    const statusMessage = document.getElementById('statusMessage');
    if (statusMessage) {
        statusMessage.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }
});

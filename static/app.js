// Global health score update function
async function updateGlobalHealthScore() {
    try {
        const response = await fetch('/api/health-score');
        const data = await response.json();
        if (data.health_score !== undefined) {
            const scoreElement = document.getElementById('gaugeValue');
            const fillElement = document.getElementById('gaugeFill');
            if (scoreElement && fillElement) {
                scoreElement.textContent = data.health_score;
                const rotation = (data.health_score / 100) * 180 - 90;
                fillElement.style.transform = `rotate(${rotation}deg)`;
            }
        }
    } catch (error) {
        console.error('Error updating health score:', error);
    }
}

// Initialize health score on page load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('gaugeValue')) {
        updateGlobalHealthScore();
    }
});


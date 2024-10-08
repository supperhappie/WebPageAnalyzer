document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('crawl-form');
    const urlInput = document.getElementById('url-input');
    const resultDiv = document.getElementById('result');
    const descriptionP = document.getElementById('description');
    const keywordsP = document.getElementById('keywords');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const loadingDiv = document.getElementById('loading');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) {
            showError('Please enter a valid URL');
            return;
        }

        showLoading();

        try {
            const response = await fetch('/crawl', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            const data = await response.json();
            console.log("Received data:", data);

            if (response.ok) {
                showResult(data.description, data.keywords);
            } else {
                showError(data.error || 'An error occurred while processing your request');
            }
        } catch (error) {
            console.error("Fetch error:", error);
            showError('An error occurred while communicating with the server');
        } finally {
            hideLoading();
        }
    });

    function showResult(description, keywords) {
        descriptionP.textContent = description;
        keywordsP.textContent = keywords;
        resultDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');
    }

    function showLoading() {
        loadingDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
    }

    function hideLoading() {
        loadingDiv.classList.add('hidden');
    }
});

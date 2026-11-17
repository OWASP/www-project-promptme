// Question submission and answer handling
document.getElementById('questionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const question = document.getElementById('question').value;
    const answerDiv = document.getElementById('answer');
    const loadingDiv = document.getElementById('loading');

    // Show loading indicator
    loadingDiv.style.display = 'block';
    answerDiv.innerHTML = ''; // Clear previous answer

    try {
        // Make the POST request to the Flask backend
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        const result = await response.json();

        if (response.ok) {
            // Start the typing effect
            typeText(answerDiv, result.answer);
        } else {
            answerDiv.innerHTML = `<strong>Error:</strong><p>${result.error}</p>`;
        }
    } catch (error) {
        answerDiv.innerHTML = `<strong>Error:</strong><p>Something went wrong. Please try again later.</p>`;
    } finally {
        // Hide loading indicator
        loadingDiv.style.display = 'none';
    }
});

// Typing effect function
function typeText(element, text, speed = 30) {
    element.innerHTML = ''; // Clear previous text
    let i = 0;

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            element.scrollTop = element.scrollHeight; // Auto-scroll for long answers
            setTimeout(type, speed);
        }
    }

    type();
}

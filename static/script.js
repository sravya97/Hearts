document.getElementById('heartButton').addEventListener('click', function() {
    // Make an AJAX request to the server to get a new message
    fetch('/get_message')
        .then(response => response.json())
        .then(data => {
            // Update the UI with the received content
            if (data.category_id !== null && data.content !== null) {
                document.getElementById('messageDisplay').innerHTML = `
                    <p><strong>Category:</strong> ${data.category_id}</p>
                    <p><strong>Message:</strong> ${data.content}</p>
                `;
            } else {
                document.getElementById('messageDisplay').innerHTML = `<p>${data.content}</p>`;
            }
        })
        .catch(error => console.error('Error fetching new message:', error));
});

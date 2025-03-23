document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation to attach the listener to a parent element (e.g., #cart-items)
    const cartItemsContainer = document.getElementById('cart-items');

    cartItemsContainer.addEventListener('click', function(event) {
        // Check if the clicked element has the class 'remove-item' (i.e., it's a remove button)
        if (event.target && event.target.classList.contains('remove-item')) {
            const itemId = event.target.getAttribute('data-id');  // Get the item ID from the button's data-id attribute
            removeItemFromCart(itemId);  // Call function to remove the item from the cart
        }
    });
});

function removeItemFromCart(itemId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // Get the CSRF token

    fetch('/remove-from-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // Include CSRF token in the request headers
        },
        body: JSON.stringify({ 'item_id': itemId })  // Send the item ID in the request body
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();  // Reload the page if the item was successfully removed
        } else {
            console.error('Error:', data.message);  // Log an error if the item was not found
        }
    })
    .catch(error => console.error('Error removing item:', error));
}

// Cart state
let cart = [];

// DOM elements
const cartCountEl = document.getElementById('cart-count');
const cartItemsEl = document.getElementById('cart-items');
const cartTotalEl = document.getElementById('cart-total');
const checkoutBtn = document.getElementById('checkout-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    renderCart();
    setupAddToCartButtons();
});

// Load cart from localStorage
function loadCart() {
    const saved = localStorage.getItem('techstore_cart');
    if (saved) {
        cart = JSON.parse(saved);
    }
}

// Save cart to localStorage
function saveCart() {
    localStorage.setItem('techstore_cart', JSON.stringify(cart));
}

// Add to cart
function addToCart(id, name, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id, name, price, quantity: 1 });
    }
    saveCart();
    renderCart();
    showNotification(`${name} added to cart!`);
}

// Remove from cart
function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    renderCart();
    showNotification('Item removed from cart.');
}

// Update quantity
function updateQuantity(id, delta) {
    const item = cart.find(item => item.id === id);
    if (item) {
        item.quantity += delta;
        if (item.quantity <= 0) {
            removeFromCart(id);
            return;
        }
        saveCart();
        renderCart();
    }
}

// Render cart UI
function renderCart() {
    // Update cart count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCountEl.textContent = totalItems;

    // Update cart items
    if (cart.length === 0) {
        cartItemsEl.innerHTML = '<p class="empty-cart">Your cart is empty.</p>';
        cartTotalEl.textContent = '0';
        checkoutBtn.disabled = true;
        return;
    }

    let html = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        html += `
            <div class="cart-item">
                <div>
                    <h4>${item.name}</h4>
                    <p>${item.price} DH × ${item.quantity}</p>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <button class="qty-btn" data-id="${item.id}" data-delta="-1">−</button>
                    <span>${item.quantity}</span>
                    <button class="qty-btn" data-id="${item.id}" data-delta="1">+</button>
                    <button class="remove-btn" data-id="${item.id}" style="margin-left: 15px; color: #ff4757;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });

    cartItemsEl.innerHTML = html;
    cartTotalEl.textContent = total;
    checkoutBtn.disabled = false;

    // Attach event listeners to new buttons
    document.querySelectorAll('.qty-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            const delta = parseInt(e.target.dataset.delta);
            updateQuantity(id, delta);
        });
    });

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            removeFromCart(id);
        });
    });
}

// Setup "Add to Cart" buttons
function setupAddToCartButtons() {
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const id = parseInt(e.target.dataset.id);
            const name = e.target.dataset.name;
            const price = parseInt(e.target.dataset.price);
            addToCart(id, name, price);
        });
    });
}

// Checkout button
checkoutBtn.addEventListener('click', () => {
    if (cart.length === 0) return;
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    alert(`Thank you for your order!\nTotal: ${total} DH\n\nThis is a demo. In a real store, you would proceed to payment.`);
    cart = [];
    saveCart();
    renderCart();
    showNotification('Order placed successfully!');
});

// Notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: fadeInOut 3s ease;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Add CSS for animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        10% { opacity: 1; transform: translateY(0); }
        90% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }
    .qty-btn {
        background: #f1f3f4;
        border: none;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        font-weight: bold;
        cursor: pointer;
    }
    .qty-btn:hover {
        background: #ddd;
    }
`;
document.head.appendChild(style);
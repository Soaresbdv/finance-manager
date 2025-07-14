// Elementos DOM
const elements = {
    login: {
        container: document.getElementById('loginContainer'),
        form: document.getElementById('loginForm'),
        email: document.getElementById('loginEmail'),
        password: document.getElementById('loginPassword'),
        message: document.getElementById('loginMessage')
    },
    register: {
        container: document.getElementById('registerContainer'),
        form: document.getElementById('registerForm'),
        email: document.getElementById('registerEmail'),
        password: document.getElementById('registerPassword'),
        message: document.getElementById('registerMessage')
    },
    buttons: {
        showRegister: document.getElementById('showRegister'),
        showLogin: document.getElementById('showLogin'),
        logout: document.getElementById('logoutBtn')
    }
};

// Funções compartilhadas
const utils = {
    toggleForms: (hide, show) => {
        hide.classList.add('hidden');
        show.classList.remove('hidden');
    },
    handleResponse: (response, messageEl, successMessage) => {
        if (response.ok) {
            messageEl.textContent = successMessage;
            messageEl.className = "message success";
            return true;
        }
        throw new Error(response.error || "Operação falhou");
    }
};

// Event Listeners
elements.buttons.showRegister?.addEventListener('click', (e) => {
    e.preventDefault();
    utils.toggleForms(elements.login.container, elements.register.container);
});

elements.buttons.showLogin?.addEventListener('click', (e) => {
    e.preventDefault();
    utils.toggleForms(elements.register.container, elements.login.container);
});

elements.login.form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: elements.login.email.value,
                password: elements.login.password.value
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.token);
            // Envia o token como cookie via fetch antes do redirecionamento
            await fetch('/set-token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${data.token}`
                }
            });
            window.location.href = "/dashboard";
        }
    } catch (error) {
        elements.login.message.textContent = error.message;
        elements.login.message.className = "message error";
    }
});

elements.register.form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: elements.register.email.value,
                password: elements.register.password.value
            })
        });
        
        if (utils.handleResponse(response, elements.register.message, "Registro concluído!")) {
            utils.toggleForms(elements.register.container, elements.login.container);
        }
    } catch (error) {
        elements.register.message.textContent = error.message;
        elements.register.message.className = "message error";
    }
});

elements.buttons.logout?.addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = "/";
});
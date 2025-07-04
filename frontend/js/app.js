const { createApp, ref } = Vue;

createApp({
    setup() {
        const email = ref('')
        const password = ref('')
        const message = ref('')

        const register = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: email.value,
                        password: password.value
                    })
                })
                const data = await response.json()
                message.value = data.message || 'Registro realizado!'
            } catch (error) {
                message.value = 'Erro no registro: ' + error.message
            }
        }

        return { email, password, message, register }
    }
}).mount('#app')
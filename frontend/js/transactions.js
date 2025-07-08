document.addEventListener('DOMContentLoaded', () => {
    const app = Vue.createApp({
        data() {
            return {
                isAuthenticated: false,
                showRegister: false,
                email: '',
                password: '',
                registerEmail: '',
                registerPassword: '',
                registerName: '',
                transactions: [],
                categories: {
                    'food': 'Alimentação',
                    'transport': 'Transporte', 
                    'housing': 'Moradia',
                    'entertainment': 'Lazer',
                    'health': 'Saúde',
                    'education': 'Educação',
                    'other': 'Outros'
                },
                
                filterCategory: '',
                filterStartDate: '',
                filterEndDate: '',
                filterType: '',  
                newDescription: '',
                newAmount: '',
                newType: 'expense',
                newCategory: 'other',
                errorMessage: '',
                successMessage: ''
            }
        },
        methods: {
            async login() {
    try {
        this.resetMessages();
        if (!this.email || !this.password) {
            throw new Error('Email e senha são obrigatórios');
        }

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: this.email,
                password: this.password
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Credenciais inválidas');
        }

        localStorage.setItem('token', data.token);
        this.isAuthenticated = true;
        await this.fetchTransactions();
        this.email = '';
        this.password = '';

    } catch (error) {
        this.errorMessage = error.message;
        console.error("Login error:", error);
    }
},
            async register() {
                try {
                    this.resetMessages();
                    
                    if (!this.registerEmail || !this.registerPassword) {
                        throw new Error('Email e senha são obrigatórios');
                    }
                
                    if (!this.registerEmail.includes('@') || !this.registerEmail.includes('.')) {
                        throw new Error('Por favor, insira um email válido');
                    }

                    if (this.registerPassword.length < 6) {
                        throw new Error('A senha deve ter pelo menos 6 caracteres');
                    }
                
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            email: this.registerEmail,
                            password: this.registerPassword,
                            name: this.registerName
                        })
                    });
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Falha no registro');
                    }
                    this.successMessage = 'Registro realizado com sucesso! Faça login.';
                    this.errorMessage = '';
                    this.email = this.registerEmail;
                    this.registerEmail = '';
                    this.registerPassword = '';
                    this.registerName = '';
                    this.showRegister = false;
                
                    await this.$nextTick();
                    const passwordField = document.querySelector('input[type="password"]');
                    if (passwordField) passwordField.focus();
                
                } catch (error) {
                    this.errorMessage = error.message;
                    console.error("Registration error:", error);
                
                    if (error.message.includes('email')) {
                        const emailField = document.querySelector('input[type="email"]');
                        if (emailField) emailField.focus();
                    } else if (error.message.includes('senha')) {
                        const passwordField = document.querySelector('input[type="password"]');
                        if (passwordField) passwordField.focus();
                    }
                }
            },
            logout() {
                localStorage.removeItem('token');
                this.isAuthenticated = false;
                this.transactions = [];
                this.resetMessages();
            },

            resetMessages() {
                this.errorMessage = '';
                this.successMessage = '';
            },

            formatDate(dateString) {
                const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
                return new Date(dateString).toLocaleDateString('pt-BR', options);
            },

            formatCurrency(amount) {
                return amount.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
            },

            async fetchTransactions() {
                try {
                    this.resetMessages();
                    const params = new URLSearchParams();
                    if (this.filterCategory) params.append('category', this.filterCategory);
                    if (this.filterType) params.append('type', this.filterType);
                    if (this.filterStartDate) params.append('start_date', this.filterStartDate);
                    if (this.filterEndDate) params.append('end_date', this.filterEndDate);

                    const response = await fetch(`/api/transactions?${params.toString()}`, {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });

                    if (!response.ok) throw new Error('Erro ao carregar transações');

                    const data = await response.json();
                    this.transactions = data.transactions;

                } catch (error) {
                    this.errorMessage = error.message;
                    console.error("Fetch error:", error);
                    
                    if (error.message.includes('401')) {
                        this.logout();
                    }
                }
            },

            async addTransaction() {
                try {
                    this.resetMessages();
                    if (!this.newDescription || !this.newAmount) {
                        throw new Error('Preencha todos os campos');
                    }

                    const response = await fetch('/api/transactions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        },
                        body: JSON.stringify({
                            description: this.newDescription,
                            amount: parseFloat(this.newAmount),
                            type: this.newType,
                            category: this.newCategory
                        })
                    });

                    const data = await response.json();
                    
                    if (!response.ok) throw new Error(data.error || 'Erro ao adicionar transação');

                    this.successMessage = 'Transação adicionada com sucesso!';
                    this.newDescription = '';
                    this.newAmount = '';
                    await this.fetchTransactions();

                } catch (error) {
                    this.errorMessage = error.message;
                    console.error("Add transaction error:", error);
                }
            }
        },
        async mounted() {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const response = await fetch('/api/validate-token', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (response.ok) {
                        this.isAuthenticated = true;
                        await this.fetchTransactions();
                    } else {
                        this.logout();
                    }
                } catch (error) {
                    this.logout();
                    console.error("Token validation error:", error);
                }
            }
        }
    });

    app.mount('#app');
});
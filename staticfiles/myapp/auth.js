document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');

    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            const users = JSON.parse(localStorage.getItem('users')) || [];
            if (users.some(user => user.email === email)) {
                alert('Email already registered!');
                return;
            }

            users.push({ username, email, password });
            localStorage.setItem('users', JSON.stringify(users));
            alert('Signup successful! Please login.');
            window.location.href = '/login/';
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const users = JSON.parse(localStorage.getItem('users')) || [];
            const user = users.find(u => u.email === email && u.password === password);

            if (!user) {
                alert('Invalid email or password!');
                return;
            }

            localStorage.setItem('loggedInUser', JSON.stringify(user));
            alert('Login successful!');
            window.location.href = '/landing/';
        });
    }
});
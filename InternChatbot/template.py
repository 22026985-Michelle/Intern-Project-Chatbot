# template.py

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login/Signup - Intern Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            overflow: hidden;
        }

        .tabs {
            display: flex;
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }

        .tab-btn {
            flex: 1;
            padding: 15px;
            border: none;
            background: none;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .tab-btn.active {
            color: #2563eb;
            position: relative;
        }

        .tab-btn.active::after {
            content: '';
            position: absolute;
            bottom: -15px;
            left: 0;
            width: 100%;
            height: 3px;
            background: #2563eb;
        }

        .form-container {
            padding: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #4b5563;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .submit-btn {
            width: 100%;
            padding: 12px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .submit-btn:hover {
            background: #1d4ed8;
        }

        .forgot-password {
            text-align: center;
            margin-top: 20px;
        }

        .forgot-password a {
            color: #2563eb;
            text-decoration: none;
            font-size: 14px;
        }

        #signup-form {
            display: none;
        }

        .error-message {
            color: #dc2626;
            font-size: 14px;
            margin-top: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('login')">Login</button>
            <button class="tab-btn" onclick="switchTab('signup')">Sign Up</button>
        </div>
        
        <div class="form-container">
            <form id="login-form">
                <div class="form-group">
                    <label for="login-email">Email</label>
                    <input type="email" id="login-email" required>
                    <div class="error-message" id="login-email-error">Please enter a valid email address</div>
                </div>
                <div class="form-group">
                    <label for="login-password">Password</label>
                    <input type="password" id="login-password" required>
                    <div class="error-message" id="login-password-error">Password must be at least 6 characters</div>
                </div>
                <button type="submit" class="submit-btn">Login</button>
                <div class="forgot-password">
                    <a href="#">Forgot password?</a>
                </div>
            </form>

            <form id="signup-form">
                <div class="form-group">
                    <label for="signup-name">Full Name</label>
                    <input type="text" id="signup-name" required>
                    <div class="error-message" id="signup-name-error">Please enter your full name</div>
                </div>
                <div class="form-group">
                    <label for="signup-email">Email</label>
                    <input type="email" id="signup-email" required>
                    <div class="error-message" id="signup-email-error">Please enter a valid email address</div>
                </div>
                <div class="form-group">
                    <label for="signup-password">Password</label>
                    <input type="password" id="signup-password" required>
                    <div class="error-message" id="signup-password-error">Password must be at least 6 characters</div>
                </div>
                <div class="form-group">
                    <label for="signup-confirm">Confirm Password</label>
                    <input type="password" id="signup-confirm" required>
                    <div class="error-message" id="signup-confirm-error">Passwords do not match</div>
                </div>
                <button type="submit" class="submit-btn">Sign Up</button>
            </form>
        </div>
    </div>

    <script>
        function switchTab(tab) {
            const loginForm = document.getElementById('login-form');
            const signupForm = document.getElementById('signup-form');
            const tabs = document.querySelectorAll('.tab-btn');
            
            tabs.forEach(btn => btn.classList.remove('active'));
            
            if (tab === 'login') {
                loginForm.style.display = 'block';
                signupForm.style.display = 'none';
                tabs[0].classList.add('active');
            } else {
                loginForm.style.display = 'none';
                signupForm.style.display = 'block';
                tabs[1].classList.add('active');
            }
        }

        // Form validation
        document.getElementById('login-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('login-email');
            const password = document.getElementById('login-password');
            let isValid = true;

            // Email validation
            if (!validateEmail(email.value)) {
                document.getElementById('login-email-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('login-email-error').style.display = 'none';
            }

            // Password validation
            if (password.value.length < 6) {
                document.getElementById('login-password-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('login-password-error').style.display = 'none';
            }

            if (isValid) {
                // Here you would typically send the data to your server
                console.log('Login form submitted:', {
                    email: email.value,
                    password: password.value
                });
            }
        });

        document.getElementById('signup-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('signup-name');
            const email = document.getElementById('signup-email');
            const password = document.getElementById('signup-password');
            const confirm = document.getElementById('signup-confirm');
            let isValid = true;

            // Name validation
            if (name.value.trim() === '') {
                document.getElementById('signup-name-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('signup-name-error').style.display = 'none';
            }

            // Email validation
            if (!validateEmail(email.value)) {
                document.getElementById('signup-email-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('signup-email-error').style.display = 'none';
            }

            // Password validation
            if (password.value.length < 6) {
                document.getElementById('signup-password-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('signup-password-error').style.display = 'none';
            }

            // Confirm password validation
            if (password.value !== confirm.value) {
                document.getElementById('signup-confirm-error').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('signup-confirm-error').style.display = 'none';
            }

            if (isValid) {
                // Here you would typically send the data to your server
                console.log('Signup form submitted:', {
                    name: name.value,
                    email: email.value,
                    password: password.value
                });
            }
        });

        function validateEmail(email) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }
    </script>
</body>
</html>
'''
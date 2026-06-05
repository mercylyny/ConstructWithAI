import React, { useState, useEffect } from 'react';
import {
  registerUser,
  loginUser,
  googleLoginUser,
  requestPasswordReset,
  confirmPasswordReset
} from '../services/api';

function LoginPage({ onLogin }) {
  const [view, setView] = useState('login'); // 'login', 'signup', 'forgot-password', 'reset-password'
  
  // Credentials & Registration States
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Password Reset States
  const [resetEmail, setResetEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [sentResetEmail, setSentResetEmail] = useState(false);
  
  // UX States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Password Visibility States
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);

  // Check URL query parameters for password reset deep-linking on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const viewParam = params.get('view');
    const tokenParam = params.get('token');
    const emailParam = params.get('email');

    if (viewParam === 'reset-password' && tokenParam && emailParam) {
      setView('reset-password');
      setResetEmail(emailParam);
      setResetToken(tokenParam);
      setError('');
      setSuccess('');
    }
  }, []);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (view === 'signup') {
        if (password !== confirmPassword) {
          setError("Passwords do not match");
          setLoading(false);
          return;
        }

        // Complexity validation check
        const hasNumber = /[0-9]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasSpecial = /[^A-Za-z0-9]/.test(password);
        const isLengthValid = password.length >= 8;

        if (!isLengthValid || !hasNumber || !hasUppercase || !hasSpecial) {
          setError("Password must be at least 8 characters long and contain at least one number, one uppercase letter, and one special character.");
          setLoading(false);
          return;
        }

        const response = await registerUser(name, email, password);
        localStorage.setItem('build_ai_token', response.access_token);
        localStorage.setItem('build_ai_user', JSON.stringify(response.user));
        setSuccess("Account created successfully!");
        
        setTimeout(() => {
          setLoading(false);
          onLogin();
        }, 800);

      } else if (view === 'login') {
        const response = await loginUser(email, password);
        localStorage.setItem('build_ai_token', response.access_token);
        localStorage.setItem('build_ai_user', JSON.stringify(response.user));
        setSuccess("Welcome back!");
        
        setTimeout(() => {
          setLoading(false);
          onLogin();
        }, 800);
      }
    } catch (err) {
      setError(err.message || "Authentication failed. Please check your credentials.");
      setLoading(false);
    }
  };

  const handleForgotPasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await requestPasswordReset(resetEmail);
      setLoading(false);
      setSentResetEmail(true);
      setSuccess("A password reset link has been generated.");
      
      // Store debug_token if present (simulated SMTP UI helper for local dev testing)
      if (response.debug_token) {
        setResetToken(response.debug_token);
      }
    } catch (err) {
      setError(err.message || "Failed to send password reset link.");
      setLoading(false);
    }
  };

  const handleResetPasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (newPassword !== confirmNewPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    const hasNumber = /[0-9]/.test(newPassword);
    const hasUppercase = /[A-Z]/.test(newPassword);
    const hasSpecial = /[^A-Za-z0-9]/.test(newPassword);
    const isLengthValid = newPassword.length >= 8;

    if (!isLengthValid || !hasNumber || !hasUppercase || !hasSpecial) {
      setError("Password must be at least 8 characters long and contain at least one number, one uppercase letter, and one special character.");
      setLoading(false);
      return;
    }

    try {
      await confirmPasswordReset(resetEmail, resetToken, newPassword);
      setLoading(false);
      setSuccess("Your password has been reset successfully! Redirecting you to login...");
      
      setTimeout(() => {
        // Clear search queries from browser bar
        window.history.replaceState({}, document.title, window.location.pathname);
        setView('login');
        setSentResetEmail(false);
        setSuccess('');
        setPassword('');
        setConfirmPassword('');
        setNewPassword('');
        setConfirmNewPassword('');
        setResetToken('');
      }, 2500);
    } catch (err) {
      setError(err.message || "Unable to reset password.");
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    const width = 500;
    const height = 600;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    
    const popup = window.open(
      '/google-auth.html',
      'GoogleSignInPopup',
      `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes,scrollbars=yes`
    );

    if (!popup) {
      setError("Please allow popups to sign in with Google");
      return;
    }

    const handlePopupMessage = async (event) => {
      if (event.origin !== window.location.origin) return;

      if (event.data && event.data.type === 'GOOGLE_SIGN_IN_SUCCESS') {
        const account = event.data.account;
        
        window.removeEventListener('message', handlePopupMessage);
        setLoading(true);
        setError('');
        
        try {
          const response = await googleLoginUser(account.name, account.email);
          localStorage.setItem('build_ai_token', response.access_token);
          localStorage.setItem('build_ai_user', JSON.stringify(response.user));
          setSuccess("Google Sign-In successful!");
          
          setTimeout(() => {
            setLoading(false);
            onLogin();
          }, 800);
        } catch (err) {
          setError(err.message || "Google Sign-In failed.");
          setLoading(false);
        }
      }
    };

    window.addEventListener('message', handlePopupMessage);
  };

  return (
    <div className="fade-in" style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '80vh',
      padding: '1rem'
    }}>
      <style>{`
        .google-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          width: 100%;
          padding: 0.75rem 1.5rem;
          background: rgba(255, 255, 255, 0.08);
          border: 1px solid rgba(255, 255, 255, 0.15);
          border-radius: 8px;
          color: #fff;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          margin-top: 1rem;
        }
        .google-btn:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.15);
          border-color: rgba(255, 255, 255, 0.25);
          transform: translateY(-1px);
        }
        .google-btn:active:not(:disabled) {
          transform: translateY(1px);
        }
        .separator {
          display: flex;
          align-items: center;
          text-align: center;
          margin: 1.5rem 0;
          color: var(--text-secondary);
          font-size: 0.85rem;
        }
        .separator::before,
        .separator::after {
          content: '';
          flex: 1;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .separator:not(:empty)::before {
          margin-right: .5em;
        }
        .separator:not(:empty)::after {
          margin-left: .5em;
        }
        .auth-toggle-link {
          color: var(--accent-color);
          cursor: pointer;
          font-weight: 500;
          transition: color 0.2s ease;
          text-decoration: none;
        }
        .auth-toggle-link:hover {
          color: var(--accent-hover);
          text-decoration: underline;
        }
        .message-alert {
          padding: 0.75rem;
          border-radius: 8px;
          font-size: 0.875rem;
          margin-bottom: 1.25rem;
          text-align: center;
          line-height: 1.4;
        }
        .error-alert {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.25);
          color: var(--danger-color);
        }
        .success-alert {
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.25);
          color: var(--success-color);
        }
        .email-outbox-sim {
          margin-top: 1.5rem;
          padding: 1rem;
          background: rgba(139, 92, 246, 0.08);
          border: 1px dashed var(--accent-color);
          border-radius: 8px;
          text-align: left;
        }
        .email-header-field {
          font-size: 0.8rem;
          margin: 0 0 0.5rem 0;
          color: var(--text-secondary);
        }
        .email-header-field strong {
          color: var(--text-primary);
        }
      `}</style>

      <div className="glass-panel" style={{ 
        width: '100%', 
        maxWidth: '420px', 
        padding: '2.5rem',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Glow ambient effect */}
        <div style={{
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.04) 0%, transparent 60%)',
          pointerEvents: 'none',
          zIndex: 0
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          
          {/* VIEW: LOGIN OR SIGNUP */}
          {(view === 'login' || view === 'signup') && (
            <>
              <h2 style={{ marginBottom: view === 'login' ? '2rem' : '0.5rem', textAlign: 'center' }}>
                {view === 'login' ? 'Login Here' : 'Create Account'}
              </h2>
              {view === 'signup' && (
                <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', textAlign: 'center', fontSize: '0.95rem' }}>
                  Join us to get started with building estimates
                </p>
              )}

              {error && <div className="message-alert error-alert">{error}</div>}
              {success && <div className="message-alert success-alert">{success}</div>}

              <form onSubmit={handleAuthSubmit} style={{ textAlign: 'left' }}>
                {view === 'signup' && (
                  <div className="input-group">
                    <label className="input-label">Full Name</label>
                    <input 
                      type="text" 
                      className="input-field" 
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="John Doe"
                      required
                    />
                  </div>
                )}

                <div className="input-group">
                  <label className="input-label">Email Address</label>
                  <input 
                    type="email" 
                    name="email"
                    autoComplete="email"
                    className="input-field" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="engineer@example.com"
                    required
                  />
                </div>

                <div className="input-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <label className="input-label" style={{ margin: 0 }}>Password</label>
                    {view === 'login' && (
                      <span 
                        onClick={() => {
                          setView('forgot-password');
                          setError('');
                          setSuccess('');
                        }} 
                        style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', cursor: 'pointer' }} 
                        className="auth-toggle-link"
                      >
                        Forgot Password?
                      </span>
                    )}
                  </div>
                  <div style={{ position: 'relative' }}>
                    <input 
                      type={showPassword ? "text" : "password"} 
                      name="password"
                      autoComplete="current-password"
                      className="input-field"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      style={{ paddingRight: '2.5rem' }}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '4px',
                        zIndex: 2
                      }}
                    >
                      {showPassword ? (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      ) : (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                          <line x1="1" y1="1" x2="23" y2="23" />
                        </svg>
                      )}
                    </button>
                  </div>

                  {/* Real-time Password Strength Checklist (Signup Only) */}
                  {view === 'signup' && password && (
                    <div style={{ 
                      marginTop: '0.5rem', 
                      padding: '0.75rem', 
                      background: 'rgba(255,255,255,0.03)', 
                      borderRadius: '8px',
                      border: '1px solid rgba(255,255,255,0.05)',
                      fontSize: '0.8rem' 
                    }}>
                      <div style={{ fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                        Password strength requirements:
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: password.length >= 8 ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{password.length >= 8 ? '✓' : '○'}</span>
                          <span>Min 8 characters</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[A-Z]/.test(password) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[A-Z]/.test(password) ? '✓' : '○'}</span>
                          <span>One uppercase letter</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[0-9]/.test(password) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[0-9]/.test(password) ? '✓' : '○'}</span>
                          <span>At least one number</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[^A-Za-z0-9]/.test(password) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[^A-Za-z0-9]/.test(password) ? '✓' : '○'}</span>
                          <span>One special char</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {view === 'signup' && (
                  <div className="input-group">
                    <label className="input-label">Confirm Password</label>
                    <div style={{ position: 'relative' }}>
                      <input 
                        type={showConfirmPassword ? "text" : "password"} 
                        className="input-field"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="••••••••"
                        style={{ paddingRight: '2.5rem' }}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        style={{
                          position: 'absolute',
                          right: '10px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          color: 'var(--text-secondary)',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          padding: '4px',
                          zIndex: 2
                        }}
                      >
                        {showConfirmPassword ? (
                          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        ) : (
                          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                            <line x1="1" y1="1" x2="23" y2="23" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                )}

                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  style={{ width: '100%', marginTop: '1rem', padding: '0.85rem' }}
                  disabled={loading}
                >
                  {loading ? (
                    <span>Authenticating...</span>
                  ) : (
                    <span>{view === 'login' ? 'Sign In' : 'Create Account'}</span>
                  )}
                </button>
              </form>

              <div className="separator">or</div>

              <button 
                type="button" 
                className="google-btn" 
                onClick={handleGoogleLogin}
                disabled={loading}
              >
                <svg width="18" height="18" viewBox="0 0 18 18" style={{ marginRight: '4px' }}>
                  <path fill="#4285F4" d="M17.64 9.2c0-.63-.06-1.25-.16-1.84H9v3.47h4.84c-.21 1.12-.84 2.07-1.79 2.7v2.24h2.9c1.69-1.55 2.69-3.85 2.69-6.57z"/>
                  <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.23l-2.9-2.24c-.8.54-1.84.87-3.06.87-2.35 0-4.34-1.58-5.05-3.72H.95v2.3C2.43 15.89 5.5 18 9 18z"/>
                  <path fill="#FBBC05" d="M3.95 10.68c-.18-.54-.28-1.12-.28-1.68s.1-1.14.28-1.68V5.02H.95C.34 6.22 0 7.57 0 9s.34 2.78.95 3.98l3-2.3z"/>
                  <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.59C13.47.8 11.43 0 9 0 5.5 0 2.43 2.11.95 5.02l3 2.3c.71-2.14 2.7-3.72 5.05-3.72z"/>
                </svg>
                <span>Continue with Google</span>
              </button>

              <p style={{ marginTop: '2.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                {view === 'login' ? (
                  <>
                    Don't have an account?{' '}
                    <span 
                      onClick={() => {
                        setView('signup');
                        setError('');
                        setSuccess('');
                      }} 
                      className="auth-toggle-link"
                    >
                      Sign Up
                    </span>
                  </>
                ) : (
                  <>
                    Already have an account?{' '}
                    <span 
                      onClick={() => {
                        setView('login');
                        setError('');
                        setSuccess('');
                      }} 
                      className="auth-toggle-link"
                    >
                      Login Here
                    </span>
                  </>
                )}
              </p>
            </>
          )}

          {/* VIEW: FORGOT PASSWORD REQUEST */}
          {view === 'forgot-password' && (
            <>
              <h2 style={{ marginBottom: '0.5rem', textAlign: 'center' }}>
                Reset Password
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2.5rem', textAlign: 'center', fontSize: '0.95rem' }}>
                Enter your email and we'll send you a secure link to reset your password.
              </p>

              {error && <div className="message-alert error-alert">{error}</div>}
              {success && <div className="message-alert success-alert">{success}</div>}

              {!sentResetEmail ? (
                <form onSubmit={handleForgotPasswordSubmit} style={{ textAlign: 'left' }}>
                  <div className="input-group">
                    <label className="input-label">Email Address</label>
                    <input 
                      type="email" 
                      className="input-field" 
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      placeholder="engineer@example.com"
                      required
                    />
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary" 
                    style={{ width: '100%', marginTop: '1rem', padding: '0.85rem' }}
                    disabled={loading}
                  >
                    {loading ? 'Sending Request...' : 'Send Reset Link'}
                  </button>
                </form>
              ) : (
                /* Simulated Password Reset Outbox */
                <div className="email-outbox-sim">
                  <div style={{ fontWeight: 'bold', fontSize: '0.9rem', marginBottom: '0.75rem', color: 'var(--accent-color)', borderBottom: '1px solid rgba(139, 92, 246, 0.2)', paddingBottom: '0.5rem' }}>
                    [Simulated SMTP Outbox]
                  </div>
                  <div className="email-header-field">To: <strong>{resetEmail}</strong></div>
                  <div className="email-header-field">Subject: <strong>Reset your BuildAI Password</strong></div>
                  
                  <div style={{ 
                    marginTop: '1rem', 
                    padding: '0.75rem', 
                    background: 'rgba(0,0,0,0.2)', 
                    borderRadius: '6px', 
                    textAlign: 'center',
                    fontSize: '0.85rem'
                  }}>
                    <p style={{ margin: '0 0 0.75rem 0', color: 'var(--text-secondary)' }}>
                      We received a request to reset your password.
                    </p>
                    <button
                      onClick={() => {
                        setError('');
                        setSuccess('');
                        // Simulate deep-linking transition with query parameters
                        const testUrl = `?view=reset-password&token=${resetToken}&email=${resetEmail}`;
                        window.history.pushState({}, document.title, testUrl);
                        setView('reset-password');
                      }}
                      style={{
                        padding: '6px 12px',
                        background: 'var(--accent-color)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        transition: 'background 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'var(--accent-hover)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'var(--accent-color)'}
                    >
                      Click here to reset password
                    </button>
                  </div>
                </div>
              )}

              <p style={{ marginTop: '2.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                Remembered your password?{' '}
                <span 
                  onClick={() => {
                    setView('login');
                    setError('');
                    setSuccess('');
                    setSentResetEmail(false);
                  }} 
                  className="auth-toggle-link"
                >
                  Back to Login
                </span>
              </p>
            </>
          )}

          {/* VIEW: RESET PASSWORD FORM */}
          {view === 'reset-password' && (
            <>
              <h2 style={{ marginBottom: '0.5rem', textAlign: 'center' }}>
                New Password
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2.5rem', textAlign: 'center', fontSize: '0.95rem' }}>
                Set a strong password for your account <strong>{resetEmail}</strong>.
              </p>

              {error && <div className="message-alert error-alert">{error}</div>}
              {success && <div className="message-alert success-alert">{success}</div>}

              <form onSubmit={handleResetPasswordSubmit} style={{ textAlign: 'left' }}>
                <div className="input-group">
                  <label className="input-label">New Password</label>
                  <div style={{ position: 'relative' }}>
                    <input 
                      type={showNewPassword ? "text" : "password"} 
                      className="input-field"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                      style={{ paddingRight: '2.5rem' }}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '4px',
                        zIndex: 2
                      }}
                    >
                      {showNewPassword ? (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      ) : (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                          <line x1="1" y1="1" x2="23" y2="23" />
                        </svg>
                      )}
                    </button>
                  </div>

                  {/* Real-time Password Strength Checklist */}
                  {newPassword && (
                    <div style={{ 
                      marginTop: '0.5rem', 
                      padding: '0.75rem', 
                      background: 'rgba(255,255,255,0.03)', 
                      borderRadius: '8px',
                      border: '1px solid rgba(255,255,255,0.05)',
                      fontSize: '0.8rem' 
                    }}>
                      <div style={{ fontWeight: 500, marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
                        Password strength requirements:
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: newPassword.length >= 8 ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{newPassword.length >= 8 ? '✓' : '○'}</span>
                          <span>Min 8 characters</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[A-Z]/.test(newPassword) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[A-Z]/.test(newPassword) ? '✓' : '○'}</span>
                          <span>One uppercase letter</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[0-9]/.test(newPassword) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[0-9]/.test(newPassword) ? '✓' : '○'}</span>
                          <span>At least one number</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: /[^A-Za-z0-9]/.test(newPassword) ? 'var(--success-color)' : 'var(--text-secondary)' }}>
                          <span>{/[^A-Za-z0-9]/.test(newPassword) ? '✓' : '○'}</span>
                          <span>One special char</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="input-group">
                  <label className="input-label">Confirm New Password</label>
                  <div style={{ position: 'relative' }}>
                    <input 
                      type={showConfirmNewPassword ? "text" : "password"} 
                      className="input-field"
                      value={confirmNewPassword}
                      onChange={(e) => setConfirmNewPassword(e.target.value)}
                      placeholder="••••••••"
                      style={{ paddingRight: '2.5rem' }}
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmNewPassword(!showConfirmNewPassword)}
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        padding: '4px',
                        zIndex: 2
                      }}
                    >
                      {showConfirmNewPassword ? (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
                          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      ) : (
                        <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 19c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                          <line x1="1" y1="1" x2="23" y2="23" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary" 
                  style={{ width: '100%', marginTop: '1rem', padding: '0.85rem' }}
                  disabled={loading}
                >
                  {loading ? 'Updating Password...' : 'Save New Password'}
                </button>
              </form>
            </>
          )}

        </div>
      </div>
    </div>
  );
}

export default LoginPage;

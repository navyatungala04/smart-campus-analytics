import React, { useState } from 'react';
import { 
  GraduationCap, 
  Lock, 
  User, 
  Eye, 
  EyeOff, 
  AlertCircle, 
  ArrowRight,
  ShieldCheck,
  Info
} from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const validate = () => {
    const errors = {};
    if (!username.trim()) {
      errors.username = 'Username or Student ID is required';
    }
    if (!password) {
      errors.password = 'Password is required';
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!validate()) {
      return;
    }

    try {
      setIsLoading(true);
      await onLoginSuccess(username.trim(), password);
    } catch (err) {
      setErrorMessage(
        err.message || 'Invalid username or password. Please verify your credentials and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      
      {/* Brand Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-xl shadow-indigo-500/25 mb-4 border border-indigo-400/20">
          <GraduationCap className="w-9 h-9" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Smart Campus Analytics
        </h1>
        <p className="mt-1 text-xs sm:text-sm text-indigo-200/90 font-medium">
          Predict, Optimize &amp; Improve Student Success
        </p>
      </div>

      {/* Login Card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-slate-100">
          
          <div className="mb-6 flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Portal Sign In</h2>
              <p className="text-xs text-slate-500 mt-0.5">Student or Faculty credentials to access your dashboard</p>
            </div>
            <div className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Secure Auth</span>
            </div>
          </div>

          {/* Form Error Banner */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5 animate-fadeIn">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            
            {/* Username Field */}
            <div>
              <label 
                htmlFor="username-input" 
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
              >
                Username or Student ID
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="username-input"
                  name="username"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(e) => {
                    setUsername(e.target.value);
                    if (fieldErrors.username) {
                      setFieldErrors({ ...fieldErrors, username: null });
                    }
                    if (errorMessage) setErrorMessage('');
                  }}
                  placeholder="e.g. stu1015, stu1008, or STU1015"
                  className={`block w-full pl-10 pr-3.5 py-2.5 text-sm border rounded-xl bg-slate-50/50 focus:bg-white text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 transition-all ${
                    fieldErrors.username 
                      ? 'border-rose-300 focus:ring-rose-500 focus:border-rose-500' 
                      : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                />
              </div>
              {fieldErrors.username && (
                <p className="mt-1 text-xs text-rose-600 font-medium">
                  {fieldErrors.username}
                </p>
              )}
            </div>

            {/* Password Field with Show/Hide Toggle */}
            <div>
              <label 
                htmlFor="password-input" 
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
              >
                Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="password-input"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (fieldErrors.password) {
                      setFieldErrors({ ...fieldErrors, password: null });
                    }
                    if (errorMessage) setErrorMessage('');
                  }}
                  placeholder="Enter your password"
                  className={`block w-full pl-10 pr-10 py-2.5 text-sm border rounded-xl bg-slate-50/50 focus:bg-white text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 transition-all ${
                    fieldErrors.password 
                      ? 'border-rose-300 focus:ring-rose-500 focus:border-rose-500' 
                      : 'border-slate-300 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-rose-600 font-medium">
                  {fieldErrors.password}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-60 transition-all cursor-pointer"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Verifying Credentials...</span>
                  </div>
                ) : (
                  <>
                    <span>Sign In to Dashboard</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

          </form>

          {/* Demo Account Reference Card */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-600 space-y-2">
              <div className="flex items-center space-x-1.5 font-bold text-slate-800">
                <Info className="w-3.5 h-3.5 text-indigo-600" />
                <span>Demo Portal Credentials</span>
              </div>
              
              <div className="p-2 bg-indigo-50/70 border border-indigo-100 rounded-lg text-[11px] text-indigo-950">
                <p className="font-semibold text-indigo-900">Faculty Evaluation Account:</p>
                <p className="font-mono text-indigo-700 mt-0.5">Username: <span className="font-bold">faculty</span> • Password: <span className="font-bold">campus123</span></p>
                <p className="text-[10px] text-indigo-600 mt-0.5">Accesses faculty directory, marks editing, &amp; recalculation engine.</p>
              </div>

              <div className="text-[11px] text-slate-500 leading-relaxed">
                <p className="font-semibold text-slate-700">Student Accounts (Password: <span className="font-mono font-bold text-slate-800">campus123</span>):</p>
                <p className="mt-0.5">
                  <code className="bg-white px-1 py-0.5 rounded border border-slate-200 font-mono text-indigo-600">stu1015</code> (High Achiever) • <code className="bg-white px-1 py-0.5 rounded border border-slate-200 font-mono text-indigo-600">stu1008</code> (At-Risk) • <code className="bg-white px-1 py-0.5 rounded border border-slate-200 font-mono text-indigo-600">stu1002</code> (Steady)
                </p>
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <p className="text-center text-xs text-slate-500 mt-6">
          Smart Campus Analytics • SQLite Persistent Session Engine
        </p>
      </div>

    </div>
  );
}

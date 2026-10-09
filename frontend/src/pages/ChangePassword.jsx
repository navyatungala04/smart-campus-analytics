import React, { useState } from 'react';
import { 
  KeyRound, 
  Lock, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  ShieldCheck, 
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { updatePassword } from '../services/api';

export default function ChangePassword({ student }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Password condition checks
  const conditions = [
    {
      id: 'length',
      label: 'At least 8 characters',
      valid: newPassword.length >= 8,
    },
    {
      id: 'uppercase',
      label: 'At least one uppercase letter (A-Z)',
      valid: /[A-Z]/.test(newPassword),
    },
    {
      id: 'lowercase',
      label: 'At least one lowercase letter (a-z)',
      valid: /[a-z]/.test(newPassword),
    },
    {
      id: 'number',
      label: 'At least one number (0-9)',
      valid: /[0-9]/.test(newPassword),
    },
    {
      id: 'special',
      label: 'At least one special character (@, #, $, !, etc.)',
      valid: /[@#$%!^&*()_+\-=\[\]{};':"\\|,.<>/?`~]/.test(newPassword),
    },
  ];

  const allConditionsMet = conditions.every(c => c.valid);
  const passwordsMatch = newPassword === confirmPassword && confirmPassword.length > 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    if (!currentPassword) {
      setErrorMessage('Please enter your current password.');
      return;
    }

    if (!newPassword) {
      setErrorMessage('Please enter a new password.');
      return;
    }

    if (!allConditionsMet) {
      setErrorMessage('The new password does not meet all required security conditions.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage('New password and confirmation do not match.');
      return;
    }

    try {
      setIsLoading(true);
      const res = await updatePassword(currentPassword, newPassword, confirmPassword);
      setSuccessMessage(res.message || 'Password updated successfully! Use your new password for future sign-ins.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setErrorMessage(err.message || 'Failed to update password. Please check your current password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Change Password</h1>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Security Settings
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Update your account password with enhanced security verification for <span className="font-semibold text-slate-700">{student?.personal_info?.student_name}</span> ({student?.personal_info?.student_id}).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Form Card */}
        <div className="lg:col-span-7 bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-xs">
          
          <h2 className="text-base font-bold text-slate-900 mb-1 flex items-center space-x-2">
            <KeyRound className="w-5 h-5 text-indigo-600" />
            <span>Update Account Password</span>
          </h2>
          <p className="text-xs text-slate-500 mb-6">
            Enter your existing password followed by your new compliant password.
          </p>

          {/* Error Banner */}
          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2.5">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Success Banner */}
          {successMessage && (
            <div className="mb-5 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-start space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-bold text-sm text-emerald-900">Success!</p>
                <p className="mt-0.5 text-emerald-800 leading-relaxed">{successMessage}</p>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5" noValidate>
            
            {/* Current Password Field */}
            <div>
              <label 
                htmlFor="current-password" 
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
              >
                Current Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="current-password"
                  name="currentPassword"
                  type={showCurrent ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={currentPassword}
                  onChange={(e) => {
                    setCurrentPassword(e.target.value);
                    if (errorMessage) setErrorMessage('');
                    if (successMessage) setSuccessMessage('');
                  }}
                  placeholder="Enter current password"
                  className="block w-full pl-10 pr-10 py-2.5 text-sm border border-slate-300 rounded-xl bg-slate-50/50 focus:bg-white text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrent(!showCurrent)}
                  aria-label={showCurrent ? 'Hide current password' : 'Show current password'}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer"
                >
                  {showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* New Password Field */}
            <div>
              <label 
                htmlFor="new-password" 
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
              >
                New Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="new-password"
                  name="newPassword"
                  type={showNew ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={newPassword}
                  onChange={(e) => {
                    setNewPassword(e.target.value);
                    if (errorMessage) setErrorMessage('');
                    if (successMessage) setSuccessMessage('');
                  }}
                  placeholder="Enter new strong password"
                  className="block w-full pl-10 pr-10 py-2.5 text-sm border border-slate-300 rounded-xl bg-slate-50/50 focus:bg-white text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowNew(!showNew)}
                  aria-label={showNew ? 'Hide new password' : 'Show new password'}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer"
                >
                  {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Confirm New Password Field */}
            <div>
              <label 
                htmlFor="confirm-password" 
                className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
              >
                Confirm New Password
              </label>
              <div className="relative rounded-xl shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  id="confirm-password"
                  name="confirmPassword"
                  type={showConfirm ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    if (errorMessage) setErrorMessage('');
                    if (successMessage) setSuccessMessage('');
                  }}
                  placeholder="Re-type new password"
                  className="block w-full pl-10 pr-10 py-2.5 text-sm border border-slate-300 rounded-xl bg-slate-50/50 focus:bg-white text-slate-900 placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  aria-label={showConfirm ? 'Hide confirm password' : 'Show confirm password'}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 focus:outline-hidden cursor-pointer"
                >
                  {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {confirmPassword && (
                <div className="mt-1.5 flex items-center space-x-1.5 text-xs">
                  {passwordsMatch ? (
                    <span className="text-emerald-600 flex items-center space-x-1 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Passwords match</span>
                    </span>
                  ) : (
                    <span className="text-rose-600 flex items-center space-x-1 font-medium">
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Passwords do not match</span>
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full sm:w-auto px-6 py-3 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-60 transition-all cursor-pointer flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>Updating Password...</span>
                  </>
                ) : (
                  <>
                    <span>Update Password</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

          </form>

        </div>

        {/* Requirements & Security Sidebar */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Password Conditions Checklist */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-slate-100">
              <ShieldCheck className="w-5 h-5 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">Password Conditions</h3>
            </div>
            
            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Your new password must satisfy all 5 criteria before updating:
            </p>

            <ul className="space-y-2.5">
              {conditions.map((c) => (
                <li key={c.id} className="flex items-start space-x-2.5 text-xs">
                  {c.valid ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0 mt-0.5 flex items-center justify-center">
                      <div className="w-1.5 h-1.5 rounded-full bg-slate-300"></div>
                    </div>
                  )}
                  <span className={c.valid ? 'text-slate-800 font-semibold' : 'text-slate-500'}>
                    {c.label}
                  </span>
                </li>
              ))}
            </ul>

            <div className="mt-5 pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Security Strength:</span>
                <span className={`font-bold ${
                  allConditionsMet ? 'text-emerald-600' : 'text-amber-600'
                }`}>
                  {allConditionsMet ? 'Strong Password' : 'Incomplete'}
                </span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-2 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${
                    allConditionsMet ? 'bg-emerald-500' : 'bg-amber-400'
                  }`}
                  style={{ width: `${(conditions.filter(c => c.valid).length / conditions.length) * 100}%` }}
                ></div>
              </div>
            </div>

          </div>

          {/* Security Notice Card */}
          <div className="bg-indigo-50/60 p-5 rounded-2xl border border-indigo-100 text-xs text-indigo-900">
            <div className="flex items-center space-x-2 font-bold mb-1.5 text-indigo-950">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>Security Guarantee</span>
            </div>
            <p className="text-indigo-800/90 leading-relaxed text-[11px]">
              Passwords are salted with a 16-byte random key and securely hashed using PBKDF2-HMAC-SHA256 (100,000 rounds). Plaintext passwords and cryptographic salts are never transmitted to unauthorized parties.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

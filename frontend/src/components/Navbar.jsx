import React from 'react';
import { 
  GraduationCap, 
  LogOut, 
  User,
  ShieldCheck 
} from 'lucide-react';

export default function Navbar({ 
  currentStudent, 
  onLogout,
  isBackendHealthy 
}) {
  const studentName = currentStudent?.personal_info?.student_name || 'Student';
  const studentId = currentStudent?.personal_info?.student_id || '';
  const department = currentStudent?.personal_info?.department || '';
  const shortDept = department.split(' ')[0] || '';

  // Get initials for avatar
  const initials = studentName
    .split(' ')
    .map(n => n[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo & Platform Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">Smart Campus Analytics</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                  Student Portal
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">Predict, Optimize &amp; Improve Student Success</p>
            </div>
          </div>

          {/* Authenticated User Controls */}
          <div className="flex items-center space-x-3">
            
            {/* Authenticated Student Profile Card */}
            {currentStudent && (
              <div className="flex items-center space-x-3 pl-3 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-xl">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                  {initials || <User className="w-4 h-4" />}
                </div>
                <div className="text-left hidden sm:block">
                  <div className="text-xs font-bold text-slate-900 leading-tight">
                    {studentName}
                  </div>
                  <div className="text-[11px] text-slate-500 flex items-center space-x-1.5">
                    <span className="font-mono font-medium text-indigo-600">{studentId}</span>
                    <span>•</span>
                    <span className="truncate max-w-[120px]">{shortDept}</span>
                  </div>
                </div>
                <div className="hidden md:flex items-center space-x-1 px-1.5 py-0.5 rounded-md bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  <span>Active</span>
                </div>
              </div>
            )}

            {/* Logout Button */}
            <button
              onClick={onLogout}
              className="px-3 py-2 rounded-xl border border-slate-300 hover:bg-rose-50 hover:text-rose-700 hover:border-rose-300 text-slate-700 text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
              title="Terminate active session and log out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>

            {/* Backend Health Dot */}
            <div className="hidden lg:flex items-center space-x-1.5 text-xs text-slate-500 pl-1 border-l border-slate-200">
              <span className={`w-2 h-2 rounded-full ${isBackendHealthy ? 'bg-emerald-500' : 'bg-rose-500'} animate-pulse`}></span>
              <span className="text-[11px]">{isBackendHealthy ? 'API Online' : 'Connecting...'}</span>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}

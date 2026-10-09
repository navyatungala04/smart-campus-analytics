import React from 'react';
import { User, Mail, BookOpen, Calendar, ShieldCheck, Sparkles, Building, IdCard } from 'lucide-react';

export default function Profile({ student, onNavigate }) {
  if (!student) return null;
  const { personal_info, segmentation, success_score } = student;

  const initials = personal_info.student_name
    .split(' ')
    .map(n => n[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Student Profile</h2>
          <p className="text-sm text-slate-500">
            Official academic enrollment credentials and campus portal identity
          </p>
        </div>
        {onNavigate && (
          <button
            onClick={() => onNavigate('change_password')}
            className="self-start sm:self-auto inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            <span>Change Password</span>
          </button>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        
        {/* Banner */}
        <div className="h-32 bg-gradient-to-r from-indigo-600 via-indigo-700 to-violet-800 relative">
          <div className="absolute right-4 top-4">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-white/20 text-white backdrop-blur-md border border-white/30">
              <ShieldCheck className="w-3.5 h-3.5 mr-1" /> Verified Demo Record
            </span>
          </div>
        </div>

        {/* Profile Card Body */}
        <div className="px-6 pb-6 pt-0 relative">
          
          <div className="flex flex-col sm:flex-row sm:items-end justify-between -mt-12 gap-4 pb-4 border-b border-slate-100">
            <div className="flex items-end space-x-4">
              <div className="w-24 h-24 rounded-2xl bg-white p-1 shadow-md">
                <div className="w-full h-full rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-600 text-white flex items-center justify-center font-black text-2xl tracking-wider shadow-inner">
                  {initials}
                </div>
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">{personal_info.student_name}</h3>
                <p className="text-xs text-slate-500 font-mono mt-0.5">{student.student_id}</p>
              </div>
            </div>

            <div className="text-right">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Success Index</span>
              <p className="text-2xl font-black text-indigo-600">{success_score.overall_score} / 100</p>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
            
            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Academic Standing</h4>

              <div className="flex items-center space-x-3 text-sm text-slate-700">
                <Building className="w-4 h-4 text-indigo-500 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">Department</span>
                  <span className="font-semibold">{personal_info.department}</span>
                </div>
              </div>

              <div className="flex items-center space-x-3 text-sm text-slate-700">
                <BookOpen className="w-4 h-4 text-indigo-500 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">Academic Standing</span>
                  <span className="font-semibold">{personal_info.academic_year} — Semester {personal_info.semester}</span>
                </div>
              </div>

              <div className="flex items-center space-x-3 text-sm text-slate-700">
                <Mail className="w-4 h-4 text-indigo-500 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">University Email</span>
                  <span className="font-semibold font-mono text-xs">{personal_info.email}</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Campus Analytics Persona</h4>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
                <div className="flex items-center space-x-2 text-indigo-700 font-bold text-sm">
                  <Sparkles className="w-4 h-4" />
                  <span>{segmentation.segment_name}</span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {segmentation.segment_description}
                </p>
                <div className="pt-2 border-t border-slate-200/60 text-xs text-slate-500">
                  <strong className="text-slate-700">Recommended Focus:</strong> {segmentation.focus_strategy}
                </div>
              </div>
            </div>

          </div>

          {/* Synthetic Demo Disclaimer */}
          <div className="mt-8 p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-amber-900 text-xs space-y-1">
            <p className="font-bold">Synthetic Demonstration Profile</p>
            <p className="text-amber-800 leading-relaxed">
              This record belongs to a synthesized cohort generated for the Smart Campus Analytics hackathon showcase. All course marks, attendance logs, and survey feedback are modeled programmatically with zero actual student personal data.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}

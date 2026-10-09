import React from 'react';
import { Activity, Calendar, Trophy, Award, Users, CheckCircle, Zap } from 'lucide-react';

export default function LmsEngagement({ student }) {
  if (!student) return null;
  const { lms_details, engagement_details } = student;

  const loginPercent = Math.min(100, Math.round((lms_details.login_frequency / 50) * 100));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">LMS Activity & Campus Engagement</h2>
        <p className="text-sm text-slate-500">
          Digital learning portal metrics, continuous coursework submissions, and campus co-curricular involvement
        </p>
      </div>

      {/* Section 1: LMS Digital Learning */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Learning Management System (LMS) Footprint</h3>
              <p className="text-xs text-slate-500">Online lecture portal access and digital homework submissions</p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
            {lms_details.login_frequency} Logins / Month
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Assignment Completion Meter */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
            <div className="flex justify-between items-center text-sm font-semibold text-slate-800">
              <span>Assignment Submission Rate</span>
              <span className="text-indigo-600 font-bold">{lms_details.assignment_completion_percentage}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${
                  lms_details.assignment_completion_percentage >= 80 ? 'bg-emerald-500' :
                  lms_details.assignment_completion_percentage >= 60 ? 'bg-amber-500' :
                  'bg-rose-500'
                }`}
                style={{ width: `${lms_details.assignment_completion_percentage}%` }}
              ></div>
            </div>
            <p className="text-xs text-slate-500">
              Submitted <strong>{lms_details.assignments_completed}</strong> of <strong>{lms_details.total_assignments}</strong> mandatory course assignments.
              {lms_details.assignments_completed < lms_details.total_assignments && (
                <span className="text-rose-600 font-medium ml-1">
                  ({lms_details.total_assignments - lms_details.assignments_completed} pending)
                </span>
              )}
            </p>
          </div>

          {/* Login Activity Meter */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
            <div className="flex justify-between items-center text-sm font-semibold text-slate-800">
              <span>Digital Activity Benchmark</span>
              <span className="text-indigo-600 font-bold">{loginPercent}% of Target</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div 
                className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                style={{ width: `${loginPercent}%` }}
              ></div>
            </div>
            <p className="text-xs text-slate-500">
              Target active baseline: 50 logins/month. Current: <strong>{lms_details.login_frequency} sessions</strong>.
            </p>
          </div>

        </div>
      </div>

      {/* Section 2: Campus Engagement & Co-Curriculars */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Co-Curricular & Campus Involvement</h3>
              <p className="text-xs text-slate-500">Extracurricular leadership, clubs, hackathons, and certifications</p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
            engagement_details.extracurricular_tier === 'High' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
            engagement_details.extracurricular_tier === 'Medium' ? 'bg-blue-100 text-blue-800 border border-blue-300' :
            'bg-slate-100 text-slate-700 border border-slate-300'
          }`}>
            {engagement_details.extracurricular_tier} Tier Engagement
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
            <div className="flex items-center space-x-2 text-slate-500 text-xs font-semibold uppercase">
              <Calendar className="w-4 h-4 text-indigo-500" />
              <span>Events Attended</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-2">{engagement_details.events_attended}</p>
            <p className="text-xs text-slate-500 mt-1">Campus fests & seminars</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
            <div className="flex items-center space-x-2 text-slate-500 text-xs font-semibold uppercase">
              <Users className="w-4 h-4 text-emerald-500" />
              <span>Clubs Active</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-2">{engagement_details.clubs_participated}</p>
            <p className="text-xs text-slate-500 mt-1">Societies & student chapters</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
            <div className="flex items-center space-x-2 text-slate-500 text-xs font-semibold uppercase">
              <Trophy className="w-4 h-4 text-amber-500" />
              <span>Hackathons</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-2">{engagement_details.hackathons_participated}</p>
            <p className="text-xs text-slate-500 mt-1">Competitive coding contests</p>
          </div>

          <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
            <div className="flex items-center space-x-2 text-slate-500 text-xs font-semibold uppercase">
              <Award className="w-4 h-4 text-violet-500" />
              <span>Certifications</span>
            </div>
            <p className="text-2xl font-bold text-slate-900 mt-2">{engagement_details.certifications_count}</p>
            <p className="text-xs text-slate-500 mt-1">Verified external MOOCs</p>
          </div>

        </div>
      </div>

    </div>
  );
}

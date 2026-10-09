import React from 'react';
import {
  LayoutDashboard,
  BookOpen,
  CalendarCheck,
  Activity,
  Briefcase,
  Award,
  MessageSquareText,
  Trophy,
  ShieldAlert,
  ListTodo,
  User,
  KeyRound,
  ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Student Dashboard', icon: LayoutDashboard, group: 'Main' },
  { id: 'academic', label: 'Academic Performance', icon: BookOpen, group: 'Analytics' },
  { id: 'attendance', label: 'Attendance', icon: CalendarCheck, group: 'Analytics' },
  { id: 'lms_engagement', label: 'LMS & Engagement', icon: Activity, group: 'Analytics' },
  { id: 'placement', label: 'Placement Readiness', icon: Briefcase, group: 'Analytics' },
  { id: 'skills', label: 'Skills & Certifications', icon: Award, group: 'Analytics' },
  { id: 'feedback', label: 'Feedback Insights', icon: MessageSquareText, group: 'Analytics' },
  { id: 'score', label: 'My Success Score', icon: Trophy, group: 'Student Success' },
  { id: 'risks', label: 'My Risk Analysis', icon: ShieldAlert, group: 'Student Success' },
  { id: 'plan', label: 'My Improvement Plan', icon: ListTodo, group: 'Student Success' },
  { id: 'profile', label: 'My Profile', icon: User, group: 'Account' },
  { id: 'change_password', label: 'Change Password', icon: KeyRound, group: 'Account' },
];

export default function Sidebar({ activePage, onNavigate, riskCount = 0, recCount = 0 }) {
  // Group navigation items
  const groups = ['Main', 'Analytics', 'Student Success', 'Account'];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6 flex-1">
        {groups.map((group) => {
          const items = NAV_ITEMS.filter(item => item.group === group);
          return (
            <div key={group} className="space-y-1">
              <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                {group}
              </p>
              <div className="space-y-0.5">
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activePage === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => onNavigate(item.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                        isActive
                          ? 'bg-indigo-50 text-indigo-700 shadow-xs'
                          : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                        <span>{item.label}</span>
                      </div>
                      
                      {/* Dynamic Alert Badges */}
                      {item.id === 'risks' && riskCount > 0 && (
                        <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700">
                          {riskCount}
                        </span>
                      )}
                      {item.id === 'plan' && recCount > 0 && (
                        <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                          {recCount}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Student Quick Status */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="text-xs text-slate-500">
          <p className="font-semibold text-slate-700">Student Portal v2.0</p>
          <p className="text-[11px] text-slate-400">Persistent SQLite Auth</p>
        </div>
      </div>
    </aside>
  );
}

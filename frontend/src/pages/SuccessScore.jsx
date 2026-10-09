import React from 'react';
import { Trophy, HelpCircle, CheckCircle2, AlertCircle, Info, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function SuccessScore({ student }) {
  if (!student) return null;
  const { success_score } = student;
  const { overall_score, breakdown } = success_score;
  const comps = breakdown.components;

  const tableData = [
    { key: 'academic', name: 'Academic Performance', ...comps.academic, formula: '50% CGPA + 30% Marks + 20% Backlog Clearance' },
    { key: 'attendance', name: 'Attendance Tracking', ...comps.attendance, formula: 'Classes Attended / Total Scheduled Classes' },
    { key: 'lms_activity', name: 'LMS Activity & Coursework', ...comps.lms_activity, formula: '40% Login Frequency + 60% Assignment Completion' },
    { key: 'engagement', name: 'Campus Engagement', ...comps.engagement, formula: 'Events (20%) + Clubs (25%) + Hackathons (30%) + Certs (15%) + Tier (10%)' },
    { key: 'placement', name: 'Placement Readiness', ...comps.placement, formula: '30% Aptitude + 40% Coding + 30% Mock (Re-weighted if mock pending)' },
    { key: 'skills', name: 'Technical & Soft Skills', ...comps.skills, formula: '60% Technical Skill + 40% Soft Skill (100% tech if soft pending)' },
    { key: 'feedback', name: 'Mentorship & Feedback', ...comps.feedback, formula: '60% Faculty Rating + 40% Satisfaction (100% faculty if survey pending)' },
  ];

  const chartData = tableData.map(d => ({
    name: d.name.split(' ')[0],
    fullName: d.name,
    contribution: d.contribution,
    rawScore: d.raw_score
  }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">My Success Score</h2>
        <p className="text-sm text-slate-500">
          Transparent multi-criteria composite index evaluating academic resilience, consistency, and career readiness
        </p>
      </div>

      {/* Hero Score Showcase */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-800 to-slate-900 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-300">Composite Overall Score</span>
          <div className="flex items-baseline space-x-3 mt-1">
            <span className="text-5xl font-black text-amber-300">{overall_score}</span>
            <span className="text-xl text-indigo-200">/ 100</span>
          </div>
          <p className="text-sm text-indigo-100 mt-2 max-w-xl">
            A balanced reflection across all seven student success pillars. No arbitrary penalties or black-box predictions.
          </p>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-xs space-y-2 max-w-sm">
          <div className="flex items-center space-x-1.5 font-bold text-amber-300">
            <ShieldCheck className="w-4 h-4" />
            <span>100% Transparent Formula</span>
          </div>
          <p className="text-indigo-100/90 leading-relaxed">
            Every point is traceable to your verified academic records, attendance logs, and assessment scores.
          </p>
        </div>
      </div>

      {/* Contribution Bar Chart */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-1">Points Contributed to Success Score</h3>
        <p className="text-xs text-slate-500 mb-4">Shows each pillar's weighted point contribution towards your total {overall_score} points</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis domain={[0, 30]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip formatter={(val, name, item) => [`+${val} pts (Raw: ${item.payload.rawScore}/100)`, item.payload.fullName]} />
              <Bar dataKey="contribution" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-900">Score Breakdown & Mathematical Weights</h3>
          <span className="text-xs text-slate-500">All Weights Sum to 100%</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
              <tr>
                <th className="px-5 py-3 text-left">Category Pillar</th>
                <th className="px-5 py-3 text-center">Raw Score (0-100)</th>
                <th className="px-5 py-3 text-center">Assigned Weight</th>
                <th className="px-5 py-3 text-center">Contribution</th>
                <th className="px-5 py-3 text-left hidden md:table-cell">Formula & Policy</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tableData.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-5 py-3.5 font-medium text-slate-900">
                    <div className="flex items-center space-x-2">
                      <span>{row.name}</span>
                      {row.mock_interview_pending && (
                        <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded-full font-medium">
                          Mock Pending
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-center font-bold text-slate-800">{row.raw_score}</td>
                  <td className="px-5 py-3.5 text-center font-medium text-slate-600">{(row.weight * 100).toFixed(0)}%</td>
                  <td className="px-5 py-3.5 text-center font-bold text-indigo-700">+{row.contribution} pts</td>
                  <td className="px-5 py-3.5 text-xs text-slate-500 hidden md:table-cell">{row.formula}</td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-slate-50 font-bold text-slate-900">
              <tr>
                <td className="px-5 py-3 text-left">Total Composite Score</td>
                <td className="px-5 py-3 text-center">-</td>
                <td className="px-5 py-3 text-center">100%</td>
                <td className="px-5 py-3 text-center text-indigo-700 text-base">{overall_score} / 100</td>
                <td className="px-5 py-3 hidden md:table-cell text-xs font-normal text-slate-500">
                  Sum of all weighted component contributions
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

    </div>
  );
}

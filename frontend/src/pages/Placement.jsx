import React from 'react';
import { Briefcase, Code, Brain, Users, CheckCircle2, Clock, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function Placement({ student }) {
  if (!student) return null;
  const { placement_details, personal_info } = student;

  const chartData = [
    { metric: 'Aptitude Test', score: placement_details.aptitude_score },
    { metric: 'Coding Speed', score: placement_details.coding_score },
    { 
      metric: 'Mock Interview', 
      score: placement_details.mock_interview_score !== null ? placement_details.mock_interview_score : 0 
    },
    { metric: 'Readiness Index', score: placement_details.placement_readiness_score },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Placement & Recruitment Readiness</h2>
        <p className="text-sm text-slate-500">
          Campus recruitment benchmarks evaluating algorithmic coding, quantitative aptitude, and interview evaluations
        </p>
      </div>

      {/* Hero Metric Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">Composite Readiness Index</span>
          <h3 className="text-3xl font-extrabold text-white">
            Placement Readiness: {placement_details.placement_readiness_score} / 100
          </h3>
          <p className="text-xs text-indigo-200/80 max-w-xl">
            Calculated from calibrated assessments in coding challenges (40%), aptitude tests (30%), and mock technical interviews (30%).
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
            placement_details.placement_readiness_score >= 75 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' :
            placement_details.placement_readiness_score >= 60 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
            'bg-rose-500/20 text-rose-300 border border-rose-500/40'
          }`}>
            {placement_details.placement_readiness_score >= 75 ? 'Tier-1 Placement Ready' :
             placement_details.placement_readiness_score >= 60 ? 'Core Recruiter Ready' :
             'Intensive Coaching Required'}
          </span>
        </div>
      </div>

      {/* Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Aptitude Card */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Quantitative Aptitude</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Brain className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-slate-900">{placement_details.aptitude_score}</span>
            <span className="text-sm text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Target cutoff: <span className="font-semibold text-slate-700">65.0</span> ({placement_details.aptitude_score >= 65 ? 'Qualified' : 'Below cutoff'})
          </p>
        </div>

        {/* Coding Card */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Algorithmic Coding</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Code className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-slate-900">{placement_details.coding_score}</span>
            <span className="text-sm text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Target cutoff: <span className="font-semibold text-slate-700">65.0</span> ({placement_details.coding_score >= 65 ? 'Qualified' : 'Below cutoff'})
          </p>
        </div>

        {/* Mock Interview Card */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Mock Interview</span>
            <div className="w-8 h-8 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            {placement_details.mock_interview_score !== null ? (
              <>
                <span className="text-3xl font-extrabold text-slate-900">{placement_details.mock_interview_score}</span>
                <span className="text-sm text-slate-400">/ 100</span>
              </>
            ) : (
              <span className="text-xl font-bold text-amber-600 flex items-center">
                <Clock className="w-4 h-4 mr-1.5" /> Pending Scheduling
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {placement_details.mock_interview_score !== null 
              ? 'Evaluated by placement mentors' 
              : 'Interim score computed using Aptitude + Coding'}
          </p>
        </div>

      </div>

      {/* Bar Chart */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-1">Recruitment Benchmark Comparison</h3>
        <p className="text-xs text-slate-500 mb-4">Screening qualification target is 65+ across all components</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="metric" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip formatter={(val) => [`${val} / 100`, 'Score']} />
              <Bar dataKey="score" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}

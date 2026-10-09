import React from 'react';
import { Award, Code2, HeartHandshake, Calendar, CheckCircle2, Tag } from 'lucide-react';

export default function Skills({ student }) {
  if (!student) return null;
  const { skills_details, engagement_details } = student;

  const skillsList = skills_details.assessed_skills 
    ? skills_details.assessed_skills.split(',').map(s => s.trim()) 
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Skills Profiling & Certifications</h2>
        <p className="text-sm text-slate-500">
          Standardized department technical evaluations, behavioral soft skill appraisals, and verified credentials
        </p>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        {/* Technical Domain Score */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Technical Domain Score</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Code2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-slate-900">{skills_details.technical_skill_score}</span>
            <span className="text-sm text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Standard: <span className="font-semibold text-slate-700">{skills_details.technical_skill_score >= 75 ? 'Advanced Domain Competency' : 'Foundational / Developing'}</span>
          </p>
        </div>

        {/* Soft Skills Score */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Soft Skills & Communication</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <HeartHandshake className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            {skills_details.soft_skill_score !== null ? (
              <>
                <span className="text-3xl font-extrabold text-slate-900">{skills_details.soft_skill_score}</span>
                <span className="text-sm text-slate-400">/ 100</span>
              </>
            ) : (
              <span className="text-lg font-bold text-amber-600">Pending Evaluation</span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {skills_details.soft_skill_score !== null 
              ? 'Communication, teamwork & presentation' 
              : 'Scheduled for upcoming behavioral round'}
          </p>
        </div>

        {/* Verified Certifications */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Verified Certifications</span>
            <div className="w-8 h-8 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-slate-900">{engagement_details.certifications_count}</span>
            <span className="text-sm text-slate-400">Credentials</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Verified MOOC & industry certifications on file
          </p>
        </div>

      </div>

      {/* Evaluated Competency Tag Grid */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">Department Evaluated Skills Matrix</h3>
            <p className="text-xs text-slate-500">Core curricular topics evaluated during semester practicals</p>
          </div>
          <div className="flex items-center space-x-1.5 text-xs text-slate-500">
            <Calendar className="w-3.5 h-3.5 text-indigo-500" />
            <span>Assessed: {skills_details.assessment_date}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2.5 pt-2">
          {skillsList.map((skill, idx) => (
            <span 
              key={idx} 
              className="inline-flex items-center px-3.5 py-1.5 rounded-lg text-sm font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200"
            >
              <CheckCircle2 className="w-4 h-4 mr-1.5 text-indigo-500" />
              {skill}
            </span>
          ))}
        </div>
      </div>

    </div>
  );
}

import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Info, BookOpen, Briefcase } from 'lucide-react';

export default function RiskAnalysis({ student }) {
  if (!student) return null;
  const { risk_analysis } = student;
  const { academic_risk, placement_risk, overall_risk_summary } = risk_analysis;

  const getSeverityStyle = (level) => {
    if (level === 'High') return {
      badge: 'bg-rose-100 text-rose-800 border-rose-300',
      border: 'border-rose-200',
      bg: 'bg-rose-50/40',
      icon: 'text-rose-600'
    };
    if (level === 'Moderate') return {
      badge: 'bg-amber-100 text-amber-800 border-amber-300',
      border: 'border-amber-200',
      bg: 'bg-amber-50/40',
      icon: 'text-amber-600'
    };
    return {
      badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
      border: 'border-emerald-200',
      bg: 'bg-emerald-50/40',
      icon: 'text-emerald-600'
    };
  };

  const acadStyle = getSeverityStyle(academic_risk.level);
  const placeStyle = getSeverityStyle(placement_risk.level);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">My Risk Analysis</h2>
        <p className="text-sm text-slate-500">
          Explainable, rule-based diagnostics pinpointing specific academic vulnerabilities and career readiness risks
        </p>
      </div>

      {/* Summary Posture Banner */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex items-start space-x-3.5">
        <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900">Overall Diagnostic Diagnosis</h3>
          <p className="text-sm text-slate-600 mt-1">{overall_risk_summary}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Academic Risk Card */}
        <div className={`rounded-xl border ${acadStyle.border} ${acadStyle.bg} bg-white p-6 shadow-xs space-y-4`}>
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Academic Standing Risk</h3>
                <p className="text-xs text-slate-500">Evaluates backlogs, CGPA, attendance & coursework</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${acadStyle.badge}`}>
              {academic_risk.level} Severity
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-700 font-medium">
            {academic_risk.explanation}
          </p>

          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Triggered Indicators ({academic_risk.triggers_count})
            </h4>

            {academic_risk.triggers.length === 0 ? (
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center space-x-2 text-emerald-800 text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>All academic indicators are within safe thresholds. Zero backlogs and compliant attendance.</span>
              </div>
            ) : (
              academic_risk.triggers.map((t, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-white border border-slate-200 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900">{t.indicator}</span>
                    <span className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                      t.severity === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {t.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">{t.message}</p>
                  <div className="text-[11px] text-slate-400 flex items-center space-x-2 pt-1 border-t border-slate-50">
                    <span>Current: <strong className="text-slate-700">{t.current_value}</strong></span>
                    <span>•</span>
                    <span>Threshold: <strong className="text-slate-700">{t.threshold}</strong></span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Placement Risk Card */}
        <div className={`rounded-xl border ${placeStyle.border} ${placeStyle.bg} bg-white p-6 shadow-xs space-y-4`}>
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Placement Screening Risk</h3>
                <p className="text-xs text-slate-500">Evaluates coding speed, aptitude tests & interview readiness</p>
              </div>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${placeStyle.badge}`}>
              {placement_risk.level} Severity
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-700 font-medium">
            {placement_risk.explanation}
          </p>

          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Triggered Indicators ({placement_risk.triggers_count})
            </h4>

            {placement_risk.triggers.length === 0 ? (
              <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center space-x-2 text-emerald-800 text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Coding and aptitude scores meet competitive recruitment qualification cutoffs.</span>
              </div>
            ) : (
              placement_risk.triggers.map((t, idx) => (
                <div key={idx} className="p-3.5 rounded-lg bg-white border border-slate-200 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-900">{t.indicator}</span>
                    <span className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                      t.severity === 'Critical' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {t.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600">{t.message}</p>
                  <div className="text-[11px] text-slate-400 flex items-center space-x-2 pt-1 border-t border-slate-50">
                    <span>Current: <strong className="text-slate-700">{t.current_value}</strong></span>
                    <span>•</span>
                    <span>Cutoff: <strong className="text-slate-700">{t.threshold}</strong></span>
                  </div>
                </div>
              ))
            )}

            {/* Informational Pending Notices */}
            {placement_risk.pending_assessments && placement_risk.pending_assessments.length > 0 && (
              <div className="p-3 rounded-lg bg-blue-50/70 border border-blue-200 text-blue-800 text-xs flex items-start space-x-2">
                <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">Informational Note (Not Penalized):</p>
                  {placement_risk.pending_assessments.map((item, i) => (
                    <p key={i} className="mt-0.5">{item}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}

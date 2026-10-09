import React from 'react';
import { 
  Trophy, 
  BookOpen, 
  CalendarCheck, 
  Briefcase, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight,
  TrendingUp,
  Sparkles,
  ShieldAlert
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar 
} from 'recharts';

export default function Dashboard({ student, onNavigate }) {
  if (!student) return null;

  const { personal_info, success_score, risk_analysis, segmentation, recommendations, academic_details, attendance_details, placement_details } = student;
  const breakdown = success_score.breakdown.components;

  // Radar chart data covering the 7 categories
  const radarData = [
    { category: 'Academic', score: breakdown.academic.raw_score, fullMark: 100 },
    { category: 'Attendance', score: breakdown.attendance.raw_score, fullMark: 100 },
    { category: 'LMS Activity', score: breakdown.lms_activity.raw_score, fullMark: 100 },
    { category: 'Engagement', score: breakdown.engagement.raw_score, fullMark: 100 },
    { category: 'Placement', score: breakdown.placement.raw_score, fullMark: 100 },
    { category: 'Skills', score: breakdown.skills.raw_score, fullMark: 100 },
    { category: 'Feedback', score: breakdown.feedback.raw_score, fullMark: 100 },
  ];

  // Subject performance bar chart
  const subjectData = (academic_details.subjects_breakdown || []).map(s => ({
    subject: s.subject_name.length > 15 ? s.subject_name.substring(0, 14) + '...' : s.subject_name,
    fullName: s.subject_name,
    marks: s.marks
  }));

  const getRiskBadge = (level) => {
    if (level === 'High') return 'bg-rose-100 text-rose-800 border-rose-300';
    if (level === 'Moderate') return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-emerald-100 text-emerald-800 border-emerald-300';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 65) return 'text-indigo-600';
    return 'text-rose-600';
  };

  return (
    <div className="space-y-6">
      
      {/* 1. Welcome & Segment Header */}
      <div className="bg-gradient-to-r from-indigo-700 via-indigo-800 to-slate-900 rounded-2xl p-6 text-white shadow-md relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-200 text-xs font-semibold uppercase tracking-wider mb-1">
              <span>{personal_info.academic_year}</span>
              <span>•</span>
              <span>Semester {personal_info.semester}</span>
              <span>•</span>
              <span>{personal_info.department}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Welcome back, {personal_info.student_name}!
            </h1>
            <p className="text-indigo-100 text-sm mt-1 max-w-2xl">
              Student Persona: <strong className="text-white underline decoration-amber-400">{segmentation.segment_name}</strong>
            </p>
            <p className="text-indigo-200/80 text-xs mt-1">
              {segmentation.focus_strategy}
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4 text-center shrink-0 min-w-[160px]">
            <p className="text-xs uppercase tracking-wider text-indigo-200 font-medium">Success Score</p>
            <div className="text-4xl font-black text-amber-300 mt-1">
              {success_score.overall_score}
              <span className="text-xs font-normal text-indigo-200 ml-1">/100</span>
            </div>
            <button 
              onClick={() => onNavigate('score')} 
              className="mt-2 text-xs font-medium text-white hover:text-amber-200 flex items-center justify-center space-x-1 mx-auto"
            >
              <span>View Breakdown</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Card 1: CGPA & Backlogs */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-indigo-200 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">CGPA Standing</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{academic_details.cgpa.toFixed(2)}</h3>
              <p className="text-xs text-slate-500 mt-1">
                Avg Marks: <span className="font-semibold text-slate-700">{academic_details.average_marks}</span>
              </p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <BookOpen className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Backlogs Status:</span>
            <span className={`font-semibold ${academic_details.backlogs === 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {academic_details.backlogs === 0 ? '0 Backlogs (Clear)' : `${academic_details.backlogs} Active Backlog(s)`}
            </span>
          </div>
        </div>

        {/* Card 2: Attendance */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-indigo-200 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Overall Attendance</p>
              <h3 className={`text-2xl font-bold mt-1 ${attendance_details.overall_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
                {attendance_details.overall_percentage}%
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                {attendance_details.classes_attended} / {attendance_details.classes_scheduled} Lectures
              </p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CalendarCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Mandatory Cutoff (75%):</span>
            <span className={`font-semibold ${attendance_details.overall_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {attendance_details.overall_percentage >= 75 ? 'Eligible' : 'Debarment Risk'}
            </span>
          </div>
        </div>

        {/* Card 3: LMS & Assignment Rate */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-indigo-200 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">LMS Submissions</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {student.lms_details.assignment_completion_percentage}%
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                {student.lms_details.assignments_completed} of {student.lms_details.total_assignments} Assignments
              </p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Monthly Logins:</span>
            <span className="font-semibold text-slate-700">{student.lms_details.login_frequency} Logins/mo</span>
          </div>
        </div>

        {/* Card 4: Placement Readiness */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs hover:border-indigo-200 transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Placement Readiness</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {placement_details.placement_readiness_score}
                <span className="text-xs font-normal text-slate-500 ml-1">/100</span>
              </h3>
              <p className="text-xs text-slate-500 mt-1">
                Coding: <span className="font-semibold text-slate-700">{placement_details.coding_score}</span> | Aptitude: <span className="font-semibold text-slate-700">{placement_details.aptitude_score}</span>
              </p>
            </div>
            <div className="w-10 h-10 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Mock Interview:</span>
            <span className="font-semibold text-slate-700">
              {placement_details.mock_interview_score ? `${placement_details.mock_interview_score}/100` : 'Pending'}
            </span>
          </div>
        </div>

      </div>

      {/* 3. Risk Diagnostic Alert Banner */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900">Diagnostic Risk Status</h4>
            <p className="text-xs text-slate-600 mt-0.5">{risk_analysis.overall_risk_summary}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getRiskBadge(risk_analysis.academic_risk.level)}`}>
            Academic: {risk_analysis.academic_risk.level}
          </span>
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getRiskBadge(risk_analysis.placement_risk.level)}`}>
            Placement: {risk_analysis.placement_risk.level}
          </span>
          <button 
            onClick={() => onNavigate('risks')}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-medium transition-colors"
          >
            Review Triggers
          </button>
        </div>
      </div>

      {/* 4. Charts Row: 7 Categories Radar & Subject Marks Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Radar Chart: 7 Categories */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">7-Dimension Competency Radar</h3>
              <p className="text-xs text-slate-500">Holistic balance across all academic and co-curricular domains</p>
            </div>
            <button onClick={() => onNavigate('score')} className="text-xs font-medium text-indigo-600 hover:text-indigo-800">
              Scores Detail →
            </button>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="category" tick={{ fill: '#475569', fontSize: 11 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <Radar name="Student" dataKey="score" stroke="#4f46e5" fill="#6366f1" fillOpacity={0.4} />
                <Tooltip formatter={(value) => [`${value}/100`, 'Score']} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart: Subject Marks */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Semester Course Performance</h3>
              <p className="text-xs text-slate-500">Marks obtained in current semester courses (Pass cutoff: 40)</p>
            </div>
            <button onClick={() => onNavigate('academic')} className="text-xs font-medium text-indigo-600 hover:text-indigo-800">
              Academics →
            </button>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={subjectData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 11 }} angle={-15} textAnchor="end" />
                <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip formatter={(val, name, item) => [`${val} Marks`, item.payload.fullName]} />
                <Bar dataKey="marks" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* 5. Top Personalized Improvement Recommendations */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Personalized Improvement Priorities</h3>
            <p className="text-xs text-slate-500">Targeted actions derived from your actual metrics and risk flags</p>
          </div>
          <button 
            onClick={() => onNavigate('plan')} 
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
          >
            <span>Complete Plan ({recommendations.length})</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.slice(0, 2).map((rec, idx) => (
            <div 
              key={idx}
              className={`p-4 rounded-xl border ${
                rec.priority === 'Critical' ? 'border-rose-200 bg-rose-50/50' :
                rec.priority === 'High' ? 'border-amber-200 bg-amber-50/50' :
                'border-slate-200 bg-slate-50/50'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-0.5 rounded-md text-xs font-bold uppercase tracking-wider ${
                  rec.priority === 'Critical' ? 'bg-rose-100 text-rose-700' :
                  rec.priority === 'High' ? 'bg-amber-100 text-amber-800' :
                  'bg-blue-100 text-blue-700'
                }`}>
                  {rec.priority} Priority
                </span>
                <span className="text-xs font-medium text-slate-500">{rec.category}</span>
              </div>
              <h4 className="text-sm font-semibold text-slate-900">{rec.suggested_action}</h4>
              <div className="mt-2 text-xs text-slate-600 space-y-1">
                <p><span className="font-medium text-slate-700">Reason:</span> {rec.reason}</p>
                <p><span className="font-medium text-slate-700">Target:</span> <span className="font-semibold text-indigo-700">{rec.improvement_target}</span></p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}

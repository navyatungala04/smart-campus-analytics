import React from 'react';
import { BookOpen, AlertCircle, CheckCircle2, TrendingUp, Award } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function Academic({ student }) {
  if (!student) return null;
  const { academic_details, personal_info } = student;
  const subjects = academic_details.subjects_breakdown || [];

  const chartData = subjects.map(s => ({
    name: s.subject_name.length > 18 ? s.subject_name.substring(0, 16) + '...' : s.subject_name,
    fullName: s.subject_name,
    marks: s.marks
  }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Academic Performance</h2>
        <p className="text-sm text-slate-500">
          Curriculum assessment metrics, cumulative GPA, and course marks for Semester {personal_info.semester}
        </p>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Cumulative GPA</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-extrabold text-slate-900">{academic_details.cgpa.toFixed(2)}</span>
            <span className="text-sm text-slate-400">/ 10.00</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Standing: <span className="font-semibold text-indigo-600">{academic_details.cgpa >= 8.5 ? 'First Class Distinction' : academic_details.cgpa >= 6.5 ? 'First Class' : 'Second Class / Needs Review'}</span>
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Active Backlogs</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-3xl font-extrabold ${academic_details.backlogs === 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {academic_details.backlogs}
            </span>
            <span className="text-sm text-slate-400">Backlogs</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Placement eligibility: <span className="font-semibold text-slate-700">{academic_details.backlogs === 0 ? 'Eligible for all drives' : 'Restricted (Remedial required)'}</span>
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Average Subject Marks</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-extrabold text-slate-900">{academic_details.average_marks}</span>
            <span className="text-sm text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Across {subjects.length} enrolled semester subjects
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Marks Range</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-2xl font-bold text-slate-800">{academic_details.min_marks} - {academic_details.max_marks}</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Min score: <span className={academic_details.min_marks < 40 ? 'text-rose-600 font-semibold' : 'text-slate-700'}>{academic_details.min_marks}</span> | Max score: <span className="text-slate-700 font-semibold">{academic_details.max_marks}</span>
          </p>
        </div>

      </div>

      {/* Coursework Bar Chart */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-1">Subject Mark Distribution</h3>
        <p className="text-xs text-slate-500 mb-4">Passing cutoff is 40. Target benchmark is 75+.</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip formatter={(val, name, item) => [`${val} / 100`, item.payload.fullName]} />
              <Bar dataKey="marks" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Enrolled Courses Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-900">Enrolled Semester Courses Detail</h3>
          <span className="text-xs text-slate-500">{subjects.length} Subjects Active</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
              <tr>
                <th className="px-5 py-3 text-left">Course Name</th>
                <th className="px-5 py-3 text-center">Marks Obtained</th>
                <th className="px-5 py-3 text-center">Benchmark (75)</th>
                <th className="px-5 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {subjects.map((sub, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-5 py-3.5 font-medium text-slate-900">{sub.subject_name}</td>
                  <td className="px-5 py-3.5 text-center font-bold text-slate-800">{sub.marks} / 100</td>
                  <td className="px-5 py-3.5 text-center">
                    <span className={`text-xs font-semibold ${sub.marks >= 75 ? 'text-emerald-600' : 'text-slate-500'}`}>
                      {sub.marks >= 75 ? 'Above Target' : `${(75 - sub.marks).toFixed(1)} below`}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-center">
                    {sub.passed ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 mr-1" /> Passed
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        <AlertCircle className="w-3 h-3 mr-1" /> Failed (&lt; 40)
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}

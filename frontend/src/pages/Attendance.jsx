import React from 'react';
import { CalendarCheck, AlertTriangle, CheckCircle, ShieldCheck, Clock } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from 'recharts';

export default function Attendance({ student }) {
  if (!student) return null;
  const { attendance_details } = student;
  const list = attendance_details.attendance_breakdown || [];

  const chartData = list.map(item => ({
    name: item.subject_name.length > 18 ? item.subject_name.substring(0, 16) + '...' : item.subject_name,
    fullName: item.subject_name,
    percentage: item.attendance_percentage
  }));

  // Consecutive classes needed to reach 75%
  const totalAtt = attendance_details.classes_attended;
  const totalSch = attendance_details.classes_scheduled;
  const neededClasses = attendance_details.overall_percentage < 75.0
    ? Math.max(1, Math.ceil((0.75 * totalSch - totalAtt) / 0.25))
    : 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Attendance Monitoring</h2>
        <p className="text-sm text-slate-500">
          Official attendance percentage and statutory university eligibility tracking (Mandatory threshold: 75.0%)
        </p>
      </div>

      {/* Top Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Overall Attendance</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-3xl font-extrabold ${attendance_details.overall_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {attendance_details.overall_percentage}%
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Status: <span className={`font-semibold ${attendance_details.overall_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {attendance_details.overall_percentage >= 75 ? 'Exam Eligible' : 'Debarment Warning'}
            </span>
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Classes Attended</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-extrabold text-slate-900">{attendance_details.classes_attended}</span>
            <span className="text-sm text-slate-400">/ {attendance_details.classes_scheduled}</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Total lectures conducted this semester
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Subjects Below 75%</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-3xl font-extrabold ${attendance_details.low_attendance_subjects === 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {attendance_details.low_attendance_subjects}
            </span>
            <span className="text-sm text-slate-400">Subjects</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Subject-level detention cutoff: 75%
          </p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Consecutive Target</p>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className={`text-3xl font-extrabold ${neededClasses === 0 ? 'text-emerald-600' : 'text-amber-600'}`}>
              {neededClasses === 0 ? '0' : `+${neededClasses}`}
            </span>
            <span className="text-sm text-slate-400">Classes</span>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {neededClasses === 0 ? 'Safe buffer maintained' : 'Required to reach 75% threshold'}
          </p>
        </div>

      </div>

      {/* Statutory Alert Banner */}
      {attendance_details.overall_percentage < 75.0 ? (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-5 flex items-start space-x-3.5 text-rose-900">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div className="text-sm">
            <h4 className="font-bold">Statutory Attendance Warning: Immediate Recovery Required</h4>
            <p className="mt-1 text-rose-800 text-xs sm:text-sm">
              Your overall attendance is currently <strong>{attendance_details.overall_percentage}%</strong>. 
              Under university academic regulations, you must attend the next <strong>{neededClasses} consecutive lectures</strong> without absence to restore eligibility and prevent examination debarment.
            </p>
          </div>
        </div>
      ) : (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 flex items-start space-x-3.5 text-emerald-900">
          <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
          <div className="text-sm">
            <h4 className="font-bold">Attendance Compliant</h4>
            <p className="mt-1 text-emerald-800 text-xs sm:text-sm">
              Your attendance is above the mandatory 75% university benchmark across courses. Continue regular attendance to safeguard your internal evaluation points.
            </p>
          </div>
        </div>
      )}

      {/* Attendance Chart with 75% Reference Line */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
        <h3 className="text-base font-bold text-slate-900 mb-1">Subject-Wise Attendance Percentage</h3>
        <p className="text-xs text-slate-500 mb-4">Dotted red line indicates mandatory 75% cutoff</p>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip formatter={(val, name, item) => [`${val}%`, item.payload.fullName]} />
              <ReferenceLine y={75} stroke="#ef4444" strokeDasharray="3 3" label={{ value: '75% Cutoff', fill: '#ef4444', fontSize: 10 }} />
              <Bar dataKey="percentage" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Granular Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-sm font-bold text-slate-900">Course Attendance Breakdown</h3>
          <span className="text-xs text-slate-500">{list.length} Courses Tracked</span>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
              <tr>
                <th className="px-5 py-3 text-left">Course Name</th>
                <th className="px-5 py-3 text-center">Attended / Total</th>
                <th className="px-5 py-3 text-center">Attendance %</th>
                <th className="px-5 py-3 text-center">Eligibility</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {list.map((c, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="px-5 py-3.5 font-medium text-slate-900">{c.subject_name}</td>
                  <td className="px-5 py-3.5 text-center text-slate-600">{c.classes_attended} / {c.total_classes}</td>
                  <td className="px-5 py-3.5 text-center font-bold text-slate-800">{c.attendance_percentage}%</td>
                  <td className="px-5 py-3.5 text-center">
                    {c.is_below_75 ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                        <AlertTriangle className="w-3 h-3 mr-1" /> Below 75%
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <CheckCircle className="w-3 h-3 mr-1" /> Eligible
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

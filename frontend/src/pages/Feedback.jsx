import React from 'react';
import { MessageSquareText, Star, Calendar, UserCheck, Heart } from 'lucide-react';

export default function Feedback({ student }) {
  if (!student) return null;
  const { feedback_details } = student;

  const facPercent = Math.round(((feedback_details.faculty_feedback_score - 1.0) / 4.0) * 100);
  const satPercent = feedback_details.student_satisfaction_score !== null 
    ? Math.round(((feedback_details.student_satisfaction_score - 1.0) / 4.0) * 100)
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Institutional & Mentorship Feedback</h2>
        <p className="text-sm text-slate-500">
          Faculty advisor appraisals, student satisfaction sentiment, and academic counseling notes
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Faculty Mentor Appraisal Card */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Faculty Advisor Appraisal</h3>
                <p className="text-xs text-slate-500">Semester mentorship rating (Scale: 1.0 - 5.0)</p>
              </div>
            </div>
            <div className="flex items-center space-x-1 text-xs text-slate-400">
              <Calendar className="w-3.5 h-3.5" />
              <span>{feedback_details.feedback_date}</span>
            </div>
          </div>

          <div className="flex items-baseline space-x-3">
            <span className="text-4xl font-extrabold text-slate-900">
              {feedback_details.faculty_feedback_score.toFixed(1)}
            </span>
            <span className="text-sm text-slate-400">/ 5.0 Stars</span>
            <span className="text-xs font-semibold text-indigo-600 ml-auto">
              ({facPercent}% Scaled)
            </span>
          </div>

          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div 
              className="bg-indigo-600 h-full rounded-full transition-all"
              style={{ width: `${facPercent}%` }}
            ></div>
          </div>

          <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200/60 leading-relaxed">
            <strong>Advisor Remark:</strong> Student demonstrates consistent academic engagement and respects instructional timelines. Focus on strengthening technical coding problem sets is recommended for upcoming recruitment cycles.
          </p>
        </div>

        {/* Student Satisfaction Survey Card */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-lg bg-pink-50 text-pink-600 flex items-center justify-center">
                <Heart className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Student Campus Experience</h3>
                <p className="text-xs text-slate-500">End-of-term student satisfaction response</p>
              </div>
            </div>
          </div>

          {feedback_details.student_satisfaction_score !== null ? (
            <>
              <div className="flex items-baseline space-x-3">
                <span className="text-4xl font-extrabold text-slate-900">
                  {feedback_details.student_satisfaction_score.toFixed(1)}
                </span>
                <span className="text-sm text-slate-400">/ 5.0 Rating</span>
                <span className="text-xs font-semibold text-pink-600 ml-auto">
                  ({satPercent}% Scaled)
                </span>
              </div>

              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-pink-500 h-full rounded-full transition-all"
                  style={{ width: `${satPercent}%` }}
                ></div>
              </div>

              <p className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200/60 leading-relaxed">
                Student self-reported positive learning experiences regarding departmental labs and course resources.
              </p>
            </>
          ) : (
            <div className="py-6 text-center space-y-2">
              <p className="text-sm font-semibold text-amber-700">Optional Survey Not Submitted</p>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                The satisfaction survey was optional. Under our missing-data policy, faculty feedback carries 100% weighting without reducing your score.
              </p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}

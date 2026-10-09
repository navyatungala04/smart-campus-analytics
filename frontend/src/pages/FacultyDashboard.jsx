import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, 
  Search, 
  Save, 
  RotateCcw, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  User, 
  LogOut, 
  BookOpen, 
  CalendarCheck, 
  TrendingUp, 
  ShieldAlert, 
  Sparkles,
  ArrowRight,
  Filter
} from 'lucide-react';
import { 
  fetchStudents, 
  fetchStudentProfile, 
  updateStudentRecords 
} from '../services/api';

export default function FacultyDashboard({ user, onLogout }) {
  const [students, setStudents] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedStudentId, setSelectedStudentId] = useState(null);
  const [studentProfile, setStudentProfile] = useState(null);
  
  // Editable form state for courses
  const [courseRows, setCourseRows] = useState([]);
  const [formErrors, setFormErrors] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingStudents, setIsLoadingStudents] = useState(true);
  const [isLoadingProfile, setIsLoadingProfile] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState(null); // { type: 'success' | 'error', text: '' }

  // 1. Load students list on mount
  useEffect(() => {
    async function loadDirectory() {
      try {
        setIsLoadingStudents(true);
        const data = await fetchStudents();
        const list = data.students || data || [];
        setStudents(list);
        if (list.length > 0) {
          // Select first student by default
          setSelectedStudentId(list[0].student_id);
        }
      } catch (err) {
        console.error('Failed to load students:', err);
        setFeedbackMessage({
          type: 'error',
          text: 'Failed to load students directory. Please verify backend connectivity.'
        });
      } finally {
        setIsLoadingStudents(false);
      }
    }
    loadDirectory();
  }, []);

  // 2. Load student profile whenever selectedStudentId changes
  useEffect(() => {
    if (!selectedStudentId) return;

    async function loadSelectedProfile() {
      try {
        setIsLoadingProfile(true);
        setFeedbackMessage(null);
        setFormErrors({});
        const profile = await fetchStudentProfile(selectedStudentId);
        setStudentProfile(profile);
        initCourseRows(profile);
      } catch (err) {
        console.error('Failed to load student profile:', err);
        setFeedbackMessage({
          type: 'error',
          text: `Failed to load details for ${selectedStudentId}: ${err.message}`
        });
      } finally {
        setIsLoadingProfile(false);
      }
    }
    loadSelectedProfile();
  }, [selectedStudentId]);

  // Build merged course editable list from academic and attendance details
  const initCourseRows = (profile) => {
    if (!profile) return;
    const academicList = profile.academic_details?.subjects_breakdown || [];
    const attendanceList = profile.attendance_details?.attendance_breakdown || [];

    // Map by subject_name
    const subjectMap = new Map();
    academicList.forEach(item => {
      subjectMap.set(item.subject_name, {
        subject_name: item.subject_name,
        marks: item.marks,
        classes_attended: 0,
        total_classes: 50,
      });
    });

    attendanceList.forEach(item => {
      if (subjectMap.has(item.subject_name)) {
        const existing = subjectMap.get(item.subject_name);
        existing.classes_attended = item.classes_attended;
        existing.total_classes = item.total_classes;
      } else {
        subjectMap.set(item.subject_name, {
          subject_name: item.subject_name,
          marks: 75,
          classes_attended: item.classes_attended,
          total_classes: item.total_classes,
        });
      }
    });

    setCourseRows(Array.from(subjectMap.values()));
  };

  // Handle Marks input change
  const handleMarksChange = (subjectName, value) => {
    const num = value === '' ? '' : parseFloat(value);
    setCourseRows(prev => prev.map(row => {
      if (row.subject_name === subjectName) {
        return { ...row, marks: num };
      }
      return row;
    }));
    validateField(subjectName, 'marks', num);
  };

  // Handle Attendance Attended input change
  const handleAttendedChange = (subjectName, value) => {
    const num = value === '' ? '' : parseInt(value, 10);
    setCourseRows(prev => prev.map(row => {
      if (row.subject_name === subjectName) {
        const updated = { ...row, classes_attended: num };
        validateAttendance(subjectName, updated.classes_attended, updated.total_classes);
        return updated;
      }
      return row;
    }));
  };

  // Handle Total Classes input change
  const handleTotalClassesChange = (subjectName, value) => {
    const num = value === '' ? '' : parseInt(value, 10);
    setCourseRows(prev => prev.map(row => {
      if (row.subject_name === subjectName) {
        const updated = { ...row, total_classes: num };
        validateAttendance(subjectName, updated.classes_attended, updated.total_classes);
        return updated;
      }
      return row;
    }));
  };

  // Real-time validation
  const validateField = (subjectName, field, value) => {
    setFormErrors(prev => {
      const copy = { ...prev };
      const key = `${subjectName}_${field}`;
      if (field === 'marks') {
        if (value === '' || isNaN(value)) {
          copy[key] = 'Marks required';
        } else if (value < 0 || value > 100) {
          copy[key] = 'Must be 0-100';
        } else {
          delete copy[key];
        }
      }
      return copy;
    });
  };

  const validateAttendance = (subjectName, attended, total) => {
    setFormErrors(prev => {
      const copy = { ...prev };
      const attKey = `${subjectName}_att`;
      const totKey = `${subjectName}_tot`;

      if (attended === '' || isNaN(attended) || attended < 0) {
        copy[attKey] = 'Attended >= 0';
      } else {
        delete copy[attKey];
      }

      if (total === '' || isNaN(total) || total <= 0) {
        copy[totKey] = 'Total > 0';
      } else {
        delete copy[totKey];
      }

      if (!copy[attKey] && !copy[totKey]) {
        if (attended > total) {
          copy[attKey] = 'Attended > Total';
        }
      }

      return copy;
    });
  };

  const hasErrors = Object.keys(formErrors).length > 0;

  // Handle Save and Recalculate
  const handleSaveChanges = async () => {
    if (hasErrors) {
      setFeedbackMessage({
        type: 'error',
        text: 'Please correct highlighted errors before saving.'
      });
      return;
    }

    try {
      setIsSaving(true);
      setFeedbackMessage(null);

      const academicPayload = courseRows.map(r => ({
        subject_name: r.subject_name,
        marks: parseFloat(r.marks)
      }));

      const attendancePayload = courseRows.map(r => ({
        subject_name: r.subject_name,
        classes_attended: parseInt(r.classes_attended, 10),
        total_classes: parseInt(r.total_classes, 10)
      }));

      const response = await updateStudentRecords(selectedStudentId, {
        academic_updates: academicPayload,
        attendance_updates: attendancePayload
      });

      if (response.updated_profile) {
        setStudentProfile(response.updated_profile);
        initCourseRows(response.updated_profile);
        
        // Also refresh student list item so score in directory reflects update
        setStudents(prev => prev.map(s => {
          if (s.student_id === selectedStudentId) {
            return {
              ...s,
              cgpa: response.updated_profile.academic_details?.cgpa || s.cgpa,
              success_score: response.updated_profile.success_score?.overall_score || s.success_score,
              academic_risk_level: response.updated_profile.risk_analysis?.academic_risk?.risk_level || s.academic_risk_level
            };
          }
          return s;
        }));

        setFeedbackMessage({
          type: 'success',
          text: `Updated successfully! New Success Score: ${response.updated_profile.success_score?.overall_score.toFixed(1)}/100 • Academic Risk: ${response.updated_profile.risk_analysis?.academic_risk?.risk_level} • CGPA: ${response.updated_profile.academic_details?.cgpa.toFixed(2)}`
        });
      }
    } catch (err) {
      console.error('Update failed:', err);
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Failed to update student records.'
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Reset current form to original profile values
  const handleReset = () => {
    if (studentProfile) {
      initCourseRows(studentProfile);
      setFormErrors({});
      setFeedbackMessage(null);
    }
  };

  // Filter students by search query and department
  const departments = ['All', ...new Set(students.map(s => s.department).filter(Boolean))];

  const filteredStudents = students.filter(s => {
    const matchesSearch = 
      (s.name && s.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (s.student_id && s.student_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesDept = selectedDept === 'All' || s.department === selectedDept;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      
      {/* Top Navigation Header for Faculty */}
      <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-40 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight text-white">Smart Campus Analytics</span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  Faculty Portal
                </span>
              </div>
              <p className="text-xs text-slate-400">Academic &amp; Attendance Management Console</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs">
              <User className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-slate-300 font-medium">
                {user?.student_name || 'Prof. Rajesh Sharma'}
              </span>
              <span className="text-slate-500 font-mono">({user?.student_id || 'FAC001'})</span>
            </div>

            <button
              onClick={onLogout}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 border border-rose-500/30 transition-colors cursor-pointer"
              title="Sign Out of Faculty Portal"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex-1 flex flex-col gap-6">
        
        {/* Banner Alert Feedback */}
        {feedbackMessage && (
          <div className={`p-4 rounded-xl border flex items-start space-x-3 text-sm shadow-xs animate-fadeIn ${
            feedbackMessage.type === 'success' 
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900' 
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}>
            {feedbackMessage.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div className="flex-1 font-medium">{feedbackMessage.text}</div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT COLUMN: Student Directory & Search (4 columns) */}
          <div className="lg:col-span-4 bg-white rounded-2xl border border-slate-200 shadow-xs p-4 flex flex-col space-y-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center justify-between">
                <span>Student Directory</span>
                <span className="text-xs font-normal text-slate-500">
                  {filteredStudents.length} of {students.length}
                </span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">Select a student to edit marks and attendance</p>
            </div>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by student name or ID..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {/* Department Filter */}
            <div className="flex items-center space-x-2 text-xs">
              <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <select
                value={selectedDept}
                onChange={e => setSelectedDept(e.target.value)}
                className="w-full py-1.5 px-2.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs focus:outline-hidden focus:ring-1 focus:ring-indigo-500"
              >
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            {/* Student List */}
            <div className="overflow-y-auto max-h-[560px] divide-y divide-slate-100 pr-1">
              {isLoadingStudents ? (
                <div className="py-8 text-center text-xs text-slate-400">Loading student roster...</div>
              ) : filteredStudents.length === 0 ? (
                <div className="py-8 text-center text-xs text-slate-400">No matching students found</div>
              ) : (
                filteredStudents.map(s => {
                  const isSelected = s.student_id === selectedStudentId;
                  return (
                    <button
                      key={s.student_id}
                      onClick={() => setSelectedStudentId(s.student_id)}
                      className={`w-full text-left p-3 rounded-xl transition-all flex items-center justify-between cursor-pointer ${
                        isSelected 
                          ? 'bg-indigo-50 border border-indigo-200 text-indigo-900 shadow-xs' 
                          : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      <div className="min-w-0 pr-2">
                        <p className="text-xs font-bold truncate text-slate-900">{s.name}</p>
                        <div className="flex items-center space-x-2 mt-0.5 text-[11px] text-slate-500">
                          <span className="font-mono">{s.student_id}</span>
                          <span>•</span>
                          <span className="truncate">{s.department}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          s.academic_risk_level === 'High' 
                            ? 'bg-rose-100 text-rose-700' 
                            : s.academic_risk_level === 'Medium'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}>
                          {s.academic_risk_level || 'Low'} Risk
                        </span>
                      </div>
                    </button>
                  );
                })
              )}
            </div>

          </div>

          {/* RIGHT COLUMN: Profile Overview & Editable Evaluation (8 columns) */}
          <div className="lg:col-span-8 space-y-6">
            
            {isLoadingProfile || !studentProfile ? (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-xs">
                <div className="w-8 h-8 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"></div>
                <p className="text-xs font-medium text-slate-500">Loading student dossier...</p>
              </div>
            ) : (
              <>
                {/* 1. Student Summary Banner */}
                <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-slate-100">
                    <div>
                      <div className="flex items-center space-x-2">
                        <h1 className="text-xl font-bold text-slate-900">
                          {studentProfile.personal_info.name}
                        </h1>
                        <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                          {studentProfile.student_id}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        {studentProfile.personal_info.department} • Semester {studentProfile.personal_info.semester} (Section {studentProfile.personal_info.section})
                      </p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                        {studentProfile.segmentation?.persona_name || 'Standard Learner'}
                      </span>
                    </div>
                  </div>

                  {/* Key Stats Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Success Score</span>
                      <div className="flex items-baseline space-x-1 mt-0.5">
                        <span className="text-xl font-extrabold text-indigo-600">
                          {studentProfile.success_score?.overall_score.toFixed(1)}
                        </span>
                        <span className="text-xs text-slate-400">/ 100</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Cumulative GPA</span>
                      <div className="flex items-baseline space-x-1 mt-0.5">
                        <span className="text-xl font-extrabold text-slate-900">
                          {studentProfile.academic_details?.cgpa.toFixed(2)}
                        </span>
                        <span className="text-xs text-slate-400">/ 10</span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Overall Attendance</span>
                      <div className="flex items-baseline space-x-1 mt-0.5">
                        <span className={`text-xl font-extrabold ${
                          studentProfile.attendance_details?.overall_percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'
                        }`}>
                          {studentProfile.attendance_details?.overall_percentage}%
                        </span>
                      </div>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Academic Risk</span>
                      <div className="mt-0.5">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-md ${
                          studentProfile.risk_analysis?.academic_risk?.risk_level === 'High'
                            ? 'bg-rose-100 text-rose-800'
                            : studentProfile.risk_analysis?.academic_risk?.risk_level === 'Medium'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}>
                          {studentProfile.risk_analysis?.academic_risk?.risk_level}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 2. Interactive Edit Table for Marks & Attendance */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                  <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div>
                      <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                        <BookOpen className="w-4 h-4 text-indigo-600" />
                        <span>Update Subject Marks &amp; Attendance Records</span>
                      </h2>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Modify subject scores (0-100) and lecture attendances. Recalculation triggers automatically upon saving.
                      </p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={handleReset}
                        disabled={isSaving}
                        className="flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold cursor-pointer disabled:opacity-50"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        <span>Reset</span>
                      </button>

                      <button
                        onClick={handleSaveChanges}
                        disabled={isSaving || hasErrors}
                        className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-md shadow-indigo-500/20 disabled:opacity-50 cursor-pointer transition-all"
                      >
                        {isSaving ? (
                          <>
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            <span>Recalculating...</span>
                          </>
                        ) : (
                          <>
                            <Save className="w-3.5 h-3.5" />
                            <span>Save &amp; Recalculate</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Editable Courses Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-xs">
                      <thead className="bg-slate-50 text-slate-500 uppercase font-semibold">
                        <tr>
                          <th className="px-4 py-3 text-left">Subject / Course</th>
                          <th className="px-4 py-3 text-center w-28">Marks (0-100)</th>
                          <th className="px-4 py-3 text-center w-28">Attended</th>
                          <th className="px-4 py-3 text-center w-28">Total Lectures</th>
                          <th className="px-4 py-3 text-center w-28">Attendance %</th>
                          <th className="px-4 py-3 text-center w-24">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {courseRows.map(row => {
                          const marksErr = formErrors[`${row.subject_name}_marks`];
                          const attErr = formErrors[`${row.subject_name}_att`];
                          const totErr = formErrors[`${row.subject_name}_tot`];
                          
                          const attPct = (row.total_classes && row.total_classes > 0)
                            ? ((row.classes_attended / row.total_classes) * 100).toFixed(1)
                            : 0;

                          const isPassing = !isNaN(row.marks) && row.marks >= 40;
                          const isCompliant = parseFloat(attPct) >= 75.0;

                          return (
                            <tr key={row.subject_name} className="hover:bg-slate-50/50">
                              {/* Subject Name */}
                              <td className="px-4 py-3 font-semibold text-slate-900">
                                {row.subject_name}
                              </td>

                              {/* Marks Input */}
                              <td className="px-4 py-3 text-center">
                                <input
                                  type="number"
                                  min="0"
                                  max="100"
                                  step="0.5"
                                  value={row.marks}
                                  onChange={e => handleMarksChange(row.subject_name, e.target.value)}
                                  className={`w-20 px-2 py-1 text-center font-bold text-xs rounded-lg border focus:outline-hidden focus:ring-2 ${
                                    marksErr
                                      ? 'border-rose-400 bg-rose-50 text-rose-700 focus:ring-rose-400'
                                      : 'border-slate-200 bg-white text-slate-800 focus:ring-indigo-500'
                                  }`}
                                />
                                {marksErr && (
                                  <p className="text-[10px] text-rose-600 font-semibold mt-0.5">{marksErr}</p>
                                )}
                              </td>

                              {/* Attended Classes */}
                              <td className="px-4 py-3 text-center">
                                <input
                                  type="number"
                                  min="0"
                                  value={row.classes_attended}
                                  onChange={e => handleAttendedChange(row.subject_name, e.target.value)}
                                  className={`w-20 px-2 py-1 text-center font-bold text-xs rounded-lg border focus:outline-hidden focus:ring-2 ${
                                    attErr
                                      ? 'border-rose-400 bg-rose-50 text-rose-700 focus:ring-rose-400'
                                      : 'border-slate-200 bg-white text-slate-800 focus:ring-indigo-500'
                                  }`}
                                />
                                {attErr && (
                                  <p className="text-[10px] text-rose-600 font-semibold mt-0.5">{attErr}</p>
                                )}
                              </td>

                              {/* Total Classes */}
                              <td className="px-4 py-3 text-center">
                                <input
                                  type="number"
                                  min="1"
                                  value={row.total_classes}
                                  onChange={e => handleTotalClassesChange(row.subject_name, e.target.value)}
                                  className={`w-20 px-2 py-1 text-center font-bold text-xs rounded-lg border focus:outline-hidden focus:ring-2 ${
                                    totErr
                                      ? 'border-rose-400 bg-rose-50 text-rose-700 focus:ring-rose-400'
                                      : 'border-slate-200 bg-white text-slate-800 focus:ring-indigo-500'
                                  }`}
                                />
                                {totErr && (
                                  <p className="text-[10px] text-rose-600 font-semibold mt-0.5">{totErr}</p>
                                )}
                              </td>

                              {/* Live Attendance Percentage */}
                              <td className="px-4 py-3 text-center font-bold">
                                <span className={`px-2 py-0.5 rounded-md ${
                                  isCompliant 
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                                }`}>
                                  {attPct}%
                                </span>
                              </td>

                              {/* Academic Status */}
                              <td className="px-4 py-3 text-center">
                                {isPassing ? (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full font-semibold text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200">
                                    Passing
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full font-semibold text-[10px] bg-rose-50 text-rose-700 border border-rose-200">
                                    Backlog
                                  </span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                </div>

                {/* 3. Real-time Recalculation Results Preview */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  
                  {/* Success Score & Persona Diagnostics */}
                  <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center space-x-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Recalculated Success Score Profile</span>
                    </h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-600">Student Success Score</span>
                        <span className="font-extrabold text-indigo-600">
                          {studentProfile.success_score?.overall_score.toFixed(1)} / 100
                        </span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div 
                          className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, studentProfile.success_score?.overall_score || 0)}%` }}
                        ></div>
                      </div>
                      
                      <div className="pt-2 text-xs text-slate-500 flex justify-between">
                        <span>Classification Persona:</span>
                        <span className="font-semibold text-slate-800">
                          {studentProfile.segmentation?.persona_name}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Risk Diagnostics */}
                  <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center space-x-1.5">
                      <ShieldAlert className="w-3.5 h-3.5 text-amber-500" />
                      <span>Active Risk Diagnostics</span>
                    </h3>
                    <div className="space-y-1.5 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Academic Risk Level:</span>
                        <span className={`font-bold ${
                          studentProfile.risk_analysis?.academic_risk?.risk_level === 'High' ? 'text-rose-600' : 'text-emerald-600'
                        }`}>
                          {studentProfile.risk_analysis?.academic_risk?.risk_level}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Placement Risk Level:</span>
                        <span className={`font-bold ${
                          studentProfile.risk_analysis?.placement_risk?.risk_level === 'High' ? 'text-rose-600' : 'text-emerald-600'
                        }`}>
                          {studentProfile.risk_analysis?.placement_risk?.risk_level}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Academic Backlogs:</span>
                        <span className="font-bold text-slate-800">
                          {studentProfile.academic_details?.backlogs}
                        </span>
                      </div>
                    </div>
                  </div>

                </div>

                {/* 4. Actionable Recommendations Generated by Engine */}
                {studentProfile.recommendations && studentProfile.recommendations.length > 0 && (
                  <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center space-x-1.5">
                      <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
                      <span>Dynamic Action Plan &amp; Recommendations</span>
                    </h3>
                    <div className="space-y-2 mt-2">
                      {studentProfile.recommendations.map((rec, idx) => (
                        <div key={idx} className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-start space-x-2 text-xs">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold shrink-0 mt-0.5 ${
                            rec.priority === 'High' 
                              ? 'bg-rose-100 text-rose-700' 
                              : 'bg-indigo-100 text-indigo-700'
                          }`}>
                            {rec.priority}
                          </span>
                          <div className="flex-1">
                            <span className="font-semibold text-slate-900">{rec.action}</span>
                            <p className="text-slate-500 text-[11px] mt-0.5">{rec.rationale}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </>
            )}

          </div>

        </div>

      </div>

    </div>
  );
}

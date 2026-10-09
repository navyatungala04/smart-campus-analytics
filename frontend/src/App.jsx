import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Academic from './pages/Academic';
import Attendance from './pages/Attendance';
import LmsEngagement from './pages/LmsEngagement';
import Placement from './pages/Placement';
import Skills from './pages/Skills';
import Feedback from './pages/Feedback';
import SuccessScore from './pages/SuccessScore';
import RiskAnalysis from './pages/RiskAnalysis';
import ImprovementPlan from './pages/ImprovementPlan';
import Profile from './pages/Profile';
import ChangePassword from './pages/ChangePassword';
import Login from './pages/Login';
import FacultyDashboard from './pages/FacultyDashboard';

import { 
  fetchHealth, 
  fetchCurrentUser, 
  loginStudent, 
  logoutStudent, 
  getSessionToken,
  fetchImprovementPlan
} from './services/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [currentStudent, setCurrentStudent] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [planStats, setPlanStats] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  // Initial load: Check API readiness and restore existing persistent session
  useEffect(() => {
    async function init() {
      try {
        setIsLoading(true);
        setError(null);
        await fetchHealth();
        setIsBackendHealthy(true);

        // Check if a persistent session token is stored in localStorage
        const existingToken = getSessionToken();
        if (existingToken) {
          const userData = await fetchCurrentUser();
          if (userData && (userData.student || userData.role === 'faculty' || userData.user?.role === 'faculty')) {
            setCurrentUser(userData.user || null);
            setCurrentSession(userData.session || null);
            const role = userData.role || userData.user?.role || 'student';
            setUserRole(role);
            if (role === 'faculty') {
              setCurrentStudent(null);
            } else {
              setCurrentStudent(userData.student);
            }
          } else {
            // Token expired, logged out, or invalid
            setCurrentUser(null);
            setCurrentStudent(null);
            setCurrentSession(null);
            setUserRole(null);
          }
        } else {
          // No active session: Show Login screen (never defaults to any student)
          setCurrentUser(null);
          setCurrentStudent(null);
          setCurrentSession(null);
          setUserRole(null);
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setError('Failed to connect to the Smart Campus Analytics API backend. Please ensure the FastAPI server is running on http://127.0.0.1:8000.');
        setIsBackendHealthy(false);
      } finally {
        setIsLoading(false);
      }
    }
    init();
  }, []);

  // Handle Login submission
  const handleLogin = async (username, password) => {
    await loginStudent(username, password);
    const userData = await fetchCurrentUser();
    if (userData && (userData.student || userData.role === 'faculty' || userData.user?.role === 'faculty')) {
      setCurrentUser(userData.user || null);
      setCurrentSession(userData.session || null);
      const role = userData.role || userData.user?.role || 'student';
      setUserRole(role);
      if (role === 'faculty') {
        setCurrentStudent(null);
      } else {
        setCurrentStudent(userData.student);
        setActivePage('dashboard');
      }
    } else {
      throw new Error('Unable to retrieve user profile for this account.');
    }
  };

  // Pre-fetch improvement plan stats to keep sidebar pending task counter accurate
  useEffect(() => {
    let isMounted = true;
    if (currentStudent?.student_id) {
      fetchImprovementPlan(currentStudent.student_id)
        .then(data => {
          if (isMounted && data && data.stats) {
            setPlanStats(data.stats);
          }
        })
        .catch(err => {
          console.error('Failed to pre-fetch improvement plan stats:', err);
        });
    } else {
      setPlanStats(null);
    }
    return () => { isMounted = false; };
  }, [currentStudent?.student_id]);

  // Handle Logout
  const handleLogout = async () => {
    try {
      setIsLoading(true);
      await logoutStudent();
    } finally {
      setCurrentUser(null);
      setCurrentStudent(null);
      setCurrentSession(null);
      setUserRole(null);
      setPlanStats(null);
      setActivePage('dashboard');
      setIsLoading(false);
    }
  };

  // Loading spinner during initial session validation
  if (isLoading && !currentUser && !currentStudent) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-indigo-400 border-t-indigo-200 rounded-full animate-spin"></div>
        <p className="text-sm font-medium text-indigo-200">Verifying session credentials...</p>
      </div>
    );
  }

  // Unauthenticated user: Display dedicated Login screen
  if (!currentUser && !currentStudent) {
    return (
      <Login onLoginSuccess={handleLogin} />
    );
  }

  // Authenticated Faculty: Render Faculty Dashboard
  if (userRole === 'faculty') {
    return (
      <FacultyDashboard 
        user={currentUser} 
        onLogout={handleLogout} 
      />
    );
  }

  const riskCount = currentStudent?.risk_analysis
    ? (currentStudent.risk_analysis.academic_risk.triggers_count + currentStudent.risk_analysis.placement_risk.triggers_count)
    : 0;

  const fallbackPendingCount = currentStudent?.recommendations
    ? currentStudent.recommendations.filter(r => !r.is_completed).length
    : 0;
  const recCount = planStats ? planStats.pending_tasks : fallbackPendingCount;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      
      {/* Top Header Navbar */}
      <Navbar 
        currentStudent={currentStudent}
        onLogout={handleLogout}
        isBackendHealthy={isBackendHealthy}
      />

      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        
        {/* Navigation Sidebar */}
        <Sidebar 
          activePage={activePage}
          onNavigate={setActivePage}
          riskCount={riskCount}
          recCount={recCount}
        />

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          
          {/* Loading Indicator */}
          {isLoading && (
            <div className="h-64 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
              <p className="text-xs font-medium text-slate-500">Loading student analytics...</p>
            </div>
          )}

          {/* Error Message */}
          {!isLoading && error && (
            <div className="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 space-y-3 text-center max-w-lg mx-auto my-12">
              <h3 className="text-base font-bold">API Connection Issue</h3>
              <p className="text-xs sm:text-sm text-rose-700">{error}</p>
            </div>
          )}

          {/* Active Page View */}
          {!isLoading && !error && currentStudent && (
            <>
              {activePage === 'dashboard' && <Dashboard student={currentStudent} onNavigate={setActivePage} />}
              {activePage === 'academic' && <Academic student={currentStudent} />}
              {activePage === 'attendance' && <Attendance student={currentStudent} />}
              {activePage === 'lms_engagement' && <LmsEngagement student={currentStudent} />}
              {activePage === 'placement' && <Placement student={currentStudent} />}
              {activePage === 'skills' && <Skills student={currentStudent} />}
              {activePage === 'feedback' && <Feedback student={currentStudent} />}
              {activePage === 'score' && <SuccessScore student={currentStudent} />}
              {activePage === 'risks' && <RiskAnalysis student={currentStudent} />}
              {activePage === 'plan' && <ImprovementPlan student={currentStudent} onPlanStatsChange={setPlanStats} />}
              {activePage === 'profile' && <Profile student={currentStudent} onNavigate={setActivePage} />}
              {activePage === 'change_password' && <ChangePassword student={currentStudent} />}
            </>
          )}

        </main>
      </div>

    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { 
  ListTodo, 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  Target, 
  Plus, 
  Edit3, 
  Trash2, 
  Calendar, 
  Sparkles, 
  User, 
  X, 
  Check, 
  AlertCircle, 
  RotateCcw,
  Tag
} from 'lucide-react';
import { 
  fetchImprovementPlan, 
  updateRecommendationStatus, 
  createCustomPlan, 
  updateCustomPlan, 
  deleteCustomPlan 
} from '../services/api';

const CATEGORIES = [
  'Academic',
  'Attendance',
  'Coding',
  'Aptitude',
  'Communication',
  'Placement',
  'Skills',
  'Other'
];

const PRIORITIES = ['Low', 'Medium', 'High'];

export default function ImprovementPlan({ student, onPlanStatsChange }) {
  const studentId = student?.student_id;

  // Data state
  const [systemRecs, setSystemRecs] = useState([]);
  const [customPlans, setCustomPlans] = useState([]);
  const [stats, setStats] = useState({
    total_tasks: 0,
    completed_tasks: 0,
    pending_tasks: 0,
    overdue_tasks: 0,
    completion_percentage: 0
  });

  // UI state
  const [filter, setFilter] = useState('all'); // 'all', 'pending', 'completed', 'critical', 'custom'
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null); // { type: 'success' | 'error', text: '' }

  // Modal state (Create / Edit)
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null); // null when creating
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'Academic',
    priority: 'Medium',
    target_date: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Delete confirmation modal state
  const [planToDelete, setPlanToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // 1. Initial Load of Improvement Plan
  useEffect(() => {
    if (!studentId) return;

    let isMounted = true;
    async function loadPlan() {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchImprovementPlan(studentId);
        if (isMounted && data) {
          setSystemRecs(data.system_recommendations || []);
          setCustomPlans(data.custom_plans || []);
          setStats(data.stats || {
            total_tasks: 0,
            completed_tasks: 0,
            pending_tasks: 0,
            overdue_tasks: 0,
            completion_percentage: 0
          });
        }
      } catch (err) {
        if (isMounted) {
          console.error('Failed to load improvement plan:', err);
          setError(err.message || 'Failed to load improvement plan. Please check backend connectivity.');
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadPlan();
    return () => { isMounted = false; };
  }, [studentId]);

  // Auto-dismiss notification after 4 seconds
  useEffect(() => {
    if (!notification) return;
    const timer = setTimeout(() => {
      setNotification(null);
    }, 4000);
    return () => clearTimeout(timer);
  }, [notification]);

  // Notify parent component of stats changes (keeps sidebar badge live in sync)
  useEffect(() => {
    if (onPlanStatsChange && stats) {
      onPlanStatsChange(stats);
    }
  }, [stats, onPlanStatsChange]);

  // Recalculate local stats helper
  const recalculateStats = (recs, customs) => {
    const todayIso = new Date().toISOString().split('T')[0];
    const sysTotal = recs.length;
    const sysCompleted = recs.filter(r => r.is_completed).length;

    const customTotal = customs.length;
    const customCompleted = customs.filter(p => p.status === 'completed').length;

    let overdueCount = 0;
    customs.forEach(p => {
      if (p.status !== 'completed' && p.target_date) {
        const tDate = p.target_date.slice(0, 10);
        if (tDate < todayIso) overdueCount += 1;
      }
    });

    const total = sysTotal + customTotal;
    const completed = sysCompleted + customCompleted;
    const pending = total - completed;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

    setStats({
      total_tasks: total,
      completed_tasks: completed,
      pending_tasks: pending,
      overdue_tasks: overdueCount,
      completion_percentage: pct
    });
  };

  // Toggle System Recommendation Completion
  const handleToggleSystemRec = async (rec) => {
    const newStatus = rec.is_completed ? 'pending' : 'completed';
    const recId = rec.id || `rec_${rec.related_metric || 'task'}`;

    // Optimistic UI update
    const updatedRecs = systemRecs.map(r => {
      if ((r.id || `rec_${r.related_metric || 'task'}`) === recId) {
        return { ...r, is_completed: newStatus === 'completed', status: newStatus };
      }
      return r;
    });
    setSystemRecs(updatedRecs);
    recalculateStats(updatedRecs, customPlans);

    try {
      const response = await updateRecommendationStatus(studentId, recId, newStatus);
      if (response && response.plan) {
        setSystemRecs(response.plan.system_recommendations || updatedRecs);
        setCustomPlans(response.plan.custom_plans || customPlans);
        setStats(response.plan.stats);
      }
      setNotification({
        type: 'success',
        text: `Recommendation updated to ${newStatus === 'completed' ? 'Completed' : 'Pending'}.`
      });
    } catch (err) {
      console.error('Failed to update recommendation status:', err);
      // Revert optimistic update on failure
      const revertedRecs = systemRecs.map(r => {
        if ((r.id || `rec_${r.related_metric || 'task'}`) === recId) {
          return { ...r, is_completed: !rec.is_completed, status: rec.is_completed ? 'completed' : 'pending' };
        }
        return r;
      });
      setSystemRecs(revertedRecs);
      recalculateStats(revertedRecs, customPlans);
      setNotification({
        type: 'error',
        text: `Failed to save completion status: ${err.message}`
      });
    }
  };

  // Toggle Custom Plan Completion
  const handleToggleCustomPlan = async (plan) => {
    const newStatus = plan.status === 'completed' ? 'pending' : 'completed';

    // Optimistic UI update
    const updatedCustoms = customPlans.map(p => {
      if (p.plan_id === plan.plan_id) {
        return { ...p, status: newStatus };
      }
      return p;
    });
    setCustomPlans(updatedCustoms);
    recalculateStats(systemRecs, updatedCustoms);

    try {
      const response = await updateCustomPlan(studentId, plan.plan_id, { status: newStatus });
      if (response && response.summary) {
        setSystemRecs(response.summary.system_recommendations || systemRecs);
        setCustomPlans(response.summary.custom_plans || updatedCustoms);
        setStats(response.summary.stats);
      }
      setNotification({
        type: 'success',
        text: `Custom task marked as ${newStatus === 'completed' ? 'Completed' : 'Pending'}.`
      });
    } catch (err) {
      console.error('Failed to update custom plan status:', err);
      // Revert optimistic update
      const revertedCustoms = customPlans.map(p => {
        if (p.plan_id === plan.plan_id) {
          return { ...p, status: plan.status };
        }
        return p;
      });
      setCustomPlans(revertedCustoms);
      recalculateStats(systemRecs, revertedCustoms);
      setNotification({
        type: 'error',
        text: `Failed to save task status: ${err.message}`
      });
    }
  };

  // Open Create Modal
  const openCreateModal = () => {
    setEditingPlan(null);
    setFormData({
      title: '',
      description: '',
      category: 'Academic',
      priority: 'Medium',
      target_date: ''
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Open Edit Modal
  const openEditModal = (plan) => {
    setEditingPlan(plan);
    setFormData({
      title: plan.title || '',
      description: plan.description || '',
      category: plan.category || 'Academic',
      priority: plan.priority || 'Medium',
      target_date: plan.target_date ? plan.target_date.slice(0, 10) : ''
    });
    setFormErrors({});
    setIsModalOpen(true);
  };

  // Validate form
  const validateForm = () => {
    const errors = {};
    if (!formData.title.trim()) {
      errors.title = 'Task title is required';
    } else if (formData.title.trim().length > 200) {
      errors.title = 'Title must be 200 characters or fewer';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Save Custom Plan (Create or Update)
  const handleSavePlan = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim() || null,
        category: formData.category,
        priority: formData.priority,
        target_date: formData.target_date ? formData.target_date.trim() : null
      };

      if (editingPlan) {
        // Update existing plan
        const response = await updateCustomPlan(studentId, editingPlan.plan_id, payload);
        if (response && response.summary) {
          setSystemRecs(response.summary.system_recommendations || systemRecs);
          setCustomPlans(response.summary.custom_plans || []);
          setStats(response.summary.stats);
        }
        setNotification({
          type: 'success',
          text: 'Custom plan updated successfully!'
        });
      } else {
        // Create new plan
        const response = await createCustomPlan(studentId, payload);
        if (response && response.summary) {
          setSystemRecs(response.summary.system_recommendations || systemRecs);
          setCustomPlans(response.summary.custom_plans || []);
          setStats(response.summary.stats);
        }
        setNotification({
          type: 'success',
          text: 'New personal plan created and saved!'
        });
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error('Failed to save plan:', err);
      setNotification({
        type: 'error',
        text: err.message || 'Failed to save custom plan.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Delete Custom Plan
  const handleDeletePlan = async () => {
    if (!planToDelete) return;
    try {
      setIsDeleting(true);
      const response = await deleteCustomPlan(studentId, planToDelete.plan_id);
      if (response && response.summary) {
        setSystemRecs(response.summary.system_recommendations || systemRecs);
        setCustomPlans(response.summary.custom_plans || []);
        setStats(response.summary.stats);
      } else {
        const remaining = customPlans.filter(p => p.plan_id !== planToDelete.plan_id);
        setCustomPlans(remaining);
        recalculateStats(systemRecs, remaining);
      }
      setNotification({
        type: 'success',
        text: 'Custom plan deleted successfully.'
      });
      setPlanToDelete(null);
    } catch (err) {
      console.error('Failed to delete custom plan:', err);
      setNotification({
        type: 'error',
        text: err.message || 'Failed to delete plan.'
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // Combine and filter tasks
  const todayIso = new Date().toISOString().split('T')[0];

  const allItems = [
    ...systemRecs.map(r => ({
      ...r,
      itemType: 'system',
      key: `sys_${r.id || r.related_metric}`,
      title: r.suggested_action,
      isDone: !!r.is_completed,
      isCriticalOrHigh: r.priority === 'Critical' || r.priority === 'High',
      isOverdue: false
    })),
    ...customPlans.map(p => {
      const isOverdue = p.status !== 'completed' && p.target_date && p.target_date.slice(0, 10) < todayIso;
      return {
        ...p,
        itemType: 'custom',
        key: `custom_${p.plan_id}`,
        isDone: p.status === 'completed',
        isCriticalOrHigh: p.priority === 'High',
        isOverdue: !!isOverdue
      };
    })
  ];

  const filteredItems = allItems.filter(item => {
    if (filter === 'pending') return !item.isDone;
    if (filter === 'completed') return item.isDone;
    if (filter === 'critical') return item.isCriticalOrHigh;
    if (filter === 'custom') return item.itemType === 'custom';
    return true; // 'all'
  });

  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center space-x-2">
            <span>My Personalized Improvement Plan</span>
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Targeted milestones combining AI-generated diagnostic recommendations and your personal custom goals
          </p>
        </div>

        <button
          onClick={openCreateModal}
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-md shadow-indigo-500/20 cursor-pointer transition-all self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Add My Own Plan</span>
        </button>
      </div>

      {/* Global Notifications / Alert Banner */}
      {notification && (
        <div className={`p-4 rounded-xl border flex items-start space-x-3 text-xs shadow-xs animate-fadeIn ${
          notification.type === 'success' 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900' 
            : 'bg-rose-50 border-rose-200 text-rose-900'
        }`}>
          {notification.type === 'success' ? (
            <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          )}
          <span className="flex-1 font-semibold">{notification.text}</span>
          <button 
            onClick={() => setNotification(null)}
            className="text-slate-400 hover:text-slate-600"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Error state */}
      {error && !notification && (
        <div className="p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Stats Overview Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Total Tasks</p>
          <div className="flex items-baseline space-x-1.5 mt-1">
            <span className="text-2xl font-extrabold text-slate-900">{stats.total_tasks}</span>
            <span className="text-xs text-slate-400">tasks</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1">
            {systemRecs.length} AI • {customPlans.length} Personal
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-emerald-600">Completed</p>
          <div className="flex items-baseline space-x-1.5 mt-1">
            <span className="text-2xl font-extrabold text-emerald-600">{stats.completed_tasks}</span>
            <span className="text-xs text-slate-400">/ {stats.total_tasks}</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Persisted in database</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-amber-600">Pending</p>
          <div className="flex items-baseline space-x-1.5 mt-1">
            <span className="text-2xl font-extrabold text-amber-600">{stats.pending_tasks}</span>
            <span className="text-xs text-slate-400">tasks</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Active action items</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-rose-600">Overdue</p>
          <div className="flex items-baseline space-x-1.5 mt-1">
            <span className={`text-2xl font-extrabold ${stats.overdue_tasks > 0 ? 'text-rose-600' : 'text-slate-800'}`}>
              {stats.overdue_tasks}
            </span>
            <span className="text-xs text-slate-400">tasks</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Past target date</p>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs col-span-2 sm:col-span-1">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-indigo-600">Overall Progress</p>
          <div className="flex items-baseline space-x-1 mt-1">
            <span className="text-2xl font-extrabold text-indigo-600">{stats.completion_percentage}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
            <div 
              className="bg-emerald-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, stats.completion_percentage)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Filter Tabs Bar */}
      <div className="bg-white rounded-xl p-3 border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-1.5 text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
              filter === 'all' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Tasks ({stats.total_tasks})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
              filter === 'pending' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Pending ({stats.pending_tasks})
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
              filter === 'completed' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Completed ({stats.completed_tasks})
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
              filter === 'critical' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Critical &amp; High Priority
          </button>
          <button
            onClick={() => setFilter('custom')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer ${
              filter === 'custom' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            My Custom Plans ({customPlans.length})
          </button>
        </div>

        <span className="text-[11px] text-slate-400 hidden md:block">
          Showing {filteredItems.length} of {allItems.length} tasks
        </span>
      </div>

      {/* Task List / Loading / Empty State */}
      {isLoading ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-xs">
          <div className="w-8 h-8 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"></div>
          <p className="text-xs font-medium text-slate-500">Loading personalized improvement roadmap...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-xs">
          <ListTodo className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No tasks found for this view</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {filter === 'custom' 
              ? 'You have not created any custom improvement plans yet. Click "Add My Own Plan" to set a personal goal.'
              : filter === 'completed'
              ? 'No completed tasks yet. Check off items as you make progress.'
              : 'All caught up or no items match the selected filter.'}
          </p>
          {filter === 'custom' && (
            <button
              onClick={openCreateModal}
              className="mt-4 inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Create Your First Goal</span>
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3.5">
          {filteredItems.map(item => {
            const isSystem = item.itemType === 'system';
            const isDone = item.isDone;

            return (
              <div
                key={item.key}
                className={`p-4 sm:p-5 rounded-xl border transition-all ${
                  isDone 
                    ? 'bg-slate-50/80 border-slate-200 opacity-60' 
                    : item.priority === 'Critical'
                    ? 'bg-white border-rose-200 shadow-xs'
                    : item.priority === 'High'
                    ? 'bg-white border-amber-200 shadow-xs'
                    : 'bg-white border-slate-200 shadow-xs'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  
                  {/* Left: Checkbox & Task Info */}
                  <div className="flex items-start space-x-3.5 flex-1 min-w-0">
                    
                    {/* Interactive Completion Checkbox */}
                    <button
                      onClick={() => isSystem ? handleToggleSystemRec(item) : handleToggleCustomPlan(item)}
                      className={`mt-1 w-5 h-5 rounded-md border flex items-center justify-center transition-colors shrink-0 cursor-pointer ${
                        isDone 
                          ? 'bg-emerald-600 border-emerald-600 text-white' 
                          : 'border-slate-300 hover:border-indigo-500 bg-white'
                      }`}
                      title={isDone ? 'Mark as Pending' : 'Mark as Completed'}
                    >
                      {isDone && <Check className="w-3.5 h-3.5" />}
                    </button>

                    <div className="space-y-1.5 flex-1 min-w-0">
                      
                      {/* Badges Row */}
                      <div className="flex flex-wrap items-center gap-2 text-[10px]">
                        
                        {/* Origin Badge (System vs Personal) */}
                        {isSystem ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                            <Sparkles className="w-3 h-3 text-indigo-500" />
                            <span>AI Recommendation</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full font-bold bg-purple-50 text-purple-700 border border-purple-200">
                            <User className="w-3 h-3 text-purple-500" />
                            <span>Personal Plan</span>
                          </span>
                        )}

                        {/* Priority Badge */}
                        <span className={`px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                          item.priority === 'Critical' ? 'bg-rose-100 text-rose-700' :
                          item.priority === 'High' ? 'bg-amber-100 text-amber-800' :
                          item.priority === 'Medium' ? 'bg-blue-100 text-blue-700' :
                          'bg-slate-100 text-slate-700'
                        }`}>
                          {item.priority} Priority
                        </span>

                        {/* Category Tag */}
                        <span className="font-semibold text-slate-500">
                          • {item.category}
                        </span>

                        {/* Target Date (for Custom Plans) */}
                        {!isSystem && item.target_date && (
                          <span className={`inline-flex items-center space-x-1 px-1.5 py-0.5 rounded ${
                            item.isOverdue 
                              ? 'bg-rose-100 text-rose-700 font-bold' 
                              : 'bg-slate-100 text-slate-600 font-medium'
                          }`}>
                            <Calendar className="w-3 h-3" />
                            <span>Due: {item.target_date.slice(0, 10)}</span>
                            {item.isOverdue && <span className="ml-1 text-[9px] uppercase tracking-wider">(Overdue)</span>}
                          </span>
                        )}

                      </div>

                      {/* Title */}
                      <h3 className={`text-sm sm:text-base font-bold ${
                        isDone ? 'line-through text-slate-400' : 'text-slate-900'
                      }`}>
                        {item.title}
                      </h3>

                      {/* Description / Diagnosis */}
                      {isSystem ? (
                        <p className="text-xs text-slate-600 leading-relaxed">
                          <span className="font-semibold text-slate-700">Diagnosis:</span> {item.reason}
                        </p>
                      ) : (
                        item.description && (
                          <p className="text-xs text-slate-600 leading-relaxed">
                            {item.description}
                          </p>
                        )
                      )}

                      {/* Metrics targets (for System recommendations) */}
                      {isSystem && (
                        <div className="pt-1.5 flex flex-wrap items-center gap-2.5 text-xs">
                          {item.current_value && (
                            <div className="bg-slate-50 px-2 py-0.5 rounded border border-slate-200/60 text-[11px]">
                              <span className="text-slate-400">Current: </span>
                              <strong className="text-slate-700">{item.current_value}</strong>
                            </div>
                          )}
                          {item.improvement_target && (
                            <div className="bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 text-indigo-700 flex items-center space-x-1 text-[11px]">
                              <Target className="w-3 h-3" />
                              <span>Target: <strong>{item.improvement_target}</strong></span>
                            </div>
                          )}
                        </div>
                      )}

                    </div>
                  </div>

                  {/* Right: Actions for Custom Plans */}
                  {!isSystem && (
                    <div className="flex items-center space-x-1 shrink-0 ml-2">
                      <button
                        onClick={() => openEditModal(item)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors cursor-pointer"
                        title="Edit Plan"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setPlanToDelete(item)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                        title="Delete Plan"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* CREATE / EDIT CUSTOM PLAN MODAL */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 animate-fadeIn">
            
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                  <ListTodo className="w-4 h-4" />
                </div>
                <h3 className="text-base font-bold text-slate-900">
                  {editingPlan ? 'Edit Personal Plan' : 'Create New Personal Plan'}
                </h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSavePlan} className="space-y-4 mt-4" noValidate>
              
              {/* Title */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Task Title <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Practice Python for 30 minutes daily"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  className={`w-full px-3 py-2 text-xs rounded-xl border focus:outline-hidden focus:ring-2 ${
                    formErrors.title 
                      ? 'border-rose-400 bg-rose-50/50 focus:ring-rose-400' 
                      : 'border-slate-200 focus:ring-indigo-500 focus:border-indigo-500'
                  }`}
                />
                {formErrors.title && (
                  <p className="text-[11px] text-rose-600 font-medium mt-1">{formErrors.title}</p>
                )}
              </div>

              {/* Description */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Description <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <textarea
                  rows="2"
                  placeholder="Add specifics, resources, or milestones..."
                  value={formData.description}
                  onChange={e => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                ></textarea>
              </div>

              {/* Category & Priority Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={e => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={formData.priority}
                    onChange={e => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                  >
                    {PRIORITIES.map(pri => (
                      <option key={pri} value={pri}>{pri}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Target Date */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Target Completion Date <span className="text-slate-400 font-normal">(Optional)</span>
                </label>
                <input
                  type="date"
                  value={formData.target_date}
                  onChange={e => setFormData({ ...formData, target_date: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Modal Buttons */}
              <div className="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-md shadow-indigo-500/20 disabled:opacity-50 cursor-pointer transition-all"
                >
                  {isSubmitting ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>Saving...</span>
                    </>
                  ) : (
                    <span>{editingPlan ? 'Save Changes' : 'Create Plan'}</span>
                  )}
                </button>
              </div>

            </form>

          </div>
        </div>
      )}

      {/* DELETE CONFIRMATION MODAL */}
      {planToDelete && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 text-center animate-fadeIn">
            <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-3">
              <Trash2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900">Delete Custom Plan?</h3>
            <p className="text-xs text-slate-500 mt-1">
              Are you sure you want to delete <span className="font-semibold text-slate-800">"{planToDelete.title}"</span>? This action cannot be undone.
            </p>

            <div className="flex items-center justify-center space-x-2 mt-6">
              <button
                onClick={() => setPlanToDelete(null)}
                disabled={isDeleting}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleDeletePlan}
                disabled={isDeleting}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md shadow-rose-500/20 disabled:opacity-50 cursor-pointer transition-all"
              >
                {isDeleting ? 'Deleting...' : 'Confirm Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

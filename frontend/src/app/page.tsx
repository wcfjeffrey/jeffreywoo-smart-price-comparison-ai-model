'use client';

import { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, Search, DollarSign, Truck, Star, TrendingUp, Calendar as CalendarIcon,
  Bell, Package, AlertTriangle, CheckCircle, X, Edit, Trash2,
  Mail, Calendar as GoogleCalendar, Clock, Eye, EyeOff, RefreshCw,
  List, LayoutGrid, FileText, FileJson, FileSpreadsheet, Shield,
  Zap, Sparkles, ChevronLeft, ChevronRight
} from 'lucide-react';

interface Supplier {
  product_name: string;
  supplier: string;
  price: number;
  delivery_time: number;
  rating: number;
}

interface ProductData {
  product_name: string;
  suppliers: Supplier[];
  best_price: {
    supplier: string;
    price: number;
    delivery_time: number;
    rating: number;
    score: number;
  };
  price_range: {
    min: number;
    max: number;
  };
  recommendations: string[];
  predictions?: {
    short_term_trend: {
      direction: string;
      change_percent: number;
      reasoning: string;
    };
    long_term_trend: {
      direction: string;
      change_percent: number;
      reasoning: string;
    };
    recommended_timing: string;
    confidence_score: number;
    factors: string[];
  };
    ml_predictions?: {
    average_predicted_price: number;
    confidence: number;
    model_used: string;
    supplier_details: Array<{
      supplier: string;
      current_price: number;
      predicted_price: number;
      confidence: number;
    }>;
  };
  hybrid_recommendation?: {
    action: string;
    recommendation: string;
    combined_confidence: number;
    reasoning: string;
  };
  risk_analysis?: {
    risk_score: number;
    risk_level: string;
    risks: Array<{
      type: string;
      severity: string;
      description: string;
    }>;
  };
}

interface Task {
  id: string;
  product_name: string;
  frequency: string;
  time: string;
  notification_method: string;
  next_run: string;
  last_run: string | null;
  active: boolean;
  email: string | null;
}

// Calendar day data structure
interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  tasks: Task[];
}

export default function HomePage() {
  const [productName, setProductName] = useState('');
  const [productData, setProductData] = useState<ProductData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleFrequency, setScheduleFrequency] = useState('weekly');
  const [scheduleTime, setScheduleTime] = useState('09:00');
  const [notificationMethod, setNotificationMethod] = useState('email');
  const [email, setEmail] = useState('');
  const [taskCreated, setTaskCreated] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksLoading, setTasksLoading] = useState(true);
  const [tasksError, setTasksError] = useState('');
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [tasksView, setTasksView] = useState<'list' | 'calendar'>('list');
  const [tasksSuccess, setTasksSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');

  // Calendar state
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDay, setSelectedDay] = useState<{
    date: Date;
    tasks: Task[];
    isCurrentMonth: boolean;
  } | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/tasks/');
      const data = await response.json();
      setTasks(data);
      setTasksError('');
    } catch (error) {
      setTasksError('Failed to fetch tasks. Make sure backend is running.');
    } finally {
      setTasksLoading(false);
    }
  };


  const handleAddTask = async () => {
    if (!productData) return;
    if ((notificationMethod === 'email' || notificationMethod === 'both') && !email) {
      setError('Please enter an email address for notifications');
      return;
    }

    try {
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productData.product_name,
          frequency: scheduleFrequency,
          time: scheduleTime,
          day_of_week: scheduleFrequency === 'weekly' ? 0 : null,
          notification_method: notificationMethod,
          email: email || null,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        })
      });

      if (response.ok) {
        setTaskCreated(true);
        setShowScheduleForm(false);
        setTimeout(() => setTaskCreated(false), 5000);
        fetchTasks();
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to create task');
      }
    } catch (err) {
      setError('Failed to create task');
    }
  };


  const deleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      const response = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
      if (response.ok) {
        setTasksSuccess('Task deleted successfully');
        setTimeout(() => setTasksSuccess(''), 3000);
        fetchTasks();
      }
    } catch (error) {
      setTasksError('Failed to delete task');
    }
  };

  const toggleTaskActive = async (task: Task) => {
    try {
      const response = await fetch(`/api/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: !task.active })
      });
      if (response.ok) {
        setTasksSuccess(`Task ${task.active ? 'paused' : 'activated'} successfully`);
        setTimeout(() => setTasksSuccess(''), 3000);
        fetchTasks();
      }
    } catch (error) {
      setTasksError('Failed to update task');
    }
  };

  const updateTask = async () => {
    if (!editingTask) return;
    try {
      const updateData = {
        frequency: editingTask.frequency,
        time: editingTask.time,
        notification_method: editingTask.notification_method,
        email: editingTask.email,
        active: editingTask.active
      };
      const response = await fetch(`/api/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      if (response.ok) {
        setTasksSuccess('Task updated successfully');
        setTimeout(() => setTasksSuccess(''), 3000);
        setEditingTask(null);
        fetchTasks();
      }
    } catch (error) {
      setTasksError('Failed to update task');
    }
  };

  const getNotificationIcon = (method: string) => {
    switch (method) {
      case 'email':
        return <Mail className="h-4 w-4 text-blue-500" />;
      case 'calendar':
        return <GoogleCalendar className="h-4 w-4 text-green-500" />;
      case 'both':
        return (
          <div className="flex gap-1">
            <Mail className="h-4 w-4 text-blue-500" />
            <GoogleCalendar className="h-4 w-4 text-green-500" />
          </div>
        );
      default:
        return <Bell className="h-4 w-4 text-gray-500" />;
    }
  };

const getFrequencyBadge = (frequency: string) => {
  const colors: Record<string, string> = {
    daily: 'bg-blue-100 text-blue-800 border border-blue-200',
    weekly: 'bg-purple-100 text-purple-800 border border-purple-200',
    monthly: 'bg-green-100 text-green-800 border border-green-200'
  };
  return <Badge className={`${colors[frequency] || 'bg-gray-100 text-gray-800 border border-gray-200'} px-3 py-1`}>{frequency}</Badge>;
};

  const downloadReport = async (format: string) => {
    if (!productData) return;
    try {
      window.open(
        `/api/reports/download/${encodeURIComponent(productData.product_name)}?format=${format}`,
        '_blank'
      );
    } catch (error) {
      setError('Failed to generate report');
    }
  };

  const handleSearch = async (searchTerm: string = productName) => {
  if (!searchTerm.trim()) {
    setError('Please enter a product name');
    return;
  }

  setLoading(true);
  setError('');
  setProductData(null);
  setShowScheduleForm(false);

  try {
    const response = await fetch(`/api/products/compare/${encodeURIComponent(searchTerm)}`);
    const result = await response.json();

    if (result.status === 'success') {
      const data = result.data || result;

      console.log("🔍 RAW DATA FROM BACKEND:", data);
      console.log("📊 Does predictions exist?", !!data.predictions);
      console.log("📊 predictions data:", data.predictions);

      // ✅ IMPORTANT: Include predictions in the productData
      setProductData({
        product_name: data.product_name || searchTerm,
        suppliers: data.suppliers || [],
        best_price: data.best_price || { supplier: '', price: 0, delivery_time: 0, rating: 0, score: 0 },
        price_range: data.price_range || { min: 0, max: 0 },
        recommendations: data.recommendations || [],
        // ✅ ADD THIS - predictions from backend
        predictions: data.predictions || {
          short_term_trend: { direction: 'stable', change_percent: 0, reasoning: 'Analysis in progress' },
          long_term_trend: { direction: 'stable', change_percent: 0, reasoning: 'Analysis in progress' },
          recommended_timing: 'Monitor market',
          confidence_score: 75,
          factors: ['Market conditions']
        },
        ml_predictions: data.ml_predictions || {
          average_predicted_price: 0,
          confidence: 0,
          model_used: 'N/A',
          supplier_details: []
        },
        hybrid_recommendation: data.hybrid_recommendation || {
          action: 'Monitor',
          recommendation: 'Hold',
          combined_confidence: 0,
          reasoning: 'Data unavailable'
        },
        risk_analysis: data.risk_analysis || {
          risk_score: 0,
          risk_level: 'low',
          risks: []
        }
      });

      const updated = [searchTerm, ...recentSearches.filter(p => p !== searchTerm)].slice(0, 5);
      setRecentSearches(updated);
      localStorage.setItem('recentSearches', JSON.stringify(updated));
      setActiveTab('dashboard');
    } else {
      setError(result.message || 'Product not found');
    }
  } catch (err) {
    console.error(err);
    setError('Failed to connect to server. Please make sure the backend is running.');
  } finally {
    setLoading(false);
  }
};

  const loadRecentSearch = (search: string) => {
    setProductName(search);
    handleSearch(search);
  };

  const clearSearch = () => {
    setProductName('');
    setProductData(null);
    setError('');
  };

  const getChartData = () => {
    if (!productData?.suppliers || productData.suppliers.length === 0) return [];
    return productData.suppliers.map(supplier => ({
      supplier: supplier.supplier,
      price: supplier.price,
      delivery: supplier.delivery_time,
      rating: supplier.rating
    }));
  };

  // Get tasks with valid dates
  const validTasks = tasks.filter(task => task.active && task.next_run);

  // Calendar functions - returns 42 days (6 weeks) to always fill the grid
  const getCalendarDays = (date: Date): CalendarDay[] => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDayOfMonth = new Date(year, month, 1);
    const startDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sunday
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const calendarDays: CalendarDay[] = [];

    // Previous month days (to fill the first week)
    const prevMonthDays = startDayOfWeek;
    for (let i = prevMonthDays - 1; i >= 0; i--) {
      const prevDate = new Date(year, month, -i);
      const dayTasks = validTasks.filter(task => {
        const taskDate = new Date(task.next_run);
        return taskDate.toDateString() === prevDate.toDateString();
      });
      calendarDays.push({ date: prevDate, isCurrentMonth: false, tasks: dayTasks });
    }

    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      const currentDate = new Date(year, month, i);
      const dayTasks = validTasks.filter(task => {
        const taskDate = new Date(task.next_run);
        return taskDate.toDateString() === currentDate.toDateString();
      });
      calendarDays.push({ date: currentDate, isCurrentMonth: true, tasks: dayTasks });
    }

    // Next month days (to fill the remaining cells - always make total 42 = 6 rows x 7 columns)
    const remainingCells = 42 - calendarDays.length;
    for (let i = 1; i <= remainingCells; i++) {
      const nextDate = new Date(year, month + 1, i);
      const dayTasks = validTasks.filter(task => {
        const taskDate = new Date(task.next_run);
        return taskDate.toDateString() === nextDate.toDateString();
      });
      calendarDays.push({ date: nextDate, isCurrentMonth: false, tasks: dayTasks });
    }

    return calendarDays;
  };

  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const goToPrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentMonth(new Date());
  };

  const formatDayLabel = (d: Date) =>
    d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });

  const CalendarModal = ({
    open,
    onClose,
    title,
    children
  }: {
    open: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
  }) => {
    if (!open) return null;

    return (
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
        <div
          className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
          onClick={onClose}
        />
        <div className="relative w-full max-w-2xl rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex items-center justify-between gap-3">
            <div className="min-w-0">
              <h3 className="text-lg font-semibold text-slate-800 truncate">{title}</h3>
              <p className="text-sm text-slate-500">All scheduled price checks for this day.</p>
            </div>
            <button
              onClick={onClose}
              className="rounded-xl p-2 hover:bg-slate-100 transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5 text-slate-600" />
            </button>
          </div>
          <div className="p-5">{children}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Modern Header */}
      <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white shadow-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl">
                <Sparkles className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  JeffreyWoo Smart Price Comparison
                </h1>
                <p className="text-slate-400 text-sm mt-1">AI-Powered Price Intelligence Platform</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Badge variant="outline" className="bg-white/10 text-white border-white/20">
                <Zap className="h-3 w-3 mr-1" /> Real-time
              </Badge>
              <Badge variant="outline" className="bg-white/10 text-white border-white/20">
                <Shield className="h-3 w-3 mr-1" /> AI Analysis
              </Badge>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Hero Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <Card className="border border-slate-200 shadow-xl bg-gradient-to-r from-white to-slate-50">
            <CardContent className="p-8">
              <div className="text-center mb-6">
                <h2 className="text-3xl font-bold text-slate-800 mb-2">Find the Best Deals</h2>
                <p className="text-slate-500">Search any product to compare prices across multiple suppliers instantly</p>
              </div>
              <div className="flex gap-3 max-w-3xl mx-auto">
                <div className="flex-1">
                  <Input
                    placeholder="Enter product name (e.g., iPhone 17 Pro, Samsung Galaxy S25, MacBook Pro)"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="text-lg py-6 rounded-xl border-2 border-slate-200 focus:border-blue-500"
                  />
                </div>
                <Button
                  onClick={() => handleSearch()}
                  disabled={loading}
                  className="px-8 py-6 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                >
                  <Search className="h-5 w-5 mr-2" />
                  {loading ? 'Analyzing...' : 'Analyze'}
                </Button>
                {productData && (
                  <Button variant="outline" onClick={clearSearch} className="px-6 py-6 rounded-xl">
                    <X className="h-5 w-5" />
                  </Button>
                )}
              </div>

              {recentSearches.length > 0 && !productData && (
                <div className="mt-4 text-center">
                  <p className="text-sm text-slate-500 mb-2">Recent searches:</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {recentSearches.map((search, i) => (
                      <Button
                        key={i}
                        variant="outline"
                        size="sm"
                        onClick={() => loadRecentSearch(search)}
                        className="text-sm rounded-full"
                      >
                        {search}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Error/Success Alerts */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6"
            >
              <Alert variant="destructive" className="bg-red-50 border-red-200">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertTitle className="text-red-800">Error</AlertTitle>
                <AlertDescription className="text-red-700">{error}</AlertDescription>
              </Alert>
            </motion.div>
          )}

          {taskCreated && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6"
            >
              <Alert className="bg-green-50 border-green-200 text-green-800">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription>✅ Task created successfully!</AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-2 bg-white shadow-sm rounded-xl p-1 border border-slate-200">
            <TabsTrigger value="dashboard" className="rounded-lg data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <TrendingUp className="h-4 w-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="tasks" className="rounded-lg data-[state=active]:bg-blue-600 data-[state=active]:text-white">
              <CalendarIcon className="h-4 w-4 mr-2" />
              Tasks & Calendar
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {productData ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                {/* Product Header */}
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl text-white p-8 shadow-xl">
                  <h2 className="text-3xl font-bold mb-2">{productData.product_name}</h2>
                  <p className="text-blue-100">Price comparison from {productData.suppliers.length} suppliers</p>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
<Card className="border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
  <CardContent className="p-6">
    <div className="flex items-center justify-between mb-4">
      <div className="p-2 bg-green-100 rounded-xl">
        <DollarSign className="h-6 w-6 text-green-600" />
      </div>
      <span className="text-xs text-slate-500">Best Price</span>
    </div>

    <p className="text-3xl font-bold text-green-600">
      ${productData.best_price?.price ? productData.best_price.price.toFixed(2) : '0.00'}
    </p>

    <p className="text-sm text-slate-600 mt-1">
      from {productData.best_price?.supplier || 'N/A'}
    </p>

    <div className="flex gap-3 mt-3 text-xs text-slate-500">
      <span>Delivery: {productData.best_price?.delivery_time || 0} days</span>
      <span>⭐ {productData.best_price?.rating || 0}/5</span>
    </div>
  </CardContent>
</Card>

                  <Card className="border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-blue-100 rounded-xl">
                          <TrendingUp className="h-6 w-6 text-blue-600" />
                        </div>
                        <span className="text-xs text-slate-500">Price Range</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-600">
                        ${productData.price_range.min.toFixed(2) || '0.00'} - ${productData.price_range.max.toFixed(2) || '0.00'}
                      </p>
                      <p className="text-sm text-slate-600 mt-1">Across all suppliers</p>
                    </CardContent>
                  </Card>

                  <Card className="border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-purple-100 rounded-xl">
                          <Package className="h-6 w-6 text-purple-600" />
                        </div>
                        <span className="text-xs text-slate-500">Suppliers</span>
                      </div>
                      <p className="text-3xl font-bold text-purple-600">{productData.suppliers.length}</p>
                      <p className="text-sm text-slate-600 mt-1">Active suppliers</p>
                    </CardContent>
                  </Card>

                  <Card className="border border-slate-200 shadow-lg hover:shadow-xl transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div
                          className={`p-2 rounded-xl ${
                            productData.risk_analysis?.risk_level === 'high'
                              ? 'bg-red-100'
                              : productData.risk_analysis?.risk_level === 'medium'
                                ? 'bg-orange-100'
                                : 'bg-green-100'
                          }`}
                        >
                          <Shield
                            className={`h-6 w-6 ${
                              productData.risk_analysis?.risk_level === 'high'
                                ? 'text-red-600'
                                : productData.risk_analysis?.risk_level === 'medium'
                                  ? 'text-orange-600'
                                  : 'text-green-600'
                            }`}
                          />
                        </div>
                        <span className="text-xs text-slate-500">Risk Level</span>
                      </div>
                      <p
                        className={`text-2xl font-bold ${
                          productData.risk_analysis?.risk_level === 'high'
                            ? 'text-red-600'
                            : productData.risk_analysis?.risk_level === 'medium'
                              ? 'text-orange-600'
                              : 'text-green-600'
                        }`}
                      >
                        {productData.risk_analysis?.risk_level?.toUpperCase() || 'LOW'}
                      </p>
                      <p className="text-sm text-slate-600 mt-1">Risk Score: {productData.risk_analysis?.risk_score || 0}/100</p>

                          {/* Show risks if any */}
    {productData.risk_analysis?.risks && productData.risk_analysis.risks.length > 0 && (
      <div className="mt-3 pt-3 border-t">
        <p className="text-xs text-slate-500 mb-1">Risk Factors:</p>
        <ul className="text-xs text-slate-600 space-y-1">
          {productData.risk_analysis.risks.map((risk, idx) => (
            <li key={idx} className="flex items-start gap-1">
              <span className="text-red-500">•</span>
              <span>{risk.description}</span>
            </li>
          ))}
        </ul>
      </div>
    )}

                    </CardContent>
                  </Card>
                </div>

                {/* Price Chart */}
                <Card className="border border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-blue-600">
                      <TrendingUp className="h-5 w-5" />
                      Price Comparison Chart
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {productData?.suppliers && productData.suppliers.length > 0 ? (
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={getChartData()}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="supplier" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)' }} />
                        <Legend />
                        <Bar dataKey="price" fill="#3B82F6" name="Price ($)" radius={[8, 8, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                    ) : (
      <div className="h-[400px] flex items-center justify-center text-slate-500">
        No supplier data available
      </div>
    )}
                  </CardContent>
                </Card>

                {/* Supplier Rankings */}
                <Card className="border border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-green-600">
                      <Truck className="h-5 w-5" />
                      Supplier Rankings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {productData?.suppliers && productData.suppliers.length > 0 ? (
                    <div className="space-y-3">
                      {productData.suppliers.map((supplier, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`flex justify-between items-center p-4 rounded-xl transition-all border ${
                            supplier.supplier === productData.best_price.supplier
                              ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 shadow-sm'
                              : 'bg-white border-slate-200 hover:shadow-md'
                          }`}
                        >
                          <div className="flex items-center gap-4">
                            <div
                              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${
                                index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-500' : index === 2 ? 'bg-orange-600' : 'bg-blue-500'
                              }`}
                            >
                              {index + 1}
                            </div>
                            <div>
                              <div className="font-semibold text-lg text-slate-800">{supplier.supplier}</div>
                              <div className="flex gap-3 mt-1 text-sm text-slate-500">
                                <span className="flex items-center gap-1"><Truck className="h-3 w-3" /> {supplier.delivery_time} days</span>
                                <span className="flex items-center gap-1"><Star className="h-3 w-3 fill-yellow-500" /> {supplier.rating}/5</span>
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-2xl text-green-600">
                ${supplier.price ? supplier.price.toFixed(2) : '0.00'}
              </div>
                            {supplier.supplier === productData.best_price.supplier && (
                              <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">Best Deal</span>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                        ) : (
      <div className="py-12 text-center text-slate-500">
        No supplier data available
      </div>
                        )}
                  </CardContent>
                </Card>

                <Card className="border-2 border-purple-200 shadow-lg bg-gradient-to-br from-indigo-50/50 via-purple-50/50 to-pink-50/50">
  <CardHeader>
    <CardTitle className="flex items-center gap-2 text-purple-700">
      <TrendingUp className="h-5 w-5" />
      Price Predictions (AI + ML Hybrid)
    </CardTitle>
  </CardHeader>
  <CardContent>
    {/* AI Predictions */}
    <div className="mb-6">
  <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
    <Sparkles className="h-4 w-4 text-blue-500" />
    AI-Powered Insights
  </h3>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

    {/* Short-term */}
    <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
  <p className="text-sm text-slate-600 mb-1">Short-term (30 days)</p>
  <div className="flex items-baseline gap-2">
    <span className={`text-xl font-bold ${
      productData.predictions?.short_term_trend?.direction === 'up' ? 'text-red-600' : 
      productData.predictions?.short_term_trend?.direction === 'down' ? 'text-green-600' : 'text-slate-600'
    }`}>
      {productData.predictions?.short_term_trend?.direction?.toUpperCase() || 'STABLE'}
    </span>
    <span className={`text-sm font-medium ${
      (productData.predictions?.short_term_trend?.change_percent || 0) > 0 ? 'text-red-500' : 'text-green-500'
    }`}>
      ({(productData.predictions?.short_term_trend?.change_percent || 0) > 0 ? '+' : ''}
      {(productData.predictions?.short_term_trend?.change_percent || 0).toFixed(1)}%)
    </span>
  </div>
  <p className="text-xs text-slate-500 mt-2">
    {productData.predictions?.short_term_trend?.reasoning || 'Analysis in progress'}
  </p>
</div>

{/* Long-term - same pattern */}
<div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-100">
  <p className="text-sm text-slate-600 mb-1">Long-term (90 days)</p>
  <div className="flex items-baseline gap-2">
    <span className={`text-xl font-bold ${
      productData.predictions?.long_term_trend?.direction === 'up' ? 'text-red-600' : 
      productData.predictions?.long_term_trend?.direction === 'down' ? 'text-green-600' : 'text-slate-600'
    }`}>
      {productData.predictions?.long_term_trend?.direction?.toUpperCase() || 'STABLE'}
    </span>
    <span className={`text-sm font-medium ${
      (productData.predictions?.long_term_trend?.change_percent || 0) > 0 ? 'text-red-500' : 'text-green-500'
    }`}>
      ({(productData.predictions?.long_term_trend?.change_percent || 0) > 0 ? '+' : ''}
      {(productData.predictions?.long_term_trend?.change_percent || 0).toFixed(1)}%)
    </span>
  </div>
  <p className="text-xs text-slate-500 mt-2">
    {productData.predictions?.long_term_trend?.reasoning || 'Analysis in progress'}
  </p>
</div>
  </div>

  {productData.predictions?.factors && productData.predictions.factors.length > 0 && (
    <div className="mt-3">
      <p className="text-xs text-slate-500">
        Affecting factors: {productData.predictions.factors.join(', ')}
      </p>
    </div>
  )}
</div>

    {/* Recommended Timing */}
    {productData.predictions?.recommended_timing && (
      <div className="mt-3 p-3 bg-amber-50 rounded-lg border border-amber-200">
        <p className="text-sm font-medium text-amber-800">📅 Recommended Timing</p>
        <p className="text-sm text-amber-700">{productData.predictions.recommended_timing}</p>
        <p className="text-xs text-amber-600 mt-1">Confidence: {productData.predictions.confidence_score}%</p>
      </div>
    )}

                    {/* ML Predictions - with safe optional chaining */}
                    {productData.ml_predictions && productData.ml_predictions.average_predicted_price > 0 && (
                      <div className="mb-6">
                        <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                          <Brain className="h-4 w-4 text-green-500" />
                          Machine Learning Forecast
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100">
                            <p className="text-sm text-slate-600 mb-1">ML Predicted Price</p>
                            <p className="text-2xl font-bold text-green-600">
                              ${productData.ml_predictions.average_predicted_price.toFixed(2)}
                            </p>
                            <p className="text-xs text-slate-500 mt-1">
                              Model: {productData.ml_predictions.model_used || 'N/A'}
                            </p>
                          </div>
                          <div className="p-4 bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl border border-cyan-100">
                            <p className="text-sm text-slate-600 mb-1">ML Confidence</p>
                            <p className="text-2xl font-bold text-teal-600">
                              {productData.ml_predictions.confidence?.toFixed(0) || 0}%
                            </p>
                          </div>
                        </div>

                        {/* Supplier-specific ML predictions */}
                        {productData.ml_predictions.supplier_details && productData.ml_predictions.supplier_details.length > 0 && (
                          <details className="mt-3">
                            <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-700">
                              View supplier-level ML predictions
                            </summary>
                            <div className="mt-2 space-y-1">
                              {productData.ml_predictions.supplier_details.map((supplier: any, idx: number) => (
                                <div key={idx} className="text-xs text-slate-600 flex justify-between">
                                  <span>{supplier.supplier}</span>
                                  <span>Current: ${supplier.current_price} → ML: ${supplier.predicted_price}</span>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                    )}

                    {/* Hybrid Recommendation - with safe optional chaining */}
                    {productData.hybrid_recommendation && (
                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-slate-700">🎯 Hybrid AI+ML Recommendation</span>
                          <span className="text-sm text-blue-600">Confidence: {productData.hybrid_recommendation.combined_confidence}%</span>
                        </div>
                        <div className={`p-4 rounded-xl border ${
                          productData.hybrid_recommendation.action === 'Buy' ? 'bg-green-100 border-green-200' :
                          productData.hybrid_recommendation.action === 'Wait' ? 'bg-yellow-100 border-yellow-200' :
                          'bg-blue-100 border-blue-200'
                        }`}>
                          <p className="font-semibold text-slate-800">
                            {productData.hybrid_recommendation.recommendation}
                          </p>
                          <p className="text-sm text-slate-600 mt-1">
                            {productData.hybrid_recommendation.reasoning}
                          </p>
                          <div className="flex gap-2 mt-2">
                            <Badge className="bg-white/80 text-slate-700">AI Confidence: {productData.predictions?.confidence_score || 0}%</Badge>
                            <Badge className="bg-white/80 text-slate-700">ML Confidence: {productData.ml_predictions?.confidence?.toFixed(0) || 0}%</Badge>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Report Generation */}
                <Card className="border border-slate-200 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-blue-600">
                      <FileText className="h-5 w-5" />
                      Generate Report
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button variant="outline" onClick={() => downloadReport('html')} className="flex-1 gap-2 hover:bg-blue-50 border-slate-200">
                        <FileText className="h-4 w-4 text-blue-600" /> HTML Report
                      </Button>
                      <Button variant="outline" onClick={() => downloadReport('json')} className="flex-1 gap-2 hover:bg-yellow-50 border-slate-200">
                        <FileJson className="h-4 w-4 text-yellow-600" /> JSON Report
                      </Button>
                      <Button variant="outline" onClick={() => downloadReport('csv')} className="flex-1 gap-2 hover:bg-green-50 border-slate-200">
                        <FileSpreadsheet className="h-4 w-4 text-green-600" /> CSV Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Schedule Price Check */}
<Card className="border-2 border-purple-200 shadow-lg">
  <CardHeader>
    <CardTitle className="flex items-center gap-2 text-purple-600">
      <CalendarIcon className="h-5 w-5" />
      Schedule Price Check
    </CardTitle>
  </CardHeader>
  <CardContent>
    {!showScheduleForm ? (
      <Button
        onClick={() => setShowScheduleForm(true)}
        className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
      >
        <Bell className="h-4 w-4 mr-2" />
        Schedule Price Check for {productData.product_name}
      </Button>
    ) : (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-slate-700 font-medium">Frequency</Label>
            <Select value={scheduleFrequency} onValueChange={setScheduleFrequency}>
              <SelectTrigger className="w-full bg-white border-2 border-slate-200 rounded-lg px-3 py-2 text-slate-700">
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent className="bg-white border-2 border-slate-200 rounded-lg shadow-lg">
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label className="text-slate-700 font-medium">Time</Label>
            <Input
              type="time"
              value={scheduleTime}
              onChange={(e) => setScheduleTime(e.target.value)}
              className="w-full bg-white border-2 border-slate-200 rounded-lg px-3 py-2 text-slate-700"
            />
          </div>
        </div>

        <div>
          <Label className="text-slate-700 font-medium">Notification Method</Label>
          <Select value={notificationMethod} onValueChange={setNotificationMethod}>
            <SelectTrigger className="w-full bg-white border-2 border-slate-200 rounded-lg px-3 py-2 text-slate-700">
              <SelectValue placeholder="Select notification method" />
            </SelectTrigger>
            <SelectContent className="bg-white border-2 border-slate-200 rounded-lg shadow-lg">
              <SelectItem value="email">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-blue-500" />
                  <span>Email Only</span>
                </div>
              </SelectItem>
              <SelectItem value="calendar">
                <div className="flex items-center gap-2">
                  <GoogleCalendar className="h-4 w-4 text-green-500" />
                  <span>Calendar Only</span>
                </div>
              </SelectItem>
              <SelectItem value="both">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-blue-500" />
                  <GoogleCalendar className="h-4 w-4 text-green-500" />
                  <span>Both</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* FIXED: Email field only shows when email or both is selected */}
        {notificationMethod === 'email' || notificationMethod === 'both' ? (
  <div>
    <Label className="text-slate-700 font-medium">Email Address</Label>
    <Input
      type="email"
      placeholder="your-email@example.com"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      className="w-full bg-white border-2 border-slate-200 rounded-lg px-3 py-2 text-slate-700"
    />
  </div>
        ): null}

        <div className="flex gap-3 pt-2">
          <Button onClick={handleAddTask} className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700">
            Create Task
          </Button>
          <Button variant="outline" onClick={() => setShowScheduleForm(false)} className="flex-1 border-2 border-slate-200 hover:bg-slate-50">
            Cancel
          </Button>
        </div>
      </div>
    )}
  </CardContent>
</Card>
              </motion.div>
            ) : (
              <Card className="border border-slate-200 shadow-lg">
                <CardContent className="p-16 text-center">
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Search className="h-12 w-12 text-blue-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-600 mb-2">Search for a Product</h3>
                  <p className="text-slate-500">Enter a product name above to see price comparison across multiple suppliers</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tasks & Calendar Tab */}
          <TabsContent value="tasks" className="space-y-6">
            <Card className="border border-slate-200 shadow-lg">
              <CardHeader className="border-b border-slate-200">
                <CardTitle className="flex items-center gap-2 text-slate-800">
                  <Bell className="h-5 w-5" />
                  Scheduled Tasks
                </CardTitle>
              </CardHeader>

              <CardContent className="p-6">
                {/* View Toggle */}
                <div className="flex justify-between items-center mb-6">
                  <div className="flex gap-2">
                    <Button
                      variant={tasksView === 'list' ? 'default' : 'outline'}
                      onClick={() => setTasksView('list')}
                      className="gap-2"
                    >
                      <List className="h-4 w-4" /> List View
                    </Button>
                    <Button
                      variant={tasksView === 'calendar' ? 'default' : 'outline'}
                      onClick={() => setTasksView('calendar')}
                      className="gap-2"
                    >
                      <LayoutGrid className="h-4 w-4" /> Calendar View
                    </Button>
                  </div>

                  <Button variant="outline" onClick={fetchTasks} className="gap-2">
                    <RefreshCw className="h-4 w-4" /> Refresh
                  </Button>
                </div>

                {/* Calendar View */}
                {tasksView === 'calendar' && (
                  <div className="space-y-4">
                    {/* Calendar Navigation */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={goToToday} className="rounded-lg border-slate-200">
                          Today
                        </Button>
                        <Button variant="outline" size="sm" onClick={goToPrevMonth} className="rounded-lg border-slate-200">
                          <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm" onClick={goToNextMonth} className="rounded-lg border-slate-200">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                      <h3 className="text-2xl font-bold text-slate-800">
                        {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                      </h3>
                    </div>

                    {/* Calendar Grid - with border */}
                    {validTasks.length === 0 ? (
                      <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-slate-200">
                        <CalendarIcon className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                        <p className="text-slate-500 font-medium">No tasks scheduled</p>
                        <p className="text-sm text-slate-400 mt-1">
                          Schedule a price check to see it on the calendar
                        </p>
                      </div>
                    ) : (
                      <>
                        {/* Weekday Headers */}
                        <div
                          style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}
                          className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-xl border border-slate-200 border-b-0 overflow-hidden"
                        >
                          {weekdays.map((day) => (
                            <div
                              key={day}
                              className="py-3 text-center text-xs md:text-sm font-semibold text-slate-600 border-r border-slate-200 last:border-r-0"
                            >
                              {day}
                            </div>
                          ))}
                        </div>

                        {/* Calendar Days - force 7 columns x 6 rows with border */}
                        <div
                          style={{ display: "grid", gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}
                          className="w-full grid-rows-6 bg-white rounded-b-xl shadow-lg border border-slate-200 overflow-hidden h-[720px]"
                        >
                          {getCalendarDays(currentMonth).map((day, idx) => {
                            const isToday = day.date.toDateString() === new Date().toDateString();
                            const hasTasks = day.tasks.length > 0;
                            const isWeekend = day.date.getDay() === 0 || day.date.getDay() === 6;

                            return (
                              <div key={idx} className="row-auto h-full border-r border-b border-slate-200 last:border-r-0">
                                <button
                                  type="button"
                                  disabled={!hasTasks}
                                  onClick={() => {
                                    if (!hasTasks) return;
                                    setSelectedDay({
                                      date: day.date,
                                      tasks: day.tasks,
                                      isCurrentMonth: day.isCurrentMonth
                                    });
                                  }}
                                  className={`inline-flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-full text-sm font-medium transition-all ${
                                    isToday
                                      ? "bg-blue-600 text-white ring-4 ring-blue-200/50"
                                      : hasTasks
                                        ? "bg-indigo-100 text-indigo-700 border border-indigo-200"
                                        : "bg-slate-100 text-slate-400 border border-slate-200"
                                  }`}
                                >
                                  {day.date.getDate()}
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    )}

                                        {/* Legend */}
                    {validTasks.length > 0 && (
                      <div className="flex items-center justify-center gap-6 mt-4 p-3 bg-white rounded-lg shadow-sm border-2 border-indigo-200">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 ring-2 ring-indigo-200"></div>
                          <span className="text-xs text-slate-600 font-medium">Today</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-indigo-100 border-2 border-indigo-200"></div>
                          <span className="text-xs text-slate-600 font-medium">Task day</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-slate-100 border-2 border-slate-200"></div>
                          <span className="text-xs text-slate-600 font-medium">Other days</span>
                        </div>
                      </div>
                    )}

                    {/* Click interaction modal */}
                    <CalendarModal
                      open={!!selectedDay}
                      onClose={() => setSelectedDay(null)}
                      title={selectedDay ? formatDayLabel(selectedDay.date) : ''}
                    >
                      {selectedDay && selectedDay.tasks.length > 0 ? (
                        <div className="space-y-3">
                          {selectedDay.tasks
                            .slice()
                            .sort((a, b) => (a.time < b.time ? -1 : 1))
                            .map((task) => (
                              <div
                                key={task.id}
                                className="p-4 rounded-xl border border-slate-200 bg-gradient-to-r from-white to-slate-50 hover:shadow-md transition"
                              >
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                  <div className="min-w-0 flex-1">
                                    <div className="font-semibold text-slate-800 truncate">
                                      {task.product_name}
                                    </div>
                                    <div className="text-sm text-slate-500 mt-1">
                                      Runs at{' '}
                                      <span className="font-medium text-slate-700">{task.time}</span> •{' '}
                                      {task.frequency}
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="bg-white border-slate-200">
                                      <Clock className="h-3.5 w-3.5 mr-1" />
                                      {task.time}
                                    </Badge>
                                    <Badge className={task.active ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-700'}>
                                      {task.active ? 'Active' : 'Paused'}
                                    </Badge>
                                  </div>
                                </div>

                                <div className="mt-3 flex flex-wrap gap-3 text-sm text-slate-600">
                                  <span className="inline-flex items-center gap-2">
                                    {getNotificationIcon(task.notification_method)}{' '}
                                    <span className="capitalize">{task.notification_method}</span>
                                  </span>
                                  {task.email && (
                                    <span className="inline-flex items-center gap-2">
                                      <Mail className="h-4 w-4 text-slate-500" />
                                      {task.email}
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                        </div>
                      ) : (
                        <div className="text-center py-10">
                          <p className="text-slate-500 font-medium">No tasks on this day.</p>
                        </div>
                      )}
                    </CalendarModal>
                  </div>
                )}

                {/* List View */}
                {tasksView === 'list' && (
                  <div className="space-y-4">
                    {tasksLoading ? (
                      <div className="text-center py-12 text-slate-500">Loading tasks...</div>
                    ) : tasks.length === 0 ? (
                      <div className="text-center py-12">
                        <Bell className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                        <p className="text-slate-500">
                          No scheduled tasks. Search for a product above and schedule a price check.
                        </p>
                      </div>
                    ) : (
                      tasks.map((task) => (
                        <div
                          key={task.id}
                          className="border border-slate-200 rounded-xl p-5 hover:shadow-md transition-shadow bg-white"
                        >
                          {editingTask?.id === task.id ? (
                            <div className="space-y-4">
                              <h3 className="font-semibold text-lg text-slate-800">Edit Task: {task.product_name}</h3>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <Label className="text-slate-700">Frequency</Label>
                                  <Select
                                    value={editingTask.frequency}
                                    onValueChange={(v) =>
                                      setEditingTask({ ...editingTask, frequency: v })
                                    }
                                  >
                                    <SelectTrigger className="border-slate-200"><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="daily">Daily</SelectItem>
                                      <SelectItem value="weekly">Weekly</SelectItem>
                                      <SelectItem value="monthly">Monthly</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div>
                                  <Label className="text-slate-700">Time</Label>
                                  <Input
                                    type="time"
                                    value={editingTask.time}
                                    onChange={(e) =>
                                      setEditingTask({ ...editingTask, time: e.target.value })
                                    }
                                    className="border-slate-200"
                                  />
                                </div>
                              </div>

                              <div>
                                <Label className="text-slate-700">Notification Method</Label>
                                <Select
                                  value={editingTask.notification_method}
                                  onValueChange={(v) =>
                                    setEditingTask({ ...editingTask, notification_method: v })
                                  }
                                >
                                  <SelectTrigger className="border-slate-200"><SelectValue /></SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="email">Email Only</SelectItem>
                                    <SelectItem value="calendar">Calendar Only</SelectItem>
                                    <SelectItem value="both">Both</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>

                              {(editingTask.notification_method === 'email' || editingTask.notification_method === 'both') && (
                                <div>
                                  <Label className="text-slate-700">Email Address</Label>
                                  <Input
                                    type="email"
                                    value={editingTask.email || ''}
                                    onChange={(e) =>
                                      setEditingTask({ ...editingTask, email: e.target.value })
                                    }
                                    className="border-slate-200"
                                  />
                                </div>
                              )}

                              <div className="flex gap-3">
                                <Button onClick={updateTask} className="bg-blue-600 hover:bg-blue-700">Save Changes</Button>
                                <Button variant="outline" onClick={() => setEditingTask(null)}>Cancel</Button>
                              </div>
                            </div>
                          ) : (
                            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 flex-wrap">
                                  <h3 className="font-semibold text-lg text-slate-800">{task.product_name}</h3>
                                  {getFrequencyBadge(task.frequency)}
                                  {task.active ? (
                                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                                  ) : (
                                    <Badge variant="secondary">Paused</Badge>
                                  )}
                                </div>

                                <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-600">
                                  <div className="flex items-center gap-1">
                                    <Clock className="h-4 w-4" /> Runs at {task.time}
                                  </div>
                                  <div className="flex items-center gap-1">
                                    {getNotificationIcon(task.notification_method)}
                                    <span className="capitalize">{task.notification_method}</span>
                                  </div>
                                  {task.email && (
                                    <div className="flex items-center gap-1">
                                      <Mail className="h-4 w-4" /> {task.email}
                                    </div>
                                  )}
                                </div>

                                <div className="flex flex-wrap gap-4 mt-2 text-xs text-slate-400">
                                  {task.last_run && <div>Last run: {new Date(task.last_run).toLocaleString()}</div>}
                                  {task.next_run && <div>Next run: {new Date(task.next_run).toLocaleString()}</div>}
                                </div>
                              </div>

                              <div className="flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => toggleTaskActive(task)}
                                  className="gap-1"
                                >
                                  {task.active ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                  {task.active ? 'Pause' : 'Activate'}
                                </Button>

                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setEditingTask(task)}
                                  className="gap-1"
                                >
                                  <Edit className="h-4 w-4" /> Edit
                                </Button>

                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => deleteTask(task.id)}
                                  className="gap-1"
                                >
                                  <Trash2 className="h-4 w-4" /> Delete
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

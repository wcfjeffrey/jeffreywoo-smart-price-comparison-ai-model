'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, TrendingUp, Star, Truck, DollarSign, Bell, Calendar, Mail, Clock } from 'lucide-react';

interface Supplier {
  product_name: string;
  supplier: string;
  price: number;
  delivery_time: number;
  rating: number;
}

interface BestPrice {
  supplier: string;
  price: number;
  delivery_time: number;
  rating: number;
  score: number;
}

interface ProductAnalysis {
  product_name: string;
  suppliers: Supplier[];
  best_price: BestPrice;
  price_range: {
    min: number;
    max: number;
  };
  recommendations: string[];
}

export function ProductInput() {
  const [productName, setProductName] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<ProductAnalysis | null>(null);
  const [error, setError] = useState('');
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleFrequency, setScheduleFrequency] = useState('weekly');
  const [scheduleTime, setScheduleTime] = useState('09:00');
  const [notificationMethod, setNotificationMethod] = useState('email');
  const [email, setEmail] = useState('');
  const [taskCreated, setTaskCreated] = useState(false);

  const handleAnalyze = async () => {
    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);
    setTaskCreated(false);

    try {
      const response = await fetch(`/api/products/compare/${encodeURIComponent(productName)}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.status === 'success' && result.data) {
        setAnalysis(result.data);
      } else {
        setError(result.message || 'Analysis failed');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError('Failed to connect to server. Please make sure the backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async () => {
    if (!analysis) return;

    if ((notificationMethod === 'email' || notificationMethod === 'both') && !email) {
      setError('Please enter an email address for notifications');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: analysis.product_name,
          frequency: scheduleFrequency,
          time: scheduleTime,
          day_of_week: scheduleFrequency === 'weekly' ? 0 : null,
          notification_method: notificationMethod,
          email: email || null
        })
      });

      if (response.ok) {
        setTaskCreated(true);
        setShowScheduleForm(false);
        // Show success message
        setTimeout(() => setTaskCreated(false), 5000);
      } else {
        const errorData = await response.json();
        setError(`Failed to add task: ${errorData.message || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Task creation error:', err);
      setError('Failed to add task. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-0 shadow-xl bg-gradient-to-br from-white to-gray-50">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-xl">
        <CardTitle className="text-2xl flex items-center gap-2">
          <Search className="h-6 w-6 text-blue-600" />
          Product Price Analysis
        </CardTitle>
        <CardDescription className="text-gray-600">
          Enter a product name to get real-time price comparison from multiple suppliers
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6 p-6">
        {/* Search Input */}
        <div className="flex gap-3">
          <Input
            placeholder="e.g., iPhone 17 Pro, MSI Titan 18 HX AI, Samsung Galaxy S25"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            className="flex-1 text-lg py-6"
          />
          <Button onClick={handleAnalyze} disabled={loading} className="px-8">
            {loading ? 'Analyzing...' : 'Analyze'}
          </Button>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="bg-red-50 border-red-200">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Success Message */}
        {taskCreated && (
          <Alert className="bg-green-50 border-green-200 text-green-800">
            <AlertDescription>
              ✅ Task created successfully! You will receive price alerts at your email.
            </AlertDescription>
          </Alert>
        )}

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6 animate-fadeIn">
            {/* Product Header */}
            <div className="text-center py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
              <h2 className="text-3xl font-bold">{analysis.product_name}</h2>
              <p className="text-blue-100 mt-1">Real-time price analysis</p>
            </div>

            {/* Best Price & Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="p-5 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  <h3 className="font-bold text-lg text-green-800">Best Price</h3>
                </div>
                <p className="text-4xl text-green-600 font-bold">${analysis.best_price.price.toFixed(2)}</p>
                <p className="text-gray-700 mt-2 font-medium">{analysis.best_price.supplier}</p>
                <div className="flex gap-3 mt-3 text-sm text-gray-600">
                  <span className="flex items-center gap-1"><Truck className="h-3 w-3" /> {analysis.best_price.delivery_time} days</span>
                  <span className="flex items-center gap-1"><Star className="h-3 w-3 fill-yellow-500" /> {analysis.best_price.rating}/5</span>
                </div>
              </div>

              <div className="p-5 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp className="h-5 w-5 text-blue-600" />
                  <h3 className="font-bold text-lg text-blue-800">Price Range</h3>
                </div>
                <p className="text-3xl font-bold text-blue-600">${analysis.price_range.min.toFixed(2)} - ${analysis.price_range.max.toFixed(2)}</p>
                <p className="text-sm text-gray-600 mt-2">Across {analysis.suppliers.length} suppliers</p>
              </div>
            </div>

            {/* All Suppliers */}
            {analysis.suppliers && analysis.suppliers.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3 text-lg flex items-center gap-2">
                  <Truck className="h-5 w-5 text-gray-600" />
                  All Suppliers
                </h3>
                <div className="space-y-3">
                  {analysis.suppliers.map((supplier, i) => (
                    <div key={i} className={`flex justify-between items-center p-4 rounded-xl transition-all hover:shadow-md ${
                      supplier.supplier === analysis.best_price.supplier 
                        ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200' 
                        : 'bg-white border border-gray-200'
                    }`}>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-lg">{supplier.supplier}</span>
                          {supplier.supplier === analysis.best_price.supplier && (
                            <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">Best Deal</span>
                          )}
                        </div>
                        <div className="flex gap-3 mt-1 text-sm text-gray-500">
                          <span>Delivery: {supplier.delivery_time} days</span>
                          <span>⭐ {supplier.rating}/5</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-2xl text-green-600">${supplier.price.toFixed(2)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {analysis.recommendations && analysis.recommendations.length > 0 && (
              <div className="p-5 bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl border border-amber-200">
                <h3 className="font-semibold mb-3 text-amber-800 flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  📋 Recommendations
                </h3>
                <ul className="space-y-2">
                  {analysis.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-700">
                      <span className="text-amber-600">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Schedule Button */}
            <Button
              onClick={() => setShowScheduleForm(!showScheduleForm)}
              variant="outline"
              className="w-full py-6 text-lg border-2 hover:bg-blue-50"
            >
              <Calendar className="h-5 w-5 mr-2" />
              {showScheduleForm ? 'Cancel' : '📅 Schedule Price Check'}
            </Button>

            {/* Schedule Form */}
            {showScheduleForm && (
              <div className="p-6 border-2 rounded-xl bg-gray-50 space-y-4">
                <h3 className="font-semibold text-xl flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  Schedule Settings for {analysis.product_name}
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-700">Frequency</Label>
                    <Select value={scheduleFrequency} onValueChange={setScheduleFrequency}>
                      <SelectTrigger className="bg-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-gray-700">Time</Label>
                    <Input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className="bg-white"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-gray-700">Notification Method</Label>
                  <Select value={notificationMethod} onValueChange={setNotificationMethod}>
                    <SelectTrigger className="bg-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="email">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" /> Email Only
                        </div>
                      </SelectItem>
                      <SelectItem value="calendar">
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" /> Calendar Only
                        </div>
                      </SelectItem>
                      <SelectItem value="both">
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4" /> <Calendar className="h-4 w-4" /> Both
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {(notificationMethod === 'email' || notificationMethod === 'both') && (
                  <div>
                    <Label className="text-gray-700">Email Address</Label>
                    <Input
                      type="email"
                      placeholder="your-email@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="bg-white"
                    />
                    <p className="text-xs text-gray-500 mt-1">You will receive price alerts at this email</p>
                  </div>
                )}

                <Button onClick={handleAddTask} className="w-full py-5 text-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
                  <Bell className="h-5 w-5 mr-2" />
                  Create Scheduled Task for {analysis.product_name}
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
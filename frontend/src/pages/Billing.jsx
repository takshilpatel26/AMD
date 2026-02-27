import React, { useState, useEffect } from 'react';
import { 
  Receipt, 
  CreditCard, 
  Download, 
  FileText,
  Calendar,
  TrendingUp,
  TrendingDown,
  DollarSign,
  IndianRupee,
  CheckCircle,
  Clock,
  AlertCircle,
  Filter,
  ChevronDown,
  ChevronRight,
  Eye,
  Printer,
  RefreshCw,
  BarChart3,
  PieChart as PieChartIcon,
  Zap
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  LineChart,
  Line
} from 'recharts';
import api from '../services/api';
import { useBillingData } from '../hooks/useRealtimeData';

// Status badge
const PaymentStatus = ({ status }) => {
  const config = {
    paid: { bg: 'bg-emerald-100', text: 'text-emerald-700', icon: CheckCircle },
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: Clock },
    overdue: { bg: 'bg-red-100', text: 'text-red-700', icon: AlertCircle },
  };
  
  const c = config[status] || config.pending;
  const Icon = c.icon;
  
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <Icon className="w-3 h-3" />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(amount || 0);
};

// Bill Card Component
const BillCard = ({ bill, onView }) => {
  const dueDate = new Date(bill.due_date);
  const isOverdue = bill.status !== 'paid' && dueDate < new Date();
  
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow border border-slate-200">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-slate-500">Bill #{bill.bill_number || bill.id}</p>
          <h4 className="font-semibold text-slate-900 mt-1">{bill.month || bill.billing_period}</h4>
        </div>
        <PaymentStatus status={isOverdue ? 'overdue' : bill.status} />
      </div>
      
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Units Consumed</span>
          <span className="font-medium text-slate-900">{bill.units_consumed || bill.energy_consumed} kWh</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Amount</span>
          <span className="font-bold text-xl text-slate-900">{formatCurrency(bill.amount || bill.total_amount)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Due Date</span>
          <span className={`text-sm font-medium ${isOverdue ? 'text-red-500' : 'text-slate-700'}`}>
            {dueDate.toLocaleDateString('en-IN')}
          </span>
        </div>
      </div>
      
      <div className="flex gap-2 mt-4 pt-4 border-t border-slate-100">
        <button
          onClick={() => onView(bill)}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-emerald-50 text-emerald-600 rounded-lg hover:bg-emerald-100 transition-colors text-sm font-medium"
        >
          <Eye className="w-4 h-4" />
          View
        </button>
        <button
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-slate-50 text-slate-600 rounded-lg hover:bg-slate-100 transition-colors text-sm font-medium"
        >
          <Download className="w-4 h-4" />
          Download
        </button>
      </div>
    </div>
  );
};

// Invoice Row Component
const InvoiceRow = ({ invoice, expanded, onToggle }) => {
  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <div 
        className="flex items-center justify-between p-4 bg-white cursor-pointer hover:bg-slate-50"
        onClick={onToggle}
      >
        <div className="flex items-center gap-4">
          <div className="p-2 bg-emerald-100 rounded-lg">
            <FileText className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p className="font-medium text-slate-900">Invoice #{invoice.invoice_number || invoice.id}</p>
            <p className="text-sm text-slate-500">{new Date(invoice.date || invoice.created_at).toLocaleDateString('en-IN')}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="font-bold text-slate-900">{formatCurrency(invoice.amount || invoice.total)}</span>
          <PaymentStatus status={invoice.status || 'pending'} />
          <ChevronRight className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />
        </div>
      </div>
      
      {expanded && (
        <div className="p-4 bg-slate-50 border-t border-slate-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-slate-500">Meter ID</p>
              <p className="font-medium text-slate-900">{invoice.meter_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Billing Period</p>
              <p className="font-medium text-slate-900">{invoice.billing_period || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Units</p>
              <p className="font-medium text-slate-900">{invoice.units || invoice.energy_consumed || 0} kWh</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Rate</p>
              <p className="font-medium text-slate-900">{formatCurrency(invoice.rate || 5)}/kWh</p>
            </div>
          </div>
          <div className="flex gap-2 mt-4">
            <button className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50">
              <Printer className="w-4 h-4" />
              Print
            </button>
            <button className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50">
              <Download className="w-4 h-4" />
              Download PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Stats Card
const StatsCard = ({ icon: Icon, label, value, subValue, trend, color, bgColor }) => (
  <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
        {subValue && <p className="text-xs text-slate-500 mt-1">{subValue}</p>}
      </div>
      <div className={`p-3 rounded-xl ${bgColor}`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
    </div>
    {trend !== undefined && (
      <div className={`flex items-center gap-1 mt-2 text-sm ${trend <= 0 ? 'text-green-500' : 'text-red-500'}`}>
        {trend <= 0 ? <TrendingDown className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
        <span>{Math.abs(trend)}% vs last month</span>
      </div>
    )}
  </div>
);

// Main Billing Page
const Billing = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [bills, setBills] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedInvoice, setExpandedInvoice] = useState(null);
  const [selectedBill, setSelectedBill] = useState(null);
  const [dateRange, setDateRange] = useState('3months');
  
  // Real-time simulated billing data
  const realtimeBilling = useBillingData();

  // Fetch data
  const fetchData = async () => {
    setLoading(true);
    try {
      const [billsData, invoicesData, summaryData] = await Promise.all([
        api.getBills(),
        api.getInvoices(),
        api.getBillingSummary()
      ]);
      setBills(billsData || realtimeBilling.bills);
      setInvoices(invoicesData || realtimeBilling.invoices);
      setSummary(summaryData || {
        current_month_units: realtimeBilling.currentMonth.units,
        current_month_amount: realtimeBilling.currentMonth.amount
      });
    } catch (err) {
      console.error('Failed to fetch billing data:', err);
      // Use realtime data as fallback
      setBills(realtimeBilling.bills);
      setInvoices(realtimeBilling.invoices);
      setSummary({
        current_month_units: realtimeBilling.currentMonth.units,
        current_month_amount: realtimeBilling.currentMonth.amount
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Calculate summary stats - prioritize live data
  const displayBills = bills.length > 0 ? bills : realtimeBilling.bills;
  const displayInvoices = invoices.length > 0 ? invoices : realtimeBilling.invoices;
  const currentMonthData = realtimeBilling.currentMonth;
  
  // Calculate stats from realtime billing data
  const totalFromPastBills = displayBills.reduce((sum, b) => sum + (b.amount || b.total_amount || 0), 0);
  const totalUnitsFromPastBills = displayBills.reduce((sum, b) => sum + (b.units_consumed || b.energy_consumed || 0), 0);
  
  const stats = {
    total_amount: totalFromPastBills + (currentMonthData.amount || 0),
    pending_amount: currentMonthData.amount || 0,
    total_units: totalUnitsFromPastBills + (currentMonthData.units || 0),
    average_rate: displayBills.length > 0 
      ? (totalFromPastBills / Math.max(1, totalUnitsFromPastBills)).toFixed(2) 
      : '5.50',
    bills_count: displayBills.length + 1, // +1 for current month
    pending_count: 1, // Current month is pending
    paid_count: displayBills.filter(b => b.status === 'paid').length,
    current_units: currentMonthData.units,
    current_amount: currentMonthData.amount,
  };

  // Monthly billing chart data
  const monthlyData = displayBills.slice(0, 6).reverse().map(bill => ({
    month: bill.month || new Date(bill.created_at).toLocaleDateString('en-IN', { month: 'short' }),
    amount: bill.amount || bill.total_amount || 0,
    units: bill.units_consumed || bill.energy_consumed || 0
  }));

  // Payment status distribution
  const paymentStatusData = [
    { name: 'Paid', value: stats.paid_count || displayBills.filter(b => b.status === 'paid').length, color: '#22C55E' },
    { name: 'Pending', value: stats.pending_count || displayBills.filter(b => b.status === 'pending').length, color: '#EAB308' },
    { name: 'Overdue', value: displayBills.filter(b => b.status === 'overdue' || (b.status !== 'paid' && new Date(b.due_date) < new Date())).length, color: '#EF4444' },
  ].filter(d => d.value > 0);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'bills', label: 'Bills', icon: Receipt },
    { id: 'invoices', label: 'Invoices', icon: FileText },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 mx-auto text-emerald-500 animate-spin mb-4" />
          <p className="text-slate-600">Loading billing data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Billing & Payments</h1>
            <p className="text-slate-500">Manage your bills, invoices and payments</p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="1month">Last Month</option>
              <option value="3months">Last 3 Months</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last Year</option>
            </select>
            <button 
              onClick={fetchData}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatsCard 
            icon={IndianRupee} 
            label="Total Billed" 
            value={formatCurrency(stats.total_amount)}
            subValue={`${stats.bills_count} bills`}
            bgColor="bg-emerald-100"
            color="text-emerald-600"
          />
          <StatsCard 
            icon={Clock} 
            label="Pending Amount" 
            value={formatCurrency(stats.pending_amount)}
            subValue={`${stats.pending_count} bills`}
            bgColor="bg-yellow-100"
            color="text-yellow-600"
          />
          <StatsCard 
            icon={Zap} 
            label="Total Units" 
            value={`${stats.total_units?.toLocaleString() || 0} kWh`}
            trend={-5}
            bgColor="bg-emerald-100"
            color="text-emerald-600"
          />
          <StatsCard 
            icon={TrendingDown} 
            label="Avg. Rate" 
            value={`₹${typeof stats.average_rate === 'number' ? stats.average_rate.toFixed(2) : stats.average_rate || '5.50'}/kWh`}
            bgColor="bg-emerald-100"
            color="text-emerald-600"
          />
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap
                ${activeTab === tab.id 
                  ? 'bg-emerald-600 text-white' 
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Current Month Live Bill */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-emerald-100 text-sm">Current Month (Live)</p>
                  <h2 className="text-3xl font-bold">{formatCurrency(currentMonthData.amount || 0)}</h2>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-2 text-blue-100">
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                    <span className="text-sm">Live Calculation</span>
                  </div>
                  <p className="text-2xl font-bold mt-1">{currentMonthData.units?.toFixed(2) || 0} kWh</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-blue-400/30">
                <div>
                  <p className="text-blue-200 text-xs">Base Amount</p>
                  <p className="font-semibold">{formatCurrency(currentMonthData.baseAmount || 0)}</p>
                </div>
                <div>
                  <p className="text-blue-200 text-xs">Fixed Charges</p>
                  <p className="font-semibold">{formatCurrency(currentMonthData.fixedCharges || 50)}</p>
                </div>
                <div>
                  <p className="text-blue-200 text-xs">Electricity Duty (15%)</p>
                  <p className="font-semibold">{formatCurrency(currentMonthData.electricityDuty || 0)}</p>
                </div>
              </div>
              <div className="mt-4 text-sm text-blue-200">
                Due Date: {currentMonthData.dueDate ? new Date(currentMonthData.dueDate).toLocaleDateString('en-IN') : 'N/A'}
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Monthly Billing Chart */}
              <div className="lg:col-span-2 bg-white rounded-xl p-5 shadow-sm border border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Monthly Billing Trend</h3>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={monthlyData}>
                      <defs>
                        <linearGradient id="amountGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                      <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
                      <YAxis stroke="#9CA3AF" fontSize={12} tickFormatter={(v) => `₹${v}`} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                        formatter={(value, name) => [name === 'amount' ? formatCurrency(value) : `${value} kWh`, name === 'amount' ? 'Amount' : 'Units']}
                      />
                      <Legend />
                      <Area 
                        type="monotone" 
                        dataKey="amount" 
                        stroke="#3B82F6" 
                        fill="url(#amountGradient)" 
                        strokeWidth={2}
                        name="Amount (₹)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

            {/* Payment Status Pie Chart */}
            <div className="bg-white rounded-xl p-5 shadow-sm border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Payment Status</h3>
              {paymentStatusData.length > 0 ? (
                <>
                  <div className="h-52">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={paymentStatusData}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {paymentStatusData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-2 mt-4">
                    {paymentStatusData.map((item) => (
                      <div key={item.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></span>
                          <span className="text-sm text-slate-600">{item.name}</span>
                        </div>
                        <span className="font-medium text-slate-900">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-center text-slate-500 py-8">No payment data</p>
              )}
            </div>
            </div>

            {/* Units vs Amount Comparison */}
            <div className="bg-white rounded-xl p-5 shadow-sm mt-6 border border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Units vs Amount Comparison</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                    <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
                    <YAxis yAxisId="amount" orientation="left" stroke="#3B82F6" fontSize={12} tickFormatter={(v) => `₹${v}`} />
                    <YAxis yAxisId="units" orientation="right" stroke="#10B981" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                      formatter={(value, name) => [name === 'Amount' ? formatCurrency(value) : `${value} kWh`, name]}
                    />
                    <Legend />
                    <Bar yAxisId="amount" dataKey="amount" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Amount" />
                    <Bar yAxisId="units" dataKey="units" fill="#10B981" radius={[4, 4, 0, 0]} name="Units (kWh)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'bills' && (
          <div>
            {displayBills.length === 0 ? (
              <div className="bg-white rounded-xl p-8 shadow-sm text-center border border-slate-200">
                <Receipt className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-medium text-slate-700">No Bills Found</h3>
                <p className="text-slate-500 mt-2">Your bills will appear here once generated</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displayBills.map((bill) => (
                  <BillCard key={bill.id} bill={bill} onView={setSelectedBill} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'invoices' && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-5 border-b border-slate-200">
              <h3 className="text-lg font-semibold text-slate-900">All Invoices</h3>
              <p className="text-sm text-slate-500">{displayInvoices.length} total invoices</p>
            </div>
            
            {displayInvoices.length === 0 ? (
              <div className="p-8 text-center">
                <FileText className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                <h3 className="text-lg font-medium text-slate-700">No Invoices Found</h3>
                <p className="text-slate-500 mt-2">Your invoices will appear here once generated</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-200">
                {displayInvoices.map((invoice) => (
                  <InvoiceRow 
                    key={invoice.id} 
                    invoice={invoice} 
                    expanded={expandedInvoice === invoice.id}
                    onToggle={() => setExpandedInvoice(expandedInvoice === invoice.id ? null : invoice.id)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Bill Detail Modal */}
        {selectedBill && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full max-h-[90vh] overflow-auto">
              <div className="p-6 border-b border-slate-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-slate-900">Bill Details</h3>
                  <button 
                    onClick={() => setSelectedBill(null)}
                    className="p-2 hover:bg-slate-100 rounded-lg"
                  >
                    <ChevronDown className="w-5 h-5 text-gray-500" />
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Bill Number</span>
                  <span className="font-semibold text-slate-900">#{selectedBill.bill_number || selectedBill.id}</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Billing Period</span>
                  <span className="font-semibold text-slate-900">{selectedBill.month || selectedBill.billing_period}</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Units Consumed</span>
                  <span className="font-semibold text-slate-900">{selectedBill.units_consumed || selectedBill.energy_consumed} kWh</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Rate</span>
                  <span className="font-semibold text-slate-900">{formatCurrency(selectedBill.rate || 5)}/kWh</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Total Amount</span>
                  <span className="font-bold text-2xl text-emerald-600">{formatCurrency(selectedBill.amount || selectedBill.total_amount)}</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-slate-200">
                  <span className="text-slate-500">Due Date</span>
                  <span className="font-semibold text-slate-900">{new Date(selectedBill.due_date).toLocaleDateString('en-IN')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Status</span>
                  <PaymentStatus status={selectedBill.status} />
                </div>
              </div>
              
              <div className="p-6 border-t border-slate-200 flex gap-3">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors font-medium">
                  <CreditCard className="w-5 h-5" />
                  Pay Now
                </button>
                <button className="flex items-center justify-center gap-2 px-4 py-3 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors">
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Billing;

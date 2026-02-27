import React, { useState, useEffect } from 'react';
import { LogIn, UserPlus, Phone, Lock, User, Eye, EyeOff, ArrowRight, ArrowLeft, MapPin } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useTheme } from '../contexts/ThemeContext';
import { useLanguage } from '../contexts/LanguageContext';
import authService from '../services/authService';

const Auth = ({ onAuthSuccess }) => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [step, setStep] = useState('mobile'); // 'mobile' or 'otp'
  const [loading, setLoading] = useState(false);
  const { isDark } = useTheme();
  const { t, language } = useLanguage();

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    village: '',
    mobile: '',
    role: 'farmer',
    otp: ['', '', '', '', '', ''],
  });

  const [otpTimer, setOtpTimer] = useState(30);
  const [canResend, setCanResend] = useState(false);
  const [timerInterval, setTimerInterval] = useState(null);
  const [displayOtp, setDisplayOtp] = useState('');

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    };
  }, [timerInterval]);

  const startTimer = () => {
    setCanResend(false);
    let timer = 30;
    setOtpTimer(timer);
    
    const interval = setInterval(() => {
      timer -= 1;
      setOtpTimer(timer);
      if (timer === 0) {
        clearInterval(interval);
        setCanResend(true);
        setOtpTimer(30);
      }
    }, 1000);
    
    setTimerInterval(interval);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleOtpChange = (index, value) => {
    // Only allow numbers
    if (value && !/^\d$/.test(value)) return;

    const newOtp = [...formData.otp];
    newOtp[index] = value;
    setFormData({ ...formData, otp: newOtp });

    // Auto-focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      if (nextInput) nextInput.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace' && !formData.otp[index] && index > 0) {
      const prevInput = document.getElementById(`otp-${index - 1}`);
      if (prevInput) prevInput.focus();
    }
  };

  const handleSendOtp = async (e) => {
    e.preventDefault();
    
    // Validate mobile number
    if (!formData.mobile || formData.mobile.length !== 10) {
      toast.error('Please enter a valid 10-digit mobile number');
      return;
    }

    // Validate required fields for signup
    if (!isLogin) {
      if (!formData.firstName.trim()) {
        toast.error('Please enter your first name');
        return;
      }
      if (!formData.lastName.trim()) {
        toast.error('Please enter your last name');
        return;
      }
      if (!formData.village.trim()) {
        toast.error('Please enter your village name');
        return;
      }
    }

    setLoading(true);
    
    try {
      let response;
      if (isLogin) {
        // Login flow
        response = await authService.loginRequest(formData.mobile);
        toast.success('OTP sent to your mobile via SMS!');
      } else {
        // Signup flow - send all required fields
        response = await authService.signupRequest(
          formData.mobile,
          formData.firstName,
          formData.lastName,
          formData.village,
          formData.role
        );
        toast.success('OTP sent! Please verify to create your account.');
      }

      setDisplayOtp(response?.otp ? String(response.otp) : '');
      
      setStep('otp');
      startTimer();
    } catch (error) {
      console.error('Error sending OTP:', error);
      toast.error(error.message || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (!canResend) return;
    
    setLoading(true);
    try {
      const response = await authService.resendOTP(formData.mobile);
      setDisplayOtp(response?.otp ? String(response.otp) : '');
      toast.success('OTP resent successfully!');
      startTimer();
    } catch (error) {
      console.error('Error resending OTP:', error);
      toast.error(error.message || 'Failed to resend OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    
    const otpCode = formData.otp.join('');
    
    // Validate OTP
    if (otpCode.length !== 6) {
      toast.error('Please enter the complete 6-digit OTP');
      return;
    }

    setLoading(true);
    
    try {
      let result;
      
      if (isLogin) {
        // Login verification
        result = await authService.loginVerify(formData.mobile, otpCode);
        toast.success(`Welcome back, ${result.user.name}!`);
      } else {
        // Signup verification
        result = await authService.signupVerify(formData.mobile, otpCode);
        toast.success(`Account created successfully! Welcome, ${result.user.name}!`);
      }
      
      // Call success callback or navigate
      if (onAuthSuccess) {
        onAuthSuccess(result.user);
      } else {
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Error verifying OTP:', error);
      toast.error(error.message || 'Invalid OTP. Please try again.');
      // Clear OTP fields on error
      setFormData({ ...formData, otp: ['', '', '', '', '', ''] });
      document.getElementById('otp-0')?.focus();
    } finally {
      setLoading(false);
    }
  };

  const handleBackToMobile = () => {
    setStep('mobile');
    setDisplayOtp('');
    setFormData({ ...formData, otp: ['', '', '', '', '', ''] });
    if (timerInterval) {
      clearInterval(timerInterval);
      setTimerInterval(null);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setStep('mobile');
    setDisplayOtp('');
    setFormData({
      firstName: '',
      lastName: '',
      village: '',
      mobile: '',
      role: 'farmer',
      otp: ['', '', '', '', '', ''],
    });
    if (timerInterval) {
      clearInterval(timerInterval);
      setTimerInterval(null);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-xl shadow-emerald-500/25 mb-4">
            <span className="text-2xl font-bold text-white">GM</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">
            Gram Meter
          </h1>
          <p className="text-slate-600">
            {step === 'mobile' 
              ? (isLogin ? 'Welcome back!' : 'Create your account')
              : 'Enter verification code'
            }
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
          {/* Tabs - Only show on mobile step */}
          {step === 'mobile' && (
            <div className="flex gap-2 mb-6 bg-slate-100 p-1 rounded-xl">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all duration-200 text-base ${
                  isLogin
                    ? 'bg-white text-emerald-600 shadow-md'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <LogIn className="w-5 h-5" />
                Login
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all duration-200 text-base ${
                  !isLogin
                    ? 'bg-white text-emerald-600 shadow-md'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <UserPlus className="w-5 h-5" />
                Register
              </button>
            </div>
          )}

          {/* Mobile Number Step */}
          {step === 'mobile' ? (
            <form onSubmit={handleSendOtp} className="space-y-5">
              {/* Signup Fields - Only for Registration */}
              {!isLogin && (
                <>
                  {/* First Name */}
                  <div>
                    <label className="block text-base font-semibold text-slate-700 mb-2">
                      First Name *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-slate-400" />
                      </div>
                      <input
                        type="text"
                        name="firstName"
                        value={formData.firstName}
                        onChange={handleChange}
                        className="block w-full pl-12 pr-4 py-3 text-lg border-2 border-slate-300 rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                        placeholder="Enter first name"
                        required={!isLogin}
                      />
                    </div>
                  </div>

                  {/* Last Name */}
                  <div>
                    <label className="block text-base font-semibold text-slate-700 mb-2">
                      Last Name *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-slate-400" />
                      </div>
                      <input
                        type="text"
                        name="lastName"
                        value={formData.lastName}
                        onChange={handleChange}
                        className="block w-full pl-12 pr-4 py-3 text-lg border-2 border-slate-300 rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                        placeholder="Enter last name"
                        required={!isLogin}
                      />
                    </div>
                  </div>

                  {/* Village */}
                  <div>
                    <label className="block text-base font-semibold text-slate-700 mb-2">
                      Village *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <MapPin className="h-5 w-5 text-slate-400" />
                      </div>
                      <input
                        type="text"
                        name="village"
                        value={formData.village}
                        onChange={handleChange}
                        className="block w-full pl-12 pr-4 py-3 text-lg border-2 border-slate-300 rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                        placeholder="Enter your village name"
                        required={!isLogin}
                      />
                    </div>
                  </div>

                  {/* Role Selection */}
                  <div>
                    <label className="block text-base font-semibold text-slate-700 mb-2">
                      Role *
                    </label>
                    <select
                      name="role"
                      value={formData.role}
                      onChange={handleChange}
                      className="block w-full px-4 py-3 text-lg border-2 border-slate-300 rounded-xl bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                    >
                      <option value="farmer">Farmer</option>
                      <option value="operator">Operator</option>
                      <option value="technician">Technician</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                </>
              )}

              {/* Mobile Number Field */}
              <div>
                <label className="block text-base font-semibold text-slate-700 mb-3">
                  Mobile Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Phone className="h-6 w-6 text-slate-400" />
                  </div>
                  <div className="absolute inset-y-0 left-12 flex items-center pointer-events-none">
                    <span className="text-slate-600 text-lg font-medium">+91</span>
                  </div>
                  <input
                    type="tel"
                    name="mobile"
                    value={formData.mobile}
                    onChange={handleChange}
                    maxLength="10"
                    className="block w-full pl-24 pr-4 py-4 text-lg border-2 border-slate-300 rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                    placeholder="Enter 10 digit number"
                    required
                    pattern="[0-9]{10}"
                  />
                </div>
                <p className="mt-2 text-sm text-slate-500">
                  We'll send you a one-time password (OTP)
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full py-4 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-bold text-lg rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center gap-2"
              >
                Send OTP
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          ) : (
            /* OTP Verification Step */
            <form onSubmit={handleVerifyOtp} className="space-y-6">
              {/* Back Button */}
              <button
                type="button"
                onClick={handleBackToMobile}
                className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Change mobile number
              </button>

              {/* Mobile Number Display */}
              <div className="text-center">
                <p className="text-slate-600 mb-2">OTP sent to</p>
                <p className="text-xl font-bold text-slate-900">
                  +91 {formData.mobile}
                </p>
                {displayOtp && (
                  <p className="mt-2 text-sm font-semibold text-emerald-700">
                    OTP: {displayOtp}
                  </p>
                )}
              </div>

              {/* OTP Input */}
              <div>
                <label className="block text-base font-semibold text-slate-700 mb-4 text-center">
                  Enter 6-Digit OTP
                </label>
                <div className="flex gap-2 justify-center">
                  {formData.otp.map((digit, index) => (
                    <input
                      key={index}
                      id={`otp-${index}`}
                      type="text"
                      inputMode="numeric"
                      maxLength="1"
                      value={digit}
                      onChange={(e) => handleOtpChange(index, e.target.value)}
                      onKeyDown={(e) => handleOtpKeyDown(index, e)}
                      className="w-12 h-14 text-center text-2xl font-bold border-2 border-slate-300 rounded-xl bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-colors"
                    />
                  ))}
                </div>
              </div>

              {/* Resend OTP */}
              <div className="text-center">
                {canResend ? (
                  <button
                    type="button"
                    onClick={handleResendOtp}
                    className="text-emerald-600 hover:text-emerald-700 font-semibold text-base"
                  >
                    Resend OTP
                  </button>
                ) : (
                  <p className="text-slate-500 text-base">
                    Resend OTP in <span className="font-bold text-emerald-600">{otpTimer}s</span>
                  </p>
                )}
              </div>

              {/* Verify Button */}
              <button
                type="submit"
                disabled={formData.otp.some(digit => !digit)}
                className="w-full py-4 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:from-slate-400 disabled:to-slate-500 text-white font-bold text-lg rounded-xl shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:-translate-y-0.5 disabled:transform-none transition-all duration-200 flex items-center justify-center gap-2 disabled:cursor-not-allowed"
              >
                Verify & Continue
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          )}
        </div>

        {/* Footer - Only show on mobile step */}
        {step === 'mobile' && (
          <p className="text-center text-base text-slate-600 mt-6">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={toggleMode}
              className="text-emerald-600 hover:text-emerald-700 font-semibold"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        )}
      </div>
    </div>
  );
};

export default Auth;

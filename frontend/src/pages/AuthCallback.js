/**
 * Auth callback page to handle Google OAuth redirect.
 */
import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin, message } from 'antd';
import { useAuth } from '../contexts/AuthContext';

const AuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { handleAuthCallback } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');

    if (token) {
      handleAuthCallback(token);
      message.success('Successfully logged in!');
      navigate('/dashboard');
    } else {
      message.error('Authentication failed. Please try again.');
      navigate('/');
    }
  }, [searchParams, navigate, handleAuthCallback]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh'
    }}>
      <Spin size="large" tip="Authenticating..." />
    </div>
  );
};

export default AuthCallback;

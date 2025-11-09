/**
 * Landing page with hero section and Google login button.
 */
import React from 'react';
import { Button, Typography, Layout } from 'antd';
import { GoogleOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import './LandingPage.css';

const { Content } = Layout;
const { Title, Paragraph } = Typography;

const LandingPage = () => {
  const { login } = useAuth();

  return (
    <Layout className="landing-page">
      <Content className="landing-content">
        <div className="hero-section">
          <div className="hero-overlay">
            <div className="hero-text">
              <Title level={1} className="hero-title">
                Audio Transcription Service
              </Title>
              <Paragraph className="hero-subtitle">
                Streamline your patient note-taking with secure, AI-powered transcription
              </Paragraph>
              <Button
                type="primary"
                size="large"
                icon={<GoogleOutlined />}
                onClick={login}
                className="login-button"
              >
                Login with Google
              </Button>
            </div>
          </div>
        </div>
      </Content>
    </Layout>
  );
};

export default LandingPage;

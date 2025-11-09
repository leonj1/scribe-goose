/**
 * Dashboard page with recordings list and recording interface.
 */
import React, { useState, useEffect } from 'react';
import { Layout, message } from 'antd';
import { useAuth } from '../contexts/AuthContext';
import { recordingApi } from '../services/api';
import DashboardHeader from '../components/DashboardHeader';
import RecordingsList from '../components/RecordingsList';
import RecordingPanel from '../components/RecordingPanel';
import './Dashboard.css';

const { Content, Sider } = Layout;

const Dashboard = () => {
  const { logout } = useAuth();
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [activeRecording, setActiveRecording] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecordings();
  }, []);

  const loadRecordings = async () => {
    try {
      setLoading(true);
      const data = await recordingApi.listRecordings();
      setRecordings(data);
    } catch (error) {
      message.error('Failed to load recordings');
      console.error('Load recordings error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      message.success('Logged out successfully');
    } catch (error) {
      message.error('Logout failed');
    }
  };

  const handleSelectRecording = (recording) => {
    if (!activeRecording) {
      setSelectedRecording(recording);
    } else {
      message.warning('Please finish or pause the current recording first');
    }
  };

  const handleNewRecording = async () => {
    if (activeRecording) {
      message.warning('Please finish the current recording first');
      return;
    }

    try {
      const newRecording = await recordingApi.createRecording();
      setActiveRecording(newRecording);
      setSelectedRecording(newRecording);
      setRecordings([newRecording, ...recordings]);
      message.success('New recording session started');
    } catch (error) {
      message.error('Failed to create recording');
      console.error('Create recording error:', error);
    }
  };

  const handleRecordingFinished = async () => {
    setActiveRecording(null);
    await loadRecordings();
  };

  const handleRecordingDeleted = async () => {
    setSelectedRecording(null);
    await loadRecordings();
  };

  return (
    <Layout className="dashboard">
      <DashboardHeader onLogout={handleLogout} />
      <Layout className="dashboard-content">
        <Sider width={300} className="recordings-sider" theme="light">
          <RecordingsList
            recordings={recordings}
            selectedRecording={selectedRecording}
            onSelect={handleSelectRecording}
            onNewRecording={handleNewRecording}
            loading={loading}
          />
        </Sider>
        <Content className="recording-content">
          <RecordingPanel
            recording={selectedRecording}
            isActive={!!activeRecording}
            onRecordingFinished={handleRecordingFinished}
            onRecordingDeleted={handleRecordingDeleted}
          />
        </Content>
        <Sider width={200} className="metadata-sider" theme="light">
          {/* Reserved for future metadata */}
        </Sider>
      </Layout>
    </Layout>
  );
};

export default Dashboard;

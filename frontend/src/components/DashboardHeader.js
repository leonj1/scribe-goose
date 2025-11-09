/**
 * Dashboard header component with user info and logout.
 */
import React from 'react';
import { Layout, Avatar, Dropdown, Typography } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import './DashboardHeader.css';

const { Header } = Layout;
const { Title } = Typography;

const DashboardHeader = ({ onLogout }) => {
  const items = [
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: onLogout,
    },
  ];

  return (
    <Header className="dashboard-header">
      <Title level={3} className="site-name">
        Audio Transcription Service
      </Title>
      <Dropdown menu={{ items }} placement="bottomRight" trigger={['click']}>
        <Avatar
          size="large"
          icon={<UserOutlined />}
          className="user-avatar"
          style={{ cursor: 'pointer' }}
        />
      </Dropdown>
    </Header>
  );
};

export default DashboardHeader;

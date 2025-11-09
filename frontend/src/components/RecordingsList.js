/**
 * Left pane component showing list of recordings.
 */
import React from 'react';
import { List, Button, Typography, Empty, Spin, Tag } from 'antd';
import { PlusOutlined, AudioOutlined } from '@ant-design/icons';
import './RecordingsList.css';

const { Title, Text } = Typography;

const RecordingsList = ({
  recordings,
  selectedRecording,
  onSelect,
  onNewRecording,
  loading,
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'processing';
      case 'paused':
        return 'warning';
      case 'ended':
        return 'success';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="recordings-list">
      <div className="recordings-header">
        <Title level={4}>Recordings</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={onNewRecording}
          size="large"
        >
          New Recording
        </Button>
      </div>

      {loading ? (
        <div className="recordings-loading">
          <Spin size="large" />
        </div>
      ) : recordings.length === 0 ? (
        <Empty
          description="No recordings yet"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <List
          className="recordings-list-items"
          dataSource={recordings}
          renderItem={(recording) => (
            <List.Item
              className={`recording-item ${
                selectedRecording?.id === recording.id ? 'selected' : ''
              }`}
              onClick={() => onSelect(recording)}
            >
              <List.Item.Meta
                avatar={<AudioOutlined style={{ fontSize: 24 }} />}
                title={
                  <div className="recording-item-header">
                    <Text strong>
                      {formatDate(recording.created_at)}
                    </Text>
                    <Tag color={getStatusColor(recording.status)}>
                      {recording.status}
                    </Tag>
                  </div>
                }
                description={
                  recording.transcription_text
                    ? recording.transcription_text.substring(0, 60) + '...'
                    : 'No transcription yet'
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default RecordingsList;

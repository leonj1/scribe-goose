/**
 * Center pane component for recording and viewing transcriptions.
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  Button,
  Typography,
  Card,
  Space,
  message,
  Modal,
  Input,
  Spin,
} from 'antd';
import {
  AudioOutlined,
  PauseOutlined,
  StopOutlined,
  DeleteOutlined,
  EditOutlined,
} from '@ant-design/icons';
import { recordingApi } from '../services/api';
import WaveformVisualizer from './WaveformVisualizer';
import './RecordingPanel.css';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

const RecordingPanel = ({
  recording,
  isActive,
  onRecordingFinished,
  onRecordingDeleted,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [chunkIndex, setChunkIndex] = useState(0);
  const [notesModalVisible, setNotesModalVisible] = useState(false);
  const [notes, setNotes] = useState('');
  const [finishing, setFinishing] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  useEffect(() => {
    if (recording) {
      setNotes(recording.notes || '');
    }
  }, [recording]);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });
      mediaRecorderRef.current = mediaRecorder;

      audioChunksRef.current = [];

      // Send chunks every 10 seconds
      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);

          // Upload chunk
          try {
            const blob = new Blob([event.data], { type: 'audio/webm' });
            await recordingApi.uploadChunk(
              recording.id,
              chunkIndex,
              blob,
              null
            );
            setChunkIndex((prev) => prev + 1);
          } catch (error) {
            console.error('Failed to upload chunk:', error);
            message.error('Failed to upload audio chunk');
          }
        }
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start(10000); // Collect data every 10 seconds
      setIsRecording(true);
      setIsPaused(false);
      message.success('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      message.error('Failed to access microphone');
    }
  };

  const pauseRecording = async () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);

      try {
        await recordingApi.pauseRecording(recording.id);
        message.info('Recording paused');
      } catch (error) {
        console.error('Failed to pause recording:', error);
        message.error('Failed to pause recording');
      }
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      message.info('Recording resumed');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    }
  };

  const finishRecording = async () => {
    stopRecording();
    setFinishing(true);

    try {
      await recordingApi.finishRecording(recording.id);
      message.success('Recording finished and transcription started');
      setChunkIndex(0);
      onRecordingFinished();
    } catch (error) {
      console.error('Failed to finish recording:', error);
      message.error('Failed to finish recording');
    } finally {
      setFinishing(false);
    }
  };

  const handleSaveNotes = async () => {
    try {
      await recordingApi.addNotes(recording.id, notes);
      message.success('Notes saved successfully');
      setNotesModalVisible(false);
    } catch (error) {
      console.error('Failed to save notes:', error);
      message.error('Failed to save notes');
    }
  };

  const handleDelete = async () => {
    Modal.confirm({
      title: 'Delete Recording',
      content: 'Are you sure you want to delete this recording?',
      okText: 'Delete',
      okType: 'danger',
      onOk: async () => {
        try {
          await recordingApi.deleteRecording(recording.id);
          message.success('Recording deleted');
          onRecordingDeleted();
        } catch (error) {
          console.error('Failed to delete recording:', error);
          message.error('Failed to delete recording');
        }
      },
    });
  };

  if (!recording) {
    return (
      <div className="recording-panel-empty">
        <AudioOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />
        <Title level={3} type="secondary">
          Select a recording or create a new one
        </Title>
      </div>
    );
  }

  if (finishing) {
    return (
      <div className="recording-panel-empty">
        <Spin size="large" tip="Finishing recording and generating transcription..." />
      </div>
    );
  }

  const showControls = isActive && recording.status !== 'ended';

  return (
    <div className="recording-panel">
      {showControls && (
        <Card className="recording-controls">
          {!isRecording ? (
            <Button
              type="primary"
              size="large"
              icon={<AudioOutlined />}
              onClick={startRecording}
              block
            >
              Start Recording
            </Button>
          ) : (
            <>
              <WaveformVisualizer isActive={isRecording && !isPaused} />
              <Space className="recording-buttons">
                {isPaused ? (
                  <Button
                    type="primary"
                    size="large"
                    icon={<AudioOutlined />}
                    onClick={resumeRecording}
                  >
                    Resume
                  </Button>
                ) : (
                  <Button
                    size="large"
                    icon={<PauseOutlined />}
                    onClick={pauseRecording}
                  >
                    Pause
                  </Button>
                )}
                <Button
                  danger
                  size="large"
                  icon={<StopOutlined />}
                  onClick={finishRecording}
                >
                  End Recording
                </Button>
              </Space>
            </>
          )}
        </Card>
      )}

      <Card className="transcription-card">
        <div className="transcription-header">
          <Title level={4}>Transcription</Title>
          <Space>
            <Button
              icon={<EditOutlined />}
              onClick={() => setNotesModalVisible(true)}
            >
              Notes
            </Button>
            {recording.status === 'ended' && (
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={handleDelete}
              >
                Delete
              </Button>
            )}
          </Space>
        </div>

        {recording.transcription_text ? (
          <Paragraph className="transcription-text">
            {recording.transcription_text}
          </Paragraph>
        ) : (
          <Text type="secondary">
            {recording.status === 'ended'
              ? 'Transcription in progress...'
              : 'Transcription will appear after recording ends'}
          </Text>
        )}
      </Card>

      <Modal
        title="Recording Notes"
        open={notesModalVisible}
        onOk={handleSaveNotes}
        onCancel={() => setNotesModalVisible(false)}
        okText="Save"
      >
        <TextArea
          rows={6}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add notes about this recording session..."
        />
      </Modal>
    </div>
  );
};

export default RecordingPanel;

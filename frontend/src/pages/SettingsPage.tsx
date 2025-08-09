import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Slider,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Save as SaveIcon,
  RestoreFromTrash as ResetIcon,
} from '@mui/icons-material';

interface Settings {
  // AI Model Settings
  aiProvider: string;
  model: string;
  temperature: number;
  maxTokens: number;
  
  // RAG Settings
  ragEnabled: boolean;
  retrievalType: string;
  documentsToRetrieve: number;
  scoreThreshold: number;
  
  // Chat Settings
  maxChatHistory: number;
  systemMessage: string;
  
  // UI Settings
  theme: string;
  autoScroll: boolean;
  showTimestamps: boolean;
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<Settings>({
    aiProvider: 'openai',
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 1000,
    
    ragEnabled: true,
    retrievalType: 'similarity',
    documentsToRetrieve: 5,
    scoreThreshold: 0.7,
    
    maxChatHistory: 10,
    systemMessage: 'You are a helpful AI assistant. Use the provided context to answer questions accurately and helpfully.',
    
    theme: 'light',
    autoScroll: true,
    showTimestamps: true,
  });

  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleInputChange = (field: keyof Settings, value: string | number | boolean) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    // Simulate save operation
    console.log('Saving settings:', settings);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleReset = () => {
    setSettings({
      aiProvider: 'openai',
      model: 'gpt-3.5-turbo',
      temperature: 0.7,
      maxTokens: 1000,
      
      ragEnabled: true,
      retrievalType: 'similarity',
      documentsToRetrieve: 5,
      scoreThreshold: 0.7,
      
      maxChatHistory: 10,
      systemMessage: 'You are a helpful AI assistant. Use the provided context to answer questions accurately and helpfully.',
      
      theme: 'light',
      autoScroll: true,
      showTimestamps: true,
    });
  };

  const aiProviders = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'google', label: 'Google (Gemini)' },
    { value: 'azure', label: 'Azure OpenAI' },
    { value: 'huggingface', label: 'Hugging Face' },
  ];

  const modelsByProvider: Record<string, string[]> = {
    openai: ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo'],
    anthropic: ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229', 'claude-3-opus-20240229'],
    google: ['gemini-pro', 'gemini-pro-vision'],
    azure: ['gpt-4', 'gpt-35-turbo'],
    huggingface: ['microsoft/DialoGPT-medium', 'microsoft/DialoGPT-large'],
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure AI models, RAG parameters, and application preferences
        </Typography>
      </Paper>

      {/* Save Success Alert */}
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        {/* AI Model Settings */}
        <Box>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Model Configuration
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>AI Provider</InputLabel>
                <Select
                  value={settings.aiProvider}
                  onChange={(e) => handleInputChange('aiProvider', e.target.value)}
                  label="AI Provider"
                >
                  {aiProviders.map(provider => (
                    <MenuItem key={provider.value} value={provider.value}>
                      {provider.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Model</InputLabel>
                <Select
                  value={settings.model}
                  onChange={(e) => handleInputChange('model', e.target.value)}
                  label="Model"
                >
                  {(modelsByProvider[settings.aiProvider] || []).map(model => (
                    <MenuItem key={model} value={model}>
                      {model}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Temperature: {settings.temperature}
                </Typography>
                <Slider
                  value={settings.temperature}
                  onChange={(_, value) => handleInputChange('temperature', value)}
                  min={0}
                  max={2}
                  step={0.1}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 1, label: '1' },
                    { value: 2, label: '2' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>

              <TextField
                fullWidth
                label="Max Tokens"
                type="number"
                value={settings.maxTokens}
                onChange={(e) => handleInputChange('maxTokens', parseInt(e.target.value))}
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid2>

        {/* RAG Settings */}
        <Grid2 xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                RAG (Retrieval Augmented Generation)
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.ragEnabled}
                    onChange={(e) => handleInputChange('ragEnabled', e.target.checked)}
                  />
                }
                label="Enable RAG"
                sx={{ mb: 2, display: 'block' }}
              />

              <FormControl fullWidth sx={{ mb: 2 }} disabled={!settings.ragEnabled}>
                <InputLabel>Retrieval Type</InputLabel>
                <Select
                  value={settings.retrievalType}
                  onChange={(e) => handleInputChange('retrievalType', e.target.value)}
                  label="Retrieval Type"
                >
                  <MenuItem value="similarity">Similarity Search</MenuItem>
                  <MenuItem value="mmr">Maximum Marginal Relevance</MenuItem>
                  <MenuItem value="similarity_score_threshold">Similarity with Threshold</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Documents to Retrieve: {settings.documentsToRetrieve}
                </Typography>
                <Slider
                  value={settings.documentsToRetrieve}
                  onChange={(_, value) => handleInputChange('documentsToRetrieve', value)}
                  min={1}
                  max={20}
                  step={1}
                  marks={[
                    { value: 1, label: '1' },
                    { value: 10, label: '10' },
                    { value: 20, label: '20' },
                  ]}
                  valueLabelDisplay="auto"
                  disabled={!settings.ragEnabled}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Score Threshold: {settings.scoreThreshold}
                </Typography>
                <Slider
                  value={settings.scoreThreshold}
                  onChange={(_, value) => handleInputChange('scoreThreshold', value)}
                  min={0}
                  max={1}
                  step={0.1}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 0.5, label: '0.5' },
                    { value: 1, label: '1' },
                  ]}
                  valueLabelDisplay="auto"
                  disabled={!settings.ragEnabled}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid2>

        {/* Chat Settings */}
        <Grid2 xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Chat Configuration
              </Typography>

              <TextField
                fullWidth
                label="Max Chat History"
                type="number"
                value={settings.maxChatHistory}
                onChange={(e) => handleInputChange('maxChatHistory', parseInt(e.target.value))}
                sx={{ mb: 2 }}
                helperText="Number of previous messages to keep in context"
              />

              <TextField
                fullWidth
                label="System Message"
                multiline
                rows={4}
                value={settings.systemMessage}
                onChange={(e) => handleInputChange('systemMessage', e.target.value)}
                sx={{ mb: 2 }}
                helperText="Instructions for the AI assistant"
              />
            </CardContent>
          </Card>
        </Grid2>

        {/* UI Settings */}
        <Grid2 xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Interface Preferences
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Theme</InputLabel>
                <Select
                  value={settings.theme}
                  onChange={(e) => handleInputChange('theme', e.target.value)}
                  label="Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="auto">Auto</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoScroll}
                    onChange={(e) => handleInputChange('autoScroll', e.target.checked)}
                  />
                }
                label="Auto-scroll to latest message"
                sx={{ mb: 2, display: 'block' }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.showTimestamps}
                    onChange={(e) => handleInputChange('showTimestamps', e.target.checked)}
                  />
                }
                label="Show message timestamps"
                sx={{ mb: 2, display: 'block' }}
              />
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          size="large"
        >
          Save Settings
        </Button>
        <Button
          variant="outlined"
          startIcon={<ResetIcon />}
          onClick={handleReset}
          size="large"
        >
          Reset to Defaults
        </Button>
      </Box>
    </Box>
  );
};

export default SettingsPage;

import apiClient from './auth';

export const chatIntake = async (text) => {
  const response = await apiClient.post('/chat/intake', { text });
  return response.data;
};

export const chatExplain = async (assessmentId, question) => {
  const response = await apiClient.post('/chat/explain', {
    assessment_id: assessmentId,
    question,
  });
  return response.data;
};

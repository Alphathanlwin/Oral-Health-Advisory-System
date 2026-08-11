import apiClient from './auth';

export const getAssessments = async (page = 1, size = 10) => {
  const response = await apiClient.get('/assessments/', { params: { page, size } });
  return response.data;
};

export const createAssessment = async (payload) => {
  const response = await apiClient.post('/assessments/', payload);
  return response.data;
};

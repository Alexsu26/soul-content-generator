// 在组件顶部添加 API URL 配置
const API_URL = import.meta.env.VITE_API_URL || '/api';

// 修改 generateContent 函数
const generateContent = async () => {
  if (!input.trim()) return;

  setLoading(true);

  try {
    const response = await fetch(`${API_URL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_input: input })
    });

    if (!response.ok) {
      throw new Error('生成失败');
    }

    const data = await response.json();
    setResult(data);
    setSelectedVersion(0);
  } catch (error) {
    console.error('Error:', error);
    alert('生成失败，请重试');
  } finally {
    setLoading(false);
  }
};
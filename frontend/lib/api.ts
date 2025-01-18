const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function sendMessage(message: string) {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    
    if (!response.ok) throw new Error('Failed to send message');
    
    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    return {
      response: "I'm sorry, I'm having trouble connecting to the server. Please try again later.",
      error: true,
    };
  }
}

export async function uploadPDF(file: File) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) throw new Error('Failed to upload PDF');

    return await response.json();
  } catch (error) {
    console.error('Error uploading PDF:', error);
    return {
      message: "Failed to upload the PDF. Please try again later.",
      error: true,
    };
  }
}
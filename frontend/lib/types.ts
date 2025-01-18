export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface ChatHistory {
  id: string;
  messages: Message[];
  title: string;
  timestamp: string;
}
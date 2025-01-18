"use client";

import { ChatHistorySidebar } from "@/components/chat-history-sidebar";
import { ChatInput } from "@/components/chat-input";
import { ChatMessage } from "@/components/chat-message";
import { FileUpload } from "@/components/file-upload";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/components/ui/use-toast";
import { sendMessage, uploadPDF } from "@/lib/api";
import { ChatHistory, Message } from "@/lib/types";
import { PanelLeftIcon, PanelRightIcon } from "lucide-react";
import { useEffect, useState } from "react";

export default function Home() {
  const [showSidebar, setShowSidebar] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [histories, setHistories] = useState<ChatHistory[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSendMessage = async (content: string) => {
    setIsLoading(true);
    try {
      const response = await sendMessage(content);
      if (response.error) {
        toast({
          title: "Error",
          description: response.response,
          variant: "destructive",
        });
      } else {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            content,
            role: 'user',
            timestamp: new Date().toISOString()
          },
          {
            id: (Date.now() + 1).toString(),
            content: response.response,
            role: 'assistant',
            timestamp: new Date().toISOString()
          }
        ]);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      const response = await uploadPDF(file);
      if (response.error) {
        toast({
          title: "Error",
          description: response.message,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Success",
          description: "File uploaded successfully",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload file. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    const chat = histories.find(h => h.id === chatId);
    if (chat) {
      setMessages(chat.messages);
    }
  };

  const handleDeleteChat = (chatId: string) => {
    setHistories(prev => prev.filter(h => h.id !== chatId));
    if (currentChatId === chatId) {
      setCurrentChatId(null);
      setMessages([]);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {showSidebar && (
        <div className="w-80 border-r">
          <ChatHistorySidebar
            histories={histories}
            currentChatId={currentChatId}
            onSelectChat={handleSelectChat}
            onDeleteChat={handleDeleteChat}
          />
        </div>
      )}
      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between p-4 border-b">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            {showSidebar ? (
              <PanelLeftIcon className="h-5 w-5" />
            ) : (
              <PanelRightIcon className="h-5 w-5" />
            )}
          </Button>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <div className="flex items-center gap-2">
              <span className="font-semibold text-lg">RAID</span>
            </div>
          </div>
        </header>
        <ScrollArea className="flex-1 p-4">
          <div className="max-w-3xl mx-auto space-y-8">
            <FileUpload onFileUpload={handleFileUpload} />
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          </div>
        </ScrollArea>
        <ChatInput
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatHistory } from "@/lib/types";
import { MessageSquare, Trash2 } from "lucide-react";

interface ChatHistorySidebarProps {
  histories: ChatHistory[];
  currentChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onDeleteChat: (chatId: string) => void;
}

export function ChatHistorySidebar({
  histories,
  currentChatId,
  onSelectChat,
  onDeleteChat,
}: ChatHistorySidebarProps) {
  return (
    <ScrollArea className="h-full w-full p-4">
      <div className="space-y-2">
        {histories.map((history) => (
          <div
            key={history.id}
            className="flex items-center gap-2"
          >
            <Button
              variant={currentChatId === history.id ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => onSelectChat(history.id)}
            >
              <MessageSquare className="mr-2 h-4 w-4" />
              {history.title}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onDeleteChat(history.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
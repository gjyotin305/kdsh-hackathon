"use client";

import { Message } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
import { Card } from "./ui/card";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}>
      <Card className={cn(
        "flex gap-3 p-4 max-w-[80%]",
        isUser ? "bg-primary text-primary-foreground" : "bg-muted"
      )}>
        {isUser ? (
          <User className="h-6 w-6 shrink-0" />
        ) : (
          <Bot className="h-6 w-6 shrink-0" />
        )}
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
      </Card>
    </div>
  );
}
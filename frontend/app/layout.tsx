import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from './providers';
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Chatbot',
  description: 'Next.js Chatbot with PDF support',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <TooltipProvider>
            {children}
          </TooltipProvider>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
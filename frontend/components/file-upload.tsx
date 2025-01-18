"use client";

import { useState } from 'react';
import { FileUp, Upload, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface FileUploadProps {
  onFileUpload: (file: File) => Promise<void>;
}

export function FileUpload({ onFileUpload }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { toast } = useToast();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      await handleFileSelection(file);
    } else {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF file",
        variant: "destructive",
      });
    }
  };

  const handleFileSelection = async (file: File) => {
    setSelectedFile(file);
    setIsUploading(true);
    setUploadProgress(0);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 500);

    try {
      await onFileUpload(file);
      setUploadProgress(100);
      toast({
        title: "Success",
        description: "File uploaded successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload file. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      clearInterval(progressInterval);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative border-2 border-dashed rounded-lg p-12 transition-all",
          "hover:bg-accent/50 group cursor-pointer",
          isDragging ? "border-primary bg-accent" : "border-muted-foreground/25",
          "flex flex-col items-center justify-center gap-4"
        )}
        onClick={() => document.getElementById('fileInput')?.click()}
      >
        <input
          type="file"
          id="fileInput"
          className="hidden"
          accept=".pdf"
          onChange={(e) => e.target.files?.[0] && handleFileSelection(e.target.files[0])}
        />
        <div className="relative">
          <FileUp className="w-12 h-12 text-muted-foreground group-hover:text-primary transition-colors" />
          {isUploading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Progress value={uploadProgress} className="w-12" />
            </div>
          )}
          {uploadProgress === 100 && !isUploading && (
            <CheckCircle2 className="absolute bottom-0 right-0 text-green-500 animate-in zoom-in" />
          )}
        </div>
        <div className="text-center">
          <p className="text-lg font-medium">Drag & drop your PDFs here</p>
          <p className="text-sm text-muted-foreground">or click to browse</p>
        </div>
      </div>

      {/* Upload Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              className="h-12 border-primary hover:border-primary/80 hover:scale-[1.02] transition-transform"
              disabled={isUploading}
              onClick={() => document.getElementById('fileInput')?.click()}
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload PDF
            </Button>
          </TooltipTrigger>
          <TooltipContent>Upload PDF files</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              className="h-12 border-blue-500 hover:border-blue-400 hover:scale-[1.02] transition-transform"
              disabled={isUploading}
            >
              <svg className="mr-2 h-4 w-4" viewBox="0 0 87.3 78" xmlns="http://www.w3.org/2000/svg">
                <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
                <path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0 -1.2 4.5h27.5z" fill="#00ac47"/>
                <path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/>
                <path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
                <path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
                <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
              </svg>
              Import from Drive
            </Button>
          </TooltipTrigger>
          <TooltipContent>Import from Google Drive</TooltipContent>
        </Tooltip>
      </div>

      {/* File Preview */}
      {selectedFile && (
        <div className="p-4 bg-accent rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileUp className="h-5 w-5 text-primary" />
              <span className="font-medium">{selectedFile.name}</span>
            </div>
            <span className="text-sm text-muted-foreground">
              {Math.round(selectedFile.size / 1024)} KB
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
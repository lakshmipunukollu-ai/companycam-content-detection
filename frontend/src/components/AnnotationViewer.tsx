import { useRef, useEffect, useCallback } from 'react';
import type { Photo, Detection } from '../types/index.ts';

interface Props {
  photo: Photo;
  detections: Detection[];
  selectedDetection: Detection | null;
  onSelectDetection: (d: Detection | null) => void;
}

const COLORS = [
  '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
  '#9966FF', '#FF9F40', '#C9CBCF', '#7BC8A4',
];

export default function AnnotationViewer({ photo, detections, selectedDetection, onSelectDetection }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const container = containerRef.current;
    if (!container) return;

    const containerWidth = container.clientWidth;
    const aspectRatio = img.naturalHeight / img.naturalWidth;
    const displayWidth = containerWidth;
    const displayHeight = containerWidth * aspectRatio;

    canvas.width = displayWidth;
    canvas.height = displayHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, displayWidth, displayHeight);

    const scaleX = displayWidth / (photo.width || img.naturalWidth);
    const scaleY = displayHeight / (photo.height || img.naturalHeight);

    detections.forEach((d, i) => {
      const color = COLORS[i % COLORS.length];
      const isSelected = selectedDetection?.id === d.id;

      const x = d.bbox.x * scaleX;
      const y = d.bbox.y * scaleY;
      const w = d.bbox.w * scaleX;
      const h = d.bbox.h * scaleY;

      ctx.strokeStyle = color;
      ctx.lineWidth = isSelected ? 3 : 2;
      ctx.strokeRect(x, y, w, h);

      if (isSelected) {
        ctx.fillStyle = color + '33';
        ctx.fillRect(x, y, w, h);
      }

      // Label background
      const label = `${d.label} (${(d.confidence * 100).toFixed(0)}%)`;
      ctx.font = '12px sans-serif';
      const textWidth = ctx.measureText(label).width;
      ctx.fillStyle = color;
      ctx.fillRect(x, y - 18, textWidth + 8, 18);

      // Label text
      ctx.fillStyle = '#fff';
      ctx.fillText(label, x + 4, y - 5);
    });
  }, [photo, detections, selectedDetection]);

  useEffect(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      imgRef.current = img;
      draw();
    };
    img.onerror = () => {
      // If image doesn't load, draw placeholder
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      canvas.width = 800;
      canvas.height = 600;
      ctx.fillStyle = '#f0f0f0';
      ctx.fillRect(0, 0, 800, 600);
      ctx.fillStyle = '#999';
      ctx.font = '16px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(photo.filename, 400, 300);
      ctx.fillText('(Image not available)', 400, 325);
    };
    img.src = `/uploads/${photo.filename}`;
  }, [photo.filename, draw]);

  useEffect(() => {
    draw();
  }, [draw]);

  useEffect(() => {
    const handleResize = () => draw();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [draw]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    const img = imgRef.current;
    if (!canvas || !img) return;

    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const scaleX = canvas.width / (photo.width || img.naturalWidth);
    const scaleY = canvas.height / (photo.height || img.naturalHeight);

    for (const d of detections) {
      const x = d.bbox.x * scaleX;
      const y = d.bbox.y * scaleY;
      const w = d.bbox.w * scaleX;
      const h = d.bbox.h * scaleY;

      if (clickX >= x && clickX <= x + w && clickY >= y && clickY <= y + h) {
        onSelectDetection(selectedDetection?.id === d.id ? null : d);
        return;
      }
    }
    onSelectDetection(null);
  };

  return (
    <div className="annotation-viewer" ref={containerRef}>
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        style={{ cursor: 'pointer', maxWidth: '100%' }}
      />
    </div>
  );
}

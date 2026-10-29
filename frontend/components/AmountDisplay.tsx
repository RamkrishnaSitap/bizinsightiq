'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useCurrency } from '@/lib/currency-context';

interface AmountDisplayProps {
  amount?: number | null;
  decimals?: number;
  className?: string;
  showBadge?: boolean;
}

interface Coords {
  top: number;
  left: number;
  placement: 'top' | 'bottom';
  arrowPercent: number;
  width: number;
}

export default function AmountDisplay({
  amount,
  decimals = 2,
  className = '',
  showBadge = false,
}: AmountDisplayProps) {
  const { formatCurrency, getHoverDetails, currency } = useCurrency();
  const [isHovered, setIsHovered] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const [coords, setCoords] = useState<Coords | null>(null);
  const triggerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const updatePosition = useCallback(() => {
    if (!triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const margin = 16;
    const tooltipWidth = Math.min(360, viewportWidth - margin * 2);

    // Vertical placement: prefer top if space >= 90px, else bottom
    const placement: 'top' | 'bottom' = rect.top >= 95 ? 'top' : 'bottom';
    const top = placement === 'top' ? rect.top - 8 : rect.bottom + 8;

    // Horizontal centering & clamping
    const idealCenter = rect.left + rect.width / 2;
    const minCenter = margin + tooltipWidth / 2;
    const maxCenter = viewportWidth - margin - tooltipWidth / 2;
    const clampedCenter = Math.max(minCenter, Math.min(maxCenter, idealCenter));

    // Arrow positioning relative to tooltip width
    const tooltipLeft = clampedCenter - tooltipWidth / 2;
    const arrowOffset = idealCenter - tooltipLeft;
    const arrowPercent = Math.max(8, Math.min(92, (arrowOffset / tooltipWidth) * 100));

    setCoords({
      top,
      left: clampedCenter,
      placement,
      arrowPercent,
      width: tooltipWidth,
    });
  }, []);

  const handleMouseEnter = () => {
    updatePosition();
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  useEffect(() => {
    if (!isHovered) return;
    const handleScrollOrResize = () => updatePosition();
    window.addEventListener('scroll', handleScrollOrResize, { passive: true });
    window.addEventListener('resize', handleScrollOrResize);
    return () => {
      window.removeEventListener('scroll', handleScrollOrResize);
      window.removeEventListener('resize', handleScrollOrResize);
    };
  }, [isHovered, updatePosition]);

  if (amount === null || amount === undefined || isNaN(amount)) {
    return <span className={className}>—</span>;
  }

  const formatted = formatCurrency(amount, decimals);
  const { inWords, alternateText } = getHoverDetails(amount);

  return (
    <>
      <span
        ref={triggerRef}
        className={`inline-block cursor-help group ${className}`}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <span className="border-b border-dotted border-slate-400/80 transition-colors group-hover:border-indigo-600 group-hover:text-indigo-600">
          {formatted}
        </span>

        {showBadge && (
          <span className="ml-1.5 text-[10px] text-indigo-600 font-semibold uppercase bg-indigo-50 px-1.5 py-0.5 rounded">
            {currency}
          </span>
        )}
      </span>

      {/* Portal Tooltip: Mounted directly to document.body so no parent overflow-hidden can EVER clip it */}
      {isMounted &&
        isHovered &&
        coords &&
        createPortal(
          <div
            style={{
              position: 'fixed',
              top: `${coords.top}px`,
              left: `${coords.left}px`,
              width: `${coords.width}px`,
              transform:
                coords.placement === 'top'
                  ? 'translate(-50%, -100%)'
                  : 'translate(-50%, 0)',
              zIndex: 99999,
            }}
            className="pointer-events-none p-3 bg-slate-950/95 backdrop-blur-md text-white rounded-xl shadow-2xl border border-slate-700/80 animate-in fade-in zoom-in-95 duration-150 text-left"
          >
            {/* Header */}
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-xs">🗣️</span>
              <span className="font-bold text-emerald-400 text-xs tracking-wide uppercase">
                In Words
              </span>
            </div>

            {/* In Words text */}
            <div className="text-slate-100 font-medium text-xs leading-relaxed break-words">
              {inWords}
            </div>

            {/* Alternate Currency Conversion */}
            {alternateText && (
              <div className="mt-2 pt-1.5 border-t border-slate-800 text-[11px] text-slate-300 flex items-center gap-1.5">
                <span>💱</span>
                <span className="font-medium text-slate-200">{alternateText}</span>
              </div>
            )}

            {/* Crisp 45-degree rotated arrow pointer */}
            {coords.placement === 'top' ? (
              <span
                className="absolute -bottom-1.5 w-3 h-3 bg-slate-950 border-r border-b border-slate-700/80 rotate-45 -translate-x-1/2"
                style={{ left: `${coords.arrowPercent}%` }}
              />
            ) : (
              <span
                className="absolute -top-1.5 w-3 h-3 bg-slate-950 border-l border-t border-slate-700/80 rotate-45 -translate-x-1/2"
                style={{ left: `${coords.arrowPercent}%` }}
              />
            )}
          </div>,
          document.body
        )}
    </>
  );
}

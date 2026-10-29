'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export type CurrencyCode = 'INR' | 'USD' | 'BOTH';
export type RateMode = 'nominal' | 'converted';

export interface CurrencyContextType {
  currency: CurrencyCode;
  setCurrency: (currency: CurrencyCode) => void;
  exchangeRate: number;
  setExchangeRate: (rate: number) => void;
  rateMode: RateMode;
  setRateMode: (mode: RateMode) => void;
  symbol: string;
  code: CurrencyCode;
  formatCurrency: (amount?: number | null, decimals?: number) => string;
  formatCompact: (amount?: number | null) => string;
  currencyLabel: (baseLabel: string) => string;
  amountToWords: (amount?: number | null, overrideCurrency?: 'INR' | 'USD') => string;
  getHoverDetails: (amount?: number | null) => {
    inWords: string;
    alternateText: string;
    tooltipText: string;
  };
}

const CurrencyContext = createContext<CurrencyContextType | undefined>(undefined);

const STORAGE_CURRENCY_KEY = 'bizinsightiq_currency';
const STORAGE_RATE_KEY = 'bizinsightiq_exchange_rate';
const STORAGE_MODE_KEY = 'bizinsightiq_rate_mode';

export function amountToWords(num?: number | null, currency: 'INR' | 'USD' = 'INR'): string {
  if (num === null || num === undefined || isNaN(num)) return '—';
  if (num === 0) return currency === 'INR' ? 'Zero Rupees' : 'Zero Dollars';

  const isNegative = num < 0;
  const absNum = Math.abs(num);
  const intPart = Math.floor(absNum);
  const decPart = Math.round((absNum - intPart) * 100);

  const ones = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
    'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'
  ];
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];

  function convertBelowThousand(n: number): string {
    let str = '';
    if (n >= 100) {
      str += ones[Math.floor(n / 100)] + ' Hundred ';
      n %= 100;
    }
    if (n >= 20) {
      str += tens[Math.floor(n / 10)] + (n % 10 !== 0 ? '-' + ones[n % 10] : '') + ' ';
    } else if (n > 0) {
      str += ones[n] + ' ';
    }
    return str.trim();
  }

  let words = '';
  if (currency === 'INR') {
    let n = intPart;
    const crore = Math.floor(n / 10000000);
    n %= 10000000;
    const lakh = Math.floor(n / 100000);
    n %= 100000;
    const thousand = Math.floor(n / 1000);
    n %= 1000;
    const hundred = n;

    if (crore > 0) words += convertBelowThousand(crore) + ' Crore ';
    if (lakh > 0) words += convertBelowThousand(lakh) + ' Lakh ';
    if (thousand > 0) words += convertBelowThousand(thousand) + ' Thousand ';
    if (hundred > 0) words += convertBelowThousand(hundred) + ' ';

    words = words.trim();
    if (!words) words = 'Zero';
    words += intPart === 1 ? ' Rupee' : ' Rupees';
    if (decPart > 0) {
      words += ' and ' + convertBelowThousand(decPart) + (decPart === 1 ? ' Paisa' : ' Paise');
    }
  } else {
    let n = intPart;
    const billion = Math.floor(n / 1000000000);
    n %= 1000000000;
    const million = Math.floor(n / 1000000);
    n %= 1000000;
    const thousand = Math.floor(n / 1000);
    n %= 1000;
    const hundred = n;

    if (billion > 0) words += convertBelowThousand(billion) + ' Billion ';
    if (million > 0) words += convertBelowThousand(million) + ' Million ';
    if (thousand > 0) words += convertBelowThousand(thousand) + ' Thousand ';
    if (hundred > 0) words += convertBelowThousand(hundred) + ' ';

    words = words.trim();
    if (!words) words = 'Zero';
    words += intPart === 1 ? ' Dollar' : ' Dollars';
    if (decPart > 0) {
      words += ' and ' + convertBelowThousand(decPart) + (decPart === 1 ? ' Cent' : ' Cents');
    }
  }

  return (isNegative ? 'Minus ' : '') + words.trim();
}

export function CurrencyProvider({ children }: { children: React.ReactNode }) {
  // Default to INR (Rupee) as requested
  const [currency, setCurrencyState] = useState<CurrencyCode>('INR');
  const [exchangeRate, setExchangeRateState] = useState<number>(83.0);
  const [rateMode, setRateModeState] = useState<RateMode>('nominal');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedCurrency = localStorage.getItem(STORAGE_CURRENCY_KEY) as CurrencyCode | null;
      if (savedCurrency === 'INR' || savedCurrency === 'USD' || savedCurrency === 'BOTH') {
        setCurrencyState(savedCurrency);
      } else {
        setCurrencyState('INR');
        localStorage.setItem(STORAGE_CURRENCY_KEY, 'INR');
      }

      const savedRate = localStorage.getItem(STORAGE_RATE_KEY);
      if (savedRate && !isNaN(Number(savedRate)) && Number(savedRate) > 0) {
        setExchangeRateState(Number(savedRate));
      }

      const savedMode = localStorage.getItem(STORAGE_MODE_KEY) as RateMode | null;
      if (savedMode === 'nominal' || savedMode === 'converted') {
        setRateModeState(savedMode);
      }
    }
  }, []);

  const setCurrency = (c: CurrencyCode) => {
    setCurrencyState(c);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_CURRENCY_KEY, c);
    }
  };

  const setExchangeRate = (rate: number) => {
    if (rate > 0) {
      setExchangeRateState(rate);
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_RATE_KEY, rate.toString());
      }
    }
  };

  const setRateMode = (mode: RateMode) => {
    setRateModeState(mode);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_MODE_KEY, mode);
    }
  };

  const symbol = currency === 'INR' ? '₹' : currency === 'USD' ? '$' : '₹/$';

  const formatCurrency = (amount?: number | null, decimals: number = 2): string => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return '—';
    }

    let inrVal = amount;
    let usdVal = amount;

    if (rateMode === 'converted') {
      inrVal = amount * exchangeRate;
    }

    if (currency === 'INR') {
      return (
        '₹' +
        inrVal.toLocaleString('en-IN', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        })
      );
    } else if (currency === 'USD') {
      return (
        '$' +
        usdVal.toLocaleString('en-US', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        })
      );
    } else {
      // BOTH
      const inrStr =
        '₹' +
        inrVal.toLocaleString('en-IN', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        });
      const usdStr =
        '$' +
        usdVal.toLocaleString('en-US', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals,
        });
      return `${inrStr} (${usdStr})`;
    }
  };

  const formatCompact = (amount?: number | null): string => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return '—';
    }

    let val = amount;
    if (currency === 'INR' && rateMode === 'converted') {
      val = amount * exchangeRate;
    }

    const absVal = Math.abs(val);
    const sign = val < 0 ? '-' : '';

    if (currency === 'INR') {
      if (absVal >= 10000000) {
        return `${sign}₹${(absVal / 10000000).toFixed(1)}Cr`;
      }
      if (absVal >= 100000) {
        return `${sign}₹${(absVal / 100000).toFixed(1)}L`;
      }
      if (absVal >= 1000) {
        return `${sign}₹${(absVal / 1000).toFixed(0)}k`;
      }
      return `${sign}₹${absVal}`;
    } else {
      if (absVal >= 1000000) {
        return `${sign}$${(absVal / 1000000).toFixed(1)}M`;
      }
      if (absVal >= 1000) {
        return `${sign}$${(absVal / 1000).toFixed(0)}k`;
      }
      return `${sign}$${absVal}`;
    }
  };

  const currencyLabel = (baseLabel: string): string => {
    return `${baseLabel} (${symbol})`;
  };

  const getHoverDetails = (amount?: number | null) => {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return { inWords: '—', alternateText: '', tooltipText: 'No value' };
    }

    let inrVal: number;
    let usdVal: number;

    if (currency === 'INR') {
      inrVal = amount;
      usdVal = amount / exchangeRate;
    } else if (currency === 'USD') {
      usdVal = amount;
      inrVal = amount * exchangeRate;
    } else {
      // BOTH
      inrVal = amount;
      usdVal = amount / exchangeRate;
    }

    let inWords: string;
    let alternateText: string;

    if (currency === 'INR') {
      inWords = amountToWords(inrVal, 'INR');
      const usdFormatted = '$' + usdVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      alternateText = `≈ ${usdFormatted} USD (@ ₹${exchangeRate}/USD)`;
    } else if (currency === 'USD') {
      inWords = amountToWords(usdVal, 'USD');
      const inrFormatted = '₹' + inrVal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      alternateText = `≈ ${inrFormatted} INR (@ ₹${exchangeRate}/USD)`;
    } else {
      // BOTH
      inWords = `${amountToWords(inrVal, 'INR')}`;
      const inrFormatted = '₹' + inrVal.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      const usdFormatted = '$' + usdVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      alternateText = `${inrFormatted} INR | ${usdFormatted} USD`;
    }

    const tooltipText = `${inWords}${alternateText ? '\n' + alternateText : ''}`;

    return { inWords, alternateText, tooltipText };
  };

  return (
    <CurrencyContext.Provider
      value={{
        currency,
        setCurrency,
        exchangeRate,
        setExchangeRate,
        rateMode,
        setRateMode,
        symbol,
        code: currency,
        formatCurrency,
        formatCompact,
        currencyLabel,
        amountToWords,
        getHoverDetails,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  );
}

export function useCurrency(): CurrencyContextType {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
}

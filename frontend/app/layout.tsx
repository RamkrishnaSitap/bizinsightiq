import type { Metadata } from 'next';
import localFont from 'next/font/local';
import './globals.css';
import { AuthProvider } from '@/lib/auth-context';
import { DatasetProvider } from '@/lib/dataset-context';
import { CurrencyProvider } from '@/lib/currency-context';

const geistSans = localFont({
  src: './fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
});
const geistMono = localFont({
  src: './fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
});

export const metadata: Metadata = {
  title: 'BizInsightIQ — AI/ML Retail Analytics Platform',
  description: 'Enterprise AI & Machine Learning Sales Intelligence, Customer Segmentation, and Predictive Analytics Platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-slate-50 text-slate-900`}>
        <AuthProvider>
          <DatasetProvider>
            <CurrencyProvider>{children}</CurrencyProvider>
          </DatasetProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

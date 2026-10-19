import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GearExchange — Two-Sided Creator Marketplace & Counter-Offer Negotiation',
  description: 'Production two-sided equipment marketplace featuring stateful counter-offer negotiation, reserved inventory locks, and verified peer reviews.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased selection:bg-emerald-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}

// Caminho: imobcloud/frontend/app/layout.js

import { Inter } from 'next/font/google';
// Esta linha é essencial. Ela importa todos os estilos do Tailwind para a sua aplicação.
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'ImobCloud',
  description: 'O seu sistema de gestão imobiliária na nuvem.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt">
      <body className={inter.className}>{children}</body>
    </html>
  );
}

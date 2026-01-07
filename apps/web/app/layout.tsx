import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'EcoImmo France 2026 | Analyse Immobilière & Énergétique',
  description:
    'Plateforme d\'analyse du marché immobilier français avec diagnostic de performance énergétique (DPE 2026) et identification des passoires thermiques.',
  keywords: [
    'immobilier',
    'DPE',
    'performance énergétique',
    'passoire thermique',
    'Loi Climat',
    'DVF',
    'ADEME',
    'France',
  ],
  authors: [{ name: 'EcoImmo France' }],
  openGraph: {
    title: 'EcoImmo France 2026',
    description: 'Analyse immobilière et énergétique pour le marché français',
    type: 'website',
    locale: 'fr_FR',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <link
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          rel="stylesheet"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <main className="relative flex min-h-screen flex-col">
          {children}
        </main>
      </body>
    </html>
  )
}

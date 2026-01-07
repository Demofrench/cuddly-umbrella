'use client'

import { useState } from 'react'

export default function HomePage() {
  const [postalCode, setPostalCode] = useState('')

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-france-blue-500 text-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <h1 className="text-2xl font-bold">EcoImmo France 2026</h1>
          <nav className="flex gap-6">
            <a href="#" className="hover:underline">
              Recherche
            </a>
            <a href="#" className="hover:underline">
              Carte
            </a>
            <a href="#" className="hover:underline">
              DPE 2026
            </a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-france-blue-500 to-france-blue-700 py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="mb-4 text-5xl font-bold">
            Analyse Immobilière & Énergétique
          </h2>
          <p className="mb-8 text-xl">
            Identifiez les passoires thermiques et anticipez la Loi Climat 2026
          </p>

          {/* Search Bar */}
          <div className="mx-auto max-w-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Code postal (ex: 75015)"
                value={postalCode}
                onChange={(e) => setPostalCode(e.target.value)}
                className="flex-1 rounded-lg px-4 py-3 text-black"
              />
              <button className="rounded-lg bg-france-red-500 px-8 py-3 font-bold hover:bg-france-red-600">
                Rechercher
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid gap-8 md:grid-cols-3">
            {/* Feature 1 */}
            <div className="rounded-lg border p-6">
              <div className="mb-4 text-4xl">🏘️</div>
              <h3 className="mb-2 text-xl font-bold">DVF + DPE</h3>
              <p className="text-muted-foreground">
                Croisement des données de ventes (DVF) et diagnostics énergétiques
                (ADEME DPE)
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-lg border p-6">
              <div className="mb-4 text-4xl">⚡</div>
              <h3 className="mb-2 text-xl font-bold">Facteur 1.9</h3>
              <p className="text-muted-foreground">
                Recalcul DPE 2026 avec le nouveau facteur de conversion électrique
                (1.9 au lieu de 2.3)
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-lg border p-6">
              <div className="mb-4 text-4xl">🤖</div>
              <h3 className="mb-2 text-xl font-bold">Mistral AI</h3>
              <p className="text-muted-foreground">
                Recommandations de rénovation personnalisées via IA souveraine
                française
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* DPE Scale Visualization */}
      <section className="bg-muted py-16">
        <div className="container mx-auto px-4">
          <h3 className="mb-8 text-center text-3xl font-bold">
            Échelle DPE 2026
          </h3>
          <div className="mx-auto max-w-3xl space-y-2">
            {[
              { class: 'A', range: '≤ 70', color: 'dpe-a' },
              { class: 'B', range: '71-110', color: 'dpe-b' },
              { class: 'C', range: '111-180', color: 'dpe-c' },
              { class: 'D', range: '181-250', color: 'dpe-d' },
              { class: 'E', range: '251-330', color: 'dpe-e' },
              {
                class: 'F',
                range: '331-420',
                color: 'dpe-f',
                warning: 'Interdit à la location dès 2028',
              },
              {
                class: 'G',
                range: '> 420',
                color: 'dpe-g',
                warning: 'Déjà interdit depuis 2025',
              },
            ].map(({ class: dpeClass, range, color, warning }) => (
              <div
                key={dpeClass}
                className={`flex items-center justify-between rounded-lg bg-${color} p-4 ${
                  dpeClass === 'F' || dpeClass === 'G'
                    ? 'text-white'
                    : 'text-black'
                }`}
              >
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-bold">{dpeClass}</span>
                  <span>{range} kWh EP/m²/an</span>
                </div>
                {warning && (
                  <span className="rounded bg-white/20 px-3 py-1 text-sm font-bold">
                    ⚠️ {warning}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>
            EcoImmo France 2026 - Conforme RGPD et EU AI Act
          </p>
          <p className="mt-2">
            Données : DVF (data.gouv.fr) + ADEME DPE (data.ademe.fr)
          </p>
        </div>
      </footer>
    </div>
  )
}

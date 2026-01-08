'use client'

import { useState } from 'react'
import { Sparkles, ArrowRight, Zap, TrendingUp, Shield } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  const [postalCode, setPostalCode] = useState('')

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="border-b bg-france-blue-500 text-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <h1 className="text-2xl font-bold">EcoImmo France 2026</h1>
          <nav className="flex gap-6">
            <Link href="/ai-doctor" className="flex items-center gap-2 rounded-lg bg-france-blue-600 px-4 py-2 font-bold hover:bg-france-blue-700">
              <Sparkles className="h-4 w-4" />
              AI Property Doctor
            </Link>
            <a href="#features" className="hover:underline">
              Fonctionnalités
            </a>
            <a href="#dpe" className="hover:underline">
              DPE 2026
            </a>
          </nav>
        </div>
      </header>

      {/* AI Property Doctor Hero Banner */}
      <section className="bg-gradient-to-r from-purple-600 via-france-blue-600 to-blue-600 py-8 text-white">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Sparkles className="h-12 w-12 animate-pulse" />
              <div>
                <h2 className="text-3xl font-bold">🏥 NOUVEAU: AI Property Doctor</h2>
                <p className="text-lg">
                  L'analyse complète en 30 secondes - Ce que 10 experts font en 3 semaines pour €5,000+
                </p>
              </div>
            </div>
            <Link
              href="/ai-doctor"
              className="flex items-center gap-2 rounded-lg bg-white px-6 py-3 font-bold text-france-blue-600 transition hover:scale-105 hover:shadow-xl"
            >
              Essayer Maintenant
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-france-blue-500 to-france-blue-700 py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="mb-4 text-5xl font-bold">
            Analyse Immobilière & Énergétique Intelligente
          </h2>
          <p className="mb-8 text-xl">
            Identifiez les passoires thermiques et anticipez la Loi Climat 2026 avec l'IA
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

          {/* Quick Stats */}
          <div className="mt-12 grid grid-cols-3 gap-8">
            <div>
              <div className="text-4xl font-bold">42,000x</div>
              <div className="text-sm opacity-90">Plus rapide que l'analyse traditionnelle</div>
            </div>
            <div>
              <div className="text-4xl font-bold">91.8%</div>
              <div className="text-sm opacity-90">Précision de valorisation (R²)</div>
            </div>
            <div>
              <div className="text-4xl font-bold">€0</div>
              <div className="text-sm opacity-90">vs €5,000+ avec experts traditionnels</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="mb-12 text-center text-4xl font-bold">
            Fonctionnalités de Pointe
          </h2>

          {/* Featured: AI Property Doctor */}
          <div className="mb-12 rounded-2xl bg-gradient-to-r from-purple-50 to-blue-50 p-8 shadow-xl">
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0">
                <Sparkles className="h-16 w-16 text-purple-600" />
              </div>
              <div className="flex-1">
                <div className="mb-2 inline-block rounded-full bg-purple-600 px-3 py-1 text-sm font-bold text-white">
                  ⭐ NOUVEAU
                </div>
                <h3 className="mb-3 text-3xl font-bold">🏥 AI Property Doctor</h3>
                <p className="mb-4 text-lg text-gray-700">
                  L'analyse immobilière qui semblait <strong>IMPOSSIBLE</strong> - maintenant réalisée en 30 secondes par l'IA!
                </p>
                <ul className="mb-6 grid grid-cols-2 gap-3">
                  <li className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-green-600" />
                    <span>Analyse photo par vision par ordinateur</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                    <span>Valorisation à 91.8% de précision (XGBoost)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-green-600" />
                    <span>Prévisions marché sur 5 ans (Prophet)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-green-600" />
                    <span>Verdict d'investissement automatique</span>
                  </li>
                </ul>
                <Link
                  href="/ai-doctor"
                  className="inline-flex items-center gap-2 rounded-lg bg-purple-600 px-6 py-3 font-bold text-white transition hover:bg-purple-700"
                >
                  Analyser un bien maintenant
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>

          {/* Other Features */}
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
      <section id="dpe" className="bg-muted py-16">
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

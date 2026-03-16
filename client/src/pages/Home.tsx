'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, Calendar, MapPin } from 'lucide-react';
import { todosEstados, CotacaoEstado } from '@/lib/mockData';

export default function Home() {
  const [estadoSelecionado, setEstadoSelecionado] = useState<CotacaoEstado>(todosEstados[0]);

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(valor);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-50">
      {/* Header */}
      <header className="border-b border-green-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-green-800">
                Cotações CEASA Sul
              </h1>
              <p className="text-green-600 mt-1">
                Monitoramento de preços diários - RS, SC, PR
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Última atualização</p>
              <p className="text-lg font-semibold text-green-800">
                {new Date().toLocaleDateString('pt-BR')}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-12">
        {/* Resumo Geral */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {todosEstados.map((estado) => (
            <Card
              key={estado.sigla}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                estadoSelecionado.sigla === estado.sigla
                  ? 'ring-2 ring-green-500 shadow-lg'
                  : ''
              }`}
              onClick={() => setEstadoSelecionado(estado)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl">{estado.sigla}</CardTitle>
                    <CardDescription>{estado.estado}</CardDescription>
                  </div>
                  {estado.aumentos.length > 0 && (
                    <div className="flex items-center gap-2 bg-red-100 px-3 py-1 rounded-full">
                      <TrendingUp className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-semibold text-red-600">
                        {estado.aumentos.length}
                      </span>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <p className="text-gray-600">
                    <span className="font-semibold text-gray-900">
                      {estado.cotacoes.length}
                    </span>{' '}
                    produtos
                  </p>
                  <p className="text-gray-600">
                    Data: <span className="font-semibold">{estado.data}</span>
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Detalhes do Estado Selecionado */}
        <Tabs defaultValue="todos" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="todos">Todos os Produtos</TabsTrigger>
            <TabsTrigger value="aumentos">
              Aumentos de Preço
              {estadoSelecionado.aumentos.length > 0 && (
                <Badge variant="destructive" className="ml-2">
                  {estadoSelecionado.aumentos.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Aba: Todos os Produtos */}
          <TabsContent value="todos">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-green-600" />
                  Cotações de {estadoSelecionado.estado}
                </CardTitle>
                <CardDescription>
                  Atualizado em {estadoSelecionado.data}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {estadoSelecionado.cotacoes.map((cotacao, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {cotacao.produto}
                        </h3>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {cotacao.regiao || 'N/A'}
                          </span>
                          <span>{cotacao.unidade}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-green-700">
                          {formatarMoeda(cotacao.preco)}
                        </p>
                        {cotacao.aumento && (
                          <p className="text-sm text-red-600 font-semibold mt-1">
                            ↑ {cotacao.aumento.percentual.toFixed(1)}%
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba: Aumentos de Preço */}
          <TabsContent value="aumentos">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-red-600" />
                  Alimentos com Aumento de Preço
                </CardTitle>
                <CardDescription>
                  Comparação com o dia anterior ({estadoSelecionado.data})
                </CardDescription>
              </CardHeader>
              <CardContent>
                {estadoSelecionado.aumentos.length > 0 ? (
                  <div className="space-y-3">
                    {estadoSelecionado.aumentos.map((cotacao, idx) => (
                      <div
                        key={idx}
                        className="p-4 border-2 border-red-200 bg-red-50 rounded-lg"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-bold text-gray-900 text-lg">
                              {cotacao.produto}
                            </h3>
                            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {cotacao.regiao || 'N/A'}
                              </span>
                              <span>{cotacao.unidade}</span>
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {cotacao.aumento?.dataAnterior}
                              </span>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className="flex items-baseline gap-2">
                              <span className="text-sm text-gray-600 line-through">
                                {formatarMoeda(
                                  cotacao.preco - (cotacao.aumento?.valor || 0)
                                )}
                              </span>
                              <span className="text-2xl font-bold text-green-700">
                                {formatarMoeda(cotacao.preco)}
                              </span>
                            </div>
                            <div className="mt-2 bg-red-600 text-white px-3 py-1 rounded-full inline-block">
                              <p className="text-sm font-bold">
                                ↑ {cotacao.aumento?.percentual.toFixed(1)}%
                              </p>
                              <p className="text-xs">
                                +{formatarMoeda(cotacao.aumento?.valor || 0)}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">
                      Nenhum aumento de preço identificado em {estadoSelecionado.estado}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Informações Adicionais */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sobre os Dados</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-gray-600 space-y-3">
              <p>
                As cotações são coletadas diariamente das Centrais de Abastecimento
                (CEASA) dos estados do Rio Grande do Sul, Santa Catarina e Paraná.
              </p>
              <p>
                Os dados são atualizados automaticamente via GitHub Actions todos os
                dias úteis.
              </p>
              <p>
                As variações de preço são calculadas comparando com o dia anterior.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Fontes de Dados</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>
                <span className="font-semibold">CEASA RS:</span>{' '}
                <a
                  href="https://ceasa.rs.gov.br/cotacoes-de-precos"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline"
                >
                  ceasa.rs.gov.br
                </a>
              </p>
              <p>
                <span className="font-semibold">CEASA SC:</span>{' '}
                <a
                  href="https://www.ceasa.sc.gov.br/index.php/cotacao-de-precos/2026-1"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline"
                >
                  ceasa.sc.gov.br
                </a>
              </p>
              <p>
                <span className="font-semibold">CEASA PR:</span>{' '}
                <a
                  href="https://celepar7.pr.gov.br/ceasa/hoje.asp"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-green-600 hover:underline"
                >
                  celepar7.pr.gov.br
                </a>
              </p>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50 mt-16">
        <div className="container py-8 text-center text-sm text-gray-600">
          <p>
            Cotações CEASA Sul © {new Date().getFullYear()} - Dados atualizados
            automaticamente
          </p>
          <p className="mt-2">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 hover:underline"
            >
              Código-fonte no GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

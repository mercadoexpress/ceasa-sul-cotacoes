'use client';
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, ExternalLink, Search, ChevronUp, ChevronDown } from 'lucide-react';

interface Cotacao {
  produto: string;
  preco: number;
  preco_min?: number;
  preco_max?: number;
  preco_anterior?: number;
  variacao_pct?: number;
  aumentou?: boolean;
  diminuiu?: boolean;
  unidade?: string;
  categoria?: string;
  precos_cidades?: Record<string, number>;
}

interface Aumento {
  produto: string;
  preco: number;
  preco_anterior: number;
  variacao_pct: number;
}

interface EstadoDados {
  estado: string;
  nome: string;
  data: string;
  cotacoes: Cotacao[];
  aumentos: Aumento[];
  total_produtos: number;
  total_aumentos: number;
  total_diminuicoes: number;
  fonte: string;
  erro?: string;
}

interface DadosCotacoes {
  ultima_atualizacao: string;
  estados: EstadoDados[];
}

type SortField = 'produto' | 'preco' | 'variacao_pct';
type SortDir = 'asc' | 'desc';

const ESTADO_CORES: Record<string, { bg: string; text: string; border: string }> = {
  PR: { bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-300' },
  SC: { bg: 'bg-purple-50', text: 'text-purple-800', border: 'border-purple-300' },
  RS: { bg: 'bg-green-50', text: 'text-green-800', border: 'border-green-300' },
};

function formatarMoeda(valor: number): string {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
}

function formatarVariacao(pct: number): string {
  const sinal = pct > 0 ? '+' : '';
  return `${sinal}${pct.toFixed(1)}%`;
}

export default function Home() {
  const [dados, setDados] = useState<DadosCotacoes | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [estadoAtivo, setEstadoAtivo] = useState<string>('PR');
  const [abaAtiva, setAbaAtiva] = useState<'todos' | 'aumentos'>('todos');
  const [busca, setBusca] = useState('');
  const [sortField, setSortField] = useState<SortField>('produto');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  useEffect(() => {
    carregarDados();
  }, []);

  async function carregarDados() {
    setCarregando(true);
    setErro(null);
    try {
      const base = import.meta.env.BASE_URL || '/';
      const url = `${base}data/cotacoes.json?t=${Date.now()}`;
      const resp = await fetch(url);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const json: DadosCotacoes = await resp.json();
      setDados(json);
      if (json.estados.length > 0) {
        setEstadoAtivo(json.estados[0].estado);
      }
    } catch (e) {
      setErro('Não foi possível carregar os dados de cotações. Os dados podem estar sendo atualizados.');
      console.error(e);
    } finally {
      setCarregando(false);
    }
  }

  function toggleSort(field: SortField) {
    if (sortField === field) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  }

  function SortIcon({ field }: { field: SortField }) {
    if (sortField !== field) return <span className="text-gray-300 ml-1 text-xs">↕</span>;
    return sortDir === 'asc'
      ? <ChevronUp className="inline w-3 h-3 ml-1" />
      : <ChevronDown className="inline w-3 h-3 ml-1" />;
  }

  const estadoAtual = dados?.estados.find(e => e.estado === estadoAtivo);

  const cotacoesFiltradas = (() => {
    if (!estadoAtual) return [];
    let lista = abaAtiva === 'aumentos'
      ? estadoAtual.cotacoes.filter(c => c.aumentou)
      : estadoAtual.cotacoes;

    if (busca.trim()) {
      const q = busca.toLowerCase();
      lista = lista.filter(c => c.produto.toLowerCase().includes(q));
    }

    return [...lista].sort((a, b) => {
      let va: number | string = a[sortField] ?? '';
      let vb: number | string = b[sortField] ?? '';
      if (sortField === 'variacao_pct') {
        va = a.variacao_pct ?? -999;
        vb = b.variacao_pct ?? -999;
      }
      if (typeof va === 'string' && typeof vb === 'string') {
        return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      }
      return sortDir === 'asc' ? (va as number) - (vb as number) : (vb as number) - (va as number);
    });
  })();

  if (carregando) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
          <p className="text-green-700 text-lg font-medium">Carregando cotações...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                🌿 Cotações CEASA Sul
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                Monitoramento diário de preços — RS, SC, PR
              </p>
            </div>
            <div className="flex items-center gap-3">
              {dados && (
                <div className="text-right">
                  <p className="text-xs text-gray-400">Última atualização</p>
                  <p className="text-sm font-semibold text-gray-700">{dados.ultima_atualizacao}</p>
                </div>
              )}
              <button
                onClick={carregarDados}
                className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                title="Atualizar dados"
              >
                <RefreshCw className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {erro && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
            ⚠ {erro}
          </div>
        )}

        {dados && (
          <>
            {/* Cards de resumo por estado */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              {dados.estados.map(estado => {
                const cores = ESTADO_CORES[estado.estado] || ESTADO_CORES.PR;
                const ativo = estadoAtivo === estado.estado;
                return (
                  <button
                    key={estado.estado}
                    onClick={() => { setEstadoAtivo(estado.estado); setAbaAtiva('todos'); setBusca(''); }}
                    className={`text-left p-4 rounded-xl border-2 transition-all ${
                      ativo
                        ? `${cores.bg} ${cores.border} shadow-md`
                        : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-sm'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className={`text-2xl font-bold ${ativo ? cores.text : 'text-gray-800'}`}>
                          {estado.estado}
                        </span>
                        <p className="text-xs text-gray-500 mt-0.5">{estado.nome}</p>
                      </div>
                      {estado.total_aumentos > 0 && (
                        <span className="flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-2 py-1 rounded-full">
                          <TrendingUp className="w-3 h-3" />
                          {estado.total_aumentos}
                        </span>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <p className="text-gray-400">Produtos</p>
                        <p className="font-semibold text-gray-700">{estado.total_produtos}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Aumentos</p>
                        <p className="font-semibold text-red-600">{estado.total_aumentos}</p>
                      </div>
                      <div>
                        <p className="text-gray-400">Quedas</p>
                        <p className="font-semibold text-green-600">{estado.total_diminuicoes}</p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400 mt-2">Data: {estado.data}</p>
                    {estado.erro && (
                      <p className="text-xs text-orange-500 mt-1">⚠ {estado.erro}</p>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Alertas de aumento */}
            {estadoAtual && estadoAtual.aumentos && estadoAtual.aumentos.length > 0 && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
                <h3 className="flex items-center gap-2 text-red-800 font-semibold mb-3 text-sm">
                  <TrendingUp className="w-4 h-4" />
                  Produtos com aumento de preço em {estadoAtual.nome}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {estadoAtual.aumentos.slice(0, 10).map(a => (
                    <div key={a.produto} className="bg-white border border-red-200 rounded-lg px-3 py-1.5 text-sm">
                      <span className="font-medium text-gray-800">{a.produto}</span>
                      <span className="ml-2 text-red-600 font-semibold">
                        +{a.variacao_pct.toFixed(1)}%
                      </span>
                      <span className="ml-1 text-gray-400 text-xs">
                        ({formatarMoeda(a.preco_anterior)} → {formatarMoeda(a.preco)})
                      </span>
                    </div>
                  ))}
                  {estadoAtual.aumentos.length > 10 && (
                    <button
                      onClick={() => setAbaAtiva('aumentos')}
                      className="text-red-600 text-sm font-medium hover:underline self-center"
                    >
                      +{estadoAtual.aumentos.length - 10} mais →
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Tabela de cotações */}
            {estadoAtual && (
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                {/* Controles */}
                <div className="p-4 border-b border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex gap-1">
                    <button
                      onClick={() => setAbaAtiva('todos')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        abaAtiva === 'todos'
                          ? 'bg-green-600 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      Todos os Produtos
                      <span className="ml-1.5 text-xs opacity-75">({estadoAtual.total_produtos})</span>
                    </button>
                    <button
                      onClick={() => setAbaAtiva('aumentos')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        abaAtiva === 'aumentos'
                          ? 'bg-red-600 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      🔺 Aumentos
                      {estadoAtual.total_aumentos > 0 && (
                        <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
                          abaAtiva === 'aumentos' ? 'bg-red-500' : 'bg-red-100 text-red-700'
                        }`}>
                          {estadoAtual.total_aumentos}
                        </span>
                      )}
                    </button>
                  </div>
                  <div className="relative w-full sm:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Buscar produto..."
                      value={busca}
                      onChange={e => setBusca(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Tabela */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50 border-b border-gray-100">
                        <th
                          className="text-left px-4 py-3 text-gray-600 font-semibold cursor-pointer hover:bg-gray-100 select-none"
                          onClick={() => toggleSort('produto')}
                        >
                          Produto <SortIcon field="produto" />
                        </th>
                        <th
                          className="text-right px-4 py-3 text-gray-600 font-semibold cursor-pointer hover:bg-gray-100 select-none"
                          onClick={() => toggleSort('preco')}
                        >
                          Preço Comum <SortIcon field="preco" />
                        </th>
                        <th className="text-right px-4 py-3 text-gray-600 font-semibold hidden md:table-cell">
                          Mín / Máx
                        </th>
                        <th
                          className="text-right px-4 py-3 text-gray-600 font-semibold cursor-pointer hover:bg-gray-100 select-none"
                          onClick={() => toggleSort('variacao_pct')}
                        >
                          Variação <SortIcon field="variacao_pct" />
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {cotacoesFiltradas.length === 0 ? (
                        <tr>
                          <td colSpan={4} className="text-center py-12 text-gray-400">
                            {busca ? `Nenhum produto encontrado para "${busca}".` : 'Nenhuma cotação disponível.'}
                          </td>
                        </tr>
                      ) : (
                        cotacoesFiltradas.map((cotacao, idx) => (
                          <tr
                            key={`${cotacao.produto}-${idx}`}
                            className={`border-b border-gray-50 hover:bg-gray-50/80 transition-colors ${
                              cotacao.aumentou ? 'bg-red-50/40' : cotacao.diminuiu ? 'bg-green-50/40' : ''
                            }`}
                          >
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                {cotacao.aumentou && <TrendingUp className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />}
                                {cotacao.diminuiu && <TrendingDown className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />}
                                {!cotacao.aumentou && !cotacao.diminuiu && (
                                  <Minus className="w-3.5 h-3.5 text-gray-200 flex-shrink-0" />
                                )}
                                <span className="font-medium text-gray-800">{cotacao.produto}</span>
                                {cotacao.categoria && cotacao.categoria !== 'GERAL' && (
                                  <span className="hidden lg:inline text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                                    {cotacao.categoria}
                                  </span>
                                )}
                              </div>
                              {cotacao.precos_cidades && Object.keys(cotacao.precos_cidades).length > 1 && (
                                <div className="mt-1 flex flex-wrap gap-2">
                                  {Object.entries(cotacao.precos_cidades).map(([cidade, preco]) => (
                                    <span key={cidade} className="text-xs text-gray-400">
                                      {cidade}: {formatarMoeda(preco)}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </td>
                            <td className="px-4 py-3 text-right">
                              <span className={`font-semibold ${
                                cotacao.aumentou ? 'text-red-600' : cotacao.diminuiu ? 'text-green-600' : 'text-gray-800'
                              }`}>
                                {formatarMoeda(cotacao.preco)}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right text-gray-400 text-xs hidden md:table-cell">
                              {cotacao.preco_min != null && cotacao.preco_max != null ? (
                                <span>
                                  {formatarMoeda(cotacao.preco_min)} / {formatarMoeda(cotacao.preco_max)}
                                </span>
                              ) : '—'}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {cotacao.variacao_pct != null ? (
                                <span className={`inline-flex items-center gap-0.5 text-xs font-semibold px-2 py-1 rounded-full ${
                                  cotacao.aumentou
                                    ? 'bg-red-100 text-red-700'
                                    : cotacao.diminuiu
                                    ? 'bg-green-100 text-green-700'
                                    : 'bg-gray-100 text-gray-500'
                                }`}>
                                  {cotacao.aumentou && <TrendingUp className="w-3 h-3" />}
                                  {cotacao.diminuiu && <TrendingDown className="w-3 h-3" />}
                                  {formatarVariacao(cotacao.variacao_pct)}
                                </span>
                              ) : (
                                <span className="text-gray-300 text-xs">—</span>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Footer da tabela */}
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-gray-400">
                  <span>
                    {cotacoesFiltradas.length} produto{cotacoesFiltradas.length !== 1 ? 's' : ''}
                    {busca && ` para "${busca}"`}
                    {' '}de {estadoAtual.total_produtos} total
                  </span>
                  <a
                    href={estadoAtual.fonte}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 hover:text-gray-600 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Fonte oficial: {estadoAtual.nome}
                  </a>
                </div>
              </div>
            )}

            {/* Informações sobre os dados */}
            <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
              {dados.estados.map(estado => (
                <div key={estado.estado} className="bg-white rounded-xl border border-gray-200 p-4 text-sm">
                  <h4 className="font-semibold text-gray-800 mb-2">{estado.nome}</h4>
                  <div className="space-y-1 text-gray-500">
                    <p>📅 Data: <span className="text-gray-700 font-medium">{estado.data}</span></p>
                    <p>📦 Produtos: <span className="text-gray-700 font-medium">{estado.total_produtos}</span></p>
                    <p>🔺 Aumentos: <span className="text-red-600 font-medium">{estado.total_aumentos}</span></p>
                    <p>🔻 Quedas: <span className="text-green-600 font-medium">{estado.total_diminuicoes}</span></p>
                  </div>
                  <a
                    href={estado.fonte}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 flex items-center gap-1 text-xs text-blue-500 hover:text-blue-700"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Ver fonte oficial
                  </a>
                </div>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-400">
            <div>
              <p className="font-medium text-gray-600">🌿 Cotações CEASA Sul</p>
              <p className="text-xs mt-0.5">Dados coletados automaticamente das fontes oficiais dos CEASAs da Região Sul</p>
            </div>
            <div className="flex gap-4 text-xs">
              <a href="https://celepar7.pr.gov.br/ceasa/hoje.asp" target="_blank" rel="noopener noreferrer" className="hover:text-gray-600 transition-colors">CEASA PR</a>
              <a href="https://www.ceasa.sc.gov.br/index.php/cotacao-de-precos" target="_blank" rel="noopener noreferrer" className="hover:text-gray-600 transition-colors">CEASA SC</a>
              <a href="https://ceasa.rs.gov.br/cotacoes-de-precos" target="_blank" rel="noopener noreferrer" className="hover:text-gray-600 transition-colors">CEASA RS</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

// Caminho: imobcloud/frontend/app/[slug]/page.js (FICHEIRO RENOMEADO E ATUALIZADO)

import Link from 'next/link';

// Função para buscar os dados da imobiliária e dos seus imóveis
async function getImobiliariaData(slug) {
  // --- ALTERAÇÃO AQUI ---
  // Trocamos 'localhost:8000' por 'backend:8000', que é o endereço
  // do serviço do backend dentro da rede do Docker.
  const imobRes = await fetch(`http://backend:8000/public/imobiliarias/slug/${slug}`, { cache: 'no-store' });
  if (!imobRes.ok) {
    if (imobRes.status === 404) return null;
    throw new Error('Falha ao buscar dados da imobiliária');
  }
  const imobiliaria = await imobRes.json();

  // --- ALTERAÇÃO AQUI ---
  // Trocamos 'localhost:8000' por 'backend:8000' também nesta chamada.
  const imoveisRes = await fetch(`http://backend:8000/imobiliarias/${imobiliaria.id}/imoveis/`, { cache: 'no-store' });
  if (!imoveisRes.ok) {
    throw new Error('Falha ao buscar imóveis');
  }
  const imoveis = await imoveisRes.json();

  return { imobiliaria, imoveis };
}

// A página agora recebe 'params', que contém o 'slug' da URL
export default async function ImobiliariaHomePage({ params }) {
  const data = await getImobiliariaData(params.slug);

  if (!data) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-100">
        <h1 className="text-4xl font-bold">Imobiliária não encontrada.</h1>
        <p className="text-lg mt-4">O endereço que você acedeu não corresponde a nenhuma imobiliária cadastrada.</p>
      </main>
    );
  }

  const { imobiliaria, imoveis } = data;

  return (
    <main className="flex min-h-screen flex-col items-center p-24 bg-gray-100">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-12">
          {imobiliaria.nome}
        </h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {imoveis.map((imovel) => (
            // --- ALTERAÇÃO AQUI ---
            // Corrigimos o link para a página de detalhes do imóvel.
            <Link href={`/imoveis/${imovel.id}`} key={imovel.id}>
              <div className="bg-white rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300 cursor-pointer h-full">
                <div className="p-6">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-2">{imovel.titulo}</h2>
                  <p className="text-gray-600 mb-4">{imovel.descricao}</p>
                  <div className="text-3xl font-bold text-blue-600 mb-4">
                    R$ {Number(imovel.preco).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="flex justify-between text-gray-700">
                    <span>{imovel.quartos} quartos</span>
                    <span>{imovel.banheiros} banheiros</span>
                    <span>{imovel.area} m²</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
        {imoveis.length === 0 && (
          <p className="text-center text-gray-500 mt-12">Nenhum imóvel cadastrado para esta imobiliária.</p>
        )}
      </div>
    </main>
  );
}

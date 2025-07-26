// Caminho: imobcloud/frontend/app/imoveis/[id]/page.js (NOVO FICHEIRO)

// Função para buscar os dados de um único imóvel
async function getImovel(id) {
  const res = await fetch(`http://backend:8000/imoveis/${id}`, { cache: 'no-store' });
  if (!res.ok) {
    // Se o imóvel não for encontrado, o Next.js mostrará a sua página 404 padrão
    if (res.status === 404) return null;
    throw new Error('Falha ao buscar dados do imóvel');
  }
  return res.json();
}

// A página recebe 'params' que contém o ID do imóvel vindo da URL
export default async function ImovelDetalhePage({ params }) {
  const imovel = await getImovel(params.id);

  // Se o imóvel não for encontrado, mostra uma mensagem
  if (!imovel) {
    return <div className="text-center text-2xl mt-20">Imóvel não encontrado.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-8">
        <div className="bg-white rounded-lg shadow-xl overflow-hidden">
          {/* Área para a imagem principal (placeholder por agora) */}
          <div className="h-96 bg-gray-300 flex items-center justify-center">
            <span className="text-gray-500">Imagem do Imóvel</span>
          </div>

          <div className="p-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{imovel.titulo}</h1>
            <p className="text-lg text-gray-600 mb-6">{imovel.descricao}</p>
            
            <div className="text-5xl font-extrabold text-blue-700 mb-8">
              R$ {Number(imovel.preco).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 border-t border-b py-6 mb-8">
              <div className="text-center">
                <div className="text-2xl font-bold">{imovel.quartos}</div>
                <div className="text-gray-500">Quartos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{imovel.banheiros}</div>
                <div className="text-gray-500">Banheiros</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{imovel.area} m²</div>
                <div className="text-gray-500">Área</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold capitalize">{imovel.tipo}</div>
                <div className="text-gray-500">Tipo</div>
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Mais Detalhes</h2>
            <p>
              Aqui podemos adicionar mais informações sobre o imóvel, como características, localização no mapa, etc.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

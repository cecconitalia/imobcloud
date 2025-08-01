Imobcloud
Uma plataforma SaaS multi-tenant robusta, projetada para imobiliárias e corretores, que oferece uma solução completa para a gestão personalizada de imóveis, usuários e atendimentos. Cada cliente opera em um ambiente isolado, acessível através de subdomínios exclusivos, garantindo segurança, escalabilidade e alta performance.

Visão Geral da Arquitetura
Imobcloud é construído com tecnologias modernas e eficientes, garantindo uma aplicação desacoplada e pronta para a nuvem.

Backend
Framework: Django

API: Django Rest Framework (DRF)

Multi-tenancy: Gerenciamento robusto de múltiplos inquilinos com isolamento de dados via django-tenants (ou similar).

Autenticação: Tokens JWT (JSON Web Tokens) para um fluxo de login, refresh e logout seguro.

Frontend
Framework: React.js

Estilização: Tailwind CSS para um desenvolvimento ágil e responsivo.

Integração: Consumo de APIs RESTful do Django via fetch/axios.

Banco de Dados
PostgreSQL: Utiliza o poder do PostgreSQL para gerenciar esquemas de banco de dados separados para cada cliente, garantindo total isolamento e segurança dos dados.

Infraestrutura
Docker: Conteinerização de todas as partes da aplicação (backend, frontend, banco de dados).

Docker Compose: Orquestração fácil e eficiente de todos os serviços em ambiente de desenvolvimento.

Pronto para Nuvem: Design preparado para deploy em ambientes de nuvem escaláveis, como AWS, Render, Railway, com suporte a HTTPS.

Multi-Tenancy com Subdomínios
Um dos pilares do Imobcloud é seu sistema multi-tenant, onde cada cliente possui seu próprio subdomínio, como cliente1.imobcloud.com ou cliente2.imobcloud.com. Isso garante que:

Dados Isolados: Os dados de cada cliente são armazenados em esquemas de banco de dados PostgreSQL distintos.

Segurança: Completa separação de informações entre os inquilinos.

Experiência Personalizada: Cada cliente acessa sua própria instância da plataforma.

Principais Funcionalidades
A plataforma Imobcloud oferece um conjunto abrangente de recursos para a gestão imobiliária:

Gestão de Imóveis: Cadastro, visualização, edição e remoção de propriedades com detalhes completos.

Gestão de Usuários e Permissões: Controle de acesso e funções para diferentes tipos de usuários dentro de cada inquilino.

Painel Administrativo Personalizado: Um painel intuitivo para cada cliente gerenciar suas operações.

Upload de Imagens: Facilidade para adicionar e gerenciar fotos de imóveis.

Página Pública de Imóveis: Uma interface visível ao público com a listagem dos imóveis disponíveis de cada cliente.

API RESTful Completa: Todos os recursos expostos via APIs para integração e extensibilidade.

Provisionamento Automático de Clientes: Processo simplificado para a criação de novos inquilinos, incluindo configuração de schema, criação de usuário admin e configurações iniciais.

Endpoints da API (Exemplos)
Todas as APIs são acessíveis sob o prefixo /api/.

Autenticação
POST /api/token/: Realiza o login do usuário.

POST /api/token/refresh/: Renova o token de acesso JWT.

Usuários
GET /api/users/: Lista todos os usuários.

POST /api/users/: Cria um novo usuário.

Imóveis
GET /api/properties/: Lista todos os imóveis.

POST /api/properties/: Cadastra um novo imóvel.

PUT /api/properties/:id/: Edita um imóvel existente.

DELETE /api/properties/:id/: Remove um imóvel.

Provisionamento de Cliente
POST /api/tenants/: Cria um novo cliente (inquilino), incluindo schema, subdomínio e usuário administrador.

Fluxo de Autenticação
O usuário acessa a plataforma via subdomínio (cliente.imobcloud.com).

Insere as credenciais (e-mail e senha) na página de login do frontend React.

O backend Django valida as credenciais e retorna um par de tokens JWT (access e refresh).

O frontend armazena o token de acesso e o inclui no cabeçalho Authorization: Bearer <token> de todas as requisições subsequentes à API.

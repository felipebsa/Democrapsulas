<p align="center">

  <img src=".github/assets/democrapsulas-banner.jpeg" width="100%">

</p>

# Democrápsulas

Um site onde as pessoas escrevem mensagens para o futuro e guardam dentro de lâmpadas. Cada lâmpada sobe pela tela com um cronômetro embaixo, e ninguém consegue ler o que está escrito até o tempo acabar. Quando chega a zero, qualquer visitante pode abrir a lâmpada, ler a mensagem e ver quem escreveu e em que dia.

O "democráticas" do nome vem do fato de que a comunidade decide algumas coisas: os votos escolhem a música de cada salão, e as lâmpadas mais votadas sobem no ranking.

O projeto ainda está em desenvolvimento. Começamos pelo planejamento e vamos construindo as páginas por etapas.

## Como o site funciona

Quem entra no site pode ficar só olhando as lâmpadas subirem e abrindo as que já foram liberadas. Para criar lâmpadas, votar, favoritar ou denunciar, precisa de uma conta. A conta usa só apelido e senha, sem e-mail e sem nome real, e o apelido é o que aparece como autor.

Ao criar uma lâmpada, a pessoa escreve a mensagem, escolhe em qual salão ela vai aparecer, define a data de abertura e decide se ela será pública ou privada. As privadas só aparecem para quem criou, dentro da conta.

Depois de aberta, cada lâmpada pode receber voto positivo ou negativo, ser marcada com uma estrela (para ir para a galeria da pessoa) ou ser denunciada.

## Os salões

O site tem cinco salões. A lógica é a mesma em todos e o que muda é o visual, o desenho da lâmpada e a música.

O Salão Asiático é uma noite de festival com lanternas de papel, em tons de vermelho e dourado. O Medieval tem castelo, tochas e pergaminhos. O Cyberpunk é uma cidade futurista com néon e chuva. O Espaço tem nebulosas, estrelas e planetas, e as lâmpadas parecem satélites. No Salão das Estações o cenário muda de estação a cada dois minutos, ao mesmo tempo para todo mundo que estiver no site.

## Páginas

1. Salão Asiático (é também a página inicial)
2. Salão Medieval
3. Salão Cyberpunk
4. Salão Espaço
5. Salão das Estações
6. Criar Lâmpada
7. Roleta de Lâmpadas, que sorteia uma lâmpada já liberada
8. Galeria, com as lâmpadas favoritas de cada pessoa
9. Ranking e Dados do Site
10. Minha Conta
11. Votação de Músicas

Todas as páginas têm botão para ligar e desligar o som e para trocar entre modo claro e escuro.

## Regras

O texto de uma lâmpada só é enviado pelo servidor depois que a data de abertura passa. Isso evita que alguém leia antes da hora olhando o código da página ou mudando o relógio do computador.

Cada pessoa tem um voto por lâmpada, mas pode trocar depois. Também há um limite de lâmpadas criadas por dia e um tempo de espera entre uma e outra. Lâmpadas que recebem muitas denúncias ficam ocultas até a gente revisar. As mensagens têm limite de tamanho e passam por um filtro de palavras impróprias.

Para o site não ficar pesado, cada salão mostra só de 20 a 30 lâmpadas públicas por vez, sorteadas entre as que existem.

## Votação de músicas

Cada salão terá músicas candidatas, três na primeira versão e cinco depois. Cada pessoa vota em uma por salão e pode mudar o voto. Quando alguém pede a trilha de um salão, o servidor calcula qual música ganhou na semana que acabou, e o salão passa a tocar essa. Se houver empate, vence a que chegou primeiro à maior pontuação.

## Tecnologias

O front-end é feito com HTML, CSS e JavaScript puro. Entre os recursos de JavaScript que mais vamos usar estão manipulação do DOM, eventos, Date, setInterval, fetch, Audio e localStorage.

O servidor é uma API em Python com FastAPI e banco PostgreSQL, com autenticação por token JWT. O acesso ao banco usa SQLAlchemy, as tabelas são criadas com migrations do Alembic e tudo roda em contêineres com Docker Compose. O código fica no GitHub, versionado com Git.

## Andamento

- [x] Estrutura do servidor com FastAPI, PostgreSQL e Docker
- [x] Contas: cadastro, login com token e rota da conta logada
- [x] Migrations do banco com Alembic
- [x] Rotas da API para criar e abrir lâmpadas
- [x] API de votos, favoritos, denúncias, roleta, ranking, dados do site e moderação
- [x] API da votação semanal de músicas e do relógio do Salão das Estações
- [x] Testes automáticos do servidor
- [ ] Combinar o contrato da API e definir o visual dos salões
- [ ] Montar a estrutura das páginas em HTML e CSS, com modo claro e escuro
- [ ] Lâmpadas subindo, cronômetros e criar/abrir lâmpadas, usando dados de exemplo
- [ ] Ligar o site à API: contas, votos, favoritos e denúncias
- [ ] Roleta, galeria, ranking e dados do site
- [ ] Música e votação semanal
- [ ] Testes e ajustes finais

## Como rodar

Por enquanto só o servidor roda. O site ainda está em construção. Você precisa de Docker e Python instalados.

1. Copie o `.env.example` para `.env` e troque o valor de `SECRET_KEY`.

2. Suba o banco, na pasta raiz do projeto:

   ```bash
   docker compose up -d db
   ```

   O PostgreSQL fica disponível na porta 5433 do seu computador.

3. Instale as dependências e crie as tabelas, dentro da pasta `backend`:

   ```bash
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   ```

4. Inicie a API, ainda dentro de `backend`:

   ```bash
   uvicorn app.main:app --reload
   ```

A documentação interativa da API abre em http://localhost:8000/docs. Lá dá para testar todas as rotas. Para as que pedem login, clique em **Authorize** e entre com apelido e senha.

Para subir a API e o banco juntos no Docker, rode `docker compose up -d --build` na raiz do projeto. Nesse caso a API cria e atualiza as tabelas sozinha ao iniciar.

### Testes

Com o banco rodando, dentro de `backend`:

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam um banco separado (`democrapsulas_test`), criado automaticamente no mesmo PostgreSQL, então não apagam nada do banco de desenvolvimento.

### Administrador

Para moderar lâmpadas denunciadas, transforme uma conta existente em admin (dentro de `backend`):

```bash
python -m app.scripts.make_admin <apelido>
```

Com o Docker: `docker compose exec api python -m app.scripts.make_admin <apelido>`.

## Rotas da API

Rotas marcadas com 🔒 precisam do token (`Authorization: Bearer <token>`). As outras funcionam sem login, mas, se o token for enviado, a resposta diz se a lâmpada é sua, qual foi seu voto e se está nos favoritos.

| Método | Rota | O que faz |
| --- | --- | --- |
| POST | `/auth/register` | Cria conta (apelido de 3 a 20 letras, números ou `_`; senha com 6 ou mais caracteres) |
| POST | `/auth/login` | Devolve o token (formulário com `username` e `password`) |
| GET 🔒 | `/auth/me` | Dados da conta logada |
| POST 🔒 | `/capsules` | Cria lâmpada: `hall`, `title`, `content`, `is_private`, `open_at` (com fuso, ex.: `2027-01-01T00:00:00-03:00`) |
| GET | `/capsules?hall=asiatico` | Até 30 lâmpadas públicas sorteadas do salão |
| GET | `/capsules/random` | Roleta: uma lâmpada já liberada (aceita `?hall=`) |
| GET | `/capsules/{id}` | Uma lâmpada |
| DELETE 🔒 | `/capsules/{id}` | Apaga sua lâmpada |
| PUT 🔒 | `/capsules/{id}/vote` | Vota `{"value": 1}` ou `{"value": -1}` (pode trocar) |
| DELETE 🔒 | `/capsules/{id}/vote` | Tira o voto |
| PUT / DELETE 🔒 | `/capsules/{id}/favorite` | Marca ou desmarca a estrela |
| POST 🔒 | `/capsules/{id}/report` | Denuncia (`{"reason": "..."}` opcional) |
| GET 🔒 | `/me/capsules` | Suas lâmpadas, incluindo privadas |
| GET 🔒 | `/me/favorites` | Galeria (suas favoritas) |
| GET | `/ranking` | Lâmpadas mais votadas (aceita `?hall=` e `?limit=`) |
| GET | `/stats` | Dados do site |
| GET | `/halls` | Lista dos salões |
| GET | `/halls/estacoes/season` | Estação atual do Salão das Estações e quanto falta para trocar |
| GET | `/halls/{salão}/songs` | Músicas candidatas e votos da semana atual |
| PUT 🔒 | `/halls/{salão}/songs/vote` | Vota numa música `{"song_id": 1}` (pode trocar) |
| GET | `/halls/{salão}/track` | Música que o salão toca: a vencedora da semana passada |
| GET 🔒 | `/admin/capsules?status=hidden` | Admin: lâmpadas ocultas (ou `reported`, denunciadas e ainda visíveis) |
| POST 🔒 | `/admin/capsules/{id}/approve` | Admin: libera a lâmpada e zera as denúncias |
| POST 🔒 | `/admin/capsules/{id}/hide` | Admin: oculta a lâmpada |
| DELETE 🔒 | `/admin/capsules/{id}` | Admin: apaga a lâmpada |

Os salões são `asiatico`, `medieval`, `cyberpunk`, `espaco` e `estacoes`.

Antes da data de abertura, `title`, `content` e `author` vêm como `null` para todo mundo, menos para quem criou. O campo `is_open` diz se a lâmpada já pode ser lida.

A semana da votação de músicas vai de segunda 00:00 a domingo 23:59, no horário de Brasília. As músicas cadastradas por enquanto são provisórias ("Faixa 1", "Faixa 2" e "Faixa 3" em cada salão, com arquivos em `audio/<salão>/faixa-N.mp3`).

As palavras bloqueadas ficam em `backend/app/core/bad_words.txt`, uma por linha. Os limites podem ser mudados no `.env` (veja o `.env.example`).

Depois de mudar um model, gere uma migration nova e aplique:

```bash
alembic revision --autogenerate -m "descrição da mudança"
alembic upgrade head
```

Rode os comandos do Alembic sempre de dentro de `backend`, porque é de lá que a API lê o `.env`.

## Quem faz

Felipe Barbosa Santos cuida do servidor (API e banco de dados) e também ajuda no front-end: [github.com/felipebsa](https://github.com/felipebsa)

Gabriel Fernandes Barbarini cuida do front-end: [github.com/FeLaLost](https://github.com/FeLaLost)

É um trabalho da disciplina de Programação Web, do curso técnico em Desenvolvimento de Sistemas (turma 1C2) da ETEC Vasco Antonio Venchiarutti, em Jundiaí. Professora: Daniela.

## Sites que nos inspiraram

- [neal.fun](https://neal.fun), pela criatividade dos experimentos interativos
- [FutureMe](https://www.futureme.org), onde se escrevem cartas para o futuro
- [Museum of Endangered Sounds](https://savethesounds.info), um painel de sons antigos de tecnologia
- [Radiooooo](https://radiooooo.com), onde se ouve música escolhendo país e década

## Créditos

As músicas, sons e imagens serão criados por nós ou tirados de bancos livres de direitos autorais. Quando forem escolhidos, as fontes ficam listadas aqui.

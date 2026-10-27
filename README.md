<p align="center">

  <img src=".github/assets/democrapsulas-banner.jpeg" width="100%">

</p>

**Status:** servidor completo (API, autenticação, migrations, testes e Docker) e primeira versão do site no ar localmente, com tela de entrada, Salão Asiático, Criar Lâmpada e Roleta.

Site de mensagens para o futuro: cada pessoa escreve uma mensagem, guarda dentro de uma lâmpada e só deixa ela ser lida quando o cronômetro chegar a zero.

---

## Visão geral

Democrápsulas é um site onde as pessoas escrevem mensagens para o futuro e guardam dentro de lâmpadas. Cada lâmpada sobe pela tela com um cronômetro embaixo, e ninguém consegue ler o que está escrito até o tempo acabar. Quando chega a zero, qualquer visitante pode abrir a lâmpada, ler a mensagem e ver quem escreveu e em que dia.

O "democráticas" do nome vem do fato de que a comunidade decide algumas coisas: os votos escolhem a música de cada salão, e as lâmpadas mais votadas sobem no ranking.

Quem entra no site pode só olhar as lâmpadas subindo e abrir as que já foram liberadas. Para criar, votar, favoritar ou denunciar, precisa de uma conta, que usa só apelido e senha, sem e-mail e sem nome real.

O texto de uma lâmpada só sai do servidor depois que a data de abertura passa. Assim ninguém consegue ler antes da hora olhando o código da página ou mudando o relógio do computador.

O projeto foi feito **começando pelo servidor**: a API e o banco ficaram prontos antes de as páginas serem ligadas a eles.

---

## Como o projeto foi feito

### Servidor

O **servidor foi planejado e desenvolvido por Felipe Barbosa Santos**, incluindo a estrutura da API, os models do banco, a autenticação, as regras de negócio, as migrations, os testes automáticos e o ambiente Docker.

Principais tecnologias:

**FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, pytest e Docker.**

### Front-end

O front-end é feito por **Gabriel Fernandes Barbarini**, com ajuda do Felipe, em HTML, CSS e JavaScript puro, sem framework e sem etapa de build. Todos os dados vêm da API. Se ela estiver desligada, as telas avisam que não conseguiram conectar.

---

## Objetivos

É um trabalho da disciplina de Programação Web, e serviu para estudar:

* API REST com FastAPI
* Autenticação com JWT
* Migrations de banco
* Testes automáticos
* Desenvolvimento com Docker
* Manipulação do DOM, eventos, `Date`, `setInterval`, `fetch`, `Audio` e `localStorage`
* Ligar um front-end feito à mão a uma API de verdade

---

## Funcionalidades

### Contas

* [x] Cadastro e login só com apelido e senha
* [x] Token JWT
* [x] Senhas com hash (Argon2)
* [x] Rotas protegidas e rotas que funcionam com ou sem login
* [x] `GET /auth/me`

### Lâmpadas

* [x] Criar, listar, abrir e apagar
* [x] Conteúdo escondido pelo servidor até a data de abertura
* [x] Lâmpadas públicas e privadas
* [x] Cada salão mostra até 30 lâmpadas públicas sorteadas
* [x] Limite por dia e tempo de espera entre uma lâmpada e outra
* [x] Limite de tamanho e filtro de palavras impróprias

### Interação

* [x] Voto positivo ou negativo, um por pessoa e com troca
* [x] Favoritos (galeria de cada pessoa)
* [x] Denúncias, com lâmpada oculta automaticamente depois de várias
* [x] Roleta que sorteia uma lâmpada já liberada
* [x] Ranking das mais votadas
* [x] Dados do site (totais e lâmpadas por salão)

### Salões e músicas

* [x] Cinco salões: Asiático, Medieval, Cyberpunk, Espaço e Estações
* [x] Votação semanal da música de cada salão
* [x] Salão toca a vencedora da semana anterior
* [x] Relógio do Salão das Estações, que troca de estação a cada dois minutos para todo mundo ao mesmo tempo

### Moderação

* [x] Lista de lâmpadas ocultas e denunciadas
* [x] Aprovar ou apagar lâmpadas
* [x] Script para transformar uma conta em admin

### Infraestrutura

* [x] PostgreSQL
* [x] Migrations com Alembic
* [x] Docker / Docker Compose
* [x] Testes automáticos com pytest

### Front-end

* [x] Tela de entrada com contadores ligados a `/stats`
* [x] Navbar com salões, som e modo claro/escuro salvos no navegador
* [x] Entrar e criar conta ligados à API
* [x] Salão Asiático com lâmpadas subindo e cronômetro real
* [x] Criar Lâmpada com prévia, rascunho salvo e erros do servidor traduzidos
* [x] Roleta de lâmpadas
* [ ] Galeria, Ranking, Votação de Músicas e Minha Conta
* [ ] Visual dos outros quatro salões
* [ ] Lâmpadas privadas no site

---

## Modelo de dados

```text
User
│
├── Capsules    (lâmpadas, cada uma em um salão)
├── Votes       (+1 ou -1 numa lâmpada)
├── Favorites   (estrela numa lâmpada)
├── Reports     (denúncia de uma lâmpada)
└── SongVotes   (voto numa Song do salão, por semana)
```

Cada voto, favorito e denúncia liga uma conta a uma lâmpada, e cada pessoa só pode ter um de cada por lâmpada.

---

## API

Rotas marcadas com 🔒 precisam do token:

```http
Authorization: Bearer <token>
```

As outras funcionam sem login, mas, se o token for enviado, a resposta diz se a lâmpada é sua, qual foi seu voto e se está nos favoritos.

Documentação interativa:

```text
http://localhost:8000/docs
```

| Recurso | Rotas |
| --- | --- |
| Contas | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` 🔒 |
| Lâmpadas | `POST /capsules` 🔒, `GET /capsules?hall=`, `GET /capsules/random`, `GET /capsules/{id}`, `DELETE /capsules/{id}` 🔒 |
| Interação | `PUT/DELETE /capsules/{id}/vote` 🔒, `PUT/DELETE /capsules/{id}/favorite` 🔒, `POST /capsules/{id}/report` 🔒 |
| Minha conta | `GET /me/capsules` 🔒, `GET /me/favorites` 🔒 |
| Ranking e dados | `GET /ranking`, `GET /stats` |
| Salões | `GET /halls/estacoes/season`, `GET /halls/{salão}/songs`, `PUT /halls/{salão}/songs/vote` 🔒, `GET /halls/{salão}/track` |
| Admin | `GET /admin/capsules?status=hidden` 🔒, `POST /admin/capsules/{id}/approve` 🔒, `DELETE /admin/capsules/{id}` 🔒 |

Os salões são `asiatico`, `medieval`, `cyberpunk`, `espaco` e `estacoes`.

### Criar uma lâmpada

```json
{
  "hall": "asiatico",
  "title": "Para mim daqui a um ano",
  "content": "...",
  "is_private": false,
  "open_at": "2027-01-01T00:00:00-03:00"
}
```

A data de abertura precisa ter fuso. Antes dela, `title`, `content` e `author` vêm como `null` para todo mundo, menos para quem criou. O campo `is_open` diz se a lâmpada já pode ser lida.

### Votação de músicas

A semana vai de segunda 00:00 a domingo 23:59, no horário de Brasília. Quando alguém pede a trilha de um salão, o servidor calcula qual música ganhou na semana anterior. Se houver empate, vence a que chegou primeiro à maior pontuação.

As músicas cadastradas por enquanto são provisórias ("Faixa 1", "Faixa 2" e "Faixa 3" em cada salão, com arquivos em `audio/<salão>/faixa-N.mp3`).

---

## Tecnologias

### Servidor

* Python 3
* FastAPI
* SQLAlchemy 2.0
* Pydantic
* PostgreSQL
* Alembic
* PyJWT e pwdlib (Argon2)
* Pytest
* Uvicorn

### Front-end

* HTML
* CSS
* JavaScript puro

### Infraestrutura

* Docker
* Docker Compose

---

## Estrutura do projeto

```text
backend/
├── app/
│   ├── core/
│   │   ├── bad_words.txt
│   │   ├── clock.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── profanity.py
│   │   └── security.py
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── scripts/
│   ├── services/
│   ├── database.py
│   └── main.py
├── tests/
├── alembic/
├── alembic.ini
├── Dockerfile
└── requirements.txt

frontend/
├── audio/
├── img/
├── js/
├── index.html
└── style.css
```

---

## Rodando localmente

### Requisitos

* Python 3.12+
* Docker
* Docker Compose

```bash
git clone https://github.com/felipebsa/democrapsulas.git
cd democrapsulas
```

Copie o `.env.example` para `.env`, troque o valor de `SECRET_KEY` e rode:

```bash
docker compose up -d --build
```

A API cria e atualiza as tabelas sozinha ao iniciar.

API:

```text
http://localhost:8000/docs
```

Para as rotas que pedem login, clique em **Authorize** e entre com apelido e senha.

### Servidor sem Docker

Suba só o banco (fica na porta 5433) e rode a API direto, dentro de `backend`:

```bash
docker compose up -d db
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Rode os comandos do Alembic sempre de dentro de `backend`, porque é de lá que a API lê o `.env`.

### Front-end

Com a API rodando, abra a pasta `frontend` com o Live Server do VS Code ou com qualquer servidor estático:

```bash
cd frontend
python -m http.server 5500
```

Site:

```text
http://localhost:5500
```

O site usa `http://localhost:8000` por padrão. Para apontar para outra API, use `index.html?api=https://minha-api.com`.

### Administrador

Para moderar lâmpadas denunciadas, transforme uma conta existente em admin:

```bash
docker compose exec api python -m app.scripts.make_admin <apelido>
```

Sem Docker, dentro de `backend`: `python -m app.scripts.make_admin <apelido>`.

### Configuração

Os limites (lâmpadas por dia, tempo de espera, lâmpadas por salão, denúncias para ocultar e tamanho do ranking) podem ser mudados no `.env`. Veja o `.env.example`.

As palavras bloqueadas ficam em `backend/app/core/bad_words.txt`, uma por linha.

---

## Testes

Os testes usam um banco separado (`democrapsulas_test`), criado automaticamente no mesmo PostgreSQL, então não apagam nada do banco de desenvolvimento.

Com o banco rodando, dentro de `backend`:

```bash
pip install -r requirements-dev.txt
pytest
```

O projeto tem **41 testes** cobrindo contas, criação e abertura de lâmpadas, votos, favoritos, denúncias, roleta, ranking, dados do site, salões, músicas, moderação e filtro de palavras.

Alguns cenários de segurança cobertos:

* conteúdo escondido antes da data de abertura;
* lâmpadas privadas visíveis só para quem criou;
* lâmpadas ocultas fora das listas públicas;
* rotas de admin bloqueadas para contas comuns.

---

## Andamento

* [x] Estrutura do servidor com FastAPI, PostgreSQL e Docker
* [x] Contas: cadastro, login com token e rota da conta logada
* [x] Migrations do banco com Alembic
* [x] Rotas para criar e abrir lâmpadas
* [x] Votos, favoritos, denúncias, roleta, ranking, dados do site e moderação
* [x] Votação semanal de músicas e relógio do Salão das Estações
* [x] Testes automáticos do servidor
* [x] Estrutura das páginas em HTML e CSS, com modo claro e escuro
* [x] Lâmpadas subindo, cronômetros e criar/abrir lâmpadas
* [x] Contas e roleta ligadas à API
* [ ] Votos, favoritos e denúncias no site
* [ ] Galeria, ranking e dados do site
* [ ] Música e votação semanal no site
* [ ] Visual dos outros salões
* [ ] Testes e ajustes finais

---

## Situação atual

A primeira versão do Democrápsulas já funciona, com:

* Contas com JWT
* Lâmpadas que só abrem na data marcada
* Votos, favoritos, denúncias e moderação
* Roleta, ranking e dados do site
* Votação semanal de músicas
* PostgreSQL com migrations
* Docker
* Testes automáticos
* Tela de entrada, Salão Asiático, Criar Lâmpada e Roleta

### Limitações

* Só o Salão Asiático tem visual pronto; os outros mostram "Em breve".
* Galeria, Ranking, Votação de Músicas e Minha Conta ainda não têm página.
* O site ainda não permite criar lâmpadas privadas, embora a API já aceite.
* As músicas são provisórias e os arquivos de áudio ainda não foram escolhidos.

### Próximos passos

* Páginas de Galeria, Ranking, Votação e Minha Conta
* Votos, favoritos e denúncias nas lâmpadas abertas
* Visual dos salões Medieval, Cyberpunk, Espaço e Estações
* Músicas definitivas
* Testes e ajustes finais

---

## Quem faz

Felipe Barbosa Santos cuida do servidor (API e banco de dados) e também ajuda no front-end: [github.com/felipebsa](https://github.com/felipebsa)

Gabriel Fernandes Barbarini cuida do front-end: [github.com/FeLaLost](https://github.com/FeLaLost)

Trabalho da disciplina de Programação Web, do curso técnico em Desenvolvimento de Sistemas (turma 1C2) da ETEC Vasco Antonio Venchiarutti, em Jundiaí. Professora: Daniela.

## Sites que nos inspiraram

* [neal.fun](https://neal.fun), pela criatividade dos experimentos interativos
* [FutureMe](https://www.futureme.org), onde se escrevem cartas para o futuro
* [Museum of Endangered Sounds](https://savethesounds.info), um painel de sons antigos de tecnologia
* [Radiooooo](https://radiooooo.com), onde se ouve música escolhendo país e década

## Créditos

As músicas, sons e imagens serão criados por nós ou tirados de bancos livres de direitos autorais. Quando forem escolhidos, as fontes ficam listadas aqui.

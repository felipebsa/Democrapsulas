# Democrápsulas · front-end

HTML, CSS e JavaScript puro. Sem build, sem framework.

## Como rodar

1. Sobe o back-end (`docker compose up` na raiz do repositório). Ele fica em `http://localhost:8000`.
2. Abre a pasta `frontend` com o Live Server do VS Code (ou qualquer servidor estático) e acessa o `index.html`.

Todos os dados vêm do back. Se ele estiver desligado, as telas avisam que não conseguiram conectar (não aparece nenhum dado inventado).

Pra apontar pra outra API: `index.html?api=https://minha-api.com`.

## Arquivos

| Arquivo | O que faz |
| --- | --- |
| `index.html` | todas as "páginas" num HTML só (entrada, salão, em breve, modais) |
| `style.css` | cores, layout, animações e responsivo |
| `js/api.js` | `fetch` base com o token e as rotas do back |
| `js/efeitos.js` | lâmpadas fantasma, parallax do fundo, luz do mouse, navbar de vidro |
| `js/interface.js` | tema, som, menus, aviso e modal de entrar/criar conta |
| `js/salao.js` | lâmpadas subindo e o cronômetro de cada uma |
| `js/criar.js` | página Criar Lâmpada (formulário, prévia, envio e erros do back) |
| `js/roleta.js` | roleta que gira e sorteia uma lâmpada aberta |
| `js/app.js` | tela de entrada, contadores e as rotas (`#/salao/asiatico`, `#/roleta`...) |

## Música

O salão pede `GET /halls/{hall}/track` e toca `audio/<arquivo>` da música vencedora. Coloca os MP3 na pasta `audio/` com o mesmo nome que tá no campo `file` do banco.

## Etapa 1 (feito)

- Tela de entrada com contadores animados (`/stats`) e botão Iniciar que destrava o som
- Navbar com dropdown de salões, menu de celular, som e tema salvos no navegador
- Entrar / criar conta (`/auth/login`, `/auth/register`, `/auth/me`)
- Salão Asiático com as lâmpadas subindo, cronômetro real e leitura das que já abriram

## Etapa 2 (feito, fecha o MVP)

- Criar Lâmpada: título, mensagem, tempo livre pra abrir (dias, horas e minutos, sem limite), pública (privada fica "em breve"), prévia com o cronômetro, rascunho salvo, erros do back traduzidos (limite por dia, espera de 2 min, palavrão). Se não estiver logado, abre o login e solta a lâmpada logo depois.
- Roleta: faixa de lanternas que gira, freia numa delas e mostra a mensagem (`/capsules/random`)
- Galeria, Ranking, Votação, Minha Conta e os outros salões mostram "Em breve"

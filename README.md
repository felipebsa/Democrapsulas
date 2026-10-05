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

O servidor deve ser uma API em Python com FastAPI e banco PostgreSQL, com autenticação por token. Isso ainda precisa ser confirmado conforme o desenvolvimento avançar. O código fica no GitHub, versionado com Git.

## Andamento

- [ ] Combinar o contrato da API e definir o visual dos salões
- [ ] Montar a estrutura das páginas em HTML e CSS, com modo claro e escuro
- [ ] Lâmpadas subindo, cronômetros e criar/abrir lâmpadas, usando dados de exemplo
- [ ] Ligar o site à API: contas, votos, favoritos e denúncias
- [ ] Roleta, galeria, ranking e dados do site
- [ ] Música e votação semanal
- [ ] Testes e ajustes finais

## Como rodar

Ainda não tem versão para rodar. Quando tiver, as instruções entram aqui.

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

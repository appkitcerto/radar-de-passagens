# Radar de Passagens

Site para achar passagens aéreas baratas, reunindo o que os criadores de conteúdo brasileiros publicam.

- **Promoções de hoje:** títulos e links das ofertas mais recentes dos feeds RSS de Melhores Destinos, Passagens Imperdíveis, Pontos pra Voar, Passageiro de Primeira e Cartões e Viagens. Atualizado a cada 3 horas por uma GitHub Action (`.github/workflows/promocoes.yml`).
- **Busca flexível:** monta buscas prontas no Google Flights, Skyscanner e Kayak, com dicas para a data escolhida.
- **Onde saem as promoções:** canais de alerta de cada site (Telegram, WhatsApp, app, newsletter).
- **Minhas rotas:** rotas e preço-alvo, salvos no navegador. Ofertas que batem com elas ficam marcadas.
- **Dicas dos especialistas:** dicas resumidas, cada uma com link para a fonte.

## Conteúdo de terceiros

O site guarda só o título, o link e a data de cada oferta, com o nome do site que a publicou. Nenhum texto das matérias é copiado: para ler a oferta, a pessoa abre o link no site original. Se algum site pedir para sair da lista, basta remover a entrada em `scripts/fetch_feeds.py`.

## Como rodar

```bash
python scripts/fetch_feeds.py promocoes.json   # baixa as promoções
python -m http.server                          # abre em http://localhost:8000
```

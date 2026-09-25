# booker

Aplicativo desktop em Python/Tkinter para leitura de arquivos PDF, com anotações,
pesquisa de conteúdo e acompanhamento do progresso de leitura.

## Arquitetura

O projeto segue uma separação em camadas:

```
presentation/   → telas Tkinter (biblioteca, leitor) e composição da UI
application/    → casos de uso/serviços (importar livro, ler, anotar)
domain/         → entidades, exceções e contratos de repositório
infrastructure/ → SQLite (persistência) e PyMuPDF (renderização/busca em PDF)
```

## Funcionalidades

- Importar arquivos PDF, EPUB e TXT para uma biblioteca pessoal (armazenada em SQLite).
- Ler livros página a página, com navegação e rolagem.
- Adicionar, listar e remover anotações por página.
- Pesquisar texto dentro do PDF e navegar até a página do resultado.
- Progresso de leitura salvo automaticamente por livro.

## Como executar

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Testes

```powershell
.venv\Scripts\pip install pytest
.venv\Scripts\python -m pytest
```

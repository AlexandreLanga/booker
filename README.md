# Booker

Booker é um aplicativo desktop de biblioteca e leitura, desenvolvido em Python com Tkinter. Ele organiza livros locais, permite ler PDF, EPUB e TXT, registrar o progresso, fazer anotações e pesquisar texto.

## Funcionalidades

- Importação de arquivos PDF, EPUB e TXT.
- Biblioteca com busca por título, autor, categoria e tags; filtros por status e favoritos; ordenação por data de inclusão, título, autor, categoria ou progresso.
- Edição do título, autor, categoria, status e favorito de cada livro.
- Leitura página a página, navegação por botões ou número de página, rolagem, zoom e tela cheia.
- Pesquisa no documento com resultados que levam diretamente à página correspondente.
- Anotações textuais associadas a páginas, com opção de listar e remover.
- Traços de marcador semitransparentes desenhados sobre a página, que podem ser limpos e são persistidos por página.
- Progresso de leitura salvo ao navegar entre paginas e restaurado ao reabrir o livro.

## Formatos e pesquisa

- **PDF:** paginas renderizadas com PyMuPDF. A pesquisa usa o texto embutido no arquivo; para documentos digitalizados ou com texto ilegivel, pode recorrer a OCR quando o Tesseract esta instalado e configurado.
- **EPUB:** o texto é extraído dos arquivos HTML/XHTML internos e apresentado em páginas geradas pelo aplicativo. A formatação original e a paginação do EPUB não são preservadas.
- **TXT:** arquivos UTF-8 são convertidos em páginas para leitura. A formatação é simples, e a divisão de páginas é automática.

EPUB e TXT são adaptados para a experiência de leitura paginada do Booker; não são renderizados como no aplicativo ou dispositivo original. A pesquisa por OCR é opcional. Sem Tesseract e os dados de idioma apropriados, PDFs cuja camada de texto não pode ser lida podem não retornar resultados de pesquisa.

## Requisitos

- Python 3.10 ou superior (o código usa anotações de tipo introduzidas no Python 3.10).
- Tkinter, incluido na maioria das instalacoes oficiais de Python para Windows e macOS. Em Linux, instale o pacote Tkinter da distribuicao se ele nao estiver disponivel.
- Dependencia de execucao: PyMuPDF, instalada por `requirements.txt`.
- Opcional: Tesseract OCR com dados de idioma portugues (`por`) e/ou ingles (`eng`) para pesquisa em paginas digitalizadas ou com texto corrompido.

## Instalacao e execucao

Na raiz do repositorio, crie o ambiente virtual e instale as dependencias:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

No PowerShell do Windows, inicie o aplicativo com:

```powershell
.venv\Scripts\python main.py
```

No macOS ou Linux, use o executavel do ambiente virtual correspondente:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Na primeira execução, o Booker cria automaticamente o banco de dados e suas tabelas.

## Uso

1. Selecione **Importar PDF** na biblioteca e escolha um arquivo PDF, EPUB ou TXT.
2. Para editar os metadados disponíveis, selecione o livro e use **Editar**. Abra o livro com um duplo clique.
3. No leitor, navegue pelas setas ou informe o número da página. Use a caixa de pesquisa para localizar texto; abra um resultado com duplo clique.
4. Na aba **Anotações**, adicione ou remova anotações. Em **Ferramentas**, ative **Marcar** para desenhar sobre a página ou use **Limpar** para apagar os traços daquela página.
5. Volte à biblioteca pelo botão **Biblioteca**. O progresso e as anotações ficam associados ao livro.

Controles adicionais do leitor: roda do mouse para rolar verticalmente, `Shift` + roda para rolar horizontalmente, `Ctrl` + roda para ajustar o zoom, `F11` para alternar tela cheia e `Esc` para sair dela. O zoom tambem pode ser alterado pelos botoes `+` e `-`; um duplo clique no percentual restaura o zoom.

## Dados e arquivos

- Banco SQLite: `~/.booker/booker.db` (no Windows, normalmente `%USERPROFILE%\\.booker\\booker.db`). O diretório é criado automaticamente.
- Os arquivos de livros não são copiados para a biblioteca: o banco guarda o caminho local de cada arquivo. Mover ou excluir o arquivo original pode impedir sua abertura.
- Remover um livro da biblioteca apaga também seus registros relacionados no banco, mas não apaga o arquivo original.
- Para fazer backup dos dados do Booker, feche o aplicativo e copie o banco SQLite. Inclua separadamente os arquivos originais dos livros.

## Estrutura do projeto

```text
main.py                         Inicializacao, composicao das dependencias e janela
application/
	dto.py                        Dados de apresentacao usados entre camadas
	services/                     Casos de uso de biblioteca, leitura e anotações
domain/
	entities.py                    Entidades de livro, progresso, anotação e marcador
	exceptions.py                  Excecoes do dominio
	repositories.py                Contratos de persistencia
	value_objects.py               Tipos de valor, como resultados de pesquisa
infrastructure/
	database.py                    Schema e inicializacao/migracao SQLite
	pdf/pymupdf_document.py         Abertura, renderização e pesquisa nos documentos
	repositories/                   Implementacoes SQLite dos repositorios
presentation/
	app.py                          Navegacao e ligacao entre servicos e telas
	theme.py                        Estilos Tkinter
	screens/                        Telas da biblioteca e do leitor
tests/                            Testes automatizados
assets/                           Recursos visuais do aplicativo
```

A aplicação separa a interface, os casos de uso, as regras/modelos de domínio e os adaptadores externos. A inicialização em `main.py` conecta os serviços aos repositórios SQLite e ao adaptador de documentos.

## Testes

Instale pytest no ambiente virtual e execute a suíte a partir da raiz do repositório:

```powershell
.venv\Scripts\python -m pip install pytest
.venv\Scripts\python -m pytest
```

No macOS ou Linux:

```bash
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

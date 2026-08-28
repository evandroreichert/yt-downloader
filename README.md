# Ferramentas de Mídia

CLI para Windows que baixa vídeos/áudios do YouTube e transcreve arquivos com Faster Whisper.

## Instalação rápida em outro PC

Requer Windows 10 ou 11 com acesso ao `winget` (App Installer da Microsoft Store).

```powershell
git clone https://github.com/evandroreichert/yt-downloader.git
cd yt-downloader
.\instalar.bat
```

Também é possível baixar o ZIP privado pelo GitHub, extrair e abrir `instalar.bat` com duplo clique.

O instalador:

- verifica Python 3.11+, FFmpeg, FFprobe, Node.js 22+ e Git;
- oferece instalar o que estiver ausente pelo `winget`;
- cria um ambiente Python isolado em `.venv`;
- instala todas as dependências;
- cria `config.json` sem substituir configurações existentes;
- executa um diagnóstico final.

O instalador não instala nem altera drivers NVIDIA, CUDA ou cuDNN.

## Como usar

Abra `iniciar.bat` com duplo clique ou execute:

```powershell
.\iniciar.bat
```

O menu oferece:

```text
1 - Baixar vídeo ou áudio do YouTube
2 - Transcrever arquivo de áudio ou vídeo
3 - Baixar do YouTube e transcrever
0 - Sair
```

### Downloads

Escolha MP4 ou MP3. Cada vídeo recebe uma pasta própria:

```text
downloads/
  Título do vídeo [id]/
    Título do vídeo [id].mp3
    Título do vídeo [id].txt
    Título do vídeo [id].srt
```

A opção 3 baixa o áudio, mantém o MP3 e gera a transcrição automaticamente.

### Transcrição

Cole o caminho de um áudio ou vídeo. Caminhos copiados com aspas são aceitos. Na primeira execução, o modelo Whisper será baixado e poderá levar alguns minutos.

A ferramenta usa GPU NVIDIA quando o CTranslate2 consegue acessá-la. Caso contrário, usa CPU automaticamente. CPU funciona sem CUDA, mas é mais lenta.

## Configuração

Edite `config.json` para personalizar:

```json
{
  "language": "pt",
  "model": "turbo",
  "batch_size": 4,
  "timestamps": true,
  "transcript_formats": ["txt", "srt"],
  "keep_downloaded_audio": true,
  "technical_logs": true
}
```

Modelos aceitos: `tiny`, `base`, `small`, `medium`, `large-v3` e `turbo`. Formatos de transcrição: `txt` e `srt`.

## Atualização

Abra `atualizar.bat`. Ele:

- usa `git pull --ff-only` somente se não houver mudanças locais rastreadas;
- atualiza o `yt-dlp` e as dependências dentro da `.venv`;
- preserva downloads e `config.json`;
- executa o diagnóstico.

Isso é especialmente importante porque o YouTube muda com frequência e versões antigas do `yt-dlp` podem parar de funcionar.

## Diagnóstico

Abra `diagnostico.bat` para conferir versões, imports, FFmpeg, Node, integridade dos pacotes e disponibilidade CUDA.

Logs técnicos ficam em `logs/media-tools.log` quando `technical_logs` está ativo.

## Solução de problemas

### Ambiente virtual não encontrado

Execute `instalar.bat` novamente. O processo é idempotente e preserva seus arquivos.

### YouTube pede para recarregar a página

Execute `atualizar.bat`. A ferramenta também tenta novamente uma vez automaticamente e usa Node.js para os desafios JavaScript atuais.

### GPU indisponível

Isso não impede o uso: a transcrição continua pela CPU. Para GPU, instale fora deste projeto drivers NVIDIA e bibliotecas CUDA 12/cuBLAS/cuDNN 9 compatíveis.

### Configuração inválida

Compare `config.json` com `config.example.json`. A mensagem de erro informa o campo incorreto.

## Desenvolvimento e testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install.ps1 -CheckOnly
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\diagnose.ps1 -CheckOnly
```

Baixe somente conteúdo que seja seu, esteja em domínio público ou para o qual você tenha autorização.

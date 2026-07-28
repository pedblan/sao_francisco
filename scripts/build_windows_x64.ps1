param(
    [string]$PythonBin = "python"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $IsWindows) {
    throw "Este build precisa ser executado no Windows."
}
if (-not [Environment]::Is64BitOperatingSystem) {
    throw "Este build precisa de um Windows x64."
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$TemporaryRoot = Join-Path ([IO.Path]::GetTempPath()) (
    "sao-francisco-windows-" + [Guid]::NewGuid().ToString("N")
)
$BuildVenv = if ($env:BUILD_VENV) {
    $env:BUILD_VENV
} else {
    Join-Path ([IO.Path]::GetTempPath()) "sao-francisco-windows-x64-venv"
}
$BuildDist = Join-Path $TemporaryRoot "dist"
$BuildWork = Join-Path $TemporaryRoot "work"
$DownloadRoot = Join-Path $TemporaryRoot "downloads"
$VerifyRoot = Join-Path $TemporaryRoot "verify"

try {
    New-Item -ItemType Directory -Force -Path $TemporaryRoot, $DownloadRoot | Out-Null
    if (-not (Test-Path (Join-Path $BuildVenv "Scripts\python.exe"))) {
        & $PythonBin -m venv $BuildVenv
        if ($LASTEXITCODE -ne 0) {
            throw "Não foi possível preparar o ambiente de build."
        }
    }
    $BuildPython = Join-Path $BuildVenv "Scripts\python.exe"
    & $BuildPython -m pip install --upgrade pip
    & $BuildPython -m pip install -r requirements.txt "pillow>=11,<13" "pyinstaller>=6.14,<7"
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível instalar as dependências do build."
    }

    & $BuildPython -m PyInstaller `
        --noconfirm `
        --clean `
        --distpath $BuildDist `
        --workpath $BuildWork `
        packaging/sao_francisco_windows.spec
    if ($LASTEXITCODE -ne 0) {
        throw "O empacotamento do aplicativo falhou."
    }

    $BuiltApp = Join-Path $BuildDist "São Francisco"
    $BuiltExe = Join-Path $BuiltApp "São Francisco.exe"
    if (-not (Test-Path $BuiltExe)) {
        throw "O executável do São Francisco não foi criado."
    }

    $FfmpegArchive = Join-Path $DownloadRoot "ffmpeg.zip"
    $FfmpegRoot = Join-Path $DownloadRoot "ffmpeg"
    Invoke-WebRequest `
        -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl-shared.zip" `
        -OutFile $FfmpegArchive
    Expand-Archive -Path $FfmpegArchive -DestinationPath $FfmpegRoot
    $FfmpegExe = Get-ChildItem $FfmpegRoot -Filter "ffmpeg.exe" -Recurse |
        Select-Object -First 1
    $FfprobeExe = Get-ChildItem $FfmpegRoot -Filter "ffprobe.exe" -Recurse |
        Select-Object -First 1
    if (-not $FfmpegExe -or -not $FfprobeExe) {
        throw "O pacote LGPL do FFmpeg não contém os executáveis esperados."
    }
    Copy-Item -Path (Join-Path $FfmpegExe.Directory.FullName "*") `
        -Destination $BuiltApp -Recurse -Force

    $DenoArchive = Join-Path $DownloadRoot "deno.zip"
    $DenoRoot = Join-Path $DownloadRoot "deno"
    Invoke-WebRequest `
        -Uri "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip" `
        -OutFile $DenoArchive
    Expand-Archive -Path $DenoArchive -DestinationPath $DenoRoot
    Copy-Item (Join-Path $DenoRoot "deno.exe") $BuiltApp -Force

    $ThirdPartyRoot = Join-Path $BuiltApp "licenças de terceiros"
    New-Item -ItemType Directory -Force -Path $ThirdPartyRoot | Out-Null
    $FfmpegLicense = Get-ChildItem $FfmpegRoot -File -Recurse |
        Where-Object { $_.Name -match "^LICENSE" } |
        Select-Object -First 1
    if ($FfmpegLicense) {
        Copy-Item $FfmpegLicense.FullName (
            Join-Path $ThirdPartyRoot "FFmpeg-LICENSE.txt"
        )
    }
    Invoke-WebRequest `
        -Uri "https://raw.githubusercontent.com/denoland/deno/main/LICENSE.md" `
        -OutFile (Join-Path $ThirdPartyRoot "Deno-LICENSE.md")

    $Readme = @"
SÃO FRANCISCO 0.1.1 — WINDOWS

1. Extraia todo o conteúdo deste ZIP para uma pasta.
2. Abra "São Francisco.exe".
3. Se o Windows proteger a primeira abertura, escolha "Mais informações" e
   depois "Executar assim mesmo".
4. No aplicativo, abra Configurações e cadastre a chave do serviço que deseja usar.

Não mova apenas o executável: os demais arquivos da pasta também são necessários.
A Ajuda do aplicativo explica como obter uma chave e como começar.
"@
    Set-Content -Path (Join-Path $BuiltApp "LEIA-ME.txt") `
        -Value $Readme -Encoding UTF8

    $env:QT_QPA_PLATFORM = "offscreen"
    $env:QT_QUICK_BACKEND = "software"
    & $BuiltExe --smoke-test
    if ($LASTEXITCODE -ne 0) {
        throw "O teste de abertura do aplicativo falhou."
    }
    & $BuiltExe --yt-dlp --version
    if ($LASTEXITCODE -ne 0) {
        throw "O componente para vídeos da internet não respondeu."
    }
    & (Join-Path $BuiltApp "ffmpeg.exe") -version | Select-Object -First 1
    & (Join-Path $BuiltApp "ffprobe.exe") -version | Select-Object -First 1
    & (Join-Path $BuiltApp "deno.exe") --version | Select-Object -First 1

    $Version = & $BuildPython -c (
        "from sao_francisco import __version__; print(__version__)"
    )
    $ZipPath = Join-Path $ProjectRoot (
        "dist\Sao-Francisco-$Version-windows-x64.zip"
    )
    New-Item -ItemType Directory -Force -Path (Split-Path $ZipPath) | Out-Null
    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath -Force
    }
    Compress-Archive -Path $BuiltApp -DestinationPath $ZipPath -CompressionLevel Optimal

    Expand-Archive -Path $ZipPath -DestinationPath $VerifyRoot
    $VerifiedApp = Join-Path $VerifyRoot "São Francisco"
    $VerifiedExe = Join-Path $VerifiedApp "São Francisco.exe"
    & $VerifiedExe --smoke-test
    if ($LASTEXITCODE -ne 0) {
        throw "O aplicativo extraído do ZIP não abriu corretamente."
    }
    & (Join-Path $VerifiedApp "ffmpeg.exe") -version | Select-Object -First 1
    & (Join-Path $VerifiedApp "deno.exe") --version | Select-Object -First 1

    Write-Host ""
    Write-Host "Build Windows x64 concluído:"
    Write-Host "  ZIP: $ZipPath"
} finally {
    if ($env:KEEP_BUILD_TEMP -eq "1") {
        Write-Host "Diretório temporário preservado em: $TemporaryRoot"
    } elseif (Test-Path $TemporaryRoot) {
        Remove-Item $TemporaryRoot -Recurse -Force
    }
}

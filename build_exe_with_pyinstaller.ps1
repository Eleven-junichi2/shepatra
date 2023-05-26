# -build exe-
pyinstaller shepatra_cli.spec
# --

# -copy config and i18n files-
Copy-Item -Path "./src/config.json" -Destination "./dist/config.json"
Copy-Item -Path "./readme.md" -Destination "./dist/readme.md"
Copy-Item -Path "./readme.jp.md" -Destination "./dist/readme.jp.md"
Copy-Item -Path "./src/i18n" -Destination "./dist/" -Recurse -Force
# --
Write-Information "Copied data files (readme, i18n, config etc) to dist dir"


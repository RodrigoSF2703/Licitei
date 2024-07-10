$exclude = @("venv", "liciteiCompras.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "liciteiCompras.zip" -Force
name: Final Minecraft Server

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  server:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install deps
        run: sudo apt update && sudo apt install -y p7zip-full screen

      - name: Restore backup
        run: |
          gh release download latest --pattern "*.7z.part*" || true
          if ls *.7z.part* 1> /dev/null 2>&1; then
            7z x server_backup.7z.part*
          fi

      - name: Run server
        run: |
          screen -dmS mc java {{JVM}} -jar {{SERVER_JAR}} nogui
          sleep infinity

      - name: Stop & backup
        if: always()
        run: |
          screen -S mc -X stuff "stop$(printf \\r)" || true
          sleep 15
          rm -f server_backup.7z*
          7z a server_backup.7z server/*
          7z a server_backup.7z.part server_backup.7z -v95m
          gh release delete latest --yes || true
          gh release create latest server_backup.7z.part*

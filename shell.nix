{ pkgs ? import <nixpkgs> { }
,
}:

let
  python = pkgs.python314;

  pythonEnv = python.withPackages (
    ps: with ps; [
      fastapi
      uvicorn
      httpx
      beautifulsoup4
      playwright
      pydantic
      pydantic-settings
      sqlalchemy
      asyncpg
      alembic
    ]
  );
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.chromium # <-- Системный Chromium, который точно запустится в Nix

    # Зависимости для надежности (Chromium их и так тянет, но пусть будут)
    pkgs.glib
    pkgs.gtk3
    pkgs.nss
    pkgs.freetype
    pkgs.fontconfig
  ];

  shellHook = ''
    echo "⚡ Среда разработки активирована! ⚡"

    # Указываем Playwright использовать бинарник из Nix
    export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH="${pkgs.chromium}/bin/chromium"

    # Запрещаем Playwright пытаться скачать свои сломанные бинарники
    export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

    echo "🎯 Playwright настроен на системный Chromium:"
    echo "   $PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"
  '';
}

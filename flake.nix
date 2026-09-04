{
  description = "Development environment for Admission Data API";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      pythonEnv = pkgs.python314.withPackages (ps: with ps; [
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
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          pythonEnv
          pkgs.ruff
        ];
      };
    };
}


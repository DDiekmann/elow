{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
  };

  outputs = { self , nixpkgs ,... }: let
    system = "x86_64-linux";
  in {
    devShells."${system}".default = let
      pkgs = import nixpkgs {
        inherit system;
      };
    in pkgs.mkShell {
      packages = with pkgs; [
        (pkgs.python3.withPackages (python-pkgs: [
          python-pkgs.pip
          python-pkgs.virtualenv
        ]))
      ];

      shellHook = ''
        python3 --version
        virtualenv venv
        source venv/bin/activate
        which python3
        pip install -r requirements.txt
      '';
    };
  };
}
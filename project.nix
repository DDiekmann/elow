{ config, modulesPath, nix2container, pkgs, ... }:

{
  require = [
    "${modulesPath}/languages/python-poetry.nix"
    "${modulesPath}/builders/docker-nix2container.nix"
    "${modulesPath}/tools/mod-lean-python.nix"
  ];

  name = "elow"; # Replace with your project name
  src = ./.; # Replace with your project's source directory

  # files to exclude (there often are files that you need to have in git, but
  # you don't want nix to rebuild your app if they change)
  # simpliarly to .gitignore you can also exclude everything and implicitly
  # list files you want included
  src_exclude = [''
    
  ''];

  python = {
    enable = true;
    package = config.python311;
    inject_app_env = true;
    prefer_wheels = false;
  };

  docker = {
    enable = true;
    command = [ "${config.out_python}/bin/hello" ]; # Replace with your project's entrypoint
    layers = with nix2container; [
      (buildLayer { deps = [ config.out_python ]; })
    ];
  };

  dev_commands = with pkgs; [
    dive
  ];
}

{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/22.11";
  };

  outputs = inputs: with inputs; let
    system = "x86_64-linux";  # TODO    Use flake utils later
    pkgs = import nixpkgs { inherit system; };
    lib = pkgs.lib;

    python_version = pkgs.python310;
    python_packages_version = pkgs.python310Packages;
    pythonpkg = python_version.withPackages (p: with p; [
      playsound
    ]);

    set_python_env = ''
      export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib$LD_LIBRARY_PATH
      export PYTHONPATH="${pythonpkg.sitePackages}:$PYTHONPATH"
      unset SOURCE_DATE_EPOCH
    '';

    script_start = pkgs: ''
      ${set_python_env}
    '' + (if (builtins.length pkgs == 0) then "" else ''
      export PATH="$PATH:${builtins.concatStringsSep ":" (builtins.map (p: "${p}/bin/") pkgs)}"
    '');

    start = pkgs.writeShellScript "start" ''
      ${script_start []}
      ${pythonpkg}/bin/python ./gnuvolca.py -d ./samples
    '';

  in {
    apps.default = {
      type = "app";
      program = "${start}";
    };

    devShells.${system}.default = pkgs.mkShell {
      shellHook = set_python_env;
    };
  };
}

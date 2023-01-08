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
      pygobject3
      simpleaudio
    ]);

    start = args: let
      script = pkgs.writeShellScript "start" ''
        export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib$LD_LIBRARY_PATH
        export PYTHONPATH="${pythonpkg.sitePackages}:$PYTHONPATH"
        unset SOURCE_DATE_EPOCH
        ${pkgs.patchelf}/bin/patchelf --set-interpreter ${pkgs.glibc}/lib/ld-linux-x86-64.so.2 ./bin/*
        set -x
        ${pythonpkg}/bin/python ./gnuvolca.py ${args}
      '';
    in {
      type = "app";
      program = "${script}";
    };

  in {
    apps.${system} = rec {
      default = upload_dir;
      upload_dir = start "--upload-set ./sets $@";
      clear = start "--clear";
      upload = start "--sample $1 --bank-nb $2";
      format = start "--format ./sets";
    };

    devShells.${system}.default = pkgs.mkShell {
      shellHook = set_python_env;
    };
  };
}

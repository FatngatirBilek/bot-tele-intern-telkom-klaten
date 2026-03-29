{
  description = "Telegram Ticket Bot Flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [
        (python3.withPackages (ps:
          with ps; [
            python-telegram-bot
            gspread
            google-auth-oauthlib
            google-auth-httplib2
            python-dotenv
          ]))
      ];

      shellHook = ''
        echo "Bot Ticket Environment Ready, dawgg 🥀🥀 "

        if [ ! -f .env ]; then
          echo "⚠️  Woy, file .env belum ada! Bikin dulu gih."
        fi
        exec zsh
      '';
    };
  };
}

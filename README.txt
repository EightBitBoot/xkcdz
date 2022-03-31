Discord Bot
-----------
   Requires python >= 3.7

   Setup
   -----
   1) Create a virtual environment for the bot in the project root directory (eg. "python -m venv venv")
   2) Install the requirements in requirements.txt
   4) Run create_library_links.sh.  This links the libraries in lib/ to venv's site packages directory (this is hacky
      and will be changed in the future)
   4) Create a file in discord_bot/ called secrets.hjson containing two keys: "bot_key" and "bot_name" with
      the corresponding values.  Bot name is just used in the identify payload sent to Discord. 

   Reference
   ---------
   https://hjson.github.io/

A better readme is coming in the future
# Init and run the project

Run the backend with backend/.env file

Run with python3.12 (you may use pyenv).
```
cd backend 
python --version
# should return 3.12
$(pyenv which python) -m venv .venv
source .venv/bin/activate
python --version
# should be 3.12 again
pip3 install -r requirements.txt
./dev.sh
```


Run the FE in new tab
```
npm run dev:5050
```

# Setup openwebui to connect with local Litellm
- enable login with user name to login with admin account

# Test your function in console.
For example, I wrote `get_user_subscriptions` under `moneta.utils.lago` and I want to test it on console mode.

```bash
# load .env file into env
python -m dotenv run python

from open_webui.moneta.utils.lago import get_user_subscriptions
get_user_subscriptions(params)
```

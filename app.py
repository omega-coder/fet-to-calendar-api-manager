import os
from fet_api_to_gcal import app

# set envionment variables (resolves HTTPS issue for OAuth)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

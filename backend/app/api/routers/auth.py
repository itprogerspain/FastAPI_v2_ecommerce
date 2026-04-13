# TODO: Implement OAuth2 social login (Google, GitHub, etc.) using SessionMiddleware.
#       Flow: GET /auth/{provider} → redirect to provider with state stored in request.session["oauth_state"].
#             GET /auth/{provider}/callback → verify state from session, exchange code for token,
#             create or retrieve user, issue JWT. Clear session["oauth_state"] after use.
#       Recommended library: authlib (pip install authlib httpx)

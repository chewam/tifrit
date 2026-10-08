// Connexion GitHub pour l'interface d'édition (/admin/). Étape 1 : renvoi vers GitHub.
// Variables d'environnement Vercel à définir : OAUTH_GITHUB_CLIENT_ID, OAUTH_GITHUB_CLIENT_SECRET
export default function handler(req, res) {
  const id = process.env.OAUTH_GITHUB_CLIENT_ID;
  if (!id) return res.status(500).send("OAUTH_GITHUB_CLIENT_ID manquant");
  const host = req.headers["x-forwarded-host"] || req.headers.host;
  const redirect = `https://${host}/api/callback`;
  const url = `https://github.com/login/oauth/authorize?client_id=${id}&scope=repo,user&redirect_uri=${encodeURIComponent(redirect)}`;
  res.writeHead(302, { Location: url });
  res.end();
}

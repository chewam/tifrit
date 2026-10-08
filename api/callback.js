// Connexion GitHub pour l'interface d'édition (/admin/). Étape 2 : échange du code contre un jeton, remis à Decap CMS.
export default async function handler(req, res) {
  const code = req.query.code;
  const r = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ client_id: process.env.OAUTH_GITHUB_CLIENT_ID, client_secret: process.env.OAUTH_GITHUB_CLIENT_SECRET, code }),
  });
  const data = await r.json();
  const ok = Boolean(data.access_token);
  const payload = ok ? { token: data.access_token, provider: "github" } : { error: data.error_description || "échec" };
  const html = `<!doctype html><html><body><script>
(function(){
  function send(){ window.opener.postMessage('authorization:github:${ok ? "success" : "error"}:' + JSON.stringify(${JSON.stringify(payload)}), '*'); }
  window.addEventListener('message', function(e){ if (/^authorizing:github/.test(e.data)) send(); });
  window.opener.postMessage('authorizing:github', '*');
})();
</script><p>Connexion ${ok ? "réussie, vous pouvez fermer cette fenêtre." : "refusée."}</p></body></html>`;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(html);
}

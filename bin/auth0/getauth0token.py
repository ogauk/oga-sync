import http.client

conn = http.client.HTTPSConnection("dev-uf87e942.eu.auth0.com")

payload = "{\"client_id\":\"kEL615CW1BS6bZIDGN1FtjZMBqzZ447K\",\"client_secret\":\"QF_JSw__M_jEZFMEWMTtXvhWsXD83fHFP5oQyi1ESofRhDz8Wp-3Ido50CPcPJSm\",\"audience\":\"https://dev-uf87e942.eu.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

headers = { 'content-type': "application/json" }

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

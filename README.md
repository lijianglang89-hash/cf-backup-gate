# Cloudflare backup gate

This repository periodically checks public VPN Gate SSTP endpoints with the
configured Cloudflare Worker and publishes the generated lists through GitHub
Pages.

The workflow requires these repository secrets:

- `CHECK_WORKER`
- `EDT_UUID`
- `EDT_DOMAIN`
- `EDGE_HOSTS`

Upstream components:

- `cmliu/edgetunnel`
- `lsh8848/cm-Workers-CheckSocks5`
- `hezhanleiok/gate`

The generated `hosts.txt` and `sub.txt` files contain connection credentials
and must be treated as private node configuration even though the repository is
public.

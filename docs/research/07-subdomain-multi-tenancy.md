# Subdomain Multi-Tenancy

## Overview

Subdomain multi-tenancy gives each tenant (school, classroom, teacher, student) their own subdomain (e.g., `school.cocapn.com`, `class101.school.cocapn.com`). Cloudflare Workers for Platforms provides the infrastructure to serve custom hostnames from a single application with per-tenant isolation.

## Cloudflare Workers for Platforms

### Core Concepts
- **Custom Hostnames**: Route arbitrary hostnames/subdomains to your Workers
- **Hostnames API**: Programmatically add/remove hostnames per tenant
- **TLS Certificates**: Automatic TLS provisioning for each hostname (free, via Cloudflare)
- **Per-request routing**: Single Worker handles all tenants, routes based on hostname
- **Worker Bindings**: Durable Objects, KV, R2, D1 (SQLite) — all can be tenant-scoped

### Architecture
```
school-a.cocapn.com ──┐
school-b.cocapn.com ──┤──→ Cloudflare Edge ──→ Worker (routes by hostname)
class1.school-a.com ──┘                        ├──→ Durable Object (tenant session)
                                               ├──→ D1 Database (tenant data)
                                               ├──→ KV (tenant config)
                                               └──→ R2 (tenant files)
```

One application, many tenants. No separate deployments per tenant.

## Per-Tenant Isolation

### Data Isolation
- **D1 (SQLite)**: One database per tenant, or one database with tenant_id column + RLS
- **KV Namespace**: Separate KV namespace per tenant (strongest isolation)
- **R2 Bucket**: Separate bucket per tenant, or prefix-based isolation within shared bucket
- **Durable Objects**: Namespace per tenant for session management

### Isolation Strategies (Strongest to Weakest)

1. **Separate infrastructure per tier**:
   - Enterprise: Dedicated D1 database, dedicated KV namespace, dedicated DO namespace
   - Standard: Shared database with tenant_id, shared KV with namespaced keys
   - Free: Shared everything, namespace by prefix

2. **Shared database, tenant_id column**:
   - Simplest to implement
   - Use D1 (SQLite) with row-level security or application-level filtering
   - Risk: bugs that leak cross-tenant data (forget WHERE tenant_id = ?)
   - Mitigation: middleware that injects tenant_id into all queries

3. **Namespace-based in KV/R2**:
   - Keys are prefixed: `tenant:{id}:config:grading`
   - Simple, but no database-level enforcement
   - Good for config, cache, and file storage

### Tenant Provisioning Flow
1. Teacher signs up → creates tenant record in central database
2. API call to Cloudflare Hostnames API → adds `school-name.cocapn.com`
3. DNS propagation (seconds with Cloudflare) → subdomain is live
4. Tenant-specific D1 database created (or tenant_id row inserted)
5. KV namespace and R2 bucket provisioned (if using per-tenant isolation)
6. Welcome email with subdomain URL

### Custom Domain Support
- Tenants can bring their own domain (e.g., `cs101.university.edu`)
- Add CNAME to Cloudflare → Worker handles it
- Automatic TLS via Cloudflare
- Same isolation model as subdomains

## Security Considerations

| Risk | Mitigation |
|------|-----------|
| Cross-tenant data leak | Tenant_id middleware, integration tests, query auditing |
| Subdomain takeover | Validate hostname ownership before provisioning |
| Tenant isolation failure | Defense in depth: app-level + database-level + infrastructure-level |
| Rate limit bypass | Per-tenant rate limits, not just per-user |
| Resource exhaustion | Per-tenant resource quotas (storage, API calls, bandwidth) |

## Pricing Implications

- **Workers**: 100K requests/day free, then $0.50/million — very cost-effective
- **D1**: 5M reads/day free, 100K writes/day free — generous for education
- **KV**: 100K reads/day free, 1K writes/day free
- **R2**: 10GB free, no egress fees (major advantage over S3)
- **Custom Hostnames**: 100 free, then $0.10/month each
- **For 1000 schools with 30 students each**: Roughly $50-200/month depending on usage

## Actionable Recommendations for Cocapn

1. **Use Workers for Platforms from the start**: The hostname routing is trivial — just check `request.headers.get('host')` in your Worker. This gives you subdomain multi-tenancy with minimal code.

2. **Shared D1 with tenant_id for MVP**: Start with one D1 database, tenant_id on every row, middleware that enforces it. This is simple and sufficient for hundreds of tenants.

3. **Upgrade to per-tenant isolation for scale**: When you hit 100+ tenants, migrate to per-tenant KV namespaces and consider per-tenant D1 databases for enterprise customers.

4. **Tenant-scoped Durable Objects**: Use a separate DO namespace per tenant for session management. This ensures session data can never leak between tenants.

5. **Provisioning API**: Build an API that handles tenant creation end-to-end:
   ```
   POST /api/tenants
   → Create tenant record in D1
   → Add hostname via Cloudflare API
   → Provision D1/KV/R2 resources
   → Return tenant object with subdomain URL
   ```

6. **Custom domain upsell**: Offer custom domains as a premium feature. Universities love having `cs101.university.edu` instead of `cs101.cocapn.com`. The technical implementation is identical to subdomains.

7. **Tenant-level feature flags**: Store feature flags per tenant in KV. This allows A/B testing across tenants and tiered feature access (free vs paid).

## Anti-Patterns

- Building per-tenant infrastructure manually when Workers for Platforms handles it
- Forgetting tenant_id in even one query (data leak)
- Not testing cross-tenant isolation (write integration tests that verify Tenant A cannot access Tenant B's data)
- Over-provisioning per-tenant resources before you need to (shared database with tenant_id scales to hundreds of tenants easily)
- Ignoring DNS propagation delays in the provisioning UX (show "pending" status)

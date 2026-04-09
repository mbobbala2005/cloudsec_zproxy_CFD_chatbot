# Architecture

BAP has four major areas that commonly show up in product questions:
- Proxy
- Nidz
- Enclave
- Prometheus

## Proxy

Proxy is the main runtime path for user traffic. It includes:
- Auth-Broker
- Envoy
- Envoy Controller
- Guacd or Guacamole-lite

### Auth-Broker

Auth-Broker handles authentication and authorization orchestration. It works with the Federation Gateway for user login and with the Policy Engine for access decisions.
It also relies on node-local application and rules state populated from Syncer and local file watchers. In the browser login flow, callback handling and later cookie or session validation depend on org-specific rule state being present on the serving node.

### Envoy

Envoy is the main request proxy for HTTP and HTTPS traffic in the ZTNA BAP path.

### Envoy Controller

Envoy Controller is the xDS control plane that programs Envoy listeners, clusters, routes, and filter chains for ZTNA proxy deployments.

### Guacd And Guacamole-lite

These components are involved in RDP and SSH access flows, translating traffic into browser-friendly sessions.

## Nidz

Nidz is the monitoring-facing area. Its core components are:
- nidz-frontend
- nidz-backend
- nidz-api

`nidz-api` includes monitoring and test-script context that is often useful when mapping product behavior to system checks.

## Enclave

Enclave is responsible for certificate management and certificate retrieval used during request handling.

## Repository Links

See `docs/repo_links.md` for canonical GitHub repository URLs.

## Component Buckets

BAP services:
- Envoy Controller
- Envoy Proxy
- Auth-Broker
- Syncer Client
- DPT Policy Engine
- PolicyGen

External services:
- SSE Dashboard
- Unified Policy Service
- BRAIN (Kafka)
- NLB
- Federation Gateway
- FROUTER

## High-Level Request Flow

### HTTP And HTTPS User Flow

1. The client starts a request.
2. Traffic reaches the load-balancing layer.
3. The request lands on a proxy instance.
4. Envoy handles the main HTTP and HTTPS proxying.
5. Envoy calls Auth-Broker for authentication and authorization decisions.
6. Enclave provides certificates used in TLS handling.
7. If the traffic is RDP or SSH, Guacd or Guacamole-lite supports protocol translation.

### Policy Configuration Flow

1. An administrator configures policy in the SSE Dashboard.
2. Unified Policy Service processes the policy definition.
3. BRAIN distributes the policy update.
4. Syncer Client receives the update inside the proxy environment.
5. Policy data is stored locally.
6. PolicyGen converts the stored policy into the required format.
7. Auth-Broker and related services consume local rules data and maintain in-memory state derived from it, such as org-specific rule-hash mappings used in session and cookie paths.
8. Policy Engine ingests the policy for enforcement.
9. Auth-Broker uses Policy Engine decisions during authorization.

Per-node sync completeness matters in this path. If local rules data or derived auth-broker state is missing on one node, login or callback behavior can fail on that node even when the broader environment is healthy.

### User Authorization Flow

1. The user requests an application through the browser.
2. Traffic passes through the NLB to Envoy.
3. Envoy checks for the application session cookie.
4. If the cookie is missing, Envoy forwards login handling to Auth-Broker.
5. Auth-Broker redirects the user through Federation Gateway and the identity provider flow.
6. After successful authentication, Auth-Broker evaluates policy and sets the application cookie.
7. On later requests, Envoy validates the cookie through Auth-Broker before forwarding traffic to the target path.

### User Traffic (LEE Workflow)

- LEE (User) initiates access requests through a web browser.
- NLB distributes incoming traffic to the proxy layer.
- Envoy Proxy acts as the primary data plane component for request routing.
- Envoy Controller manages the lifecycle and dynamic configuration of Envoy Proxy instances.
- Envoy queries Auth-Broker to validate user permissions.
- Federation Gateway handles requests that require external identity or service federation.
- FROUTER delivers authorized traffic to the final destination.

## Detailed Reference Flows

These deeper flow diagrams are useful for architecture and RCA agents because they capture the end-to-end request path, cookie handling, federation flow, policy evaluation, and app-connectivity decisions. They are the right reference when a question is more specific than the high-level summary above.

### Life Cycle Of A BAP Request

```mermaid
sequenceDiagram
    participant Client as Browser (Client)
    participant DNS as "DNS Resolver"
    participant FRoute as "Froute53 / Route53"
    participant SNI as "SNI Proxy / L4 LB"
    participant ZProxy as "ZProxy (VPP / Envoy)"
    participant Enclave as "Enclave (cert store)"
    participant AuthBroker as "Auth-Broker"
    participant SLPKI as "SL-PKI"
    participant FedGW as "Fed-GW"
    participant IdP as "Org SAML IdP"
    participant PolicyEngine as "Policy Engine"
    participant AppGW as "AppGW / ACGw"
    participant MTProxy as "MT-Proxy"
    participant Frouter as "Frouter"
    participant AppConnector as "App Connector / ACGw"
    participant IPS as "IPS (optional)"
    participant App as "Private Application"

    %% DNS / anycast / SNI lookup
    Client->>DNS: DNS request for <app-hostname>
    DNS->>FRoute: resolve via anycasted nameserver
    FRoute-->>DNS: return SNI Proxy / L4 LB IP(s)
    DNS-->>Client: return SNI Proxy IP(s)

    %% TCP / TLS towards SNI Proxy -> ZProxy/Envoy
    Client->>SNI: TCP handshake + TLS ClientHello (SNI)
    SNI->>ZProxy: new TCP session, send Proxy-Protocol header + TLS Hello
    ZProxy->>Enclave: request certificate for <app-hostname>
    Enclave-->>ZProxy: provide certificate
    ZProxy-->>Client: complete TLS handshake

    %% Initial HTTP: no cookie -> redirect to Fed-GW via Auth-Broker
    Client->>ZProxy: GET / Host:<app> Cookie:<empty>
    Note right of ZProxy: Envoy sees no app cookie and forwards request + metadata to Auth-Broker
    ZProxy->>AuthBroker: /loginvalidate or /login (request + metadata)
    Note right of AuthBroker: validate cookie if present or build Fed-GW JWT

    AuthBroker->>SLPKI: sign JWT for Fed-GW request
    SLPKI-->>AuthBroker: signed JWT
    AuthBroker-->>Client: 303 Redirect to Fed-GW (Location: .../gw/auth/begin/?v=<JWT>)

    %% Fed-GW -> IdP SAML flow
    Client->>FedGW: Fed-GW receives JWT, validates it, looks up org SAML config
    FedGW-->>Client: redirect to Org SAML IdP with SAML Request
    Client->>IdP: SAML Request (login / MFA if required)
    Note right of IdP: Optional login challenge / MFA
    IdP-->>Client: redirect back to Fed-GW with signed SAML response

    FedGW->>SLPKI: build JWT from SAML fields and sign
    FedGW-->>Client: 303 Redirect back to App (logincallback?X-SIG-Umbrella-SAML=<JWT>)

    %% Second HTTP: login-callback -> AuthBroker -> Policy evaluation
    Client->>ZProxy: second HTTP request (login callback) with Fed-GW JWT
    ZProxy->>AuthBroker: forward JWT
    AuthBroker->>SLPKI: validate Fed-GW JWT
    AuthBroker->>PolicyEngine: authorization request (auth data)
    PolicyEngine-->>AuthBroker: allowed / blocked (+ IPS requirement, session info)

    alt Policy = Allowed
        AuthBroker-->>Client: 303 Redirect to original App URL
        Note right of AuthBroker: Set-Cookie: x-ztna-app-sid = <signed-cookie> (app info, IPS flags, timeouts)
    else Policy = Blocked
        AuthBroker-->>Client: 403 Forbidden (block URI), no cookie
    end

    %% Third HTTP: subsequent request with cookie -> cookie validation -> connect to app
    Client->>ZProxy: third HTTP request to App with x-ztna-app-sid cookie
    ZProxy->>AuthBroker: validate cookie
    Note right of AuthBroker: 1. validate cookie and determine IPS setting
    Note right of AuthBroker: 2. identify connectivity type: App Connector or CNHE
    Note right of AuthBroker: 3. resolve FQDN via DNS if required
    Note right of AuthBroker: 4. generate Proxy-Protocol header based on routing info

    alt App Connector path
        AuthBroker->>AppGW: request AppGW / AppConnector connection details
        AppGW-->>AuthBroker: appGW IP / DC / connector details
        AuthBroker->>ZProxy: provide Proxy-Protocol header + routing
        ZProxy->>MTProxy: forward proxied traffic (includes Proxy-Protocol header)
        MTProxy->>Frouter: encapsulate into GENEVE and send to Frouter
        Frouter->>AppConnector: route to AppConnector / ACGw
        AppConnector->>App: DTLS to application
    else CNHE path
        Note right of AuthBroker: if AppConnector is not available, treat path as CNHE
        AuthBroker->>ZProxy: send Proxy-Protocol header with routing to Frouter / CNHE path
        ZProxy->>MTProxy: forward to MTProxy, then Frouter, then CNHE, then application
    end

    opt Optional IPS inspection
        Frouter->>IPS: send traffic to IPS (inline)
        IPS-->>Frouter: inspected / forwarded traffic
    end

    %% Application response: reverse path
    App-->>AppConnector: application response
    AppConnector->>Frouter: reverse path
    Frouter->>MTProxy: deliver to MT-Proxy
    MTProxy->>ZProxy: deliver back to Envoy
    ZProxy->>SNI: forward back to SNI Proxy
    SNI-->>Client: response to browser
```

### Flow Of A BAP Request With Function Calls

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant NLB
    participant EnvoyController as "Envoy Controller (XDS)"
    participant Envoy as "Envoy Proxy (auth filter)"
    participant AuthBroker as "Auth-Broker"
    participant AppEngine as "ApplicationEngine (app cache / FileWatcher)"
    participant PolicyBroker as "PolicyBroker / Policy Engine (DPT)"
    participant Guacd as "Guacamole-lite (guacd)"
    participant MTProxy as "MT-Proxy"
    participant Frouter as "Frouter"
    participant FedGW as "Federation Gateway (Fed-GW)"
    participant IdP
    participant Server
    participant Brain as "BRAIN (synchroniser)"

    rect rgb(240,240,255)
      Note over Brain,AppEngine: BRAIN (kafka or sync) writes private_resources.<org>.org.gz into AppSyncDir (/opt/brain/sync) and network objects
    end

    Brain->>AppEngine: sync private_resources / network-objects (to /opt/brain/sync)
    Note right of AppEngine: File watcher (synapse) picks changes and converts resources into Applications

    Note over EnvoyController,Envoy: Envoy Controller programs Envoy through XDS
    EnvoyController->>Envoy: XDS config (apps / listeners / filters)

    %% Client requests the App external URL
    Client->>NLB: HTTPS request to App External URL
    NLB->>Envoy: forward request (original client request)
    Envoy->>Envoy: auth filter checks for app cookie (x-ztna-app-sid)
    alt No app cookie (first visit)
        Envoy->>AuthBroker: GET /v1/login (headers: x-envoy-ztna-app-url, client IP, UA, ...)
        Note right of AuthBroker: loginHandler extracts auth context (headers -> AuthContext)
        AuthBroker->>AuthBroker: validate headers, embargo, build callback URL
        AuthBroker->>AuthBroker: makeLoginReqURL() -> fetchSignedJWT()
        AuthBroker-->>Client: HTTP 303 Redirect to FedGW login URL (signed payload)
        Client->>FedGW: redirected to FedGW (login request)
        FedGW->>IdP: redirect to IdP (SAML login)
        IdP->>FedGW: SAML Response (after user authenticates)
        FedGW-->>Client: redirect back to AuthBroker login callback URL (SAML / JWT)
        Client->>AuthBroker: GET /v1/logincallback?... (via browser)
        AuthBroker->>AuthBroker: decode payload / extract identity
        AuthBroker->>AppEngine: lookup app / app config (App FQDN -> app)
        AuthBroker->>PolicyBroker: evaluatePolicy() (policy engine + reasoner)
        alt Policy allows access
            AuthBroker->>AuthBroker: set app cookie (x-ztna-app-sid) on app domain
            AuthBroker-->>Client: redirect back to App External URL (on app domain)
        else Policy denies access
            AuthBroker-->>Client: serve block / error page
        end
    else App cookie present
        Envoy->>AuthBroker: GET /v1/loginvalidate (cookie present)
        AuthBroker->>AuthBroker: validate cookie, evaluate policy / expiry
        alt cookie OK
            AuthBroker-->>Envoy: 200 OK (auth OK)
        else cookie invalid
            AuthBroker-->>Envoy: 401 or redirect to /v1/login
        end
    end

    %% After cookie validated, Envoy forwards to app internal
    Envoy->>Envoy: internal routing (app match)
    Envoy->>Server: request forwarded to App Internal URL
    Server-->>Envoy: server response
    Envoy-->>Client: return server response

    %% RDP/SSH special flow (guacd + MT proxy)
    alt Private resource is RDP/SSH
        AuthBroker->>AuthBroker: generate Proxy-Protocol, call GetTokenForRDP / GetTokenSSH
        Note right of AuthBroker: rdpssh constructs token (expiry + Proxy-Protocol)
        AuthBroker->>Guacd: supply token (or respond to client with token)
        Guacd->>MTProxy: connect using token / Proxy-Protocol
        MTProxy->>Frouter: RDP / SSH flow -> Frouter -> Server
        Frouter->>Server: RDP / SSH session
        Server-->>Frouter: RDP / SSH session data
        Frouter-->>MTProxy: proxy back
        MTProxy-->>Guacd: proxied session
        Guacd-->>Client: HTTP(S) Web UI / websocket stream (browser)
    end

    Note over AppEngine,AuthBroker: AppEngine watches Brain and exposes GetApp() used by AuthBroker to obtain app metadata
```

### Authentication And Authorization Flow

```mermaid
sequenceDiagram
    participant Client
    participant ZProxy
    participant AuthBroker as "Auth-Broker"
    participant FedGW as "Fed-GW"
    participant IdP
    participant Server

    Client->>ZProxy: App External URL
    Note right of ZProxy: Check for app cookie
    ZProxy->>AuthBroker: /loginvalidate or /login
    Note right of AuthBroker: validate cookie if present

    alt Auth cookie validation failed or cookie absent
        Note right of AuthBroker: set callback URL on app domain
        AuthBroker-->>ZProxy: redirect to Fed-GW
        ZProxy->>Client: redirect to Fed-GW
        Client->>FedGW: SAML Request
        Note right of FedGW: Auth cookie check? [Future]

        opt Auth cookie check failed
            FedGW->>Client: redirect to IdP
            Client->>IdP: SAML Request

            opt Optional IdP login flow
                IdP->>Client: login challenge response flows
                IdP->>Client: redirect back to Fed-GW
                Client->>FedGW: callback to Fed-GW
                Note right of FedGW: set auth cookie [Future]
            end

            FedGW->>Client: redirect back to Proxy on app domain
            Client->>ZProxy: callback to Proxy on app domain
            ZProxy-->>AuthBroker: /logincallback
            Note right of AuthBroker: evaluate policy and set app cookie
            AuthBroker-->>ZProxy: redirect to original App External URL
            ZProxy->>Client: redirect to original App External URL
            Client->>ZProxy: callback on App External URL
            Note right of ZProxy: app cookie check?
        end

    else Auth cookie check OK
        AuthBroker-->>ZProxy: 200 OK
    end

    ZProxy->>Server: App Internal URL
    Server->>ZProxy: server response
    ZProxy->>Client: server response
```

## Mental Model For Escalation Questions

Use this simplified mapping when answering CFD questions:
- login and authorization questions usually start with `Auth-Broker`
- request routing and proxying questions usually start with `Envoy`
- dynamic proxy config questions usually start with `Envoy Controller`
- RDP and SSH browser-session questions usually start with `Guacd` or `Guacamole-lite`
- certificate questions usually start with `Enclave`
- monitoring or check-definition questions usually start with `Nidz`

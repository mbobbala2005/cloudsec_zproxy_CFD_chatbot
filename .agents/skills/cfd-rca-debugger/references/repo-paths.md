# Repository Paths

Set these environment variables:

- `NIDZ_API_REPO_PATH`
- `AUTH_BROKER_REPO_PATH`
- `ENVOY_REPO_PATH`
- `ENVOY_CONTROLLER_REPO_PATH`
- `POLICY_BROKER_REPO_PATH`
- `POLICY_GEN_REPO_PATH`
- `GUACD_REPO_PATH`
- `GUACAMOLE_LITE_REPO_PATH`
- `TERRAFORM_REPO_PATH`
- `OPS_REPO_PATH`
- `RELEASE_INFO_REPO_PATH`

Use them like this:
- product code path debugging: `AUTH_BROKER`, `ENVOY`, `ENVOY_CONTROLLER`, `POLICY_*`, `GUAC*`
- check or monitor implementation lookup: `NIDZ_API`
- runtime config and platform behavior: `OPS`, `TERRAFORM`
- waves, rollouts, and regression timing: `RELEASE_INFO`

Suggested local paths:

- `REPO_BASE_DIR=$HOME/cisco`
- `NIDZ_API_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_nidz_api`
- `AUTH_BROKER_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_auth`
- `ENVOY_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_envoy_zproxy`
- `ENVOY_CONTROLLER_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_envoy_controller`
- `POLICY_BROKER_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_policy_broker`
- `POLICY_GEN_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_policy_gen`
- `GUACD_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_guacd`
- `GUACAMOLE_LITE_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_guacamole_lite`
- `TERRAFORM_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_terraform`
- `OPS_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_ops`
- `RELEASE_INFO_REPO_PATH=$REPO_BASE_DIR/cloudsec_zproxy_release_info`

Preferred unattended repo access uses the GitHub App helper in `scripts/github_auth.py` through `./scripts/sync_repos.py` or `./scripts/prepare_repo_context.sh`.

SSH remotes still work for local development, but deployed automation should prefer GitHub App backed HTTPS access so clone, fetch, and pull do not depend on interactive SSH setup.

Canonical repo remotes:

- `git@github.com:cisco-sbg/cloudsec_zproxy_nidz_api.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_auth.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_envoy_zproxy.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_envoy_controller.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_policy_broker.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_policy_gen.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_guacd.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_guacamole_lite.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_terraform.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_ops.git`
- `git@github.com:cisco-sbg/cloudsec_zproxy_release_info.git`

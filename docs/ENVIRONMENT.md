# Environment

The benchmark runs against four locally reachable WebArena applications. Use the deployment and seeded accounts described below.

## WebArena Deployment

Use the upstream WebArena repository as the deployment reference:

- Repository: <https://github.com/web-arena-x/webarena>
- Website: <https://webarena.dev/>
- Upstream environment guide: <https://github.com/web-arena-x/webarena/tree/main/environment_docker>

The submitted snapshot was prepared against the canonical WebArena application set. The local reference checkout used for environment documentation was:

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/web-arena-x/webarena.git` |
| Local checkout | `v0.2.0-107-gdce0468` |
| Commit | `dce04686a56253aefba7b18a4fa0937cf1dc987b` |

WebArena provides two setup paths: a pre-installed AMI and individual Docker images. The upstream guide describes service startup, environment reset, base-url rewrites for Magento/GitLab, and service health checks. This artifact relies on that upstream deployment rather than repackaging Docker images or site databases.

The A11yDetectBench task assets in this artifact use local WebArena URLs, most commonly:

| Site | URL expected by task assets |
| --- | --- |
| GitLab | `http://localhost:8023/` |
| Reddit/Postmill forum | `http://localhost:9999/` |
| Shopping/Magento storefront | `http://localhost:7770/` |
| Shopping Admin/Magento admin | `http://localhost:7780/admin/` |

The task files, sign-in probes and scoring rules refer to these origins. If the services run on another host, forward the four ports to the machine running the agent. Configure the sites’ advertised base URLs to match the table.

## Runtime dependencies

The archived environment records Python 3.11.14, Playwright 1.58.0, PyYAML 6.0.3 and Pillow 12.1.1. The [quick start](../README.md) installs the corresponding public dependencies. Playwright supplies Chromium for sign-in and evaluation. The original agent runner uses browser-use’s browser discovery. Have Chrome or Chromium available to browser-use.

| Component | Configuration |
| --- | --- |
| OpenAI-compatible model | Set `OPENAI_API_KEY`, optionally `OPENAI_BASE_URL`, and pass the model name using `--model`. |
| Azure OpenAI | Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and pass the deployment name using `--model`. Set `OPENAI_API_VERSION` when needed. |
| WebArena account | Set `WEBARENA_<SITE>_USERNAME` and `WEBARENA_<SITE>_PASSWORD`. Replace `<SITE>` with `GITLAB`, `REDDIT`, `SHOPPING` or `SHOPPING_ADMIN`. |

The public model and sign-in adapters read these settings. Use the seeded site identities, including the Reddit account named in the login probe. For an authenticated task, the runner creates a fresh local session and checks that the account page is accessible. The `runtime_auth_state_placeholder.json` value in a task signals that sign-in is required.

## browser-use Version

The submitted experiments used browser-use as the browser-agent framework.

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/browser-use/browser-use.git` |
| Package version | `0.12.6` |
| Local checkout | `0.12.6-dirty` |
| Commit | `329c67f069427e928ff81ad52415efdca7692007` |

The local checkout had a small structured-output robustness patch in:

- `browser_use/llm/openai/chat.py`
- `browser_use/llm/azure/chat.py`

The patch adds optional structured-output parse-failure dumps and optional multi-JSON salvage through `salvage_multi_json`. It is included as `third_party/browser-use-0.12.6-structured-output.patch` rather than vendoring the full browser-use repository. Apply that patch to browser-use 0.12.6 if you want the runner flags `--capture-structured-failures` and `--salvage-multi-json` to match the submitted protocol.

Apply the included patch to the browser-use source that the runner actually imports. With the pip installation from the quick start, use the following from the benchmark root.

```sh
PKG_DIR=$(python -c "import sysconfig; print(sysconfig.get_path('purelib'))")
patch -d "$PKG_DIR" -p1 < third_party/browser-use-0.12.6-structured-output.patch
```

If you keep an editable browser-use checkout at `../browser-use`, the original runners prefer that checkout. Apply the patch there. The archived model deployment names identify the historical runs. Access to a model deployment depends on the model provider.

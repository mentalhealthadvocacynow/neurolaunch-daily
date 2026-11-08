# NeuroLaunch Daily

A static Astro site with Python source extraction, Groq-powered summaries, and a daily GitHub Actions workflow. Includes search, category filters, article pages, archive, and a clearly labeled sample.

## 1. Run locally

Requires Node 22 and Python 3.12.

```sh
npm install
npm run dev
```

## 2. Deploy to GitHub Pages

1. Create a repository named `neurolaunch-daily` and upload this folder's contents (including `.github`). Use `main` as the default branch.
2. In Settings → Pages → Build and deployment, select GitHub Actions.
3. Push to main, or run the Generate and publish workflow manually with Generate unchecked. This publishes the sample without needing Groq.
4. The standard project URL is `https://YOUR_USERNAME.github.io/neurolaunch-daily/`.

The workflow calculates the repository base path automatically. For custom domains, change SITE_URL and BASE_PATH in the workflow and configure the domain in Pages settings.

## 3. Configure generation

Under Settings → Secrets and variables → Actions:

Secret:
- `GROQ_API_KEY`: your Groq API key.

Repository variables:
- `GROQ_MODEL`: an available model in your Groq account that supports JSON object response mode. No model is hardcoded; verify availability in your console.
- `SOURCE_URLS`: individual article URLs, one per line. Start here for reliable discovery.
- `SOURCE_FEED_URL`: optional verified HTTPS NeuroLaunch RSS, Atom, or URL sitemap endpoint. No feed is assumed. Sitemap indexes are not recursively traversed; supply a leaf URL sitemap. A feed may expose non-article links, which extraction can reject.
- `SOURCE_PERMISSION_CONFIRMED`: set to `true` only after reviewing source access and reuse permissions. robots.txt is checked separately; it does not grant copyright permission.
- `DAILY_LIMIT`: optional, defaults to 2, capped at 10.
- `AUTO_PUBLISH`: defaults off. Set to `true` to enable generation on the daily schedule.

Manually run the workflow with Generate checked to create and immediately publish a test batch. All generated articles are marked unreviewed. Review the results before enabling the schedule. This starter does NOT implement an editorial pull-request queue or automated medical fact-checking. Manual generation and AUTO_PUBLISH publish without human approval. For mandatory approval, protect the github-pages environment with a required reviewer if your GitHub plan supports it.

Schedule: 14:23 UTC daily. Scheduled runs can be delayed and depend on GitHub Actions availability. Generation still needs Groq and source-site network access; only hosting, storage, and orchestration live on GitHub.

## 4. Generate locally

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY='your-key'
export GROQ_MODEL='your-available-json-capable-model'
export SOURCE_PERMISSION_CONFIRMED=true
export SOURCE_URLS='https://neurolaunch.com/your-permitted-article/'
python scripts/generate.py
npm run build
```

Export variables yourself; `.env` is not automatically loaded. Never commit credentials.

## Behavior and limitations

- Each successful article saves Markdown and a processed-URL manifest. Existing processed URLs are skipped; source updates are not automatically re-summarized.
- Groq SDK retries transient API errors. Extraction failures are logged. Any failed article aborts the deployment, leaving the existing live website intact. Successfully generated local files from that failed job are not committed.
- Structure validation is not factual verification. Review source fidelity, health claims, and permissions yourself.
- Extracted input is capped at 45,000 characters, so very long sources may be truncated.
- No raw source text is committed. Generated text is sanitized before Markdown rendering.
- There is no database, browser-side API key, persistent server, or external analytics.
- It is an independent project, not an exact visual clone or an endorsed NeuroLaunch product.
- The workflow pushes content commits to main. Branch protection may prevent this; adapt to a pull-request flow if your repository requires one.
- `npm install` is used for the first deployment. Commit the generated package-lock.json and switch to `npm ci` for reproducible builds. Pin action commit SHAs and dependency versions for stronger supply-chain controls.

## Remove the demo

Delete `src/content/articles/welcome.md` when ready. Keep an empty `.gitkeep` in that directory if removing every article.

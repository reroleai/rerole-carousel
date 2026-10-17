# Setup: Claude → GitHub → Meta → Instagram

```
 Claude Code (this folder)        GitHub (public repo)                 Meta / Instagram
 ─────────────────────────        ───────────────────────────          ────────────────
 /ig-carousel writes the copy     stores posts/ and out/*.jpg          Instagram downloads the
 render.py makes the JPEGs   ──►  Action runs publish.py        ──►    JPEGs from GitHub and
 you review, then git push        with your token as a secret          publishes the carousel
```

Allow about 30 minutes. You do parts 1–3 once, and only part 5 for each new post.
Meta renames its menus from time to time. If a button below has a slightly
different name, look for the closest match.

---

## Part 1. Make @rerole.ai a professional account (2 min)

Instagram only lets apps publish to Business or Creator accounts.

1. In the Instagram app, go to your profile → ☰ → **Settings and activity**.
2. Open **Account type and tools** → **Switch to professional account**.
3. Choose **Business** (or Creator) and pick a category such as *Software* or *Career coach*.

You **don't** need a Facebook Page for this setup.

---

## Part 2. Create the Meta app and get a token (15 min)

### 2.1 Developer account
1. Go to **https://developers.facebook.com** and click **Get Started**.
2. Log in with Facebook and verify your email and phone when asked.

### 2.2 Create the app
1. Go to **My Apps** → **Create App**.
2. App name: `ReRole Publisher`. Contact email: your email.
3. Use case: choose **Manage messaging & content on Instagram**.
4. Business portfolio: choose **I don't want to connect a business portfolio yet**. You can add one later.
5. Click **Create app** and re-enter your Facebook password.

### 2.3 Add the permissions
1. In the left menu, open **Use cases** → **Customize** next to the Instagram use case.
2. Open **API setup with Instagram login**.
3. Under **Permissions**, make sure these two are added:
   - `instagram_business_basic`
   - `instagram_business_content_publish`

### 2.4 Give @rerole.ai a role on the app
While the app is in **Development mode** (the default), it only works for accounts that
have a role on it. That's fine, because @rerole.ai is the only account it needs to post to.

1. Left menu → **App roles** → **Roles** → **Add People** → **Instagram Tester**.
2. Enter `rerole.ai` and submit.
3. Accept the invite. On the web, log in to instagram.com as @rerole.ai and go to
   **Settings → Website permissions → Apps and websites → Tester invites → Accept**.

### 2.5 Generate the access token
1. Go back to **API setup with Instagram login** → **Generate access tokens**.
2. Click **Add account** and log in as **@rerole.ai**. Approve the permissions.
3. Click **Generate token** next to the account and copy it.
   - This is a **long-lived token, valid for 60 days**. Part 6 covers refreshing it.
   - Treat it like a password. Keep it in a password manager, and never paste it into a
     file in this folder, a chat, or a commit.
4. The **Instagram account ID** is the number shown next to the account in the same panel.
   Copy that too. This is your `IG_USER_ID`.

To confirm the ID from a terminal, first run this. It prompts for the token without
showing it or saving it to your shell history:

```bash
read -s IG_ACCESS_TOKEN && export IG_ACCESS_TOKEN
```

Then run this:

```bash
curl -s -G https://graph.instagram.com/v23.0/me --data-urlencode "fields=user_id,username" --data-urlencode "access_token=$IG_ACCESS_TOKEN"
```

It should print `"username": "rerole.ai"` and a `user_id`.

**Leave the app in Development mode.** You don't need App Review to post to an account
that has a role on the app.

---

## Part 3. Put the project on GitHub (10 min)

### 3.1 Create the repo
Instagram fetches the images from a public URL, so the repo has to be **public**. Anyone
can see a post's images and copy once you push them, before Instagram publishes them.
If that's a problem, see "Private repo" at the end.

Using the GitHub CLI (`brew install gh`, then `gh auth login` once):

```bash
cd "/Users/madhur/Downloads/Instagram Post/Instagram Automation/rerole-carousel"
```

```bash
git init -b main && git add . && git commit -m "feat: ReRole carousel pipeline"
```

```bash
gh repo create rerole-carousel --public --source . --push
```

Or on github.com: **New repository** → name `rerole-carousel` → **Public** → **Create**.
Then follow the "push an existing repository" commands it shows.

### 3.2 Add the two secrets
Repo on github.com → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**. Add both:

| Name              | Value                                  |
|-------------------|----------------------------------------|
| `IG_USER_ID`      | the Instagram account ID from 2.5      |
| `IG_ACCESS_TOKEN` | the token from 2.5                     |

Or from the terminal. These prompt for the value, so it stays out of your shell history:

```bash
gh secret set IG_USER_ID
```

```bash
gh secret set IG_ACCESS_TOKEN
```

### 3.3 Let the workflow record what it posted
Go to **Settings** → **Actions** → **General** → **Workflow permissions** and select
**Read and write permissions** → **Save**. The workflow commits `published.json` after
each post, so the same carousel never posts twice.

---

## Part 4. First post (5 min)

1. In the repo, open the **Actions** tab. Enable workflows if GitHub asks.
2. Pick **Publish to Instagram** → **Run workflow**. Leave **Dry run** ticked → **Run**.
3. Open the run. The log lists nine image URLs and the caption. Open one URL in your
   browser and check the slide appears. If it does, Instagram can fetch it too.
4. Click **Run workflow** again, untick **Dry run** this time, and run it.
5. After about a minute the carousel is live on @rerole.ai, and `published.json` gets a
   new commit.
6. Add the alt text in the Instagram app: post → ⋯ → **Edit** → **Alt text**. It's printed
   at the end of the log and saved in `out/<slug>/alt_text.txt`.

---

## Part 5. The routine for every new post

In Claude Code, in this folder:

1. Ask for the content: `/ig-carousel salary negotiation for freshers`
2. Review the copy and edit it until you're happy. Then ask Claude to
   *"save it as posts/2026-10-21-salary-negotiation.json and render it"*.
   Start the file name with the date: the queue posts files in name order.
3. Look at the JPEGs in `out/<slug>/`.
4. Push:

```bash
git add posts out && git commit -m "feat: add salary negotiation carousel" && git push
```

5. Post it with **Run workflow** (empty post field = next in the queue), or let the
   schedule pick it up.

### Turn on automatic posting
Once a manual run has worked, open `.github/workflows/publish.yml`, uncomment the
`schedule:` block, and set the time. Cron uses **UTC**: `30 13 * * 1,3,5` means
Mon/Wed/Fri at 19:00 IST. Commit and push.

Each scheduled run posts the oldest rendered post that isn't in `published.json` yet.
If there's nothing new, it does nothing. To keep a post out of the queue, don't push it
until it's ready.

---

## Part 6. Refresh the token (every ~50 days)

The token expires after 60 days. Refresh it before then. Load the current token (input is hidden):

```bash
read -s IG_ACCESS_TOKEN && export IG_ACCESS_TOKEN
```

Then refresh it and save the new token straight into the GitHub secret:

```bash
curl -s -G https://graph.instagram.com/refresh_access_token --data-urlencode "grant_type=ig_refresh_token" --data-urlencode "access_token=$IG_ACCESS_TOKEN" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'], end='')" | gh secret set IG_ACCESS_TOKEN
```

That pipes the new token into the secret without displaying it. If the token has already
expired, generate a new one as in step 2.5.

---

## Troubleshooting

| Error in the Action log | Fix |
|---|---|
| `Missing environment variables` | A secret is missing or misspelled (Part 3.2). |
| `Graph API 400 … Invalid OAuth access token` / code 190 | Token expired or was pasted wrong. Refresh it (Part 6). |
| `Graph API 403` / code 10 or 200 | The `instagram_business_content_publish` permission is missing (2.3), or the token is for a different account. |
| `Only photo or video can be accepted` / image download failed | The repo is private, or the images weren't pushed. Open the URL from the log in a private browser window. |
| `Container … failed with status ERROR` | An image isn't 1080x1350 JPEG. Re-run `render.py` and push again. |
| `already in published.json` | That post was already published. Remove its entry from `published.json` to post it again. |
| `git push` fails in "Record what was posted" | Workflow permissions aren't set to read and write (3.3). |

Instagram also caps how many posts an account can publish through the API each day.
A few a week is far below it.

## Private repo

`raw.githubusercontent.com` links to a private repo need a login, and Instagram can't log
in. To keep the repo private, host `out/` on a public bucket instead, such as Cloudflare
R2 or AWS S3, or on a folder on rerole.ai. Then change `IMAGE_BASE_URL` in the workflow to
`https://<your-host>/out/{slug}`.

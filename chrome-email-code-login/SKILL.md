---
name: chrome-email-code-login
description: Use the moment a Claude in Chrome tab lands on a sign-in page for one of Eddy's own accounts that signs in by email (one-time code, magic link, "continue with email", WorkOS AuthKit, Clerk, Supabase, Auth0 passwordless), after the profile check confirms the right Chrome profile. Sign Eddy in yourself by reading the code from his mail in the same Chrome. Never stop at a login wall to ask him to sign in.
---

# chrome-email-code-login: sign Eddy in with the code from his inbox

A login wall is not a reason to stop. Eddy's mail is already open in the same Chrome profile, so an email code is something Claude can fetch and enter. Stopping to say "sign in and tell me when you're done" is the failure this skill exists to prevent.

## When this applies

- The tab shows a sign-in page that offers email sign-in: an email field with "Continue with email", "Send code", "Send magic link", or a hosted auth page (WorkOS AuthKit `*.authkit.app`, Clerk, Supabase, Auth0, Stytch, Magic).
- The account is Eddy's own, on a site he already uses, and the email is one of his Chrome profile emails (`~/.claude/chrome/browser-profiles.json`).
- The Chrome profile is right. Step 1 checks this first, because a login wall on a daily site can also mean the wrong browser was picked.

## When it does not

- The page asks for a **password**. Passwords are Eddy's to type. Say so in one line and wait.
- The site is a bank, broker, payment provider, government service, or anything where the code protects money or identity. Say so and wait.
- The sign-in would create a new account rather than enter an existing one.
- The code arrives by SMS or an authenticator app. Claude cannot read those; say so and wait.

## Steps

1. **Confirm the profile.** `list_connected_browsers`, map the current deviceId through `~/.claude/chrome/browser-profiles.json`, and check its email is the account the site expects (the `Chrome profile:` line of the nearest CLAUDE.md, or the account Eddy named). Wrong profile: `select_browser` the right one and reload the page before anything else. Right profile: carry on, do not ask.
2. **Prefer a one-click provider.** If the page offers "Continue with Google" (or another provider) for the same email the profile is signed into, click that. No code needed. Otherwise:
3. **Request the code.** Click the email field, type the profile's email, click the continue button. Note the time. Read the page once more: if it now asks for a password, stop as above. If it says a code or link was sent, continue.
4. **Open the mail in a new tab** (`tabs_create_mcp`, never Eddy's own tabs). Superhuman first: `https://mail.superhuman.com`. If Superhuman is not signed in for this profile, Gmail: `https://mail.google.com/mail/u/?authuser=<email>`. Give it two or three seconds to load.
5. **Find the message.** In Superhuman the new code is usually the unread row at the top of Important, and the row's snippet already contains the digits ("Your one-time code is 123456"), so one `find` for "rows from <sender> with subject <subject>" on the inbox returns the code without opening the thread. Open the thread only to check the time: Superhuman shows local clock time, so compare against the local time of step 3, and only accept a message **after** it; an older code is spent. Earlier codes for the same site often sit in Other or Trash, so the subject alone is not enough. If the row is not in Important, navigate the tab to `https://mail.superhuman.com/inbox/other` (Superhuman's split for automated mail, where most code emails land) and `find` again. **Never use keyboard shortcuts in Superhuman.** Every letter is a command (`f` forwards the open thread, `c` composes, `e` marks done) and a key name the extension does not map, such as `slash`, falls through as letters: on 2026-11-08 that opened a forward draft on someone's thread and typed the query into its To field (discarded with `cmd+shift+,`, nothing sent). Navigate by URL and click; to search, click the Search button, type, press Return.

**A "Sign up for <site>" subject means the address has no account there.** Entering that code would create one, which Claude never does. Close the tabs, leave the email, and tell Eddy which address the site knows nothing about; he may use a different email or Google for that site.
6. **Read the code or link** from text (`find` or `get_page_text`), never from a screenshot; the digits must be exact. Codes are usually 6 digits, sometimes 8, sometimes letters. Thread bodies in Superhuman can render collapsed ("Show message"), another reason the inbox snippet is the better source. For a magic link, read the link href with `find` or `read_page` and open it in the sign-in tab instead of typing anything.
7. **Not there yet?** Wait 10 seconds and look again, up to four times (about 45 seconds). Mail can lag. After that, tell Eddy the code never arrived and what you searched for.
8. **Enter the code** in the sign-in tab: click the code field (a single field or the first of six boxes, both accept the digits typed in sequence) and type it. AuthKit submits itself after the last digit and returns to the page that hit the wall; press Return only if nothing happens in three seconds. Confirm the tab has left the auth domain and shows the app. The extension can refuse `find` or `read_page` on the auth domain partway through ("Permission denied for reading pages on this domain") even after allowing it earlier; screenshots and clicks still work, so take a screenshot and click the first box by its coordinates instead of stopping.
9. **Clean up.** Close the mail tab. Leave the message alone: no reply, no archive, no mark done. Never write the code into chat, a report, or a file.

Then get on with the task that hit the wall.

## Known sites

Per site details (auth provider, sender, subject, code length, how long it stays valid) live in `sites.local.md` beside this file. It is untracked on purpose because it names accounts and internal sign-in pages. Read it before step 3 so the mail search uses the right sender and subject. Add a row there (never here) the first time a new site is signed into this way. If the file is missing, carry on without it and create it after the first sign-in.

## Rules this sits under

- The global CLAUDE.md Chrome rules still decide which browser to use: Eddy's real Chrome through the extension, never a Playwright or Puppeteer browser, and the profile is chosen on purpose first.
- Steps 3 to 8 use `browser_batch` where two or more steps are known in advance; it is several times faster than one call per action.
- If the extension refuses a site (permission not granted), tell Eddy which site needs allowing in the extension and wait. Do not route around it.

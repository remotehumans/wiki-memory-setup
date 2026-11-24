# Storage and Connectors

## Choosing storage

Offer these and let the user choose. Recommend GitHub when they are comfortable with it, but never require it.

| Storage | History | Best for | Setup flag |
|---|---|---|---|
| GitHub (private repository) | Git: every change, undoable | Version control, backups, cloud agents and several computers | `--storage github` |
| This computer only | Git on this computer | Trying it out; add GitHub later | `--storage local` |
| Google Drive | Drive version history | Google Workspace users | `--storage google-drive` |
| OneDrive or SharePoint | Microsoft version history | Microsoft 365 users, or where IT has not approved GitHub | `--storage onedrive` or `--storage sharepoint` |
| Dropbox | Dropbox version history | Existing Dropbox users | `--storage dropbox` |
| iCloud Drive | iCloud history | Apple-only users | `--storage icloud` |
| Something else | Whatever it offers | Other setups | `--storage other` |

Rules:

- For a sync folder (Drive, OneDrive, SharePoint, Dropbox, iCloud), create the wiki inside the user's synced folder and do not use Git there. A `.git` folder inside a sync folder can be corrupted by the sync client.
- Typical synced folder locations on a Mac: Google Drive `~/Library/CloudStorage/GoogleDrive-<email>/My Drive`, OneDrive and SharePoint `~/Library/CloudStorage/OneDrive-<name>`, Dropbox `~/Dropbox` or `~/Library/CloudStorage/Dropbox`, iCloud `~/Library/Mobile Documents/com~apple~CloudDocs`. On Windows they are usually under `C:\Users\<name>\` (`OneDrive`, `Dropbox`) or the `G:` drive for Google Drive. Look for the real folder rather than guessing.
- Make sure the folder is set to stay on the device ("Available offline" or "Always keep on this device"), so the agent reads real files, not placeholders.
- If a conflict copy appears (a file with a computer or user name added), merge it into the real page and delete the copy.

### GitHub walkthrough

Go one step at a time and wait for the user at each step.

1. Check for a GitHub account. If none, send them to https://github.com/signup and wait.
2. Check `git` is installed (`git --version`). If not, help install it for their system.
3. If the GitHub CLI is available, run `gh auth login` and let the user finish in the browser. Otherwise guide them to create a **private** repository on github.com.
4. Create the wiki with `--storage github --remote <repo URL>`, confirm the repository is private, then push.
5. Explain in one line: every change is saved and can be undone, and other agents can use the same wiki.

## Connecting the wiki as context

Once the wiki exists, offer to connect it to the other AI apps the user uses, so those apps can answer from it.

- **GitHub:** Claude.ai and ChatGPT both offer GitHub connectors. Connect the private repository.
- **Google Drive:** Claude.ai and ChatGPT both offer Google Drive connectors. Point them at the wiki folder.
- **OneDrive or SharePoint:** use the Microsoft 365 or SharePoint connector where the app offers one.
- **Dropbox:** use the Dropbox connector where offered.
- **Claude.ai Projects or ChatGPT Projects:** add the connected wiki, or its key pages, as project knowledge.

Most connectors only read. Connected apps can answer questions from the wiki, but new knowledge should be filed by an agent that can write to the folder (Claude desktop with Cowork, Claude Code, Codex, Cursor or similar). Tell the user this in one plain sentence.

Some cloud-drive connectors read only Google Docs or Office files, not plain `.md` files. After connecting, ask the app one question about a known person. If it cannot see the pages, connect the GitHub repository instead, or use an app that can open the folder.

Connector names and availability change. Check what the user's app offers rather than promising a specific one.

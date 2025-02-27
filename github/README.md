# GitHub user repositories plugin

This plugin lets you search & open GitHub user repositories in the browser.

You'll first need to provide your [GitHub access token](https://github.com/settings/tokens) (only needs the *repo* scope) with `gh your-access-token-here`.  
Please refer to the [keyring](https://pypi.org/project/keyring/) documentation should your Linux installation be missing an appropriate backend.

Next, you'll need to create a local cache of your repositories. Simply trigger `gh ` and press `[enter]`. This may take a few seconds.  
You can rebuild the local cache anytime with `gh rebuild cache`.

Now you're ready to search for a repository with `gh repo-name`.

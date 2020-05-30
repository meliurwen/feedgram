# How to Contribute

Thank you for considering contributing. All contributions are welcome and appreciated!

## Support Questions

Please don't use the Gitlab issue tracker for asking support questions. All support questions should be discussed on _IRC_, _Slack_ or _Discord_.

## Documentation (RTFM!)

Before start contributing or asking dummy questions is best practice to consult first the following sources:

+ The [README.md](https://gitlab.com/meliurwen/feedgram/-/blob/develop/README.md) in the repo
+ The project's documentation
+ The official [Telgram's bot API Docs](https://core.telegram.org/bots/api)
+ Google

## Bug Reports

> **Note:** Be sure to have censored any sensitive data before posting, especially in the logs!

[Gitlab issues](https://gitlab.com/meliurwen/feedgram/-/issues/) is used for tracking bugs and proposing new features. Please consider the following when opening an issue:

+ Avoid opening duplicate issues by taking a look at the current open issues.
+ Follow [this template](.templates/ISSUE-BUG.md).
+ Provide details on the app version, operating system and Python version you are running.
+ Provide the **expected** and the **actual** behavior.
+ Provide steps to reproduce the issue
+ Include complete log tracebacks and error messages.
+ An optional description to give more context

## Feature Proposal

[Gitlab issues](https://gitlab.com/meliurwen/feedgram/-/issues/) is used for tracking bugs and proposing new features. Please consider the following when opening an issue:

+ Avoid opening duplicate issues by taking a look at the current open issues.
+ Follow [this template](.templates/ISSUE-FEATURE.md) (as a reference see #22).
+ The feature must be concrete enough to visualize, broken into parts, easy to manage and the task not too heavy.
+ Provide a short description from the point of view the actor(s) who will benefit from it, specifying what feature you want and what the actors should achieve with it. In other words you have to **justify** why the feature can be beneficial for the project.
+ Provide a list of acceptance criteria.
+ If you have clear ideas on how implement this feature write a checklist (not too much precise but also not too much vague) on changes you have to bring to the project.
+ If your ideas are not so clear write the checklist during the discussion with other contributors in the thread or other related places (Slack, Discord or IRC).
+ To give more context you can optionally add a (not too long) description with images attached.

## Pull Requests

All pull requests are welcome, but please consider the following:

+ **You cannot merge into master**.
+ Follow [this template](.templates/MERGE-DEV.md) (as a reference see !27).
+ Please open an issue first if a relevant one is not already open.
+ Include tests.
+ Include documentation for new features.
+ If your patch is supposed to fix a bug, please open an issue first.
+ Avoid introducing new dependencies.
+ Clarity is preferred over brevity.
+ Please follow _Flake8_ and _Pylint_, with the exception of what is ignored in [setup.cfg](https://gitlab.com/meliurwen/feedgram/-/blob/develop/setup.cfg). In the pipeline _Pylint_ and _Flake8_ compliance is checked before tests. Tests will not run if your patch is not _Pylint_ and _Flake8_ compliant.
+ Before the merge the code will be reviewed and should pass an acceptance testing from other contributors and/or project leaders.
+ Provide a changelog (not too much detailed) about your changes

> **Info:** for contributors who have write permissions to master [here the template](.templates/MERGE-MASTER.md) for the merge request.
> **Note:** the merge requests to _master_ **_must only come from_** the _dev_ branch. In case an hotfix is necessary you can only branch from master, apply the fix (maybe cherry-picking from other branches) and then merge back to master.

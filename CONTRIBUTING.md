# Contributing

## Code of Conduct

All members of the project community must abide by the [SAP Open Source Code of Conduct](https://github.com/SAP/.github/blob/main/CODE_OF_CONDUCT.md).
Only by respecting each other we can develop a productive, collaborative community.
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting [a project maintainer](REUSE.toml).

## Engaging in Our Project

We use GitHub to manage reviews of pull requests.

There are different ways to contribute:

* **Code**: add features, bug fixes, tests, or documentation changes.
* **Time**: support testing, triage, and collaboration with the maintainers.

* If you are a new contributor, see: [Steps to Contribute](#steps-to-contribute)

* Before implementing your change, create an issue that describes the problem you would like to solve or the code that should be enhanced. Please note that you are willing to work on that issue.

* The team will review the issue and decide whether it should be implemented as a pull request. In that case, they will assign the issue to you. If the team decides against picking up the issue, the team will post a comment with an explanation.

## Steps to Contribute

Should you wish to work on an issue, please claim it first by commenting on the GitHub issue that you want to work on. This is to prevent duplicated efforts from other contributors on the same issue.

If you have questions about one of the issues, please comment on them, and one of the maintainers will clarify.

Recommended flow for code contributions:

1. Read the [Definition of Done](#definition-of-done) and project coding guidelines.
2. Align with maintainers on scope in the issue before starting larger changes.
3. Implement your contribution and add or update tests where relevant.
4. Open a pull request against `main` and explain:
	- Reason for the change
	- What was implemented and why
	- Any migration or compatibility impact
5. Stay available to address review feedback and follow-up fixes.

## Contributing Code or Documentation

You are welcome to contribute code in order to fix a bug or to implement a new feature that is logged as an issue.

The following rule governs code contributions:

* Contributions must be licensed under the [Apache 2.0 License](./LICENSE).
* Due to legal reasons, contributors will be asked to accept a Developer Certificate of Origin (DCO) when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).
* Contributions must follow our [guidelines on AI-generated code](https://github.com/SAP/.github/blob/main/CONTRIBUTING_USING_GENAI.md) in case you are using such tools.

## Definition of Done

To keep quality and reliability high, contributions should meet these criteria:

* Unit tests and integration tests pass for affected areas.
* CI checks are green for your pull request.
* Lint checks pass without new issues.

## Documentation Expectations

When adding features or changing behavior:

* Update user-facing package documentation in [PYPIDESCRIPTION.md](PYPIDESCRIPTION.md) where applicable.
* Update or add inline code documentation where necessary.
* Update relevant documentation under [docs](docs) if the change affects usage.

## Issues and Planning

* We use GitHub issues to track bugs and enhancement requests.

* Please provide as much context as possible when you open an issue. The information you provide must be comprehensive enough to reproduce that issue for the assignee.

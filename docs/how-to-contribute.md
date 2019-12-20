# How to Contribute


## Versions

- Versions of farm-core work on `major.minor.revision`
- Major version is reserved for a large change, such as a large set of feature additions. Backwards compatibility IS NOT assumed.
- Minor version indicates feature changes. Backwards compatibility IS NOT assumed.
- Revision version indicates only bugfixes and minor required changes. Backwards compatibility IS assumed.
- Once a new major revision is reached, the head of `master` should be tagged, following convention `v<major>.0.0`. E.g. `v1.0.0`.

## Branches

- Bleeding edge is always `master`. `master` is not assumed to be stable.
- Release branches exist, and are considered stable. These follow the naming convention `release/major.minor.x` e.g. `release/0.10.x`. At creation of this branch, a tag with minor revision `0` should be added to `master` at the branch point.  E.g. `v0.10.0. The release branches are updated only if they really must be, such as security fixes from master that need to be included. If a change is made to the release branch, then it gets a new tag in that branch. E.g. `v0.10.5`. These branches are not merged back into `master`.
- Feature branches exist, and are created as a development branch for a specific feature, or code change. For simplicity, refactors, code deletions, etc also fall under this category. The naming convention for these are `feature/short-description-of-feature` . Once the feature development is complete, a pull request is raised, merging back into master once code review has been completed.
- Bugfix branches exist, and are very similar to feature branches, but should only ever include fixes, and never new features. The naming convention for these is `bugfix/short-description-of-bug. Like feature requests, these must be code reviewed before merging to master.

## Pull requests

- A pull request should happen whenever a bugfix or feature branch is finished, and needs to be merged back into master.
- The reviewer is likely the Automation Lab maintainer (so probably me at this point), but this bit isn't properly defined yet.
- The reviewer will add code comments with requested changes.
- New commits can be made to the feature or bugfix branch to address the requested changes, which should update the pull request.
- Once the reviewer has approved the changes, the developer who raised the pull request must merge it back into `master`.

## Syncing repositories

- Since there is one core `farm-core`  repository, and many customer repositories `farm-<customer_name>`, steps must be taken to prevent changes to the core repository breaking the customer deployments.
- To allow this, customer deployments should always use a release branch of farm-core , and not follow the master, feature, or bugfix branches.
- Any time the `farm-<customer_name>` repository updates to using a newer revision of `farm-core`, a tag should be added to the `farm-<customer_name>`  head, which matches the version of farm-core that it is compatible with.
- This means that in order to use a customer repository, the same tag is checked out in `farm-core` and `farm-<customer_name>`, and everything is guaranteed to work.

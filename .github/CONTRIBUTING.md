# Contributing
We'd love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## We Use [Github Flow](https://guides.github.com/introduction/flow/index.html), So All Code Changes Happen Through Pull Requests
Pull requests are the best way to propose changes to the codebase. We follow the **shared repository model**.

## The Shared Repository Model
### Short Version
When you want to work on something, clone the repository and make a new branch for your feature. As you implement changes, commit them to your local branch. Then, push that branch to the GitHub remote and make a pull request. Include issue numbers in commit messages and the pull request message if applicable.
### Long Version
#### Writing your Code
1. `clone` the repository:
`$ git clone https://github.com/GSA/tbm-scan.git`
2. `checkout` a branch for your feature before doing anything:
`$ git checkout -b shiny-new-feature`
3. Do some work, staging files you've edited for commit like this:
`$ git add [file.name]`
 You can `add` one, several, or all modified files. To add all, use a dot:
 `$ git add .`
 4. `commit` those changes to your local branch.
 `$ git commit`
 5. To `push` those commits to the remote repository as a non-master branch, run:
 `git push origin shiny-new-feature`
 6. This will create a shiny-new-feature branch on the origin repository, ie. the repository on GitHub.
 7. You should now be able to see your branch on the origin repositor. To make the Pull Request, click on your branch name. Then, click the "Pull Request" button, either on the top right of the screen, or in the center of the page under the label "Your recently pushed branches:". Click the Send Pull request button. Await someone's code review.
 
 #### Reviewing your Code
 You can review pull requests at https://github.com/GSA/tbm-scan/pulls. If you like the code, you can merge it into master by pressing the big green Merge button. And then you're done!
 
 If there's a gray bar saying "This pull request cannot be automatically merged.", then you've got some more work ahead of you. That's because the file(s) that your pull request modifies was/were updated in the meantime. To avoid a conflict on the remote, GitHub won't let you automatically merge into master. This means you need to update your Pull Request by merging the origin's master branch into your feature branch. In short, you need to “merge upstream master” in your branch:
```
git checkout shiny-new-feature
git fetch upstream
git merge upstream/master
```
If there are no conflicts (or they could be fixed automatically), a file with a default commit message will open, and you can simply save and quit this file.

If there are merge conflicts, you need to solve those conflicts. See [this](https://help.github.com/articles/resolving-a-merge-conflict-using-the-command-line/) for an explanation on how to do this. Once the conflicts are merged and the files where the conflicts were solved are added, you can run `git commit` to save those fixes.

If you have uncommitted changes at the moment you want to update the branch with master, you will need to stash them prior to updating (see the [stash docs](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning)). This will effectively store your changes and they can be reapplied after updating.

After your feature branch has been update locally, you can now update your pull request by pushing to the branch on GitHub:
`git push origin shiny-new-feature`

#### Deleting your Branch
Once your feature branch is accepted, you’ll probably want to get rid of the branch. You can do that to the remote master right within the pull request page. To delete the branch locally, you need to pull the remote master down into your local master. Then git will know it's safe to delete your branch.
```
git checkout master
git pull
```
Now that your local master is even with the remote, you can do:
`git branch -d shiny-new-feature`
Make sure you use a lower-case -d, or else git won’t warn you if your feature branch has not actually been merged.
 
## Report bugs using Github's [issues](https://github.com/GSA/tbm-scan/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](); it's that easy!

## Write bug reports with detail, background, and sample code
[This is an example](http://stackoverflow.com/q/12488905/180626) of a bug report.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can. 
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style
This might not be strictly enforced, but this is generally a good thing.

## License
By contributing, you agree that your contributions will be licensed under its Creative Commons Zero v1.0 Universal.

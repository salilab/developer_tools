# Tools for helping with Git repositories

`setup_git.py` sets up a git repository, installing git hooks to check formatting and other common problems and bootstrapping subrepositories. To use, put a _copy_ of `bootstrap_setup_git.py` in the root of your repository and add `developer_tools` as a subrepository at `tools/dev_tools` in your main repository.

The git hooks check standards on commits and make sure there are no untracked files in the repository.
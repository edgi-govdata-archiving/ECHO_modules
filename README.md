# **IMPORTANT! We've moved development of this repo to the `main` branch. You will not be able to merge changes into `master`.**

## **UPDATING LOCAL CLONES**

(via [this link](https://www.hanselman.com/blog/EasilyRenameYourGitDefaultBranchFromMasterToMain.aspx), thanks!)

If you have a local clone, you can update and change your default branch with the steps below.

```sh
git checkout master
git branch -m master main
git fetch
git branch --unset-upstream
git branch -u origin/main
git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main
```

The above steps accomplish:

1. Go to the master branch
2. Rename master to main locally
3. Get the latest commits from the server
4. Remove the link to origin/master
5. Add a link to origin/main
6. Update the default branch to be origin/main



# ECHO_modules
A repository for code modules that can supplement the Jupyter notebooks.

A core goal of EEW is to open up the "black box" of EPA data and its analysis. That's why we've turned to Jupyter Notebooks, which expose both the ECHO database itself as well as the code we use to make sense of the data.

But, the more functionality we add - the more ability we give to users to interact with ECHO in meaningful ways - the more code we have to write. Big blocks of code may dissuade some people from engaging. This was already mentioned in one of Chris's student surveys.

With something like this, we can hide the less meaningful and interactive parts of the code, without, of course, black-boxing everything.

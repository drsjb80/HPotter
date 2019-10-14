# HPotter developer instructions 
These are useful commands for developers

## Git Steps

On your current feature branch:

    git stash 

**Confirm that stash didn't produce an error.** <br>
<br>
Then run:

    git checkout dev

Followed by:

    git pull

After all changes are pulled from the remote, run:

    git checkout "feature branch name"

Now run:

    git rebase dev

Followed by:

    git stash pop

Now run:

    git status

Then:

    git add "all files you want added in to commit"

After this:

    git commit -m "Message about what the commit is for"

Finally:

    git push

## If this is the first push of a branch:

    git push -u origin "feature branch name"
    
## Pull Request reviews

### Pull requests(PR) can be approved by anyone on the team
To pull a branch to perform a PR:

    git branch -t "branch name"
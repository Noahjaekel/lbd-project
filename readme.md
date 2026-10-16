## working with git

## conda environment
- on first use run `conda create --file environment.yaml`
- on every subsequent login run: 
    `conda env update --file environment.yaml --prune`
    `conda activate lbd-project`
- to add a new package use `conda install packagename` avoid using `pip` whenever possible.
- if you made any changes to the environment (e.g. installing new packages) run: `conda export > environment.yaml`. This updates the environment specification.

## getting started
1) open a new terminal in the folder you want to place this project
2) run `git clone https://github.com/Noahjaekel/lbd-project.git`
3) run `cd lbd-project`
4) run `conda create --file environment.yaml`
5) run `conda activate lbd-project`


## typical workflow
1) `git pull`
2) `conda env update --file environment.yaml --prune`
3) `conda activate lbd-project`
4) *make changes*
2) `git add -A`
3) `git commit -m "informative message"`
4) `git push`
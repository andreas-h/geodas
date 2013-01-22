git checkout gh-pages
cd .. && mkdir doc && cd doc/
git checkout master .
git reset HEAD
make clean dirhtml
find ../ -mindepth 1 -maxdepth 1 | grep -v .git | grep -v ../doc | grep -v .nojekyll | grep -v .gitignore | xargs rm -rf
mv -fv _build/dirhtml/* ../
git checkout gh-pages
git add -Af ../
git rm -rf .
cd ..
git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
git push github gh-pages --force
git checkout master
echo "Don't forget to `cd ..`, as the current Makefile deletes the cwd"

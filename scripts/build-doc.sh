#!/bin/sh

rm -rf .bld
mkdir .bld

cat *.md > .bld/markdown_all.md

echo "Copying html and css"
cp head.html .bld/head.html
cp foot.html .bld/foot.html
cp style.css .bld/style.css


echo "Converting dia to svg"
find ./img/ -name "*.dia" | parallel dia -e {.}.svg {}

mkdir .bld/img
cp -v img/*.png .bld/img
cp -v img/*.svg .bld/img



cd .bld

echo "Generating markdown"
markdown markdown_all.md > markdown_all.html

echo "Generating HTML"
cat head.html markdown_all.html foot.html > all.html

echo "Printing HTML"
wkhtmltopdf all.html all.pdf

echo "Copying result"
cp all.pdf ../
echo "DONE"

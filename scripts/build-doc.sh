#!/bin/sh

rm -rf .bld
mkdir .bld

cat *.md > .bld/markdown_all.md

cp head.html .bld/head.html
cp foot.html .bld/foot.html
cp style.css .bld/style.css
cp -r img/ .bld/img

cd .bld

markdown markdown_all.md > markdown_all.html

cat head.html markdown_all.html foot.html > all.html

wkhtmltopdf all.html all.pdf

cp all.pdf ../

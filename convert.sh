#!/bin/bash
for f in /Users/AYU/Desktop/Capstone/econbiz/*.pdf
do
 echo "Processing $f file..."
 pdftotext -enc UTF-8 $f
done

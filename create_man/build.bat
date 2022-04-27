@echo off
cd ..
mkdocs build
copy create_man\test-website.py .\site
cd create_man
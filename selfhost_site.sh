#! /bin/bash


sudo systemctl stop nginx
sudo nginx -s stop

sudo cp config/mcm-prd-local /etc/nginx/sites-available/mcm-prd-local

sudo rm  /etc/nginx/sites-enabled/*
sudo ln -s /etc/nginx/sites-available/mcm-prd-local /etc/nginx/sites-enabled/mcm-prd-local


python scrape.py

sudo rm -rf /etc/nginx/html/mcm-proxy
sudo mkdir /etc/nginx/html/mcm-proxy

sudo cp -r tmp/* /etc/nginx/html/mcm-proxy

#! /bin/bash

sudo rm -rf /etc/nginx/html/mcm-proxy
sudo mkdir /etc/nginx/html/mcm-proxy

sudo cp -r tmp/* /etc/nginx/html/mcm-proxy

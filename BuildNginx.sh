#! /bin/bash

sudo apt update
sudo apt upgrade -y

# Install Dependencies
sudo apt install -y curl build-essential make gcc libpcre3 libpcre3-dev libpcre++-dev zlib1g-dev libbz2-dev libxslt1-dev libxml2-dev libgeoip-dev libgoogle-perftools-dev libperl-dev libssl-dev libcurl4-openssl-dev git libssl-dev libgd-dev

# libgd2-xpm-dev

export NGINX_VERSION="1.14.2"
export BASE_PATH=${}PWD}

# Clone Repos
( cd /usr/src; sudo git clone https://github.com/yumauri/nginx_unsecure_cookie_module.git )
( cd /usr/src; sudo git clone https://github.com/openresty/echo-nginx-module.git )


export CONFIG="\
		--prefix=/etc/nginx \
		--sbin-path=/usr/sbin/nginx \
		--modules-path=/usr/lib/nginx/modules \
		--conf-path=/etc/nginx/nginx.conf \
		--error-log-path=/var/log/nginx/error.log \
		--http-log-path=/var/log/nginx/access.log \
		--pid-path=/var/run/nginx.pid \
		--lock-path=/var/run/nginx.lock \
		--http-client-body-temp-path=/var/cache/nginx/client_temp \
		--http-proxy-temp-path=/var/cache/nginx/proxy_temp \
		--http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
		--http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp \
		--http-scgi-temp-path=/var/cache/nginx/scgi_temp \
		--user=nginx \
		--group=nginx \
		--with-http_ssl_module \
		--with-http_realip_module \
		--with-http_addition_module \
		--with-http_sub_module \
		--with-http_dav_module \
		--with-http_flv_module \
		--with-http_mp4_module \
		--with-http_gunzip_module \
		--with-http_gzip_static_module \
		--with-http_random_index_module \
		--with-http_secure_link_module \
		--with-http_stub_status_module \
		--with-http_auth_request_module \
		--with-http_xslt_module=dynamic \
		--with-http_image_filter_module=dynamic \
		--with-http_geoip_module=dynamic \
		--with-threads \
		--with-stream \
		--with-stream_ssl_module \
		--with-stream_ssl_preread_module \
		--with-stream_realip_module \
		--with-stream_geoip_module=dynamic \
		--with-http_slice_module \
		--with-mail \
		--with-mail_ssl_module \
		--with-compat \
		--with-file-aio \
		--with-http_v2_module \
		--with-ipv6
		--with-threads \
		--with-stream \
		--with-stream_ssl_module \
		--add-module=/usr/src/nginx_unsecure_cookie_module \
		--add-module=/usr/src/echo-nginx-module \
	" \

mkdir ~/build
cd ~/build

wget https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz

tar xvf nginx-${NGINX_VERSION}.tar.gz

cd nginx-${NGINX_VERSION}

./configure $CONFIG --with-debug

make -j$(getconf _NPROCESSORS_ONLN)
sudo make install

sudo useradd -r nginx

sudo mkdir -p /var/cache/nginx

sudo sudo touch /var/cache/nginx/client_temp

sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled


# Build the service
sudo tee /etc/systemd/system/nginx.service > /dev/null <<EOT
[Unit]
Description=The NGINX HTTP and reverse proxy server
After=syslog.target network.target remote-fs.target nss-lookup.target

[Service]
Type=forking
PIDFile=/var/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOT

sudo chmod 644 /etc/systemd/system/nginx.service

# Install Nginx Config
sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bck

sudo tee /etc/nginx/nginx.conf > /dev/null <<EOT

user  nginx nginx;
worker_processes  $(getconf _NPROCESSORS_ONLN);

#error_log  logs/error.log;
#error_log  logs/error.log  notice;
#error_log  logs/error.log  info;

#pid        logs/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;


    sendfile        on;
    #tcp_nopush     on;

    #keepalive_timeout  0;
    keepalive_timeout  65;

    #gzip  on;

    server {
        listen       80;
        server_name  localhost;

        #charset koi8-r;

        #access_log  logs/host.access.log  main;

        location / {
            root   html;
            index  index.html index.htm;
        }
    }
    include /etc/nginx/sites-available/*;
}
EOT


cd ${BASE_PATH}
cd config
sudo cp * /etc/nginx/sites-available

sudo ln -s /etc/nginx/sites-available/mcm-prd /etc/nginx/sites-enabled/mcm-prd

# Clean up
sudo rm -rf /usr/src/nginx_unsecure_cookie_module
sudo rm -rf /usr/src/echo-nginx-module
rm -rf ~/build

sudo systemctl start nginx



# sudo cp ~/build/nginx-1.14.2/objs/ngx_http_unsecure_cookie_filter_module.so /usr/share/nginx/modules/


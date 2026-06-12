# Nginx proxy deployment procres for internal loadbalncer or private ip
## Install Nginx on Amazon Linux 2
Run the following on the public-facing EC2 (nginx) instance.

### After cloneing your repo change frontend index.html file url must be empty only
once chek in your config file below one is comented or uncomented if commented please uncoment and build the package
```
 const backendIP = "";  // For reverse proxy it is mandatory and keep it empty dont pass anty url or ip here  

```
```bash
sudo yum update -y
sudo yum install -y nginx
# Enable and start nginx
sudo systemctl enable --now nginx
```
### create a proxy file and paste the file from git and chage the backend private ip if you are using internal loadbalncer change it 
```bash
sudo vi /etc/nginx/conf.d/reverse-proxy.conf
```
### paste below file and give backend private ip or internal loadblancer
```
server {
    listen 80;
    server_name _;

    # Proxy API requests to backend
    location /users {
        proxy_pass http://172.31.27.126:5000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_redirect off;
    }

    # Frontend files
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

    # React build
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```
# Verify
2. Test and reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Deploy index.html  to Nginx
sudo cp index.html /usr/share/nginx/html/

# reload nginx
sudo systemctl reload nginx
```

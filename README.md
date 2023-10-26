# vcst-edi-web
## Build Container file
podman build -t name_of_container .
## After Build Run Container
podman run -p 8000:8000 -v $(pwd):/app name_of_container

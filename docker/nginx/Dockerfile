FROM nginx:alpine

# Remove the default nginx config — we replace it with our own
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom config into the container
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

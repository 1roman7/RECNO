# Remove the ExecStart line with uvicorn and replace with a proxy pass approach if needed.
# Since user accesses the site through port 443 with an ERR_QUIC_PROTOCOL_ERROR,
# it means Uvicorn is trying to speak HTTP but getting HTTPS requests, OR
# Uvicorn is trying to speak HTTPS but failing due to permissions/certificates.
# Let's use NGINX as reverse proxy on 443 and uvicorn on 8000

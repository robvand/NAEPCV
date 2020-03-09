curl -H "Content-Type: application/json" \
    -H 'Authorization: Bearer $bearer' \
    -i -v -X POST \
    -d "{ \"roomId\": \"$roomId\", \"text\": \"hi\" }" \
    https://api.ciscospark.com/v1/messages
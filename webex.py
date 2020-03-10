botId = "Y2lzY29zcGFyazovL3VzL0FQUExJQ0FUSU9OL2Y2NThiYjZjLTVkMzUtNDNkNC05YmJmLTAzOTBlNTJiNDMzZA"
bearer = "ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
botName = "gitlab-amslab"
botUsername = "gitlab-amslab@webex.bot"
roomId = "Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl"

message = "hi"
header = "what"

curl -H "Content-Type: application/json" \
    -H 'Authorization: Bearer ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f' \
    -i -v -X POST \
    -d "{ \"roomId\": \"Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl\", \"text\": \"$PCV\" }" \
    https://api.ciscospark.com/v1/messages
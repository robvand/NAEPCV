#post output of PCV query to Webex Teams room
curl --request POST \
--header "Authorization: Bearer ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f" \
--form "files=@output_"$CI_PIPELINE_ID.txt"" \
--form "roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl" \
--form "text=pipeline results" \
https://api.ciscospark.com/v1/messages

#todo get specific output only
#cat output_"$CI_PIPELINE_ID".txt | grep "Later Epoch Smart Events" -A 13 > tmp.txt
#cat output_"$CI_PIPELINE_ID".txt | grep msg >> tmp.txt

curl -H "Content-Type: application/json" -H 'Authorization: Bearer "ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"'-i -v -X POST -d ' {"roomId": "Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl", "text":" \
###################\n Hello Rob, we are kicking off pipeline: \
"}' https://api.ciscospark.com/v1/messages
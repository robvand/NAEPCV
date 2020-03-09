curl --request POST \
--header "Authorization: Bearer ODc5ZDVmZGUtM2Q0Yy00MzM3LTk2YmItYjlhYzZkNTZjN2VmYTk3ZjdlY2ItOTEx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f" \
--form "files=@output_'"$CI_PIPELINE_ID.txt"" \
--form "roomId=Y2lzY29zcGFyazovL3VzL1JPT00vYmMzNGIyZjAtNjFmYS0xMWVhLWI4NTgtMTM5NTgxNTJhYmNl" \
--form "text=pipeline results" \
https://api.ciscospark.com/v1/messages